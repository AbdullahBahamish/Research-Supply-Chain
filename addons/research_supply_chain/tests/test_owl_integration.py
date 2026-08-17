from odoo.tests.common import TransactionCase  # type: ignore  # pyfly: ignore [missing-import]


class TestOWLIntegration(TransactionCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.researcher = cls.env['research.researcher'].create({
            'name': 'Dr. Alan Turing',
            'email': 'alan.turing@research.org',
        })
        cls.project = cls.env['research.project'].create({
            'project_name': 'Quantum Computing Initiative',
            'lead_researcher_id': cls.researcher.id,
            'project_status': 'in_progress',
        })
        cls.budget = cls.env['project.budget'].create({
            'project_id': cls.project.id,
            'total_amount': 100000.0,
            'spent_amount': 75000.0,
        })

    def test_utilization_rate_computation(self):
        """Verify that budget utilization_rate float field computes accurately for the OWL gauge widget."""
        self.assertAlmostEqual(self.budget.utilization_rate, 75.0, places=2)

        self.budget.spent_amount = 90000.0
        self.assertAlmostEqual(self.budget.utilization_rate, 90.0, places=2)

    def test_owl_rdf_exporter(self):
        """Verify semantic Web Ontology Language (OWL/RDF XML) generator."""
        owl_xml = self.env['research.owl.exporter'].export_projects_to_owl_xml([self.project.id])
        self.assertIn('<owl:Ontology', owl_xml)
        self.assertIn('Quantum Computing Initiative', owl_xml)
        self.assertIn('rsc:ResearchProject', owl_xml)
