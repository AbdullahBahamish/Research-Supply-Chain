# Getting Started & Operations Guide

This guide provides step-by-step instructions for installing, configuring, upgrading, and operating the **Research Supply Chain** Odoo 19 module.

---

## System Prerequisites

- **Odoo Version**: Odoo 19.0 (Enterprise or Community Edition)
- **Python Runtime**: Python 3.10+ (using Odoo's embedded Python environment)
- **Database Engine**: PostgreSQL 12+

---

## Installation & Environment Setup

### 1. Addon Placement
Copy or clone this repository into your Odoo custom addons directory:

```bash
cd /path/to/odoo/custom_addons
git clone https://github.com/AbdullahBahamish/Research-Supply-Chain.git
```

### 2. Configure `odoo.conf`
Ensure the custom addons directory is added to your `addons_path` in `odoo.conf`:

```ini
[options]
addons_path = /path/to/odoo/addons,d:\Center\Github_Profile\Research-Supply-Chain\addons
```

### 3. Module Activation & Upgrade Commands

#### CLI Installation / Upgrade (Recommended)
```bash
./odoo-bin -c odoo.conf -d research_db -i research_supply_chain
```

To upgrade an existing installation after pulling code updates:
```bash
./odoo-bin -c odoo.conf -d research_db -u research_supply_chain
```

#### Web Interface Activation
1. Log into your Odoo instance as Administrator.
2. Navigate to **Apps**.
3. Clear the search bar filter (`Apps`).
4. Search for `Research Supply Chain`.
5. Click **Activate** (or **Upgrade** if already installed).

---

## Common Errors & Troubleshooting Matrix

| Symptom / Error Log | Root Cause | Solution |
| :--- | :--- | :--- |
| `python: can't open file 'odoo-bin'` | Command executed outside of Odoo server directory. | Change directory (`cd`) to your Odoo installation root before executing `odoo-bin`. |
| `ModuleNotFoundError: No module named 'babel'` | Command executed using global system Python instead of Odoo's virtual environment. | Use Odoo's bundled Python executable path (`/path/to/odoo/venv/bin/python`). |
| `AccessError: Restricted model access` | User account is missing required security group. | Assign user to **Research User**, **Research Officer**, or **Research Manager** under Settings ➔ Users. |
| `ValidationError: End date before start date` | Date range validation trigger failed. | Ensure `end_date` is scheduled on or after `start_date`. |

---

## Repository Directory Reference

```
Research-Supply-Chain/
├── README.md                                    # Main repository overview
├── odools.toml                                  # Toolchain settings
├── scripts/
│   └── generate_fake_data.py                    # Bulk synthetic data generation script
├── docs/                                        # Complete 8-guide technical documentation suite
│   ├── INDEX.md                                 # Technical documentation index
│   ├── ARCHITECTURE.md                          # Architecture, ER diagram, and security model
│   ├── DATA_MODELS.md                           # Model field-by-field specification
│   ├── PYTHON_CONCEPTS_GUIDE.md                 # Python OOP, decorators, generators, & itertools
│   ├── API_DOCUMENTATION.md                     # REST/JSON-RPC API endpoint guide
│   ├── POSTMAN_API_GUIDE.md                     # Postman testing guide
│   ├── Research_Supply_Chain.postman_collection.json # Ready-to-use Postman collection
│   ├── TESTING_AND_DATA_GENERATION.md           # Test suite & synthetic data guide
│   └── GETTING_STARTED.md                       # Installation & operations guide
└── addons/
    └── research_supply_chain/
        ├── __init__.py                          # Package root
        ├── __manifest__.py                      # Odoo module manifest
        ├── controllers/
        │   └── main.py                          # REST API controllers & sanitizers
        ├── data/
        │   ├── research_supply_chain_data.xml   # Sequences & initial data
        │   └── ir_cron_data.xml                 # Scheduled cron jobs
        ├── demo/
        │   └── research_supply_chain_demo.xml   # Initial demo dataset
        ├── models/                              # ORM models & abstract mixins
        │   ├── research_project.py
        │   ├── researcher.py
        │   ├── research_project_researcher.py
        │   ├── project_budget.py
        │   ├── research_requirement.py
        │   ├── research_resource.py
        │   ├── experiment.py
        │   ├── experiment_resource.py
        │   ├── research_output.py
        │   ├── research_paper.py
        │   ├── project_tag.py
        │   ├── mixins.py
        │   └── sample_data_wizard.py
        ├── security/
        │   ├── research_security.xml            # Groups & record rules
        │   └── ir.model.access.csv              # Model access rights (ACL)
        ├── tests/                               # Automated unit test suite
        │   ├── test_research_project.py
        │   ├── test_researcher.py
        │   ├── test_requirements.py
        │   ├── test_experiment.py
        │   ├── test_cron_jobs.py
        │   ├── test_dynamic_changes.py
        │   └── test_inverse_functions.py
        └── views/                               # Odoo UI views & menus
```
