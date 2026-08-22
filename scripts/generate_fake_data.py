#!/usr/bin/env python3
"""
Artificial Data Generator Script for Research Supply Chain Odoo Module.

This script populates synthetic artificial data for stress testing and operational evaluation.
Can be executed within the Odoo Shell environment:
    python odoo-bin shell -c odoo.conf -d <database_name> < scripts/generate_fake_data.py

Or imported inside Odoo environment:
    from scripts.generate_fake_data import generate_all_fake_data
    generate_all_fake_data(env, count=20)
"""

import random
from datetime import datetime, timedelta

def get_random_date(start_days_ago=180, end_days_ahead=180):
    start = datetime.now() - timedelta(days=start_days_ago)
    end = datetime.now() + timedelta(days=end_days_ahead)
    random_date = start + timedelta(seconds=random.randint(0, int((end - start).total_seconds())))
    return random_date.strftime('%Y-%m-%d')

PROJECT_TITLES = [
    "AI-Driven Supply Chain Logistics Optimization",
    "Quantum-Accelerated Network Routing Architecture",
    "Genomic Data Stream Pipeline for Specimen Logistics",
    "Autonomous Micro-Drone Fleet for Urgent Lab Reagents",
    "Decentralized Cold-Chain Supply Tracking via Blockchain",
    "Predictive Inventory Forecasting for Lab Equipment",
    "High-Throughput Cryo-EM Sample Preparation Automation",
    "Bio-Pharma Reagent Cold Supply Chain Resilience Benchmark",
]

PROJECT_DESCRIPTIONS = [
    "Developing end-to-end Machine Learning pipelines to balance supply inventory with active research requirements.",
    "Applying quantum annealing and QAOA algorithms to multi-commodity allocation problems across regional labs.",
    "Designing real-time genomic sample metadata tracking and distributed storage architectures.",
    "Deploying autonomous aerial vehicles for micro-logistics deliveries across multi-building research centers.",
    "Implementing immutable audit logs for temperature-sensitive research samples across international transport networks.",
]

POSITIONS = [
    "Principal Investigator",
    "Senior Postdoctoral Researcher",
    "Research Software Engineer",
    "Lead Bioinformatician",
    "Quantum Architect",
    "Logistics Data Analyst",
]

EXPERTISE_LIST = [
    "Machine Learning, Optimization, Python",
    "Quantum Computing, QAOA, Qiskit",
    "Genomics, Nextflow, Distributed Systems",
    "Robotics, ROS2, Autonomous Systems",
    "Supply Chain Management, Operations Research",
]

RESOURCE_TYPES = ["dataset", "equipment", "software", "service"]
REQUIREMENT_CATEGORIES = ["dataset", "hardware", "software", "service", "expertise"]
OUTPUT_TYPES = ["paper", "dataset", "software", "report"]

