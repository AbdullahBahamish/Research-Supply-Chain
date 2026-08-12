from odoo import models, fields, api  # type: ignore  # pyfly: ignore [missing-import]
from odoo.exceptions import ValidationError  # type: ignore  # pyfly: ignore [missing-import]

class ProjectBudget(models.Model):
    _name = "project.budget"
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
