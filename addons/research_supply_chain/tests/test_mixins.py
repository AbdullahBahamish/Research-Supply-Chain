from odoo.tests.common import TransactionCase  # type: ignore  # pyfly: ignore [missing-import]


class TestMixins(TransactionCase):

    def setUp(self):
        super().setUp()
        self.project_1 = self.env["research.project"].create({
            "project_name": "Mixin Test Project Alpha",
            "project_status": "proposed",
        })
        self.project_2 = self.env["research.project"].create({
            "project_name": "Mixin Test Project Beta",
            "project_status": "in_progress",
        })
        self.project_3 = self.env["research.project"].create({
            "project_name": "Mixin Test Project Gamma",
            "project_status": "in_progress",
        })

    def test_01_audit_mixin_log_system_event(self):
        """Test ResearchAuditMixin._log_system_event logs entries and caps history."""
        self.project_1._log_system_event("Audit Event #1")
        self.assertIn("Audit Event #1", self.project_1.audit_notes or "")

        # Log 35 entries to verify entry capping at 30
        for i in range(2, 36):
            self.project_1._log_system_event(f"Audit Event #{i}")

        log_lines = self.project_1.audit_notes.strip().split("\n")
        self.assertLessEqual(len(log_lines), 30)

    def test_02_exportable_mixin_generate_record_stream(self):
        """Test ExportableDataMixin.generate_record_stream generator yields dictionaries."""
        projects = self.project_1 | self.project_2 | self.project_3
        stream = self.env["research.project"].generate_record_stream(
            projects, ["project_name", "project_status"]
        )
        stream_list = list(stream)
        self.assertEqual(len(stream_list), 3)
        self.assertEqual(stream_list[0]["project_name"], "Mixin Test Project Alpha")
        self.assertEqual(stream_list[0]["project_status"], "proposed")

    def test_03_exportable_mixin_grouped_summary(self):
        """Test ExportableDataMixin.get_grouped_summary_by_status uses itertools.groupby."""
        projects = self.project_1 | self.project_2 | self.project_3
        summary = self.env["research.project"].get_grouped_summary_by_status(
            projects, status_field="project_status"
        )
        self.assertIn("in_progress", summary)
        self.assertEqual(summary["in_progress"]["count"], 2)
        self.assertIn("Mixin Test Project Beta", summary["in_progress"]["names"])
        self.assertIn("Mixin Test Project Gamma", summary["in_progress"]["names"])

    def test_04_system_audit_log_decorator(self):
        """Test system_audit_log decorator attached to create method."""
        proj = self.env["research.project"].create({
            "project_name": "Decorated Create Project",
        })
        self.assertIn("Create Research Project", proj.audit_notes or "")
