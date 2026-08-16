import re
from odoo import api, fields, models  # type: ignore  # pyfly: ignore [missing-import]
from odoo.exceptions import ValidationError  # type: ignore  # pyfly: ignore [missing-import]


class Researcher(models.Model):
    _name = "research.researcher"
    _description = "Researcher"
    _rec_name = "name"
    _order = "name"

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
        # Field-level ACL: HR linkage is admin/manager territory only. This is
        # enforced at the ORM layer (not just the view), so it can't be
        # bypassed by calling write()/create() directly (e.g. via RPC/API).
        groups="research_supply_chain.group_research_manager,research_supply_chain.group_research_admin",
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
        # Field-level ACL: a researcher must never be able to self-declare as
        # PI. This matters now that researchers can write their own profile
        # (rule_researcher_self_write) - without this, that self-write ability
        # would let any researcher flip this flag on themselves. Restricting
        # at the field level (not just hiding it in the view) blocks that
        # regardless of whether the write comes through the UI or the API.
        groups="research_supply_chain.group_research_manager,research_supply_chain.group_research_admin",
    )
    active = fields.Boolean(
        default=True,
    )
    project_line_ids = fields.One2many(
        "research.project.researcher",
        "researcher_id",
        string="Project Allocations",
    )

    _user_unique = models.Constraint(
        "UNIQUE(user_id)",
        "A researcher profile already exists for this user account.",
    )
    _check_position_length = models.Constraint(
        "CHECK(position IS NULL OR LENGTH(TRIM(position)) >= 2)",
        "Job position must be at least 2 characters long.",
    )

    @api.constrains("email")
    def _check_email_format(self):
        for record in self:
            if record.email and not self.EMAIL_REGEX.match(record.email.strip()):
                raise ValidationError(
                    f"The email address '{record.email}' does not appear to be valid."
                )