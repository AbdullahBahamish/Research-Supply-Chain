# Research-Supply-Chain

An open-source **Odoo 19** module for managing the lifecycle of research projects, team allocations, project requirements, shared resources, experimental runs, project budgets, and research outputs.

## 📖 Documentation Suite

Comprehensive technical documentation is available in the **[`docs/`](file:///d:/Center/Github_Profile/Research-Supply-Chain/docs/)** folder:

- 📘 **[Documentation Index](file:///d:/Center/Github_Profile/Research-Supply-Chain/docs/INDEX.md)** — Main documentation hub & executive overview.
- 🏛️ **[Architecture & System Design](file:///d:/Center/Github_Profile/Research-Supply-Chain/docs/ARCHITECTURE.md)** — System layers, Mermaid ER diagram, and security matrix.
- 📊 **[Data Models Specification](file:///d:/Center/Github_Profile/Research-Supply-Chain/docs/DATA_MODELS.md)** — Exhaustive field-by-field reference for all 10 Odoo models.
- 🐍 **[Advanced Python Concepts Guide](file:///d:/Center/Github_Profile/Research-Supply-Chain/docs/PYTHON_CONCEPTS_GUIDE.md)** — Hands-on implementation of OOP, decorators, regex, recursion, & iterators.
- 📡 **[API Specification & Reference](file:///d:/Center/Github_Profile/Research-Supply-Chain/docs/API_DOCUMENTATION.md)** — Endpoints, JSON payloads, responses, and error specs.
- 🚀 **[Postman API Testing Guide](file:///d:/Center/Github_Profile/Research-Supply-Chain/docs/POSTMAN_API_GUIDE.md)** — Pre-built Postman collection & endpoint guide.
- 🧪 **[Testing & Synthetic Data](file:///d:/Center/Github_Profile/Research-Supply-Chain/docs/TESTING_AND_DATA_GENERATION.md)** — XML, Python Shell, and UI Wizard test data pipelines.
- 🚀 **[Getting Started & Deployment](file:///d:/Center/Github_Profile/Research-Supply-Chain/docs/GETTING_STARTED.md)** — Installation, environment setup, and troubleshooting guide.

---

## 📌 Architecture Overview

The `research_supply_chain` module implements the complete MVP scope:

```
                  +-----------------------+
                  |    res.users          |
                  +-----------+-----------+
                              |
                              v
                  +-----------+-----------+
                  |  research.researcher  |
                  +-----------+-----------+
                              |
                              v
                  +-----------+-----------+
                  | research.project.     |
                  | researcher            |
                  +-----------+-----------+
                              ^
                              |
+-----------------+   +-------+-------+   +-------------------+
| project.budget  |---| research.     |---| research.         |
|                 |   | project       |   | requirement       |
+-----------------+   +-------+-------+   +-------------------+
                              |
                              |
                      +-------+-------+
                      | research.     |
                      | resource      |
                      +-------+-------+
                              |
                              v
                      +-------+-------+
                      | research.     |
                      | experiment    |
                      +-------+-------+
                              |
                              v
                      +-------+-------+
                      | research.     |
                      | output        |
                      +---------------+
                              |
                              v
                      +---------------+
                      | research.     |
                      | paper         |
                      +---------------+
```

---

## 🗂️ Core Models

| Model Technical Name | Description | Key Fields & Relationships |
|---|---|---|
| `research.researcher` | Researcher / Team Member | `user_id`, `position`, `expertise`, `is_principal`, `project_line_ids` |
| `research.project` | Research Project | `code`, `project_name`, `lead_researcher_id`, `start_date`, `end_date`, `project_status`, `budget_ids`, `requirement_ids`, `resource_ids`, `experiment_ids`, `paper_ids` |
| `research.project.researcher` | Project Team Allocation | `project_id`, `researcher_id`, `role`, `allocated_pct`, `join_date` |
| `project.budget` | Project Financial Budget | `project_id`, `currency_id`, `total_amount`, `spent_amount`, `remaining_amount` |
| `research.requirement` | Requirement / Request | `project_id`, `category`, `name`, `quantity`, `priority`, `status`, `needed_by` |
| `research.resource` | Shared Hardware / Dataset | `name`, `resource_type`, `specification`, `availability_status`, `owner_project_id` |
| `research.experiment` | Experimental Run | `project_id`, `name`, `objective`, `methodology`, `status`, `created_by`, `experiment_resource_ids`, `output_ids` |
| `research.experiment.resource` | Experiment Resource Usage | `experiment_id`, `resource_id`, `purpose`, `quantity` |
| `research.output` | Deliverable / Output | `experiment_id`, `project_id`, `output_type`, `name`, `status` |
| `research.paper` | Publication / Academic Paper | `paper_name`, `paper_author`, `paper_doi`, `paper_status`, `paper_github_url`, `project_id`, `output_id` |

---

## 🚀 Installation & Usage

### 1. Module Placement
Ensure `addons/research_supply_chain` is included in your Odoo `addons_path`.

```bash
./odoo-bin -c odoo.conf -d research_db -i research_supply_chain
```

### 2. Loading Demo Data
Run Odoo with `--demo` flag or enable demo data on database creation to load initial sample projects, researchers, budgets, requirements, equipment, experiments, and research outputs:

```bash
./odoo-bin -c odoo.conf -d research_db_demo --dev=all
```

---

## 🧪 Testing

Automated test coverage is provided under `addons/research_supply_chain/tests/`:

```bash
./odoo-bin -c odoo.conf -d research_test_db --test-enable --test-tags=research_supply_chain
```

---

## 📄 License
Licensed under the **MIT License**. See [`LICENSE`](file:///d:/Center/Github_Profile/Research-Supply-Chain/LICENSE) for details.
