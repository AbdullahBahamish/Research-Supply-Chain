from odoo.tests.common import TransactionCase  # type: ignore  # pyfly: ignore [missing-import]

class TestResearchProject(TransactionCase):

    def setUp(self):
        super().setUp()
        self.user = self.env['res.users'].create({
            'name': 'Test Researcher User',
            'login': 'test_researcher_user',
            'email': 'test@example.com',
        })
        self.researcher = self.env['research.researcher'].create({
            'user_id': self.user.id,
            'position': 'Senior Scientist',
        })
        self.project = self.env['research.project'].create({
            'project_name': 'Quantum Computing in Logistics',
            'lead_researcher_id': self.researcher.id,
        })

    def test_project_creation_and_sequence(self):
        self.assertTrue(self.project.code, "Project code should be generated automatically.")
        self.assertEqual(self.project.project_status, 'proposed')
        self.assertEqual(self.project.lead_researcher_id.id, self.researcher.id)

    def test_project_budget_calculation(self):
        budget = self.env['project.budget'].create({
            'project_id': self.project.id,
            'total_amount': 50000.0,
            'spent_amount': 15000.0,
        })
        self.assertEqual(budget.remaining_amount, 35000.0)

    def test_team_allocation(self):
        allocation = self.env['research.project.researcher'].create({
            'project_id': self.project.id,
            'researcher_id': self.researcher.id,
            'role': 'Lead Quantum Physicist',
            'allocated_pct': 75.0,
        })
        self.assertIn(allocation, self.project.researcher_line_ids)
        self.assertEqual(allocation.allocated_pct, 75.0)
