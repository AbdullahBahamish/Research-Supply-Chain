from unittest.mock import patch, MagicMock
from odoo.tests.common import TransactionCase  # type: ignore  # pyfly: ignore [missing-import]
from odoo import fields, http  # type: ignore  # pyfly: ignore [missing-import]
# pyrefly: ignore [missing-import]
from odoo.addons.research_supply_chain.controllers import main


class TestAPIControllers(TransactionCase):

    def setUp(self):
        super().setUp()
        self.controller = main.ResearchSupplyChainAPIController()
        self.user_admin = self.env.ref("base.user_admin")
        self.project = self.env["research.project"].create({
            "project_name": "API Test Quadcopter Navigation",
            "project_status": "in_progress",
            "start_date": fields.Date.today(),
        })
        self.paper = self.env["research.paper"].create({
            "paper_name": "Autonomous Flight Algorithms",
            "paper_status": "published",
            "paper_publication_date": fields.Date.today(),
            "paper_doi": f"10.1000/api_{self.project.id}",
            "project_id": self.project.id,
        })

        self.mock_request = MagicMock()
        self.mock_request.env = self.env(user=self.user_admin)

        p1 = patch.object(http, "request", self.mock_request)
        p2 = patch.object(main, "request", self.mock_request)

        p1.start()
        p2.start()

        self.addCleanup(p1.stop)
        self.addCleanup(p2.stop)

    def test_01_api_get_projects(self):
        """Test POST /api/v1/projects endpoint returns filtered project list."""
        result = self.controller.api_get_projects(
            filters={"project_status": "in_progress"},
            limit=10,
        )
        self.assertEqual(result.get("status"), 200)
        self.assertGreaterEqual(result.get("count", 0), 1)

    def test_02_api_create_project(self):
        """Test POST /api/v1/project/create endpoint safely creates a project."""
        result = self.controller.api_create_project(
            vals={
                "project_name": "New API Created Micro-Grid",
                "project_description": "Created via test suite",
                "project_status": "proposed",
            }
        )
        self.assertEqual(result.get("status"), 201)
        self.assertIn("project", result)
        self.assertEqual(result["project"]["project_name"], "New API Created Micro-Grid")

    def test_03_api_get_researchers(self):
        """Test POST /api/v1/researchers directory endpoint (email privacy filter)."""
        result = self.controller.api_get_researchers(limit=10)
        self.assertEqual(result.get("status"), 200)

    def test_04_api_get_experiments(self):
        """Test POST /api/v1/experiments endpoint returns grouped experiment map."""
        result = self.controller.api_get_experiments(limit=10)
        self.assertEqual(result.get("status"), 200)
        self.assertIn("grouped_by_status", result)

    def test_05_api_get_papers(self):
        """Test POST /api/v1/papers endpoint returns internal publications list."""
        result = self.controller.api_get_papers(limit=10)
        self.assertEqual(result.get("status"), 200)

    def test_06_api_public_papers(self):
        """Test POST /api/v1/papers/public unauthenticated public citation endpoint."""
        public_user = self.env.ref("base.public_user")
        self.mock_request.env = self.env(user=public_user)
        result = self.controller.api_public_papers(limit=10)
        self.assertEqual(result.get("status"), 200)
        self.assertGreaterEqual(result.get("count", 0), 1)

