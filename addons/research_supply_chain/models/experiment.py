from datetime import timedelta
from odoo import api, fields, models  # type: ignore  # pyfly: ignore [missing-import]
from odoo.exceptions import ValidationError  # type: ignore  # pyfly: ignore [missing-import]


class Experiment(models.Model):
    _name = "research.experiment"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Research Experiment"
    _rec_name = "name"
    _order = "status, start_date desc, name"

    code = fields.Char(
        string="Experiment Code",
        readonly=True,
        copy=False,
    )
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
    owner_id = fields.Many2one(
        "res.users",
        string="Owner",
        default=lambda self: self.env.user,
        index=True,
        tracking=True,
        help=(
            "The researcher responsible for this experiment. Defaults to "
            "its creator. Only the owner (or a Research Manager/"
            "Administrator) may modify or delete this record - see "
            "research_security.xml."
        ),
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

    _unique_name_per_project = models.Constraint(
        "UNIQUE(project_id, name)",
        "An experiment with this title already exists in the selected project.",
    )
    _check_date_range = models.Constraint(
        "CHECK(start_date IS NULL OR end_date IS NULL OR end_date >= start_date)",
        "The experiment's end date must be on or after its start date.",
    )
    _check_running_start_date = models.Constraint(
        "CHECK(status != 'running' OR start_date IS NOT NULL)",
        "Running experiments must have a start date.",
    )
    _check_completed_end_date = models.Constraint(
        "CHECK(status != 'completed' OR end_date IS NOT NULL)",
        "Completed experiments must have an end date.",
    )
    _check_objective_required_for_active_status = models.Constraint(
        "CHECK(status NOT IN ('running', 'completed') OR (objective IS NOT NULL AND trim(objective) != ''))",
        "An objective is required before an experiment can be marked as 'Running' or 'Completed'.",
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

    def action_start(self):
        for record in self:
            record.check_access_rights("write")
            record.check_access_rule("write")
            if record.status != "planned":
                continue
            if not record.objective or not record.objective.strip():
                raise ValidationError(
                    f"An objective is required before experiment '{record.name}' can be started."
                )
            if not record.start_date:
                record.start_date = fields.Date.context_today(record)
            record.status = "running"
            if hasattr(record, "message_post"):
                record.message_post(body=f"Experiment '{record.name}' started.")
            if hasattr(record, "activity_schedule"):
                record.activity_schedule(
                    "mail.mail_activity_data_todo",
                    date_deadline=fields.Date.context_today(record) + timedelta(days=7),
                    summary="Experiment Progress Review",
                    note=f"Review progress for experiment: {record.name}",
                    user_id=record.owner_id.id if record.owner_id else self.env.uid,
                )
        return True

    def action_complete(self):
        for record in self:
            record.check_access_rights("write")
            record.check_access_rule("write")
            if record.status != "running":
                continue
            if not record.end_date:
                record.end_date = fields.Date.context_today(record)
            record.status = "completed"
            if hasattr(record, "message_post"):
                record.message_post(body=f"Experiment '{record.name}' marked as completed.")
        return True

    def action_cancel(self):
        for record in self:
            record.check_access_rights("write")
            record.check_access_rule("write")
            if record.status in ["completed", "cancelled"]:
                continue
            record.status = "cancelled"
            if hasattr(record, "message_post"):
                record.message_post(body=f"Experiment '{record.name}' cancelled.")
        return True

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get("code"):
                vals["code"] = (
                    self.env["ir.sequence"].next_by_code("research.experiment")
                    or "New"
                )
        return super().create(vals_list)