from odoo import models, fields, api  # type: ignore  # pyfly: ignore [missing-import]
from odoo.exceptions import ValidationError  # type: ignore  # pyfly: ignore [missing-import]

class ResearchRequirement(models.Model):
    _name = "research.requirement"
    _description = "Research Requirement"
    _rec_name = "name"

    project_id = fields.Many2one(
        "research.project",
        string="Project",
        required=True,
        ondelete="cascade",
    )
    category = fields.Selection(
        [
            ("dataset", "Dataset"),
            ("hardware", "Hardware"),
            ("software", "Software"),
            ("service", "Service"),
            ("expertise", "Expertise"),
            ("other", "Other"),
        ],
        string="Category",
        default="hardware",
        required=True,
    )
    name = fields.Char(
        string="Requirement Name",
        required=True,
    )
    description = fields.Text(
        string="Description",
    )
    quantity = fields.Float(
        string="Quantity",
        default=1.0,
    )
    priority = fields.Selection(
        [
            ("low", "Low"),
            ("medium", "Medium"),
            ("high", "High"),
        ],
        string="Priority",
        default="medium",
        required=True,
    )
    status = fields.Selection(
        [
            ("requested", "Requested"),
            ("approved", "Approved"),
            ("fulfilled", "Fulfilled"),
            ("cancelled", "Cancelled"),
        ],
        string="Status",
        default="requested",
        required=True,
    )
    requested_date = fields.Date(
        string="Requested Date",
        default=fields.Date.context_today,
    )
    needed_by = fields.Date(
        string="Needed By",
    )

    @api.constrains("quantity")
    def _check_quantity(self):
        for record in self:
            if record.quantity <= 0.0:
                raise ValidationError("Requirement quantity must be greater than zero.")

    @api.constrains("requested_date", "needed_by")
    def _check_dates(self):
        for record in self:
            if record.requested_date and record.needed_by and record.needed_by < record.requested_date:
                raise ValidationError("Needed by date cannot be earlier than requested date.")
