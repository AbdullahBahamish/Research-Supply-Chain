import re
import itertools
from odoo import api, models, fields  # type: ignore  # pyfly: ignore [missing-import]
from odoo.exceptions import ValidationError  # type: ignore  # pyfly: ignore [missing-import]
from .mixins import system_audit_log

class ResearchProject(models.Model):
    _name = "research.project"
    _inherit = ["research.audit.mixin", "research.exportable.mixin"]
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
    )
    project_description = fields.Text(
        string="Project Description",
    )
    lead_researcher_id = fields.Many2one(
        "research.researcher",
        string="Lead Researcher",
        ondelete="set null",
    )
    start_date = fields.Date(
        string="Project Start Date",
    )
    end_date = fields.Date(
        string="Project End Date",
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
                raise ValidationError("Project end date cannot be earlier than start date.")

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

        # 3. Difference: Find skills lead researcher has that team members lack
        lead_skills = set(map(str.strip, self.lead_researcher_id.expertise.split(","))) if self.lead_researcher_id and self.lead_researcher_id.expertise else set()
        unique_to_lead = lead_skills - set().union(*all_skill_sets[1:]) if len(all_skill_sets) > 1 else lead_skills

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