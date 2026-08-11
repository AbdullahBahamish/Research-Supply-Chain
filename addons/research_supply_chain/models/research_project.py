from odoo import api, models, fields

class ResearchProject(models.Model):
    _name = "research.project"
    _description = "Research Project"

    code = fields.Char(
        string="Project Code",
        readonly=True,
        copy=False,
    )

    project_name = fields.Char(
        string = "Project Title", 
        required = True,
    )

    project_description= fields.Text(
        string = "Project Description", 
    )

    start_date = fields.Date(
        string = "Project Start Date",
    )

    end_date = fields.Date(
        string = "Project End Date",
    )

    project_status = fields.Selection(
        [
            ("proposed", "Proposed"),
            ("approved", "Approved"),
            ("in_progress", "In Progress"),
            ("completed", "Completed"),
            ("archived", "Archived"),
        ],
        string = "Status",
        default = "proposed",
        required =True,
    )

    active = fields.Boolean(
        default = True,
    )

    paper_ids = fields.One2many(
        "research.paper",
        "project_id",
        string = "Research Papers",
    )

    @api.model 
    def create(self, vals):
        vals["code"] = self.env["ir.sequence"].next_by_code(
            "research.project"
        )
        return super().create(vals)