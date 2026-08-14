from odoo import models, fields, api  # type: ignore  # pyfly: ignore [missing-import]
from odoo.exceptions import ValidationError  # type: ignore  # pyfly: ignore [missing-import]

class Experiment(models.Model):
    _name = "research.experiment"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Research Experiment"
    _rec_name = "name"

    project_id = fields.Many2one(
        "research.project",
        string="Project",
        required=True,
        ondelete="cascade",
        tracking=True,
    )
    name = fields.Char(
        string="Experiment Title",
        required=True,
        tracking=True,
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
        tracking=True,
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
    resource_count = fields.Integer(
        string="Resource Count",
        compute="_compute_counts",
        inverse="_inverse_resource_count",
        aggregator="sum",
    )
    output_count = fields.Integer(
        string="Output Count",
        compute="_compute_counts",
        inverse="_inverse_output_count",
        aggregator="sum",
    )

    @api.depends("experiment_resource_ids", "output_ids")
    def _compute_counts(self):
        for record in self:
            record.resource_count = len(record.experiment_resource_ids)
            record.output_count = len(record.output_ids)

    def _inverse_resource_count(self):
        for record in self:
            current_count = len(record.experiment_resource_ids)
            target_count = record.resource_count
            if target_count > current_count:
                default_resource = self.env["research.resource"].search([], limit=1)
                if default_resource:
                    for i in range(current_count, target_count):
                        self.env["research.experiment.resource"].create({
                            "experiment_id": record.id,
                            "resource_id": default_resource.id,
                            "purpose": f"Allocated resource {i + 1}",
                        })
            elif target_count < current_count and target_count >= 0:
                to_remove = record.experiment_resource_ids[target_count:]
                to_remove.unlink()

    def _inverse_output_count(self):
        for record in self:
            current_count = len(record.output_ids)
            target_count = record.output_count
            if target_count > current_count:
                for i in range(current_count, target_count):
                    self.env["research.output"].create({
                        "experiment_id": record.id,
                        "name": f"New Output {i + 1}",
                    })
            elif target_count < current_count and target_count >= 0:
                to_remove = record.output_ids[target_count:]
                to_remove.unlink()

    @api.onchange("project_id")
    def _onchange_project_id(self):
        if self.project_id:
            if not self.start_date:
                self.start_date = self.project_id.start_date
            if not self.end_date:
                self.end_date = self.project_id.end_date

    # ─── Validation Constraints ───────────────────────────────────────────────

    @api.constrains("start_date", "end_date")
    def _check_experiment_dates(self):
        for record in self:
            if record.start_date and record.end_date and record.end_date < record.start_date:
                raise ValidationError(
                    "❌ Invalid Experiment Dates\n\n"
                    f"Experiment '{record.name}' has an end date ({record.end_date}) "
                    f"that is earlier than its start date ({record.start_date}).\n"
                    "Please set an end date on or after the start date."
                )

    @api.constrains("name", "project_id")
    def _check_unique_name_per_project(self):
        for record in self:
            if record.name and record.project_id:
                duplicate = self.search_count([
                    ("name", "=", record.name.strip()),
                    ("project_id", "=", record.project_id.id),
                    ("id", "!=", record.id),
                ])
                if duplicate:
                    raise ValidationError(
                        "❌ Duplicate Experiment Title\n\n"
                        f"An experiment named '{record.name}' already exists "
                        f"in project '{record.project_id.name}'.\n"
                        "Please provide a unique experiment title within this project."
                    )

    @api.constrains("status", "objective")
    def _check_objective_required_when_running(self):
        for record in self:
            if record.status in ("running", "completed") and not (record.objective or "").strip():
                raise ValidationError(
                    "❌ Objective Required\n\n"
                    f"Experiment '{record.name}' cannot be set to status "
                    f"'{record.status.title()}' without an Objective.\n"
                    "Please fill in the Objective field before updating the status."
                )

    @api.constrains("status", "start_date")
    def _check_running_requires_start_date(self):
        for record in self:
            if record.status == "running" and not record.start_date:
                raise ValidationError(
                    "❌ Start Date Required\n\n"
                    f"Experiment '{record.name}' is marked as 'Running' but has no start date.\n"
                    "Please enter the start date of the experiment."
                )

    @api.constrains("status", "end_date")
    def _check_completed_requires_end_date(self):
        for record in self:
            if record.status == "completed" and not record.end_date:
                raise ValidationError(
                    "❌ End Date Required\n\n"
                    f"Experiment '{record.name}' is marked as 'Completed' but has no end date.\n"
                    "Please enter the completion date of the experiment."
                )

    @api.model
    def cron_update_experiment_statuses(self):
        """
        Cron function: Updates experiment statuses based on start and end dates.
        - Moves 'planned' experiments to 'running' if start_date <= today.
        """
        today = fields.Date.context_today(self)
        starting_experiments = self.search([
            ("status", "=", "planned"),
            ("start_date", "!=", False),
            ("start_date", "<=", today),
        ])
        for exp in starting_experiments:
            exp.status = "running"

        return True