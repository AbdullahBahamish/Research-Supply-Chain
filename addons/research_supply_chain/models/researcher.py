import re
from odoo import models, fields, api  # type: ignore  # pyfly: ignore [missing-import]
from odoo.exceptions import ValidationError  # type: ignore  # pyfly: ignore [missing-import]

class Researcher(models.Model):
    _name = "research.researcher"
    _description = "Researcher"
    _rec_name = "name"

    EMAIL_REGEX = re.compile(r"^[^@]+@[^@]+\.[^@]+$")

    user_id = fields.Many2one(
        "res.users",
        string="User",
        required=True,
        ondelete="cascade",
    )
    employee_id = fields.Many2one(
        "hr.employee",
        string="HR Employee",
        ondelete="set null",
        help="Linked standard Odoo HR Employee profile.",
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
        store=True,
        readonly=False,
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

    # ─── Validation Constraints ───────────────────────────────────────────────

    @api.constrains("user_id")
    def _check_user_id_unique(self):
        for record in self:
            if record.user_id and self.search_count([("user_id", "=", record.user_id.id), ("id", "!=", record.id)]) > 0:
                raise ValidationError(
                    "❌ Duplicate Researcher Profile\n\n"
                    f"A researcher profile already exists for user '{record.user_id.name}'.\n"
                    "Each user account can only be linked to one researcher profile."
                )

    @api.constrains("email")
    def _check_email_format(self):
        for record in self:
            if record.email and not self.EMAIL_REGEX.match(record.email.strip()):
                raise ValidationError(
                    "❌ Invalid Email Address\n\n"
                    f"The email address '{record.email}' does not appear to be valid.\n"
                    "Please enter a properly formatted email address (e.g., user@example.com)."
                )

    @api.constrains("position")
    def _check_position_length(self):
        for record in self:
            if record.position and len(record.position.strip()) < 2:
                raise ValidationError(
                    "❌ Invalid Position\n\n"
                    "Job position must be at least 2 characters long.\n"
                    "Please provide a valid position title."
                )
