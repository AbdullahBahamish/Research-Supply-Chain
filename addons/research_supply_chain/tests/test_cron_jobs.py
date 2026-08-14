from odoo.tests.common import TransactionCase  # type: ignore  # pyfly: ignore [missing-import]
from odoo import fields  # type: ignore  # pyfly: ignore [missing-import]
from datetime import timedelta

class TestCronJobs(TransactionCase):

    def setUp(self):
        super().setUp()
        self.user = self.env['res.users'].create({
            'name': 'Test Cron User',
            'login': 'test_cron_user',
            'email': 'cron_test@example.com',
        })
        self.researcher = self.env['research.researcher'].create({
            'user_id': self.user.id,
            'position': 'Research Scientist',
        })
        self.project = self.env['research.project'].create({
            'project_name': 'Quantum Simulation Project',
            'lead_researcher_id': self.researcher.id,
            'project_status': 'proposed',
            'start_date': fields.Date.today() - timedelta(days=1),
            'end_date': fields.Date.today() + timedelta(days=30),
        })

    def test_cron_update_project_statuses(self):
        """Test automatic status update for starting projects."""
        res = self.env['research.project'].cron_update_project_statuses()
        self.assertTrue(res)
        self.assertEqual(self.project.project_status, 'in_progress')

    def test_cron_check_budget_alerts(self):
        """Test budget audit and alert logging."""
        budget = self.env['project.budget'].create({
            'project_id': self.project.id,
            'total_amount': 10000.0,
            'spent_amount': 9500.0,
        })
        res = self.env['project.budget'].cron_check_budget_alerts()
        self.assertTrue(res)
        self.assertIn('High budget utilization', budget.audit_notes or '')

    def test_cron_check_overdue_requirements(self):
        """Test escalation of overdue requirements."""
        req = self.env['research.requirement'].create({
            'project_id': self.project.id,
            'name': 'High Performance GPU',
            'priority': 'medium',
            'status': 'requested',
            'needed_by': fields.Date.today() - timedelta(days=2),
        })
        res = self.env['research.requirement'].cron_check_overdue_requirements()
        self.assertTrue(res)
        self.assertEqual(req.priority, 'high')

    def test_cron_update_experiment_statuses(self):
        """Test transition of planned experiments to running."""
        exp = self.env['research.experiment'].create({
            'project_id': self.project.id,
            'name': 'Quantum Circuit Benchmark',
            'status': 'planned',
            'start_date': fields.Date.today() - timedelta(days=1),
        })
        res = self.env['research.experiment'].cron_update_experiment_statuses()
        self.assertTrue(res)
        self.assertEqual(exp.status, 'running')

    def test_cron_check_paper_statuses(self):
        """Test paper review check execution."""
        paper = self.env['research.paper'].create({
            'paper_name': 'Quantum Algorithms Draft',
            'project_id': self.project.id,
            'paper_status': 'submitted',
        })
        res = self.env['research.paper'].cron_check_paper_statuses()
        self.assertTrue(res)
        self.assertIn('pending publication review', paper.audit_notes or '')
