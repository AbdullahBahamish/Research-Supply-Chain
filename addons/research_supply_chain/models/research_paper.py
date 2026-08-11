from odoo import models, fields 

class ResearchPaper(models.Model):
    _name = "research.paper"
    _description = "Research Paper"

    paper_name = fields.Char(
        string ="Paper Title", 
        required = True
    ) 

    paper_author = fields.Char(
        string="Paper Author"
    )   

    paper_publication_date = fields.Date(
        string = "Paper Publication Date",
    )

    paper_abstract = fields.Text(
        string = "Paper Abstract",
    )

    paper_doi = fields.Char(
        string="Paper DOI",
    )

    paper_status = fields.Selection(
        [
            ("draft", "Draft"),
            ("submitted", "Submitted"), 
            ("published", "Published"),
            ("archived", "Archived"),
        ],
        string = "Status",
        default = "draft",
        required =True,
    )

    paper_github_url = fields.Char(
        string="Paper Code Repository"
    )

    project_id = fields.Many2one(
        "research.project",
        string="Research Project", 
        ondelete="set null",
    )

    # author_ids = fields.Many2many(
    #     "research.author",
    #     string="Authors",
    # )

    def action_submit(self):
        for record in self:
            if record.paper_status != "draft":
                continue

            record.paper_status = "submitted"
