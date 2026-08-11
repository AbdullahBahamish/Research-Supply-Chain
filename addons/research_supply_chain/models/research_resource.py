from odoo import models, fields  # type: ignore  # pyfly: ignore [missing-import]

class ResearchResource(models.Model):
    _name = "research.resource"
    _description = "Research Resource"
    _rec_name = "name"

    resource_type = fields.Selection(
        [
            ("dataset", "Dataset"),
            ("equipment", "Equipment"),
            ("software", "Software"),
            ("service", "Service"),
            ("other", "Other"),
        ],
        string="Resource Type",
        required=True,
        default="equipment",
    )
    name = fields.Char(
        string="Resource Name",
        required=True,
    )
    description = fields.Text(
        string="Description",
    )
    specification = fields.Text(
        string="Specification",
    )
    availability_status = fields.Selection(
        [
            ("available", "Available"),
            ("in_use", "In Use"),
            ("unavailable", "Unavailable"),
        ],
        string="Availability Status",
        default="available",
        required=True,
    )
    owner_project_id = fields.Many2one(
        "research.project",
        string="Owner Project",
        ondelete="set null",
    )
    notes = fields.Text(
        string="Notes",
    )
