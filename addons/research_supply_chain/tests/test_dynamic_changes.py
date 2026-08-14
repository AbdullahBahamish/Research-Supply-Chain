from odoo.tests.common import TransactionCase  # type: ignore  # pyfly: ignore [missing-import]
from odoo import fields  # type: ignore  # pyfly: ignore [missing-import]
from datetime import timedelta

class TestDynamicChanges(TransactionCase):

    def setUp(self):
        super().setUp()
        self.user = self.env['res.users'].create({
            'name': 'Dynamic Test User',
            'login': 'dynamic_test_user',
            'email': 'dynamic@example.com',
        })
        self.researcher = self.env['research.researcher'].create({
            'user_id': self.user.id,
            'position': 'Lead AI Engineer',
        })
        self.project = self.env['research.project'].create({
            'project_name': 'Dynamic Optimization Model',
            'lead_researcher_id': self.researcher.id,
            'start_date': fields.Date.today(),
            'end_date': fields.Date.today() + timedelta(days=60),
        })

    def test_project_dynamic_computed_totals(self):
        """Test dynamic budget total aggregations on research.project."""
        self.env['project.budget'].create({
            'project_id': self.project.id,
            'total_amount': 50000.0,
            'spent_amount': 25000.0,
        })
        self.assertEqual(self.project.total_budget_amount, 50000.0)
        self.assertEqual(self.project.total_spent_amount, 25000.0)
        self.assertEqual(self.project.remaining_budget_amount, 25000.0)
        self.assertEqual(self.project.budget_utilization, 50.0)

    def test_project_dynamic_onchange_dates(self):
        """Test onchange date validation warning."""
        res = self.project._onchange_dates()
        self.assertFalse(res)  # Valid dates return no warning

        self.project.end_date = fields.Date.today() - timedelta(days=5)
        warn_res = self.project._onchange_dates()
        self.assertTrue(warn_res and 'warning' in warn_res)

    def test_requirement_onchange_category(self):
        """Test requirement priority auto-setting based on category."""
        req = self.env['research.requirement'].new({
            'project_id': self.project.id,
            'name': 'NVIDIA H100 Cluster',
            'category': 'hardware',
        })
        req._onchange_category()
        self.assertEqual(req.priority, 'high')

    def test_paper_computed_repository_name(self):
        """Test paper computed repository_name field."""
        paper = self.env['research.paper'].create({
            'paper_name': 'Deep Learning for Supply Chains',
            'project_id': self.project.id,
            'paper_github_url': 'https://github.com/org/supply-chain-ai',
        })
        self.assertEqual(paper.repository_name, 'org/supply-chain-ai')
