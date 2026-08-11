from odoo import models, fields  # type: ignore  # pyfly: ignore [missing-import]

class ResearchOutput(models.Model):
    _name = "research.output"
    _description = "Research Output"
    _rec_name = "name"

    experiment_id = fields.Many2one(
        "research.experiment",
        string="Experiment",
        required=True,
        ondelete="cascade",
    )
    project_id = fields.Many2one(
        "research.project",
        string="Project",
        related="experiment_id.project_id",
        store=True,
        readonly=True,
    )
    output_type = fields.Selection(
        [
            ("paper", "Paper"),
            ("dataset", "Dataset"),
            ("software", "Software"),
            ("report", "Report"),
            ("thesis", "Thesis"),
            ("other", "Other"),
        ],
        string="Output Type",
        required=True,
        default="paper",
    )
    name = fields.Char(
        string="Title",
        required=True,
    )
    status = fields.Selection(
        [
            ("draft", "Draft"),
            ("under_review", "Under Review"),
            ("accepted", "Accepted"),
            ("published", "Published"),
        ],
        string="Status",
        default="draft",
        required=True,
    )
