from odoo import models, fields, api  # type: ignore  # pyfly: ignore [missing-import]
from odoo.exceptions import ValidationError  # type: ignore  # pyfly: ignore [missing-import]

class ResearchResource(models.Model):
    _name = "research.resource"
    _description = "Research Resource"
    _rec_name = "name"
    _order = "name"

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
    product_id = fields.Many2one(
        "product.product",
        string="Inventory Product",
        ondelete="set null",
        help="Linked standard Odoo inventory product catalog item.",
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
        index=True,
    )
    owner_project_id = fields.Many2one(
        "research.project",
        string="Owner Project",
        ondelete="set null",
    )
    notes = fields.Text(
        string="Notes",
    )
    active = fields.Boolean(
        default=True,
        help="Archived resources are hidden from default views.",
    )

    # ─── Validation Constraints ───────────────────────────────────────────────
    _sql_constraints = [
        models.Constraint(
            "check_name_min_length",
            "CHECK(LENGTH(TRIM(name)) >= 3)",
            "Resource name must be at least 3 characters long.",
        ),
        models.Constraint(
            "unique_resource_per_project",
            "UNIQUE(name, owner_project_id)",
            "A resource with this name already exists in the selected project.",
        ),
    ]

    # @api.constrains("name")
    # def _check_name_length(self):
    #     for record in self:
    #         if len((record.name or "").strip()) < 3:
    #             raise ValidationError(
    #                 "❌ Resource Name Too Short\n\n"
    #                 "Resource name must be at least 3 characters long.\n"
    #                 "Please provide a descriptive resource name."
    #             )

    # @api.constrains("name", "owner_project_id")
    # def _check_unique_resource_per_project(self):
    #     for record in self:
    #         if record.name and record.owner_project_id:
    #             count = self.sudo().search_count([
    #                 ("name", "=", record.name.strip()),
    #                 ("owner_project_id", "=", record.owner_project_id.id),
    #                 ("id", "!=", record.id),
    #             ])
    #             if count > 0:
    #                 raise ValidationError(
    #                     "❌ Duplicate Resource Name\n\n"
    #                     f"A resource named '{record.name}' is already owned by project '{record.owner_project_id.name}'.\n"
    #                     "Please use a unique resource name."
    #                 )
