from odoo import api, models, fields  # type: ignore  # pyfly: ignore [missing-import]
from odoo.exceptions import ValidationError  # type: ignore  # pyfly: ignore [missing-import]

class ResearchProject(models.Model):
    _name = "research.project"
    _description = "Research Project"
    _rec_name = "project_name"

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
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("code"):
                vals["code"] = (
                    self.env["ir.sequence"].next_by_code("research.project")
                    or "New"
                )
        return super().create(vals_list)

    @api.constrains("start_date", "end_date")
    def _check_project_dates(self):
        for record in self:
            if record.start_date and record.end_date and record.end_date < record.start_date:
                raise ValidationError("Project end date cannot be earlier than start date.")