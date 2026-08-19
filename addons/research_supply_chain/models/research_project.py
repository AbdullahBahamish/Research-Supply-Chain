import re
from odoo import api, fields, models  # type: ignore  # pyfly: ignore [missing-import]
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
    _order = "project_status, start_date desc, project_name"

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
        index=True,
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
        index=True,
    )
    active = fields.Boolean(
        default=True,
    )
    tag_ids = fields.Many2many(
        "research.project.tag",
        string="Tags",
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

    _code_unique = models.Constraint(
        "UNIQUE(code)",
        "Project code must be unique across all projects.",
    )
    _check_dates_valid = models.Constraint(
        "CHECK(start_date IS NULL OR end_date IS NULL OR end_date >= start_date)",
        "Project end date must be on or after the start date.",
    )
    _check_project_name_length = models.Constraint(
        "CHECK(LENGTH(TRIM(project_name)) >= 5)",
        "Project title must be at least 5 characters long.",
    )
    _check_status_requires_start_date = models.Constraint(
        "CHECK(project_status NOT IN ('in_progress', 'completed') OR start_date IS NOT NULL)",
        "Project status requires a start date.",
    )
    _check_completed_requires_end_date = models.Constraint(
        "CHECK(project_status != 'completed' OR end_date IS NOT NULL)",
        "Completed projects must have an end date.",
    )

    @api.depends("budget_ids.total_amount", "budget_ids.spent_amount", "budget_ids.remaining_amount")
    def _compute_budget_totals(self):
        for project in self:
            total_b = sum(b.total_amount for b in project.budget_ids)
            spent = sum(b.spent_amount for b in project.budget_ids)
            rem = sum(b.remaining_amount for b in project.budget_ids)
            project.total_budget_amount = total_b
            project.total_spent_amount = spent
            project.remaining_budget_amount = rem
            project.budget_utilization = (spent / total_b * 100.0) if total_b else 0.0

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
            if project.budget_ids:
                total_b = project.budget_ids[0].total_amount
                if total_b:
                    project.budget_ids[0].spent_amount = total_b * (project.budget_utilization / 100.0)

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
            elif 0 <= target_count < current_count:
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
            elif 0 <= target_count < current_count:
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

    def action_analyze_team_skills(self):
        self.ensure_one()
        all_skill_sets = []
        for line in self.researcher_line_ids:
            if line.researcher_id.expertise:
                skills = set(map(str.strip, line.researcher_id.expertise.split(",")))
                all_skill_sets.append(skills)

        if not all_skill_sets:
            return {"total_unique_skills": [], "shared_skills": []}

        total_unique = set().union(*all_skill_sets)
        shared_core = set.intersection(*all_skill_sets) if len(all_skill_sets) > 1 else total_unique

        lead_skills = (
            set(map(str.strip, self.lead_researcher_id.expertise.split(",")))
            if self.lead_researcher_id and self.lead_researcher_id.expertise
            else set()
        )
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
        self.ensure_one()
        # completed_exps = list(filter(lambda exp: exp.status == "completed", self.experiment_ids))
        # completed_names = list(map(lambda exp: exp.name.upper(), completed_exps))
        # total_req_qty = sum(req.quantity for req in self.requirement_ids)

        # return {
        #     "completed_count": len(completed_exps),
        #     "completed_names": completed_names,
        #     "total_requirements_quantity": total_req_qty,
        # }

        completed_exps = self.experiment_ids.filtered(lambda exp: exp.status == "completed")

        return {
            "completed_count": len(completed_exps),
            "completed_names": completed_exps.mapped(lambda exp: exp.name.upper()),
            "total_req_qty": sum(self.requirement_ids.mapped('quantity')),
        }

    def unlink(self):
        if self.filtered(
            lambda project: project.project_status in {"in_progress", "completed"}
        ):
            raise ValidationError("Project cannot be deleted because it is in progress or completed.")

        return super().unlink()    

    @api.model
    def cron_update_project_statuses(self):
        today = fields.Date.context_today(self)
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

    @api.model
    def _name_search(self, name="", domain=None, operator="ilike", limit=100, order=None):
        domain = domain or []
        if name:
            domain = ["|", ("project_name", operator, name), ("code", operator, name)] + domain
        return self._search(domain, limit=limit, order=order)


    # Prevent editing core project properties when status is completed or archived,
    # and log system audit entries when state/budget fields change.
    # @api.onchange()
    # def _onchange_core_properties(self):
    #     for record in self: 
    #         if record.status in ['completed', 'archived']:
    #             raise ValidationError(f"Core properties of a project cannot be edited when the project is {record.status}")

    def write(self, vals):
        protected_fields = {
            "project_name",
            "project_description",
            "visibility",
            "lead_researcher_id",
            "start_date",
            "end_date",
        }
        
        if protected_fields.intersection(vals):
            for record in self:
                if record.project_status in {"completed", "archived"}:
                    raise ValidationError(
                        f"Core properties of project '{record.project_name}' "
                        f"cannot be edited when it is {record.project_status}."
                    )
        return super().write(vals)