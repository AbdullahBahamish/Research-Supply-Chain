import re
from odoo import models, fields, api  # type: ignore  # pyfly: ignore [missing-import]
from odoo.exceptions import ValidationError  # type: ignore  # pyfly: ignore [missing-import]

class ResearchPaper(models.Model):
    _name = "research.paper"
    _inherit = ["research.audit.mixin"]
    _description = "Research Paper"
    _rec_name = "paper_name"

    # Compiled Regex for DOI validation
    DOI_REGEX = re.compile(r"^10\.\d{4,9}/[-._;()/:A-Z0-9]+$", re.IGNORECASE)

    # Compiled Regex with named groups for GitHub URL parsing
    GITHUB_URL_REGEX = re.compile(r"github\.com/(?P<owner>[\w-]+)/(?P<repo>[\w-]+)")

    paper_name = fields.Char(
        string="Paper Title",
        required=True,
    )
    paper_author = fields.Char(
        string="Paper Author",
    )
    paper_publication_date = fields.Date(
        string="Paper Publication Date",
    )
    paper_abstract = fields.Text(
        string="Paper Abstract",
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
        string="Status",
        default="draft",
        required=True,
    )
    paper_github_url = fields.Char(
        string="Paper Code Repository",
    )
    project_id = fields.Many2one(
        "research.project",
        string="Research Project",
        ondelete="set null",
    )
    output_id = fields.Many2one(
        "research.output",
        string="Research Output",
        ondelete="set null",
    )

    @api.constrains("paper_doi")
    def _check_doi_format(self):
        """Demonstrates REGULAR EXPRESSIONS (re.match)."""
        for record in self:
            if record.paper_doi and not self.DOI_REGEX.match(record.paper_doi):
                raise ValidationError(f"DOI '{record.paper_doi}' does not match standard DOI format.")

    def action_parse_github_repository(self) -> dict:
        """Demonstrates REGULAR EXPRESSIONS with named groups (re.search)."""
        self.ensure_one()
        if not self.paper_github_url:
            return {"owner": False, "repo": False}

        match = self.GITHUB_URL_REGEX.search(self.paper_github_url)
        if match:
            return {
                "owner": match.group("owner"),
                "repo": match.group("repo"),
            }
        return {"owner": False, "repo": False}

    def action_submit(self):
        for record in self:
            if record.paper_status != "draft":
                continue
            record.paper_status = "submitted"
            record._log_system_event(f"Paper '{record.paper_name}' submitted for publication review.")

