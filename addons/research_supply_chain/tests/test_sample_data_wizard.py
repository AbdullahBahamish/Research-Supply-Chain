from odoo.tests.common import TransactionCase  # type: ignore  # pyfly: ignore [missing-import]


class TestSampleDataWizard(TransactionCase):

    def test_01_sample_data_wizard_generation(self):
        """Test research.sample.data.wizard action_generate_data populates records."""
        initial_projects = self.env["research.project"].search_count([])
        initial_researchers = self.env["research.researcher"].search_count([])

        wizard = self.env["research.sample.data.wizard"].create({
            "num_projects": 3,
            "num_researchers": 3,
        })
        action = wizard.action_generate_data()

        self.assertEqual(action.get("type"), "ir.actions.client")
        self.assertEqual(action.get("tag"), "display_notification")

        new_projects = self.env["research.project"].search_count([])
        new_researchers = self.env["research.researcher"].search_count([])

        self.assertEqual(new_projects, initial_projects + 3)
        self.assertEqual(new_researchers, initial_researchers + 3)