def generate_all_fake_data(env, num_projects=5, num_researchers=8):
    """
    Generate synthetic fake data across all Research Supply Chain models.
    """
    print(f"--- [Research Supply Chain] Generating {num_projects} Projects and {num_researchers} Researchers ---")

    # 1. Create Res Users & Researchers
    researchers = []
    # Add base admin/demo if available
    admin_researcher = env['research.researcher'].search([('user_id', '=', env.ref('base.user_admin').id)], limit=1)
    if admin_researcher:
        researchers.append(admin_researcher)

    for i in range(num_researchers):
        name = f"Dr. Synthetic Researcher {i+1}"
        email = f"synth_researcher_{i+1}_{random.randint(1000, 9999)}@research.org"
        
        user = env['res.users'].create({
            'name': name,
            'login': email,
            'email': email,
        })
        
        researcher = env['research.researcher'].create({
            'user_id': user.id,
            'position': random.choice(POSITIONS),
            'expertise': random.choice(EXPERTISE_LIST),
            'is_principal': random.choice([True, False]),
        })
        researchers.append(researcher)

    print(f"Created {len(researchers)} researchers.")

    # 2. Create Projects & Associated Records
    for p_idx in range(num_projects):
        lead_r = random.choice(researchers)
        start_d = get_random_date(start_days_ago=120, end_days_ahead=30)
        end_d = get_random_date(start_days_ago=0, end_days_ahead=240)

        title = f"{random.choice(PROJECT_TITLES)} #{p_idx+1}"
        project = env['research.project'].create({
            'project_name': title,
            'project_description': random.choice(PROJECT_DESCRIPTIONS),
            'lead_researcher_id': lead_r.id,
            'start_date': start_d,
            'end_date': end_d,
            'project_status': random.choice(['proposed', 'approved', 'in_progress', 'completed']),
        })

        # Project Team Members
        team_sample = random.sample(researchers, min(len(researchers), random.randint(2, 4)))
        for member in team_sample:
            env['research.project.researcher'].create({
                'project_id': project.id,
                'researcher_id': member.id,
                'role': 'Co-Investigator' if member.is_principal else 'Research Associate',
                'allocated_pct': random.choice([25.0, 50.0, 75.0, 100.0]),
                'join_date': start_d,
            })

        # Project Budget
        total_amt = float(random.randint(50, 500) * 1000)
        spent_amt = float(random.randint(10, int(total_amt / 1000)) * 1000)
        env['project.budget'].create({
            'project_id': project.id,
            'total_amount': total_amt,
            'spent_amount': spent_amt,
            'start_date': start_d,
            'end_date': end_d,
        })

        # Requirements
        for req_i in range(random.randint(1, 3)):
            env['research.requirement'].create({
                'project_id': project.id,
                'name': f"Req: {random.choice(REQUIREMENT_CATEGORIES).capitalize()} Allocation #{req_i+1}",
                'category': random.choice(REQUIREMENT_CATEGORIES),
                'description': f"Specific synthetic requirement for project {project.code}",
                'quantity': float(random.randint(1, 10)),
                'priority': random.choice(['low', 'medium', 'high']),
                'status': random.choice(['requested', 'approved', 'fulfilled']),
                'requested_date': start_d,
            })

        # Resources
        project_resources = []
        for res_i in range(random.randint(1, 3)):
            res = env['research.resource'].create({
                'name': f"Resource {random.choice(['H100 Node', 'Sequencers Unit', 'Drone Fleet', 'SAN Storage'])} #{p_idx+1}-{res_i+1}",
                'resource_type': random.choice(RESOURCE_TYPES),
                'description': f"High-capacity resource owned by {project.project_name}",
                'specification': "Standard artificial benchmark spec v1.0",
                'availability_status': random.choice(['available', 'in_use']),
                'owner_project_id': project.id,
            })
            project_resources.append(res)

        # Experiments
        for exp_i in range(random.randint(1, 3)):
            exp_status = random.choice(['planned', 'running', 'completed'])
            exp = env['research.experiment'].create({
                'project_id': project.id,
                'name': f"Exp {exp_i+1}: {project.project_name[:25]} Trial",
                'objective': "Validate operational throughput and efficiency under load.",
                'methodology': "Execute randomized operational cycles across 5 test iterations.",
                'status': exp_status,
                'start_date': start_d,
                'owner_id': env.uid,
            })

            # Allocate resource to experiment
            if project_resources:
                res_to_use = random.choice(project_resources)
                env['research.experiment.resource'].create({
                    'experiment_id': exp.id,
                    'resource_id': res_to_use.id,
                    'purpose': "Primary computational execution node",
                    'quantity': 1.0,
                })

            # Experiment Outputs & Papers
            if exp_status == 'completed' or random.choice([True, False]):
                output_type = random.choice(OUTPUT_TYPES)
                out = env['research.output'].create({
                    'experiment_id': exp.id,
                    'output_type': output_type,
                    'name': f"Output: {exp.name} - Results",
                    'status': random.choice(['draft', 'under_review', 'published']),
                })

                if output_type == 'paper':
                    env['research.paper'].create({
                        'paper_name': f"Study on {exp.name}",
                        'paper_author': f"{lead_r.name}, {random.choice(researchers).name}",
                        'project_id': project.id,
                        'output_id': out.id,
                        'paper_status': random.choice(['draft', 'submitted', 'published']),
                        'paper_abstract': f"Synthetic evaluation abstract for experiment {exp.name}.",
                        'paper_github_url': "https://github.com/AbdullahBahamish/Research-Supply-Chain",
                    })

    env.cr.commit()
    print("--- [Research Supply Chain] Artificial data generation complete! ---")


# Execute automatically if run directly in `odoo shell`
if 'env' in locals() or 'env' in globals():
    generate_all_fake_data(env, num_projects=6, num_researchers=6)
