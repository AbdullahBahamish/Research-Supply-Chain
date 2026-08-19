from odoo import api, fields, models  # type: ignore  # pyfly: ignore [missing-import]
from odoo.exceptions import ValidationError  # type: ignore  # pyfly: ignore [missing-import]


class ResearchRequirement(models.Model):
    _name = "research.requirement"
    _description = "Research Requirement"
    _rec_name = "name"
    _order = "priority desc, needed_by asc, name"

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
    owner_id = fields.Many2one(
        "res.users",
        string="Owner",
        default=lambda self: self.env.user,
        index=True,
        help=(
            "The researcher who raised this requirement. Defaults to its "
            "creator. Only the owner (or a Research Manager/Administrator) "
            "may modify or delete this record."
        ),
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
        digits=(16, 2),
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
        index=True,
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
        index=True,
    )
    requested_date = fields.Date(
        string="Requested Date",
        default=fields.Date.context_today,
    )
    needed_by = fields.Date(
        string="Needed By",
        index=True,
    )
    active = fields.Boolean(
        default=True,
        help="Archived requirements are hidden from default views.",
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

    _check_positive_quantity = models.Constraint(
        "CHECK(quantity > 0)",
        "Quantity must be strictly greater than zero.",
    )
    _check_dates_chronology = models.Constraint(
        "CHECK(requested_date IS NULL OR needed_by IS NULL OR needed_by >= requested_date)",
        "The 'Needed By' date must be on or after the 'Requested Date'.",
    )
    _check_name_min_length = models.Constraint(
        "CHECK(LENGTH(TRIM(name)) >= 3)",
        "Requirement name must be at least 3 characters long.",
    )

    @api.constrains("parent_id")
    def _check_parent_recursion(self):
        if not self._check_recursion():
            raise ValidationError("Requirement cannot be its own parent")
        
        # for record in self:
        #     has_cycle = (
        #         record._has_cycle("parent_id")
        #         if hasattr(record, "_has_cycle")
        #         else not record._check_recursion("parent_id")
        #     )
        #     if has_cycle:
        #         raise ValidationError(
        #             f"Requirement '{record.name}' cannot be its own parent or cause a circular hierarchy loop."
        #         )

    @api.onchange("category")
    def _onchange_category(self):
        if self.category == "hardware":
            self.priority = "high"
        elif self.category in ["service", "expertise"]:
            self.priority = "medium"
        elif self.category in ["dataset", "software", "other"]:
            self.priority = "low"

    def calculate_recursive_total_quantity(self) -> float:
        self.ensure_one()
        total = self.quantity
        if not self.child_ids:
            return total

        for child in self.child_ids:
            total += child.calculate_recursive_total_quantity()

        return total

    @api.model
    def cron_check_overdue_requirements(self):
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

    def action_approve(self):
        for record in self:
            record.check_access_rights("write")
            record.check_access_rule("write")
            if record.status != "requested":
                continue
            record.status = "approved"
            if hasattr(record, "_log_system_event"):
                record._log_system_event(f"Requirement '{record.name}' approved for project procurement.")
        return True

    def action_fulfill(self):
        for record in self:
            record.check_access_rights("write")
            record.check_access_rule("write")
            if record.status != "approved":
                continue
            record.status = "fulfilled"
            if hasattr(record, "_log_system_event"):
                record._log_system_event(f"Requirement '{record.name}' marked as fulfilled.")
        return True

    def action_cancel(self):
        for record in self:
            record.check_access_rights("write")
            record.check_access_rule("write")
            if record.status in ["fulfilled", "cancelled"]:
                continue
            record.status = "cancelled"
            if hasattr(record, "_log_system_event"):
                record._log_system_event(f"Requirement '{record.name}' cancelled.")
        return True

    def action_reset_draft(self):
        for record in self:
            record.check_access_rights("write")
            record.check_access_rule("write")
            if record.status != "cancelled":
                continue
            record.status = "requested"
            if hasattr(record, "_log_system_event"):
                record._log_system_event(f"Requirement '{record.name}' reset to requested state.")
        return True

    @api.ondelete(at_uninstall=False)
    def _unlink_except_protected_status(self):
        protected_status = {"approved", "fulfilled"}
        if any(record.status in protected_status for record in self):
            raise ValidationError(
                "Cannot delete a requirement that has already been approved or fulfilled."
            )
        return True

    def write(self, vals):
        # Prevent modifying requirement properties once the status 
        # is fulfilled or approved, while allowing status transitions.
        for record in self:
            if record.status in {"approved", "fulfilled"}:
                non_status_fields = set(vals.keys()) - {"status"}
                if non_status_fields:
                    raise ValidationError(
                        f"Cannot modify requirement properties once it has been {record.status}."
                    )
        return super().write(vals)
        
