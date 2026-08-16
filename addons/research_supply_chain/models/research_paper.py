import re
from odoo import api, fields, models  # type: ignore  # pyfly: ignore [missing-import]
from odoo.exceptions import ValidationError  # type: ignore  # pyfly: ignore [missing-import]


class ResearchPaper(models.Model):
    _name = "research.paper"
    _inherit = ["research.audit.mixin", "mail.thread", "mail.activity.mixin"]
    _description = "Research Paper"
    _order = "paper_publication_date desc, paper_name"
    _rec_name = "paper_name"

    DOI_REGEX = re.compile(r"^10\.\d{4,9}/[-._;()/:A-Za-z0-9]+$", re.IGNORECASE)
    GITHUB_URL_REGEX = re.compile(r"github\.com/(?P<owner>[\w-]+)/(?P<repo>[\w-]+)")

    paper_name = fields.Char(
        string="Paper Title",
        required=True,
        tracking=True,
    )
    paper_author = fields.Char(
        string="Paper Author",
        tracking=True,
    )
    paper_publication_date = fields.Date(
        string="Paper Publication Date",
        tracking=True,
    )
    paper_abstract = fields.Text(
        string="Paper Abstract",
    )
    paper_doi = fields.Char(
        string="Paper DOI",
        tracking=True,
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
        tracking=True,
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
    repository_name = fields.Char(
        string="Repository Name",
        compute="_compute_repository_name",
        inverse="_inverse_repository_name",
        store=True,
    )

    _sql_constraints = [
        (
            "check_published_doi_required",
            "CHECK (paper_status != 'published' OR (paper_doi IS NOT NULL AND trim(paper_doi) != ''))",
            "A valid DOI is required when the paper status is set to 'Published'.",
        ),
        (
            "check_published_date_required",
            "CHECK(paper_status != 'published' OR paper_publication_date IS NOT NULL)",
            "A publication date is required when the paper status is set to 'Published'.",
        ),
        (
            "check_paper_name_length",
            "CHECK(paper_name IS NULL OR length(trim(paper_name)) >= 5)",
            "Paper title must be at least 5 characters long.",
        ),
    ]

    @api.constrains("paper_doi")
    def _check_doi_format(self):
        for record in self:
            if record.paper_doi and not self.DOI_REGEX.match(record.paper_doi.strip()):
                raise ValidationError(
                    f"DOI '{record.paper_doi}' does not match standard notation (e.g. 10.1000/182)."
                )

    @api.depends("paper_github_url")
    def _compute_repository_name(self):
        for record in self:
            parsed = record.action_parse_github_repository()
            if parsed and parsed.get("owner") and parsed.get("repo"):
                record.repository_name = f"{parsed['owner']}/{parsed['repo']}"
            else:
                record.repository_name = False

    def _inverse_repository_name(self):
        for record in self:
            if record.repository_name:
                record.paper_github_url = f"https://github.com/{record.repository_name.strip()}"
            else:
                record.paper_github_url = False

    @api.onchange("project_id")
    def _onchange_project_id(self):
        if self.project_id and self.project_id.lead_researcher_id and not self.paper_author:
            self.paper_author = self.project_id.lead_researcher_id.name

    def action_parse_github_repository(self) -> dict:
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
            record.check_access_rights("write")
            record.check_access_rule("write")
            if record.paper_status != "draft":
                continue
            record.paper_status = "submitted"
            record._log_system_event(f"Paper '{record.paper_name}' submitted for publication review.")
        return True

    @api.model
    def cron_check_paper_statuses(self):
        submitted_papers = self.search([("paper_status", "=", "submitted")])
        for paper in submitted_papers:
            paper._log_system_event(
                f"Cron Job Notice: Paper '{paper.paper_name}' is currently pending publication review."
            )
        return True