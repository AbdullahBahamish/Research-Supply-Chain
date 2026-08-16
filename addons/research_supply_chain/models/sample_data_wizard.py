from datetime import timedelta
import random
from odoo import models, fields  # type: ignore  # pyfly: ignore [missing-import]

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

        project_titles = [
            "AI Logistics Optimization",
            "Quantum Network Routing",
            "Genomic Sequencing Pipeline",
            "Autonomous Lab Drone Fleet",
            "Cold-Chain Sample Tracking",
        ]

        for p_i in range(self.num_projects):
            lead = random.choice(researchers) if researchers else self.env["research.researcher"].search([], limit=1)
            today = fields.Date.today()
            project = self.env["research.project"].create({
                "project_name": f"{random.choice(project_titles)} #{random.randint(100, 999)}",
                "project_description": "Synthetic project created via Sample Data Wizard.",
                "lead_researcher_id": lead.id if lead else False,
                "start_date": today,
                "end_date": today + timedelta(days=180),
                "project_status": "in_progress",
            })

            # Create budget
            self.env["project.budget"].create({
                "project_id": project.id,
                "total_amount": float(random.randint(50, 300) * 1000),
                "spent_amount": float(random.randint(10, 50) * 1000),
                "start_date": today,
                "end_date": today + timedelta(days=180),
            })

            # Create requirement
            self.env["research.requirement"].create({
                "project_id": project.id,
                "name": f"High Performance Cluster Unit #{p_i+1}",
                "category": "hardware",
                "description": "GPU cluster access required for research modeling.",
                "quantity": float(random.randint(1, 8)),
                "priority": "high",
                "status": "approved",
                "requested_date": today,
            })

            # Create resource
            resource = self.env["research.resource"].create({
                "name": f"HPC Computing Node Cluster #{p_i+1}",
                "resource_type": "equipment",
                "specification": "Dual EPYC, 8x H100 80GB",
                "availability_status": "in_use",
                "owner_project_id": project.id,
            })

            # Create experiment
            exp = self.env["research.experiment"].create({
                "project_id": project.id,
                "name": f"Trial Experiment {p_i + 1}",
                "objective": "Validation of algorithm performance.",
                "methodology": "Run 5-fold cross validation trial.",
                "status": "running",
                "start_date": today,
            })

            # Link resource to experiment
            self.env["research.experiment.resource"].create({
                "experiment_id": exp.id,
                "resource_id": resource.id,
                "purpose": "Primary Execution Node",
                "quantity": 1.0,
            })

            # Create output & paper
            out = self.env["research.output"].create({
                "experiment_id": exp.id,
                "output_type": "paper",
                "name": f"Paper on {project.project_name}",
                "status": "draft",
            })

            self.env["research.paper"].create({
                "paper_name": out.name,
                "paper_author": lead.name if lead else "Author",
                "project_id": project.id,
                "output_id": out.id,
                "paper_status": "draft",
                "paper_abstract": "Abstract generated automatically for sample data evaluation.",
            })

        return {
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "title": "Data Created!",
                "message": f"Successfully generated {self.num_projects} projects and {self.num_researchers} researchers with budgets, resources, experiments, and papers!",
                "sticky": False,
                "next": {"type": "ir.actions.act_window_close"},
            },
        }
