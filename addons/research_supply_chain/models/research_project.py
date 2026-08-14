import re
import itertools
from odoo import api, models, fields  # type: ignore  # pyfly: ignore [missing-import]
from odoo.exceptions import ValidationError  # type: ignore  # pyfly: ignore [missing-import]
from .mixins import system_audit_log

class ResearchProject(models.Model):
    _name = "research.project"
    _inherit = [
        "research.audit.mixin",
        "research.exportable.mixin",
        "mail.thread",
        "mail.activity.mixin",
    ]
    _description = "Research Project"
    _rec_name = "project_name"

    # Compiled Regex pattern for project sequence validation (e.g. PRJ00001 or PRJ-2026-001)
    CODE_REGEX = re.compile(r"^(PRJ\d{5}|PRJ-\d{4}-\d{3,5}|New)$")

    code = fields.Char(
        string="Project Code",
        readonly=True,
        copy=False,
    )
    project_name = fields.Char(
        string="Project Title",
        required=True,
        tracking=True,
    )
    project_description = fields.Text(
        string="Project Description",
    )
    visibility = fields.Selection(
        [
            ("public", "Public"),
            ("private", "Private"),
        ],
        string="Visibility",
        default="public",
        required=True,
        tracking=True,
        help="Public projects are visible to all users; Private projects are visible only to team members and managers.",
    )
    analytic_account_id = fields.Many2one(
        "account.analytic.account",
        string="Analytic Account",
        ondelete="set null",
        help="Analytic Account for standard financial accounting & budget tracking.",
    )
    lead_researcher_id = fields.Many2one(
        "research.researcher",
        string="Lead Researcher",
        ondelete="set null",
        tracking=True,
    )
    start_date = fields.Date(
        string="Project Start Date",
        tracking=True,
    )
    end_date = fields.Date(
        string="Project End Date",
        tracking=True,
    )
    project_status = fields.Selection(
        [
            ("proposed", "Proposed"),
            ("approved", "Approved"),
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
            ("archived", "Archived"),
        ],
        string="Status",
        default="proposed",
        required=True,
        tracking=True,
    )
    active = fields.Boolean(
        default=True,
    )
    researcher_line_ids = fields.One2many(
        "research.project.researcher",
        "project_id",
        string="Team Members",
    )
    budget_ids = fields.One2many(
        "project.budget",
        "project_id",
        string="Budgets",
    )
    requirement_ids = fields.One2many(
        "research.requirement",
        "project_id",
        string="Requirements",
    )
    resource_ids = fields.One2many(
        "research.resource",
        "owner_project_id",
        string="Owned Resources",
    )
    experiment_ids = fields.One2many(
        "research.experiment",
        "project_id",
        string="Experiments",
    )
    paper_ids = fields.One2many(
        "research.paper",
        "project_id",
        string="Research Papers",
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id,
    )
    total_budget_amount = fields.Monetary(
        string="Total Budget",
        compute="_compute_budget_totals",
        inverse="_inverse_total_budget_amount",
        currency_field="currency_id",
        aggregator="sum",
    )
    total_spent_amount = fields.Monetary(
        string="Total Spent",
        compute="_compute_budget_totals",
        inverse="_inverse_total_spent_amount",
        currency_field="currency_id",
        aggregator="sum",
    )
    remaining_budget_amount = fields.Monetary(
        string="Remaining Budget",
        compute="_compute_budget_totals",
        inverse="_inverse_remaining_budget_amount",
        currency_field="currency_id",
        aggregator="sum",
    )
    budget_utilization = fields.Float(
        string="Budget Utilization (%)",
        compute="_compute_budget_totals",
        inverse="_inverse_budget_utilization",
        aggregator="avg",
    )
    experiment_count = fields.Integer(
        string="Experiment Count",
        compute="_compute_counts",
        inverse="_inverse_experiment_count",
        aggregator="sum",
    )
    paper_count = fields.Integer(
        string="Paper Count",
        compute="_compute_counts",
        inverse="_inverse_paper_count",
        aggregator="sum",
    )

    @api.depends("budget_ids.total_amount", "budget_ids.spent_amount", "budget_ids.remaining_amount")
    def _compute_budget_totals(self):
        for project in self:
            tot = sum(b.total_amount for b in project.budget_ids)
            spent = sum(b.spent_amount for b in project.budget_ids)
            rem = sum(b.remaining_amount for b in project.budget_ids)
            project.total_budget_amount = tot
            project.total_spent_amount = spent
            project.remaining_budget_amount = rem
            project.budget_utilization = (spent / tot * 100.0) if tot else 0.0

    def _inverse_total_budget_amount(self):
        for project in self:
            if project.budget_ids:
                project.budget_ids[0].total_amount = project.total_budget_amount
            elif project.total_budget_amount:
                self.env["project.budget"].create({
                    "project_id": project.id,
                    "total_amount": project.total_budget_amount,
                })

    def _inverse_total_spent_amount(self):
        for project in self:
            if project.budget_ids:
                project.budget_ids[0].spent_amount = project.total_spent_amount
            elif project.total_spent_amount:
                self.env["project.budget"].create({
                    "project_id": project.id,
                    "spent_amount": project.total_spent_amount,
                })

    def _inverse_remaining_budget_amount(self):
        for project in self:
            if project.budget_ids:
                project.budget_ids[0].remaining_amount = project.remaining_budget_amount
            elif project.remaining_budget_amount:
                self.env["project.budget"].create({
                    "project_id": project.id,
                    "total_amount": project.remaining_budget_amount,
                    "spent_amount": 0.0,
                })

    def _inverse_budget_utilization(self):
        for project in self:
            if project.total_budget_amount:
                project.total_spent_amount = project.total_budget_amount * (project.budget_utilization / 100.0)

    @api.depends("experiment_ids", "paper_ids")
    def _compute_counts(self):
        for project in self:
            project.experiment_count = len(project.experiment_ids)
            project.paper_count = len(project.paper_ids)

    def _inverse_experiment_count(self):
        for project in self:
            current_count = len(project.experiment_ids)
            target_count = project.experiment_count
            if target_count > current_count:
                for i in range(current_count, target_count):
                    self.env["research.experiment"].create({
                        "project_id": project.id,
                        "name": f"New Experiment {i + 1}",
                    })
            elif target_count < current_count and target_count >= 0:
                to_remove = project.experiment_ids[target_count:]
                to_remove.unlink()

    def _inverse_paper_count(self):
        for project in self:
            current_count = len(project.paper_ids)
            target_count = project.paper_count
            if target_count > current_count:
                for i in range(current_count, target_count):
                    self.env["research.paper"].create({
                        "project_id": project.id,
                        "paper_name": f"New Research Paper {i + 1}",
                    })
            elif target_count < current_count and target_count >= 0:
                to_remove = project.paper_ids[target_count:]
                to_remove.unlink()

    @api.onchange("start_date", "end_date")
    def _onchange_dates(self):
        if self.start_date and self.end_date and self.end_date < self.start_date:
            return {
                "warning": {
                    "title": "Invalid Project Dates",
                    "message": "The project end date is scheduled before the start date.",
                }
            }

    @api.onchange("lead_researcher_id")
    def _onchange_lead_researcher(self):
        if self.lead_researcher_id:
            existing_researchers = self.researcher_line_ids.mapped("researcher_id")
            if self.lead_researcher_id not in existing_researchers:
                self.researcher_line_ids = [(0, 0, {
                    "researcher_id": self.lead_researcher_id.id,
                    "role": "Lead Researcher",
                    "allocated_pct": 100.0,
                })]

    @api.model_create_multi
    @system_audit_log("Create Research Project")
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("code"):
                vals["code"] = (
                    self.env["ir.sequence"].next_by_code("research.project")
                    or "New"
                )
        return super().create(vals_list)

    @api.constrains("code")
    def _check_code_format(self):
        """Demonstrates Regular Expressions (re.match)."""
        for record in self:
            if record.code and not self.CODE_REGEX.match(record.code):
                raise ValidationError(f"Project code '{record.code}' fails format validation.")

    @api.constrains("start_date", "end_date")
    def _check_project_dates(self):
        for record in self:
            if record.start_date and record.end_date and record.end_date < record.start_date:
                raise ValidationError(
                    "❌ Invalid Project Dates\n\n"
                    f"Project '{record.project_name}' has an end date ({record.end_date}) "
                    f"that is earlier than its start date ({record.start_date}).\n"
                    "Please correct the dates before saving."
                )

    @api.constrains("project_name")
    def _check_project_name(self):
        for record in self:
            if len((record.project_name or "").strip()) < 5:
                raise ValidationError(
                    "❌ Project Title Too Short\n\n"
                    "Project title must be at least 5 characters long. "
                    f"'{record.project_name}' is too short.\n"
                    "Please provide a more descriptive title."
                )

    @api.constrains("project_status", "start_date")
    def _check_status_requires_start_date(self):
        statuses_requiring_dates = ("in_progress", "completed")
        for record in self:
            if record.project_status in statuses_requiring_dates and not record.start_date:
                raise ValidationError(
                    f"❌ Start Date Required\n\n"
                    f"A project with status '{record.project_status.replace('_', ' ').title()}' "
                    "must have a start date set.\n"
                    "Please enter the project start date."
                )

    @api.constrains("project_status", "end_date")
    def _check_completed_requires_end_date(self):
        for record in self:
            if record.project_status == "completed" and not record.end_date:
                raise ValidationError(
                    "❌ End Date Required for Completed Projects\n\n"
                    f"Project '{record.project_name}' is marked as Completed "
                    "but has no end date recorded.\n"
                    "Please set the project end date."
                )

    @api.constrains("lead_researcher_id", "researcher_line_ids")
    def _check_lead_is_team_member(self):
        for record in self:
            if record.lead_researcher_id and record.researcher_line_ids:
                team_researchers = record.researcher_line_ids.mapped("researcher_id")
                if record.lead_researcher_id not in team_researchers:
                    raise ValidationError(
                        "❌ Lead Researcher Not in Team\n\n"
                        f"'{record.lead_researcher_id.name}' is set as Lead Researcher "
                        "but is not listed in the project team members.\n"
                        "Please add them to the Team Members tab or change the lead researcher."
                    )

    def action_analyze_team_skills(self):
        """
        Demonstrates Sets & Set Operations:
        - Union (|)
        - Intersection (&)
        - Difference (-)
        """
        self.ensure_one()
        all_skill_sets = []
        for line in self.researcher_line_ids:
            if line.researcher_id.expertise:
                # Split skills by comma into a set
                skills = set(map(str.strip, line.researcher_id.expertise.split(",")))
                all_skill_sets.append(skills)

        if not all_skill_sets:
            return {"total_unique_skills": [], "shared_skills": []}

        # 1. Union: Combine all unique skills across team members using functools / reduce or set.union
        total_unique = set().union(*all_skill_sets)

        # 2. Intersection: Find core skills shared by all team members
        shared_core = set.intersection(*all_skill_sets) if len(all_skill_sets) > 1 else total_unique

        # 3. Difference: Find skills lead researcher has that other team members lack
        lead_skills = set(map(str.strip, self.lead_researcher_id.expertise.split(","))) if self.lead_researcher_id and self.lead_researcher_id.expertise else set()
        other_team_skill_sets = [
            set(map(str.strip, line.researcher_id.expertise.split(",")))
            for line in self.researcher_line_ids
            if line.researcher_id != self.lead_researcher_id and line.researcher_id.expertise
        ]
        other_skills_union = set().union(*other_team_skill_sets) if other_team_skill_sets else set()
        unique_to_lead = lead_skills - other_skills_union

        return {
            "total_unique_skills": list(total_unique),
            "shared_core_skills": list(shared_core),
            "unique_to_lead": list(unique_to_lead),
        }

    def action_get_functional_summary(self):
        """
        Demonstrates Functional Programming (map, filter, lambda):
        - map() to extract titles
        - filter() to find completed experiments
        - sum() with generator expression
        """
        self.ensure_one()
        # 1. filter() + lambda: Get completed experiments
        completed_exps = list(filter(lambda exp: exp.status == 'completed', self.experiment_ids))

        # 2. map() + lambda: Get names of completed experiments
        completed_names = list(map(lambda exp: exp.name.upper(), completed_exps))

        # 3. Generator expression + sum: Total requirements quantity
        total_req_qty = sum(req.quantity for req in self.requirement_ids)

        return {
            "completed_count": len(completed_exps),
            "completed_names": completed_names,
            "total_requirements_quantity": total_req_qty,
        }

    @api.model
    def cron_update_project_statuses(self):
        """
        Cron function: Automatically updates project statuses based on start and end dates.
        - Moves 'approved' or 'proposed' projects to 'in_progress' if start_date <= today.
        - Logs audit notices for 'in_progress' projects whose end_date is past today.
        """
        today = fields.Date.context_today(self)

        # 1. Transition proposed/approved projects to in_progress if start_date <= today
        starting_projects = self.search([
            ("project_status", "in", ["proposed", "approved"]),
            ("start_date", "!=", False),
            ("start_date", "<=", today),
        ])
        for project in starting_projects:
            project.project_status = "in_progress"
            project._log_system_event(
                f"Cron Job: Project status automatically updated to 'In Progress' (Start Date: {project.start_date})."
            )

        # 2. Flag overdue in_progress projects
        overdue_projects = self.search([
            ("project_status", "=", "in_progress"),
            ("end_date", "!=", False),
            ("end_date", "<", today),
        ])
        for project in overdue_projects:
            project._log_system_event(
                f"Cron Job Alert: Project end date ({project.end_date}) has passed. Project remains in progress."
            )

        return True