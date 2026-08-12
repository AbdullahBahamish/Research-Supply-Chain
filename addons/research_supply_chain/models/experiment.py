from odoo import models, fields, api  # type: ignore  # pyfly: ignore [missing-import]
from odoo.exceptions import ValidationError  # type: ignore  # pyfly: ignore [missing-import]

class Experiment(models.Model):
    _name = "research.experiment"
    _description = "Research Experiment"
    _rec_name = "name"

    project_id = fields.Many2one(
        "research.project",
        string="Project",
        required=True,
        ondelete="cascade",
    )
    name = fields.Char(
        string="Experiment Title",
        required=True,
    )
    objective = fields.Text(
        string="Objective",
    )
    methodology = fields.Text(
        string="Methodology",
    )
    status = fields.Selection(
        [
            ("planned", "Planned"),
            ("running", "Running"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="planned",
        required=True,
    )
    start_date = fields.Date(
        string="Start Date",
    )
    end_date = fields.Date(
        string="End Date",
    )
    created_by = fields.Many2one(
        "res.users",
        string="Created By",
        default=lambda self: self.env.user,
        required=True,
    )
    experiment_resource_ids = fields.One2many(
        "research.experiment.resource",
        "experiment_id",
        string="Used Resources",
    )
    output_ids = fields.One2many(
        "research.output",
        "experiment_id",
        string="Outputs",
    )

    @api.constrains("start_date", "end_date")
    def _check_experiment_dates(self):
        for record in self:
            if record.start_date and record.end_date and record.end_date < record.start_date:
                raise ValidationError("Experiment end date cannot be earlier than start date.")