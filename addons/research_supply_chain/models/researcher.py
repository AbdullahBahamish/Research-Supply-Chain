from odoo import models, fields, api  # type: ignore  # pyfly: ignore [missing-import]
from odoo.exceptions import ValidationError  # type: ignore  # pyfly: ignore [missing-import]

class Researcher(models.Model):
    _name = "research.researcher"
    _description = "Researcher"
    _rec_name = "name"

    user_id = fields.Many2one(
        "res.users",
        string="User",
        required=True,
        ondelete="cascade",
    )
    name = fields.Char(
        related="user_id.name",
        string="Name",
        store=True,
        readonly=False,
    )
    email = fields.Char(
        related="user_id.email",
        string="Email",
        readonly=True,
    )
    position = fields.Char(
        string="Position",
    )
    expertise = fields.Text(
        string="Expertise",
    )
    is_principal = fields.Boolean(
        string="Is Principal Investigator",
        default=False,
    )
    active = fields.Boolean(
        default=True,
    )
    project_line_ids = fields.One2many(
        "research.project.researcher",
        "researcher_id",
        string="Project Allocations",
    )

    @api.constrains("user_id")
    def _check_user_id_unique(self):
        for record in self:
            if record.user_id and self.search_count([("user_id", "=", record.user_id.id), ("id", "!=", record.id)]) > 0:
                raise ValidationError("A researcher profile already exists for this user account.")
