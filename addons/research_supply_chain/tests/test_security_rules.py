from odoo.tests.common import TransactionCase  # type: ignore  # pyfly: ignore [missing-import]
from odoo.exceptions import AccessError  # type: ignore  # pyfly: ignore [missing-import]


class TestSecurityRules(TransactionCase):

    def setUp(self):
        super().setUp()
        # Security Groups
        self.group_user = self.env.ref("research_supply_chain.group_research_user")
        self.group_officer = self.env.ref("research_supply_chain.group_research_officer")
        self.group_manager = self.env.ref("research_supply_chain.group_research_manager")

        # Test Users
        self.user_regular = self.env["res.users"].create({
            "name": "Standard Research User",
            "login": "standard_user_security",
            "email": "user_sec@example.com",
            "groups_id": [(6, 0, [self.group_user.id])],
        })
        self.user_officer = self.env["res.users"].create({
            "name": "Research Officer User",
            "login": "officer_user_security",
            "email": "officer_sec@example.com",
            "groups_id": [(6, 0, [self.group_officer.id])],
        })
        self.user_manager = self.env["res.users"].create({
            "name": "Research Manager User",
            "login": "manager_user_security",
            "email": "manager_sec@example.com",
            "groups_id": [(6, 0, [self.group_manager.id])],
        })

        # Researchers
        self.researcher_regular = self.env["research.researcher"].create({
            "user_id": self.user_regular.id,
            "position": "Research Assistant",
        })

        # Projects
        self.public_project = self.env["research.project"].create({
            "project_name": "Public Open Science Project",
            "visibility": "public",
        })
        self.private_project = self.env["research.project"].create({
            "project_name": "Classified Lab Project",
            "visibility": "private",
        })

    def test_01_public_project_visibility(self):
        """Test public projects are visible to standard research users."""
        public_projects = self.env["research.project"].with_user(self.user_regular).search([("id", "=", self.public_project.id)])
        self.assertIn(self.public_project, public_projects)

    def test_02_private_project_visibility_restriction(self):
        """Test unassigned users cannot see private projects."""
        private_projects = self.env["research.project"].with_user(self.user_regular).search([("id", "=", self.private_project.id)])
        self.assertNotIn(self.private_project, private_projects)

    def test_03_private_project_assigned_member_access(self):
        """Test assigning a user to a private project allows read access."""
        self.env["research.project.researcher"].create({
            "project_id": self.private_project.id,
            "researcher_id": self.researcher_regular.id,
            "role": "Data Analyst",
        })
        private_projects = self.env["research.project"].with_user(self.user_regular).search([("id", "=", self.private_project.id)])
        self.assertIn(self.private_project, private_projects)

    def test_04_experiment_ownership_security(self):
        """Test non-owner users cannot modify experiments owned by others unless manager."""
        exp = self.env["research.experiment"].with_user(self.user_officer).create({
            "project_id": self.public_project.id,
            "name": "Officer Owned Experiment",
            "owner_id": self.user_officer.id,
        })
        self.assertEqual(exp.owner_id, self.user_officer)

        # Standard user attempting to modify officer's experiment should trigger AccessError or be blocked
        with self.assertRaises(AccessError):
            exp.with_user(self.user_regular).write({"name": "Tampered Experiment Name"})

    def test_05_manager_full_override_authority(self):
        """Test Research Manager can edit any project and budget."""
        budget = self.env["project.budget"].create({
            "project_id": self.private_project.id,
            "total_amount": 100000.0,
        })
        budget.with_user(self.user_manager).write({"spent_amount": 25000.0})
        self.assertEqual(budget.spent_amount, 25000.0)
