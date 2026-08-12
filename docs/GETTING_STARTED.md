# Getting Started & Deployment Guide

This guide provides step-by-step instructions for setting up, installing, upgrading, and troubleshooting the **Research Supply Chain** Odoo 19 module.

---

## 📋 Prerequisites

- **Odoo Version**: Odoo 19.0 (Enterprise or Community Edition)
- **Python Version**: Python 3.10+ (using Odoo's embedded Python environment)
- **Database Engine**: PostgreSQL 12+

---

## 🚀 Installation & Module Loading

### Step 1: Clone Repository into Addons Path
Clone or copy this repository into your Odoo custom addons directory:

```bash
cd /path/to/odoo/custom_addons
git clone https://github.com/AbdullahBahamish/Research-Supply-Chain.git
```

### Step 2: Configure `odoo.conf`
Ensure the custom addons directory is added to your `addons_path` in `odoo.conf`:

```ini
[options]
addons_path = D:\Program Files D\Odoo 19.0.20260810\server\odoo\addons,d:\Center\Github_Profile\Research-Supply-Chain\addons
```

### Step 3: Install or Upgrade Module

#### Option A: Via Command Line (Recommended for Developers)
Ensure you use **Odoo's embedded Python executable**, not global system Python:

```cmd
# Navigate to Odoo server directory
cd "D:\Program Files D\Odoo 19.0.20260810\server"

# Run upgrade command
"..\python\python.exe" odoo-bin -c odoo.conf -d <YOUR_DB_NAME> -u research_supply_chain
```

#### Option B: Via Odoo Web Browser Interface
1. Log into your Odoo instance as Administrator.
2. Navigate to **Apps**.
3. Clear the search bar filter (click `X` on **Apps**).
4. Search for `Research Supply Chain`.
5. Click **Activate** (or **Upgrade** if already installed).

---

## 🛠️ Common Errors & Troubleshooting

### Issue 1: `python: can't open file 'odoo-bin': No such file or directory`
- **Cause**: Command executed outside of Odoo server directory (e.g. `C:\Windows\System32`).
- **Fix**: `cd` into your Odoo installation's `server` folder before executing `odoo-bin`.

### Issue 2: `ModuleNotFoundError: No module named 'babel'`
- **Cause**: Using global system Python (e.g. `C:\Program Files\Python314\python.exe`) instead of Odoo's bundled Python virtual environment.
- **Fix**: Use `"..\python\python.exe"` (or the exact path to Odoo's Python executable).

### Issue 3: No Fake Data Appearing
- **Cause**: Database was not initialized with `--demo` flag.
- **Fix**: As of recent updates, demo XML is included directly under `"data"` in [__manifest__.py](file:///d:/Center/Github_Profile/Research-Supply-Chain/addons/research_supply_chain/__manifest__.py). Simply run `-u research_supply_chain` or use the in-app wizard (**Research Supply Chain ➔ Tools ➔ Generate Sample Data**).

---

## 📁 Repository Structure Overview

```
Research-Supply-Chain/
├── README.md
├── docs/
│   ├── INDEX.md
│   ├── ARCHITECTURE.md
│   ├── DATA_MODELS.md
│   ├── TESTING_AND_DATA_GENERATION.md
│   └── GETTING_STARTED.md
├── scripts/
│   └── generate_fake_data.py
└── addons/
    └── research_supply_chain/
        ├── __init__.py
        ├── __manifest__.py
        ├── data/
        │   └── research_supply_chain_data.xml
        ├── demo/
        │   └── research_supply_chain_demo.xml
        ├── models/
        │   ├── __init__.py
        │   ├── researcher.py
        │   ├── research_project.py
        │   ├── research_project_researcher.py
        │   ├── project_budget.py
        │   ├── research_requirement.py
        │   ├── research_resource.py
        │   ├── experiment.py
        │   ├── experiment_resource.py
        │   ├── research_output.py
        │   ├── research_paper.py
        │   └── sample_data_wizard.py
        ├── security/
        │   ├── research_security.xml
        │   └── ir.model.access.csv
        ├── static/
        │   └── description/
        └── views/
            ├── researcher_views.xml
            ├── research_project_views.xml
            ├── project_budget_views.xml
            ├── research_requirement_views.xml
            ├── research_resource_views.xml
            ├── experiment_views.xml
            ├── research_output_views.xml
            ├── research_paper_views.xml
            ├── sample_data_wizard_views.xml
            └── research_supply_chain_menus.xml
```
