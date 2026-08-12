# Synthetic Data Generation & Testing Guide

This guide explains how to generate, manage, and verify test/fake data within the **Research Supply Chain** module.

---

## 🎯 Overview of Data Pipelines

To evaluate views, stress-test search filters, verify database constraints, and demonstrate functionality, 3 complementary data generation pipelines are implemented:

```
                                    Synthetic Data Pipelines
                                               │
             ┌─────────────────────────────────┼────────────────────────────────┐
             │                                 │                                │
             ▼                                 ▼                                ▼
+──────────────────────────+     +──────────────────────────+     +──────────────────────────+
|  Pipeline 1: Demo XML    |     |  Pipeline 2: UI Wizard   |     | Pipeline 3: Python Script|
|  (Self-Contained Data)   |     |  (Interactive Web UI)    |     | (Odoo Shell Bulk Script) |
+──────────────────────────+     +──────────────────────────+     +──────────────────────────+
| Location:                |     | Location:                |     | Location:                |
| demo/research_supply_... |     | Tools -> Generate Sample |     | scripts/generate_fake... |
| Automatic on install     |     | 1-click in browser       |     | Bulk benchmark testing   |
+──────────────────────────+     +──────────────────────────+     +──────────────────────────+
```

---

## 📌 Pipeline 1: Native Self-Contained XML Data

- **File**: [addons/research_supply_chain/demo/research_supply_chain_demo.xml](file:///d:/Center/Github_Profile/Research-Supply-Chain/addons/research_supply_chain/demo/research_supply_chain_demo.xml)
- **Manifest Listing**: Included under `"data"` in [__manifest__.py](file:///d:/Center/Github_Profile/Research-Supply-Chain/addons/research_supply_chain/__manifest__.py).

### How it Works
Unlike default Odoo demo files which require `--demo` flags upon DB creation, this dataset is self-contained and included under `"data"`. Whenever the module is installed or upgraded, Odoo populates:
- 4 Researchers (PI, Postdoc, Bioinformatician, Quantum Scientist)
- 4 Funded Projects (`AI Supply Chain`, `Quantum Network Routing`, `Genomic Sequencing`, `Autonomous Drone Logistics`)
- 4 Budgets ($90,000 to $300,000)
- Requirements, Resources (H100 GPUs, QPU Cloud channels, NovaSeq arrays), Experiments, Outputs, and Papers.

### How to Load
Upgrade the module from CMD or Odoo UI:
```bash
python odoo-bin -c odoo.conf -d <your_database_name> -u research_supply_chain
```

---

## 📌 Pipeline 2: Interactive UI Wizard ("Generate Sample Data")

- **Source Files**: [models/sample_data_wizard.py](file:///d:/Center/Github_Profile/Research-Supply-Chain/addons/research_supply_chain/models/sample_data_wizard.py) & [views/sample_data_wizard_views.xml](file:///d:/Center/Github_Profile/Research-Supply-Chain/addons/research_supply_chain/views/sample_data_wizard_views.xml)

### How to Use via Web Browser
1. Log into Odoo web interface.
2. Open **Research Supply Chain** module.
3. Click on **Tools** ➔ **Generate Sample Data**.
4. Set the number of **Projects** and **Researchers** to create.
5. Click **Generate Fake Data**.

```
+-------------------------------------------------------------+
| Generate Sample Data                                    [X] |
+-------------------------------------------------------------+
| Number of Projects:     [ 5 ]                               |
| Number of Researchers:  [ 5 ]                               |
|                                                             |
| Clicking "Generate Fake Data" will populate synthetic       |
| records across Projects, Researchers, Budgets, Requirements,|
| Resources, Experiments, Outputs, and Research Papers.       |
|                                                             |
| [ Generate Fake Data ]  [ Cancel ]                          |
+-------------------------------------------------------------+
```

---

## 📌 Pipeline 3: Bulk Odoo Shell Script

- **Script File**: [scripts/generate_fake_data.py](file:///d:/Center/Github_Profile/Research-Supply-Chain/scripts/generate_fake_data.py)

### How to Use
For high-volume stress testing (e.g. creating 50 projects and 20 researchers):

#### Command Line Execution:
```bash
# Using Odoo's Python executable
"..\python\python.exe" odoo-bin shell -c odoo.conf -d <your_database_name> < scripts/generate_fake_data.py
```

#### Interactive Odoo Shell Execution:
```python
python odoo-bin shell -c odoo.conf -d <your_database_name>

>>> from scripts.generate_fake_data import generate_all_fake_data
>>> generate_all_fake_data(env, num_projects=20, num_researchers=10)
```

---

## 🧪 Verification & Audit Commands

To verify that synthetic data was correctly populated in PostgreSQL/Odoo:

```python
# In Odoo shell:
print("Projects:", env['research.project'].search_count([]))
print("Researchers:", env['research.researcher'].search_count([]))
print("Budgets:", env['project.budget'].search_count([]))
print("Experiments:", env['research.experiment'].search_count([]))
print("Papers:", env['research.paper'].search_count([]))
```
