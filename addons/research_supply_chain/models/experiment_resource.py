from odoo import models, fields, api  # type: ignore  # pyfly: ignore [missing-import]
from odoo.exceptions import ValidationError  # type: ignore  # pyfly: ignore [missing-import]

class ExperimentResource(models.Model):
    _name = "research.experiment.resource"
    _description = "Experiment Resource Allocation"

    experiment_id = fields.Many2one(
        "research.experiment",
        string="Experiment",
        required=True,
        ondelete="cascade",
    )
    resource_id = fields.Many2one(
        "research.resource",
        string="Resource",
        required=True,
        ondelete="cascade",
    )
    purpose = fields.Char(
        string="Purpose",
    )
    quantity = fields.Float(
        string="Quantity",
        default=1.0,
    )

    @api.constrains("experiment_id", "resource_id")
    def _check_experiment_resource_unique(self):
        for record in self:
            if record.experiment_id and record.resource_id:
                count = self.search_count([
                    ("experiment_id", "=", record.experiment_id.id),
                    ("resource_id", "=", record.resource_id.id),
                    ("id", "!=", record.id),
                ])
                if count > 0:
                    raise ValidationError("A resource can only be assigned once per experiment.")

    @api.constrains("quantity")
    def _check_quantity(self):
        for record in self:
            if record.quantity <= 0.0:
                raise ValidationError("Resource quantity assigned to an experiment must be greater than zero.")
