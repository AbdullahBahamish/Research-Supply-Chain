from odoo.tests.common import TransactionCase  # type: ignore  # pyfly: ignore [missing-import]
from odoo import fields  # type: ignore  # pyfly: ignore [missing-import]
from datetime import timedelta

class TestInverseFunctions(TransactionCase):

    def setUp(self):
        super().setUp()
        self.user = self.env['res.users'].create({
            'name': 'Inverse Test User',
            'login': 'inverse_test_user',
            'email': 'inverse_original@example.com',
        })
        self.researcher = self.env['research.researcher'].create({
            'user_id': self.user.id,
            'position': 'Principal Investigator',
        })
        self.project = self.env['research.project'].create({
            'project_name': 'Inverse Dynamics Research',
            'lead_researcher_id': self.researcher.id,
            'start_date': fields.Date.today(),
            'end_date': fields.Date.today() + timedelta(days=90),
        })

    def test_project_budget_remaining_amount_inverse(self):
        """Test setting remaining_amount on project.budget updates total_amount."""
        budget = self.env['project.budget'].create({
            'project_id': self.project.id,
            'total_amount': 100000.0,
            'spent_amount': 30000.0,
        })
        self.assertEqual(budget.remaining_amount, 70000.0)

        # Set remaining_amount directly to trigger inverse
        budget.remaining_amount = 80000.0
        self.assertEqual(budget.total_amount, 110000.0)

    def test_research_paper_repository_name_inverse(self):
        """Test setting repository_name on research.paper updates paper_github_url."""
        paper = self.env['research.paper'].create({
            'paper_name': 'Quantum Supply Chains Paper',
            'project_id': self.project.id,
        })

        # Set repository_name directly
        paper.repository_name = 'research-lab/quantum-scm'
        self.assertEqual(paper.paper_github_url, 'https://github.com/research-lab/quantum-scm')

        # Clear repository_name
        paper.repository_name = False
        self.assertFalse(paper.paper_github_url)

    def test_research_project_totals_inverse(self):
        """Test setting budget totals and utilization directly on research.project."""
        budget = self.env['project.budget'].create({
            'project_id': self.project.id,
            'total_amount': 50000.0,
            'spent_amount': 10000.0,
        })

        # Test total_budget_amount inverse
        self.project.total_budget_amount = 60000.0
        self.assertEqual(budget.total_amount, 60000.0)

        # Test total_spent_amount inverse
        self.project.total_spent_amount = 20000.0
        self.assertEqual(budget.spent_amount, 20000.0)

        # Test remaining_budget_amount inverse
        self.project.remaining_budget_amount = 50000.0
        self.assertEqual(budget.total_amount, 70000.0)

        # Test budget_utilization inverse
        self.project.budget_utilization = 50.0
        self.assertEqual(budget.spent_amount, 35000.0)

    def test_research_project_counts_inverse(self):
        """Test setting experiment_count and paper_count directly on research.project."""
        self.assertEqual(self.project.experiment_count, 0)
        self.assertEqual(self.project.paper_count, 0)

        # Set experiment_count to 3
        self.project.experiment_count = 3
        self.assertEqual(len(self.project.experiment_ids), 3)

        # Set experiment_count down to 1
        self.project.experiment_count = 1
        self.assertEqual(len(self.project.experiment_ids), 1)

        # Set paper_count to 2
        self.project.paper_count = 2
        self.assertEqual(len(self.project.paper_ids), 2)

        # Set paper_count down to 0
        self.project.paper_count = 0
        self.assertEqual(len(self.project.paper_ids), 0)

    def test_experiment_counts_inverse(self):
        """Test setting output_count on research.experiment."""
        experiment = self.env['research.experiment'].create({
            'project_id': self.project.id,
            'name': 'Inverse Scaling Experiment',
        })
        self.assertEqual(experiment.output_count, 0)

        # Set output_count to 2
        experiment.output_count = 2
        self.assertEqual(len(experiment.output_ids), 2)

        # Set output_count to 1
        experiment.output_count = 1
        self.assertEqual(len(experiment.output_ids), 1)

    def test_researcher_email_inverse(self):
        """Test editing researcher email updates underlying user email."""
        self.assertEqual(self.user.email, 'inverse_original@example.com')

        # Update researcher email directly
        self.researcher.email = 'inverse_updated@example.com'
        self.assertEqual(self.user.email, 'inverse_updated@example.com')

    def test_research_output_project_id_inverse(self):
        """Test updating output project_id updates experiment project_id."""
        new_project = self.env['research.project'].create({
            'project_name': 'Secondary Project',
        })
        experiment = self.env['research.experiment'].create({
            'project_id': self.project.id,
            'name': 'Cross Project Experiment',
        })
        output = self.env['research.output'].create({
            'experiment_id': experiment.id,
            'name': 'Cross Output',
        })
        self.assertEqual(output.project_id.id, self.project.id)

        # Update output project_id
        output.project_id = new_project.id
        self.assertEqual(experiment.project_id.id, new_project.id)
