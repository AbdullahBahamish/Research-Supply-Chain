from odoo.tests.common import TransactionCase  # type: ignore  # pyfly: ignore [missing-import]

class TestRequirements(TransactionCase):

    def setUp(self):
        super().setUp()
        self.project = self.env['research.project'].create({
            'project_name': 'Autonomous Drone Logistics',
        })

    def test_requirement_creation(self):
        req = self.env['research.requirement'].create({
            'project_id': self.project.id,
            'name': 'LiDAR Sensor Units',
            'category': 'hardware',
            'quantity': 4.0,
            'priority': 'high',
        })
        self.assertEqual(req.status, 'requested')
        self.assertEqual(req.priority, 'high')

    def test_requirement_status_update(self):
        req = self.env['research.requirement'].create({
            'project_id': self.project.id,
            'name': 'Flight Control Software License',
            'category': 'software',
        })
        req.write({'status': 'approved'})
        self.assertEqual(req.status, 'approved')
        req.write({'status': 'fulfilled'})
        self.assertEqual(req.status, 'fulfilled')
