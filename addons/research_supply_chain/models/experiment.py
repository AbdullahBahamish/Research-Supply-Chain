from odoo import api, fields, models  # type: ignore  # pyfly: ignore [missing-import]


class Experiment(models.Model):
    _name = "research.experiment"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Research Experiment"
    _rec_name = "name"
    _order = "status, start_date desc, name"

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
    active = fields.Boolean(
        default=True,
        help="Archived experiments are hidden from default views.",
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

    _sql_constraints = [
        (
            "unique_name_per_project",
            "UNIQUE(project_id, name)",
            "An experiment with this title already exists in the selected project.",
        ),
        (
            "check_date_range",
            "CHECK(start_date IS NULL OR end_date IS NULL OR end_date >= start_date)",
            "The experiment's end date must be on or after its start date.",
        ),
        (
            "check_running_start_date",
            "CHECK(status != 'running' OR start_date IS NOT NULL)",
            "Running experiments must have a start date.",
        ),
        (
            "check_completed_end_date",
            "CHECK(status != 'completed' OR end_date IS NOT NULL)",
            "Completed experiments must have an end date.",
        ),
        (
            "check_objective_required_for_active_status",
            "CHECK(status NOT IN ('running', 'completed') OR (objective IS NOT NULL AND trim(objective) != ''))",
            "An objective is required before an experiment can be marked as 'Running' or 'Completed'.",
        ),
    ]

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
                for i in range(current_count, target_count):
                    res = self.env["research.resource"].create({
                        "name": f"New Resource {i + 1}",
                        "resource_type": "equipment",
                    })
                    self.env["research.experiment.resource"].create({
                        "experiment_id": record.id,
                        "resource_id": res.id,
                    })
            elif 0 <= target_count < current_count:
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
                        "output_type": "paper",
                    })
            elif 0 <= target_count < current_count:
                to_remove = record.output_ids[target_count:]
                to_remove.unlink()

    @api.onchange("project_id")
    def _onchange_project_id(self):
        if self.project_id:
            if not self.start_date:
                self.start_date = self.project_id.start_date
            if not self.end_date:
                self.end_date = self.project_id.end_date

    @api.model
    def cron_update_experiment_statuses(self):
        today = fields.Date.context_today(self)
        starting_experiments = self.search([
            ("status", "=", "planned"),
            ("start_date", "!=", False),
            ("start_date", "<=", today),
        ])
        for exp in starting_experiments:
            exp.status = "running"

        return True