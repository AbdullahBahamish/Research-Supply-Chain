from odoo import models, fields, api  # type: ignore  # pyfly: ignore [missing-import]
from odoo.exceptions import ValidationError  # type: ignore  # pyfly: ignore [missing-import]

class ResearchProjectResearcher(models.Model):
    _name = "research.project.researcher"
    _description = "Research Project Researcher Allocation"

    project_id = fields.Many2one(
        "research.project",
        string="Project",
        required=True,
        ondelete="cascade",
    )
    researcher_id = fields.Many2one(
        "research.researcher",
        string="Researcher",
        required=True,
        ondelete="cascade",
    )
    role = fields.Char(
        string="Role",
    )
    allocated_pct = fields.Float(
        string="Allocation (%)",
        default=100.0,
    )
    join_date = fields.Date(
        string="Join Date",
        default=fields.Date.context_today,
    )

    # ─── Validation Constraints ───────────────────────────────────────────────

    @api.constrains("project_id", "researcher_id")
    def _check_project_researcher_unique(self):
        for record in self:
            if record.project_id and record.researcher_id:
                count = self.search_count([
                    ("project_id", "=", record.project_id.id),
                    ("researcher_id", "=", record.researcher_id.id),
                    ("id", "!=", record.id),
                ])
                if count > 0:
                    raise ValidationError(
                        "❌ Duplicate Team Member\n\n"
                        f"Researcher '{record.researcher_id.name}' is already assigned to project '{record.project_id.project_name}'.\n"
                        "Each researcher can only be added once per project team."
                    )

    @api.constrains("allocated_pct")
    def _check_allocated_pct(self):
        for record in self:
            if record.allocated_pct < 0.0 or record.allocated_pct > 100.0:
                raise ValidationError(
                    "❌ Invalid Allocation Percentage\n\n"
                    f"Allocation percentage ({record.allocated_pct}%) must be between 0% and 100%.\n"
                    "Please enter a valid percentage."
                )
