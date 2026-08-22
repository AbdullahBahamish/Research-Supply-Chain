from odoo import models, fields, api  # type: ignore  # pyfly: ignore [missing-import]
from odoo.exceptions import ValidationError  # type: ignore  # pyfly: ignore [missing-import]

class ProjectBudget(models.Model):
    _name = "project.budget"
    _inherit = ["research.audit.mixin"]
    _description = "Project Budget"
    _order = "start_date desc, id desc"
    _rec_name = "project_id"

    project_id = fields.Many2one(
        "research.project",
        string="Project",
        required=True,
        ondelete="cascade",
    )
    analytic_account_id = fields.Many2one(
        "account.analytic.account",
        string="Analytic Account",
        related="project_id.analytic_account_id",
        store=True,
        readonly=False,
        help="Linked Odoo Analytic Account for financial budget tracking.",
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
        inverse="_inverse_remaining_amount",
        store=True,
    )
    utilization_rate = fields.Float(
        string="Budget Utilization (%)",
        compute="_compute_utilization_rate",
        help="Percentage of total allocated budget spent.",
    )
    start_date = fields.Date(
        string="Start Date",
    )
    end_date = fields.Date(
        string="End Date",
    )

    @api.depends("total_amount", "spent_amount")
    def _compute_utilization_rate(self):
        for record in self:
            if record.total_amount > 0.0:
                record.utilization_rate = (record.spent_amount / record.total_amount) * 100.0
            else:
                record.utilization_rate = 0.0

    @api.depends("total_amount", "spent_amount")
    def _compute_remaining_amount(self):
        for record in self:
            record.remaining_amount = record.total_amount - record.spent_amount

    def _inverse_remaining_amount(self):
        for record in self:
            record.total_amount = record.spent_amount + record.remaining_amount

    _project_budget_unique = models.Constraint(
        "UNIQUE(project_id)",
        "Each project can only have one main budget record.",
    )
    _check_amounts_positive = models.Constraint(
        "CHECK(total_amount >= 0.0 AND spent_amount >= 0.0)",
        "Total and spent budget amounts cannot be negative.",
    )
    _check_dates_valid = models.Constraint(
        "CHECK(start_date IS NULL OR end_date IS NULL OR end_date >= start_date)",
        "Budget end date must be on or after the start date.",
    )

    # @api.constrains("project_id")
    # def _check_project_budget_unique(self):
    #        for record in self:
    #            if record.project_id:
    #                count = self.search_count([
    #                    ("project_id", "=", record.project_id.id),
    #                    ("id", "!=", record.id),
    #                ])
    #                if count > 0:
    #                    raise ValidationError(
    #                        "❌ Duplicate Budget Record\n\n"
    #                        f"Project '{record.project_id.project_name}' already has a budget assigned.\n"
    #                        "Each project can only have one main budget record."
    #                    )
   

    # @api.constrains("total_amount", "spent_amount")
    # def _check_amounts(self):
    #     for record in self:
    #         if record.total_amount < 0.0:
    #             raise ValidationError(
    #                 "❌ Negative Budget Amount\n\n"
    #                 "Total budget amount cannot be negative.\n"
    #                 "Please enter a valid positive total budget."
    #             )
    #         if record.spent_amount < 0.0:
    #             raise ValidationError(
    #                 "❌ Negative Spent Amount\n\n"
    #                 "Spent budget amount cannot be negative.\n"
    #                 "Please enter a valid spent amount."
    #             )


    # @api.constrains("start_date", "end_date")
    # def _check_dates(self):
    #     for record in self:
    #         if record.start_date and record.end_date and record.end_date < record.start_date:
    #             raise ValidationError(
    #                 "❌ Invalid Budget Period\n\n"
    #                 f"Budget end date ({record.end_date}) is earlier than start date ({record.start_date}).\n"
    #                 "Please correct the budget dates."
    #             )


    @api.onchange("spent_amount", "total_amount")
    def _onchange_amounts(self):
        if self.total_amount > 0.0 and self.spent_amount > self.total_amount:
            return {
                "warning": {
                    "title": "Overbudget Warning",
                    "message": f"Spent amount (${self.spent_amount:,.2f}) exceeds total allocated budget (${self.total_amount:,.2f}).",
                }
            }
        elif self.total_amount > 0.0 and (self.spent_amount / self.total_amount) >= 0.90:
            pct = (self.spent_amount / self.total_amount) * 100.0
            return {
                "warning": {
                    "title": "High Utilization Warning",
                    "message": f"Budget utilization has reached {pct:.1f}%.",
                }
            }

    @api.onchange("project_id")
    def _onchange_project_id(self):
        if self.project_id:
            if not self.start_date:
                self.start_date = self.project_id.start_date
            if not self.end_date:
                self.end_date = self.project_id.end_date

    # ------------------ Magic Methods & Domain Helpers ------------------

    def __str__(self) -> str:
        """Magic Method: Friendly string formatting for single record."""
        if len(self) == 1:
            return f"ProjectBudget(Project={self.project_id.project_name}, Total=${self.total_amount:,.2f})"
        return super().__str__()

    def combine_budget(self, other: "ProjectBudget") -> dict:
        """Helper method: Calculates combined budget totals with another budget record."""
        self.ensure_one()
        other.ensure_one()
        return {
            "combined_total": self.total_amount + other.total_amount,
            "combined_spent": self.spent_amount + other.spent_amount,
            "combined_remaining": self.remaining_amount + other.remaining_amount,
        }

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
        return percentage

    @api.model
    def cron_check_budget_alerts(self):
        """
        Cron function: Periodically audits project budgets.
        - Logs alerts for overbudget records (spent_amount > total_amount).
        - Logs warnings for high budget utilization (>= 90%).
        - Logs alerts for budgets whose end_date has expired.
        """
        today = fields.Date.context_today(self)
        budgets = self.search([])
        for budget in budgets:
            utilization = budget.utilization_percentage
            if budget.spent_amount > budget.total_amount:
                budget._log_system_event(
                    f"Cron Job Alert: Overbudget detected! Spent ${budget.spent_amount:,.2f} exceeding total ${budget.total_amount:,.2f} ({utilization:.1f}%)."
                )
            elif utilization >= 90.0:
                budget._log_system_event(
                    f"Cron Job Warning: High budget utilization detected ({utilization:.1f}% used of ${budget.total_amount:,.2f})."
                )

            if budget.end_date and budget.end_date < today:
                budget._log_system_event(
                    f"Cron Job Alert: Budget period expired on {budget.end_date}."
                )

        return True
    

    def write(self, vals):
        # Enforce validation so spent_amount 
        # cannot exceed total_budget_amount upon write operations.
        for record in self: 
            total_amount = vals.get("total_amount", record.total_amount)
            spent_amount = vals.get("spent_amount", record.spent_amount)
            
            if spent_amount > total_amount:
                raise ValidationError(
                    "spent_amount can not exceed total_budget_amount"
                )
        return super().write(vals)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            total_amount = vals.get("total_amount", 0.0)
            spent_amount = vals.get("spent_amount", 0.0)
            if spent_amount > total_amount:
                raise ValidationError(
                    "Spent amount cannot exceed total allocated budget amount."
                )

            project_id = vals.get("project_id")

            if project_id: 
                existing_budget = self.search([("project_id", "=", project_id)], limit=1)

                if existing_budget:
                    raise ValidationError(
                        f"The project '{self.env['research.project'].browse(project_id).project_name}' already has a budget assigned."
                    )

        return super().create(vals_list)

                

                

