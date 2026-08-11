from odoo import models, fields  # type: ignore  # pyfly: ignore [missing-import]

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

    _sql_constraints = [
        (
            "user_id_unique",
            "unique(user_id)",
            "A researcher profile already exists for this user account.",
        ),
    ]
