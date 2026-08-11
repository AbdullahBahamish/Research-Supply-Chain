from odoo.tests.common import TransactionCase  # type: ignore  # pyfly: ignore [missing-import]

class TestResearcher(TransactionCase):

    def setUp(self):
        super().setUp()
        self.user = self.env['res.users'].create({
            'name': 'Dr. Alice Smith',
            'login': 'dr_alice_smith',
            'email': 'alice@research.org',
        })

    def test_researcher_creation(self):
        researcher = self.env['research.researcher'].create({
            'user_id': self.user.id,
            'position': 'Lead Researcher',
            'expertise': 'Robotics & AI',
            'is_principal': True,
        })
        self.assertEqual(researcher.name, 'Dr. Alice Smith')
        self.assertEqual(researcher.email, 'alice@research.org')
        self.assertTrue(researcher.is_principal)
