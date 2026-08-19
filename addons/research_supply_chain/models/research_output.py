from odoo import models, fields, api  # type: ignore  # pyfly: ignore [missing-import]
from odoo.exceptions import ValidationError  # type: ignore  # pyfly: ignore [missing-import]

class ResearchOutput(models.Model):
    _name = "research.output"
    _description = "Research Output"
    _order = "output_type, name, id"
    _rec_name = "name"

    experiment_id = fields.Many2one(
        "research.experiment",
        string="Experiment",
        required=True,
        ondelete="cascade",
    )
    project_id = fields.Many2one(
        "research.project",
        string="Project",
        related="experiment_id.project_id",
        store=True,
        readonly=False,
    )
    source_ref = fields.Reference(
        selection=[
            ("research.project", "Project"),
            ("research.experiment", "Experiment"),
            ("research.paper", "Paper"),
        ],
        string="Source Reference",
        help="Optional dynamic reference linking this output to a related entity.",
    )
    output_type = fields.Selection(
        [
            ("paper", "Paper"),
            ("dataset", "Dataset"),
            ("software", "Software"),
            ("report", "Report"),
            ("thesis", "Thesis"),
            ("other", "Other"),
        ],
        string="Output Type",
        required=True,
        default="paper",
    )
    name = fields.Char(
        string="Title",
        required=True,
    )
    owner_id = fields.Many2one(
        "res.users",
        string="Owner",
        default=lambda self: self.env.user,
        index=True,
        help=(
            "The researcher responsible for this output. Defaults to its "
            "creator. Only the owner (or a Research Manager/Administrator) "
            "may modify or delete this record."
        ),
    )
    description = fields.Text(
        string="Description",
    )
    status = fields.Selection(
        [
            ("draft", "Draft"),
            ("under_review", "Under Review"),
            ("accepted", "Accepted"),
            ("published", "Published"),
        ],
        string="Status",
        default="draft",
        required=True,
    )

    # ─── Validation Constraints ───────────────────────────────────────────────
    _check_name_length = models.Constraint(
        "CHECK(LENGTH(TRIM(name)) >= 3)",
        "Output title must be at least 3 characters long.",
    )
    _unique_output_per_experiment = models.Constraint(
        "UNIQUE(name, experiment_id)",
        "An output with this title already exists in the selected experiment.",
    )

    # @api.constrains("name")
    # def _check_name_length(self):
    #     for record in self:
    #         if len((record.name or "").strip()) < 3:
    #             raise ValidationError(
    #                 "❌ Output Title Too Short\n\n"
    #                 "Research output title must be at least 3 characters long.\n"
    #                 "Please provide a complete title."
    #             )

    # @api.constrains("name", "experiment_id")
    # def _check_unique_output_per_experiment(self):
    #     for record in self:
    #         if record.name and record.experiment_id:
    #             count = self.search_count([
    #                 ("name", "=", record.name.strip()),
    #                 ("experiment_id", "=", record.experiment_id.id),
    #                 ("id", "!=", record.id),
    #             ])
    #             if count > 0:
    #                 raise ValidationError(
    #                     "❌ Duplicate Output Title\n\n"
    #                     f"An output named '{record.name}' already exists in experiment '{record.experiment_id.name}'.\n"
    #                     "Please use a unique output title."
    #                 )