from datetime import timedelta
import random
from odoo import models, fields  # type: ignore  # pyfly: ignore [missing-import]
from odoo.exceptions import ValidationError  # type: ignore  # pyfly: ignore [missing-import]

class ResearchSampleDataWizard(models.TransientModel):
    _name = "research.sample.data.wizard"
    _description = "Generate Sample Data Wizard"

    num_projects = fields.Integer(
        string="Number of Projects",
        default=5,
        required=True,
    )
    num_researchers = fields.Integer(
        string="Number of Researchers",
        default=5,
        required=True,
    )

    def action_generate_data(self):
        self.ensure_one()
        if self.num_projects < 1:
            raise ValidationError("Please specify at least 1 project to generate.")
        if self.num_researchers < 1:
            raise ValidationError("Please specify at least 1 researcher to generate.")

        positions = [
            "Principal Investigator",
            "Senior Postdoc",
            "Research Software Engineer",
            "Lead Bioinformatician",
            "Quantum Architect",
        ]
        expertise_list = [
            "AI & Machine Learning",
            "Quantum Algorithms & Cryptography",
            "Genomics & Bioinformatics",
            "Robotics & Autonomous Logistics",
        ]

        # ── 1. Researchers ───────────────────────────────────────────────────
        researchers = []
        for i in range(self.num_researchers):
            rand_id = random.randint(10000, 99999)
            login = f"user_synth_{rand_id}@example.com"
            user = self.env["res.users"].create({
                "name": f"Dr. Synthetic Researcher {rand_id}",
                "login": login,
                "email": login,
            })
            researcher = self.env["research.researcher"].create({
                "user_id": user.id,
                "position": random.choice(positions),
                "expertise": random.choice(expertise_list),
                "is_principal": random.choice([True, False]),
            })
            researchers.append(researcher)

        # ── 2. Project Tags (get-or-create) ──────────────────────────────────
        default_tags = [
            ("AI & Machine Learning", 1),
            ("Quantum Computing", 2),
            ("Genomics & Bio", 3),
            ("Logistics & Robotics", 4),
            ("High Priority", 5),
        ]
        created_tags = []
        for tag_name, color in default_tags:
            tag = self.env["research.project.tag"].search([("name", "=", tag_name)], limit=1)
            if not tag:
                tag = self.env["research.project.tag"].create({"name": tag_name, "color": color})
            created_tags.append(tag)

        project_titles = [
            "AI Logistics Optimization",
            "Quantum Network Routing",
            "Genomic Sequencing Pipeline",
            "Autonomous Lab Drone Fleet",
            "Cold-Chain Sample Tracking",
        ]

        req_categories = ["hardware", "software", "service", "dataset", "expertise"]
        resource_types = ["equipment", "software", "service", "dataset", "other"]
        output_types = ["paper", "dataset", "report", "software", "thesis"]

        for p_i in range(self.num_projects):
            lead = random.choice(researchers) if researchers else self.env["research.researcher"].search([], limit=1)
            today = fields.Date.today()
            sample_tags = random.sample(created_tags, k=random.randint(1, min(2, len(created_tags)))) if created_tags else []

            # ── Project ───────────────────────────────────────────────────────
            project = self.env["research.project"].create({
                "project_name": f"{random.choice(project_titles)} #{random.randint(100, 999)}",
                "project_description": "Synthetic project created via Sample Data Wizard.",
                "lead_researcher_id": lead.id if lead else False,
                "start_date": today,
                "end_date": today + timedelta(days=180),
                "project_status": "in_progress",
                "tag_ids": [(6, 0, [t.id for t in sample_tags])],
            })

            # ── Team Members ──────────────────────────────────────────────────
            # Add lead researcher as team member
            if lead:
                self.env["research.project.researcher"].create({
                    "project_id": project.id,
                    "researcher_id": lead.id,
                    "role": "Lead Investigator",
                    "allocated_pct": 80.0,
                    "join_date": today,
                })
            # Add a second team member if available and different from lead
            secondary = next((r for r in researchers if r != lead), None)
            if secondary:
                # Guard against duplicate assignment (UNIQUE constraint)
                already_assigned = self.env["research.project.researcher"].search_count([
                    ("project_id", "=", project.id),
                    ("researcher_id", "=", secondary.id),
                ])
                if not already_assigned:
                    self.env["research.project.researcher"].create({
                        "project_id": project.id,
                        "researcher_id": secondary.id,
                        "role": "Research Associate",
                        "allocated_pct": 50.0,
                        "join_date": today,
                    })

            # ── Budget (one per project — UNIQUE constraint) ──────────────────
            self.env["project.budget"].create({
                "project_id": project.id,
                "total_amount": float(random.randint(50, 300) * 1000),
                "spent_amount": float(random.randint(5, 45) * 1000),
                "start_date": today,
                "end_date": today + timedelta(days=180),
            })

            # ── Requirements (2 per project, different categories) ────────────
            cats = random.sample(req_categories, k=2)

            hw_req = self.env["research.requirement"].create({
                "project_id": project.id,
                "name": f"{random.choice(['HPC Cluster', 'GPU Node', 'Storage Array', 'Network Switch'])} #{p_i + 1}",
                "category": cats[0],
                "description": "Primary hardware requirement for research computation.",
                "quantity": float(random.randint(1, 8)),
                "priority": "high",
                "status": "approved",
                "requested_date": today,
                "needed_by": today + timedelta(days=30),
                "approval_note": "Approved via automated sample data generation.",
            })

            # Child sub-requirement under the first requirement
            self.env["research.requirement"].create({
                "project_id": project.id,
                "parent_id": hw_req.id,
                "name": f"Sub-component: {hw_req.name} Setup",
                "category": cats[0],
                "description": "Setup and configuration sub-task for the parent requirement.",
                "quantity": 1.0,
                "priority": "medium",
                "status": "requested",
                "requested_date": today,
                "needed_by": today + timedelta(days=45),
            })

            # Second requirement with a different category
            self.env["research.requirement"].create({
                "project_id": project.id,
                "name": f"{random.choice(['Cloud API Access', 'Software License', 'Dataset Subscription', 'Consulting Hours'])} #{p_i + 1}",
                "category": cats[1],
                "description": "Secondary software/service requirement for the project.",
                "quantity": float(random.randint(1, 20)),
                "priority": random.choice(["low", "medium"]),
                "status": "requested",
                "requested_date": today,
                "needed_by": today + timedelta(days=60),
            })

            # ── Resources (2 per project, different types) ────────────────────
            res_types = random.sample(resource_types, k=2)

            primary_resource = self.env["research.resource"].create({
                "name": f"{random.choice(['HPC Node', 'GPU Cluster', 'Sequencer Unit', 'Lab Instrument'])} #{p_i + 1}",
                "resource_type": res_types[0],
                "specification": "Auto-generated synthetic resource specification.",
                "availability_status": "in_use",
                "owner_project_id": project.id,
            })

            secondary_resource = self.env["research.resource"].create({
                "name": f"{random.choice(['MATLAB License', 'Cloud SDK', 'Reference Dataset', 'Keycard Pool'])} #{p_i + 1}",
                "resource_type": res_types[1],
                "description": "Secondary resource — software or service type.",
                "availability_status": "available",
                "owner_project_id": project.id,
            })

            # ── Experiments (2 per project: running + planned) ────────────────
            running_exp = self.env["research.experiment"].create({
                "project_id": project.id,
                "name": f"Primary Trial Experiment {p_i + 1}",
                "objective": "Validation of algorithm performance on synthetic data.",
                "methodology": "Run 5-fold cross validation trial with held-out test set.",
                "status": "running",
                "start_date": today,
            })

            planned_exp = self.env["research.experiment"].create({
                "project_id": project.id,
                "name": f"Follow-up Benchmarking Experiment {p_i + 1}",
                "objective": "Extended benchmarking against baseline methods after primary trial completes.",
                "methodology": "Compare primary trial results against 3 classical baseline algorithms.",
                "status": "planned",
            })

            # ── Experiment Resources ──────────────────────────────────────────
            self.env["research.experiment.resource"].create({
                "experiment_id": running_exp.id,
                "resource_id": primary_resource.id,
                "purpose": "Primary computation node for running experiment",
                "quantity": 1.0,
            })

            self.env["research.experiment.resource"].create({
                "experiment_id": running_exp.id,
                "resource_id": secondary_resource.id,
                "purpose": "Secondary software/data resource for running experiment",
                "quantity": 1.0,
            })

            self.env["research.experiment.resource"].create({
                "experiment_id": planned_exp.id,
                "resource_id": primary_resource.id,
                "purpose": "Planned resource allocation for upcoming benchmarking",
                "quantity": 1.0,
            })

            # ── Outputs (2 per project: paper + report/dataset) ───────────────
            out_type_1 = "paper"
            out_type_2 = random.choice(["dataset", "report", "software", "thesis"])

            primary_out = self.env["research.output"].create({
                "experiment_id": running_exp.id,
                "output_type": out_type_1,
                "name": f"Research Paper: {project.project_name}",
                "description": "Primary paper output from the running experiment.",
                "status": "draft",
            })

            self.env["research.output"].create({
                "experiment_id": planned_exp.id,
                "output_type": out_type_2,
                "name": f"Supplementary {out_type_2.capitalize()}: {project.project_name}",
                "description": f"Secondary {out_type_2} output planned for the follow-up benchmarking experiment.",
                "status": "draft",
            })

            # ── Research Paper ────────────────────────────────────────────────
            self.env["research.paper"].create({
                "paper_name": primary_out.name,
                "paper_author": lead.name if lead else "Author",
                "project_id": project.id,
                "output_id": primary_out.id,
                "paper_status": "draft",
                "paper_abstract": "Abstract generated automatically for sample data evaluation.",
            })

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Sample Data Created!",
                "message": (
                    f"Successfully generated {self.num_projects} projects and "
                    f"{self.num_researchers} researchers, each with: "
                    "project tags, team members, budget, 3 requirements (incl. child), "
                    "2 resources, 2 experiments (running + planned), "
                    "3 experiment resource links, 2 outputs, and 1 paper."
                ),
                "sticky": False,
                "next": {"type": "ir.actions.act_window_close"},
            },
        }