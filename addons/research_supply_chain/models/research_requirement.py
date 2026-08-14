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
    product_id = fields.Many2one(
        "product.product",
        string="Catalog Product",
        ondelete="set null",
        help="Linked standard Odoo product item for procurement.",
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

    parent_id = fields.Many2one(
        "research.requirement",
        string="Parent Requirement",
        ondelete="cascade",
    )
    child_ids = fields.One2many(
        "research.requirement",
        "parent_id",
        string="Child Requirements",
    )

    # ─── Validation Constraints ───────────────────────────────────────────────

    @api.constrains("quantity")
    def _check_quantity(self):
        for record in self:
            if record.quantity <= 0.0:
                raise ValidationError(
                    "❌ Invalid Requirement Quantity\n\n"
                    f"Requirement '{record.name}' has quantity {record.quantity}.\n"
                    "Quantity must be greater than zero."
                )

    @api.constrains("requested_date", "needed_by")
    def _check_dates(self):
        for record in self:
            if record.requested_date and record.needed_by and record.needed_by < record.requested_date:
                raise ValidationError(
                    "❌ Invalid Requirement Schedule\n\n"
                    f"Requirement '{record.name}' has 'Needed By' date ({record.needed_by}) "
                    f"earlier than 'Requested Date' ({record.requested_date}).\n"
                    "Please adjust the schedule."
                )

    @api.constrains("parent_id")
    def _check_recursion(self):
        for record in self:
            if not record._check_recursion():
                raise ValidationError(
                    "❌ Circular Parent Requirement\n\n"
                    f"Requirement '{record.name}' cannot be its own parent or cause a circular hierarchy loop.\n"
                    "Please select a valid parent requirement."
                )

    @api.constrains("name")
    def _check_name_length(self):
        for record in self:
            if len((record.name or "").strip()) < 3:
                raise ValidationError(
                    "❌ Requirement Name Too Short\n\n"
                    "Requirement name must be at least 3 characters long."
                )

    @api.onchange("category")
    def _onchange_category(self):
        if self.category == "hardware":
            self.priority = "high"
        elif self.category in ["service", "expertise"]:
            self.priority = "medium"
        elif self.category in ["dataset", "software", "other"]:
            self.priority = "low"

    def calculate_recursive_total_quantity(self) -> float:
        """
        Demonstrates RECURSION:
        Recursively calculates total quantity across nested requirement trees.
        """
        self.ensure_one()
        total = self.quantity
        if not self.child_ids:
            return total

        for child in self.child_ids:
            total += child.calculate_recursive_total_quantity()

        return total

    @api.model
    def cron_check_overdue_requirements(self):
        """
        Cron function: Identifies pending requirements whose 'needed_by' date has passed.
        - Escalates priority of overdue requested or approved requirements to 'high'.
        """
        today = fields.Date.context_today(self)
        overdue_reqs = self.search([
            ("status", "in", ["requested", "approved"]),
            ("needed_by", "!=", False),
            ("needed_by", "<", today),
        ])
        for req in overdue_reqs:
            if req.priority != "high":
                req.priority = "high"

        return True
