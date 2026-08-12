from odoo import models, fields, api  # type: ignore  # pyfly: ignore [missing-import]
from odoo.exceptions import ValidationError  # type: ignore  # pyfly: ignore [missing-import]

class ProjectBudget(models.Model):
    _name = "project.budget"
    _inherit = ["research.audit.mixin"]
    _description = "Project Budget"
    _rec_name = "project_id"

    project_id = fields.Many2one(
        "research.project",
        string="Project",
        required=True,
        ondelete="cascade",
    )
    currency_id = fields.Many2one(
        "res.currency",
        string="Currency",
        default=lambda self: self.env.company.currency_id,
        required=True,
    )
    total_amount = fields.Monetary(
        string="Total Amount",
        currency_field="currency_id",
        required=True,
        default=0.0,
    )
    spent_amount = fields.Monetary(
        string="Spent Amount",
        currency_field="currency_id",
        default=0.0,
    )
    remaining_amount = fields.Monetary(
        string="Remaining Amount",
        currency_field="currency_id",
        compute="_compute_remaining_amount",
        store=True,
    )
    start_date = fields.Date(
        string="Start Date",
    )
    end_date = fields.Date(
        string="End Date",
    )

    @api.constrains("project_id")
    def _check_project_budget_unique(self):
        for record in self:
            if record.project_id:
                count = self.search_count([
                    ("project_id", "=", record.project_id.id),
                    ("id", "!=", record.id),
                ])
                if count > 0:
                    raise ValidationError("A project can only have one budget record.")

    @api.depends("total_amount", "spent_amount")
    def _compute_remaining_amount(self):
        for record in self:
            record.remaining_amount = record.total_amount - record.spent_amount

    @api.constrains("total_amount", "spent_amount")
    def _check_amounts(self):
        for record in self:
            if record.total_amount < 0.0:
                raise ValidationError("Total budget amount cannot be negative.")
            if record.spent_amount < 0.0:
                raise ValidationError("Spent budget amount cannot be negative.")

    @api.constrains("start_date", "end_date")
    def _check_dates(self):
        for record in self:
            if record.start_date and record.end_date and record.end_date < record.start_date:
                raise ValidationError("Budget end date cannot be earlier than start date.")

    # ------------------ Magic Methods & Operator Overloading ------------------

    def __str__(self) -> str:
        """Magic Method: Friendly string formatting."""
        return f"ProjectBudget(Project={self.project_id.project_name}, Total=${self.total_amount:,.2f})"

    def __add__(self, other: "ProjectBudget") -> dict:
        """Operator Overloading: Overloads '+' to calculate combined budget totals."""
        if not isinstance(other, ProjectBudget):
            return NotImplemented
        return {
            "combined_total": self.total_amount + other.total_amount,
            "combined_spent": self.spent_amount + other.spent_amount,
            "combined_remaining": self.remaining_amount + other.remaining_amount,
        }

    def __eq__(self, other) -> bool:
        """Operator Overloading: Overloads '==' to compare budget amounts."""
        if not isinstance(other, ProjectBudget):
            return False
        return self.total_amount == other.total_amount

    def is_budget_positive(self) -> bool:
        """Domain Helper: Checks if remaining budget amount is positive (> 0.0)."""
        self.ensure_one()
        return self.remaining_amount > 0.0

    # ------------------ Properties & Error Handling ------------------

    @property
    def utilization_percentage(self) -> float:
        """Property: Managed getter calculating budget utilization percentage."""
        try:
            percentage = (self.spent_amount / self.total_amount) * 100.0
        except ZeroDivisionError:
            percentage = 0.0
        else:
            pass  # Executed if no exception occurred
        finally:
            pass  # Always executed for cleanup
        return percentage

