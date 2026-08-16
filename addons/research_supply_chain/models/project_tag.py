from odoo import models, fields  # type: ignore  # pyfly: ignore [missing-import]

class ResearchProjectTag(models.Model):
    _name = "research.project.tag"
    _description = "Research Project Tag"
    _order = "name"

    name = fields.Char(
        string="Tag Name",
        required=True,
    )
    color = fields.Integer(
        string="Color Index",
        default=0,
    )

    _sql_constraints = [
        ("name_uniq", "UNIQUE(name)", "Tag name must be unique!"),
    ]
