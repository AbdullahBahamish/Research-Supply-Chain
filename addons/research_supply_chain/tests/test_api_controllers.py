from odoo.tests.common import HttpCase  # type: ignore  # pyfly: ignore [missing-import]
import json


class TestAPIControllers(HttpCase):

    def setUp(self):
        super().setUp()
        self.user_admin = self.env.ref("base.user_admin")
        self.project = self.env["research.project"].create({
            "project_name": "API Test Quadcopter Navigation",
            "project_status": "in_progress",
        })
        self.paper = self.env["research.paper"].create({
            "paper_name": "Autonomous Flight Algorithms",
            "paper_status": "published",
            "paper_doi": "10.1000/182",
            "project_id": self.project.id,
        })

    def test_01_api_get_projects(self):
        """Test POST /api/v1/projects endpoint returns filtered project list."""
        self.authenticate("admin", "admin")
        payload = {
            "jsonrpc": "2.0",
            "params": {
                "filters": {
                    "project_status": "in_progress",
                },
                "limit": 10,
            },
        }
        response = self.url_open(
            "/api/v1/projects",
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(response.status_code, 200)
        res_data = response.json()
        self.assertIn("result", res_data)
        result = res_data["result"]
        self.assertEqual(result.get("status"), 200)
        self.assertGreaterEqual(result.get("count", 0), 1)

    def test_02_api_create_project(self):
        """Test POST /api/v1/project/create endpoint safely creates a project."""
        self.authenticate("admin", "admin")
        payload = {
            "jsonrpc": "2.0",
            "params": {
                "vals": {
                    "project_name": "New API Created Micro-Grid",
                    "project_description": "Created via HttpCase test suite",
                    "project_status": "proposed",
                }
            },
        }
        response = self.url_open(
            "/api/v1/project/create",
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(response.status_code, 200)
        res_data = response.json()
        self.assertIn("result", res_data)
        result = res_data["result"]
        self.assertEqual(result.get("status"), 201)
        self.assertIn("project", result)
        self.assertEqual(result["project"]["project_name"], "New API Created Micro-Grid")

    def test_03_api_get_researchers(self):
        """Test POST /api/v1/researchers directory endpoint (email privacy filter)."""
        self.authenticate("admin", "admin")
        payload = {
            "jsonrpc": "2.0",
            "params": {"limit": 10},
        }
        response = self.url_open(
            "/api/v1/researchers",
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(response.status_code, 200)
        res_data = response.json()
        self.assertIn("result", res_data)
        result = res_data["result"]
        self.assertEqual(result.get("status"), 200)

    def test_04_api_get_experiments(self):
        """Test POST /api/v1/experiments endpoint returns grouped experiment map."""
        self.authenticate("admin", "admin")
        payload = {
            "jsonrpc": "2.0",
            "params": {"limit": 10},
        }
        response = self.url_open(
            "/api/v1/experiments",
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(response.status_code, 200)
        res_data = response.json()
        self.assertIn("result", res_data)
        result = res_data["result"]
        self.assertEqual(result.get("status"), 200)
        self.assertIn("grouped_by_status", result)

    def test_05_api_get_papers(self):
        """Test POST /api/v1/papers endpoint returns internal publications list."""
        self.authenticate("admin", "admin")
        payload = {
            "jsonrpc": "2.0",
            "params": {"limit": 10},
        }
        response = self.url_open(
            "/api/v1/papers",
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(response.status_code, 200)
        res_data = response.json()
        self.assertIn("result", res_data)
        result = res_data["result"]
        self.assertEqual(result.get("status"), 200)

    def test_06_api_public_papers(self):
        """Test POST /api/v1/papers/public unauthenticated public citation endpoint."""
        payload = {
            "jsonrpc": "2.0",
            "params": {"limit": 10},
        }
        # Note: No self.authenticate call here - testing public route
        response = self.url_open(
            "/api/v1/papers/public",
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
        )
        self.assertEqual(response.status_code, 200)
        res_data = response.json()
        self.assertIn("result", res_data)
        result = res_data["result"]
        self.assertEqual(result.get("status"), 200)
        self.assertGreaterEqual(result.get("count", 0), 1)
