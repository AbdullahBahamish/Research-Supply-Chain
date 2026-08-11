from odoo.tests.common import TransactionCase  # type: ignore  # pyfly: ignore [missing-import]

class TestExperiment(TransactionCase):

    def setUp(self):
        super().setUp()
        self.user = self.env.user
        self.project = self.env['research.project'].create({
            'project_name': 'Bioinformatics Genome Mapping',
        })
        self.resource = self.env['research.resource'].create({
            'name': 'DNA Sequencer X100',
            'resource_type': 'equipment',
            'availability_status': 'available',
        })
        self.experiment = self.env['research.experiment'].create({
            'project_id': self.project.id,
            'name': 'High-Throughput Sequencing Run #1',
            'objective': 'Sequence 100 plant samples',
        })

    def test_experiment_creation(self):
        self.assertEqual(self.experiment.status, 'planned')
        self.assertEqual(self.experiment.created_by, self.user)

    def test_experiment_resource_assignment(self):
        exp_res = self.env['research.experiment.resource'].create({
            'experiment_id': self.experiment.id,
            'resource_id': self.resource.id,
            'purpose': 'Sample sequencing',
            'quantity': 1.0,
        })
        self.assertIn(exp_res, self.experiment.experiment_resource_ids)

    def test_experiment_output_creation(self):
        output = self.env['research.output'].create({
            'experiment_id': self.experiment.id,
            'output_type': 'dataset',
            'name': 'Plant Genome Sequence Dataset v1',
            'status': 'published',
        })
        self.assertIn(output, self.experiment.output_ids)
        self.assertEqual(output.project_id, self.project)
