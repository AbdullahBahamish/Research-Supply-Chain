# Architecture & System Design

This document details the architectural foundation, entity relationships, security controls, and design patterns of the **Research Supply Chain** module.

---

## System Architecture Layers

The module follows Odoo's standard Model-View-Controller (MVC) architecture, extending the framework through cleanly isolated domain layers:

```
+-------------------------------------------------------------------+
|                        Web Presentation Layer                     |
|  (Kanban Views, Form Views, List Views, Search Filters, Menus)    |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|                       Business Logic & Domain Layer               |
|   (Python ORM Models, Business Constraints, Computed Fields)      |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|                    Security & Access Control Layer                |
|       (IR Access Rights CSV, Group Rules, Record-Level Rules)     |
+-------------------------------------------------------------------+
                                  |
                                  v
+-------------------------------------------------------------------+
|                       Persistence Layer                           |
|               (PostgreSQL Relational Storage Engine)              |
+-------------------------------------------------------------------+
```

---

## Entity-Relationship (ER) Diagram

The diagram below maps all custom models, foreign key relationships, cardinalities, and mixin inheritances within the module.

```mermaid
erDiagram
    RES_USERS ||--|| RESEARCH_RESEARCHER : "linked user account"
    RESEARCH_RESEARCHER ||--o{ RESEARCH_PROJECT : "leads project"
    RESEARCH_RESEARCHER ||--o{ RESEARCH_PROJECT_RESEARCHER : "assigned allocation"
    RESEARCH_PROJECT ||--o{ RESEARCH_PROJECT_RESEARCHER : "team allocation"
    RESEARCH_PROJECT ||--o| PROJECT_BUDGET : "financial budget"
    RESEARCH_PROJECT ||--o{ RESEARCH_REQUIREMENT : "project requirements"
    RESEARCH_PROJECT ||--o{ RESEARCH_RESOURCE : "owned resources"
    RESEARCH_PROJECT ||--o{ RESEARCH_EXPERIMENT : "experiments"
    RESEARCH_PROJECT ||--o{ RESEARCH_PAPER : "research papers"
    RESEARCH_PROJECT }|--|{ RESEARCH_PROJECT_TAG : "project tags"

    RESEARCH_EXPERIMENT ||--o{ RESEARCH_EXPERIMENT_RESOURCE : "allocates resource"
    RESEARCH_RESOURCE ||--o{ RESEARCH_EXPERIMENT_RESOURCE : "used by experiment"

    RESEARCH_EXPERIMENT ||--o{ RESEARCH_OUTPUT : "generates output"
    RESEARCH_OUTPUT ||--o| RESEARCH_PAPER : "linked publication"

    RESEARCH_AUDIT_MIXIN ||--|> RESEARCH_PROJECT : "inherits audit log"
    RESEARCH_EXPORTABLE_MIXIN ||--|> RESEARCH_PROJECT : "inherits stream export"

    RESEARCH_RESEARCHER {
        int id PK
        int user_id FK
        string position
        text expertise
        boolean is_principal
    }

    RESEARCH_PROJECT {
        int id PK
        string code
        string project_name
        string visibility
        int lead_researcher_id FK
        date start_date
        date end_date
        string project_status
    }

    PROJECT_BUDGET {
        int id PK
        int project_id FK
        int currency_id FK
        monetary total_amount
        monetary spent_amount
        monetary remaining_amount
    }

    RESEARCH_REQUIREMENT {
        int id PK
        int project_id FK
        string category
        string name
        float quantity
        string priority
        string status
    }

    RESEARCH_RESOURCE {
        int id PK
        int owner_project_id FK
        string resource_type
        string name
        string availability_status
    }

    RESEARCH_EXPERIMENT {
        int id PK
        int project_id FK
        string name
        int owner_id FK
        string status
    }

    RESEARCH_OUTPUT {
        int id PK
        int experiment_id FK
        string output_type
        string name
        string status
    }

    RESEARCH_PAPER {
        int id PK
        int project_id FK
        int output_id FK
        string paper_name
        string paper_status
        string paper_doi
    }

    RESEARCH_PROJECT_TAG {
        int id PK
        string name
        int color
    }
```

---

## Security & Access Control Model

The security architecture operates on a multi-tiered access control paradigm configured in `security/research_security.xml` and `security/ir.model.access.csv`:

### 1. User Security Groups
- **`group_research_user` (Research User / Viewer)**: Read access to public projects, experiments, papers, and resource directories.
- **`group_research_officer` (Research Officer)**: Create and update permissions for project requirements, experiments, resources, and outputs.
- **`group_research_manager` (Research Manager)**: Full administrative authority over projects, financial budgets, security rules, and archival.

### 2. Access Rights Table (`ir.model.access.csv`)

| Model ID | Model Technical Name | Read | Write | Create | Delete |
| :--- | :--- | :---: | :---: | :---: | :---: |
| `model_research_researcher` | Researcher Profile | Yes | Yes | Yes | Yes |
| `model_research_project` | Research Project | Yes | Yes | Yes | Yes |
| `model_research_project_tag` | Research Project Tag | Yes | Yes | Yes | Yes |
| `model_research_project_researcher` | Team Allocation | Yes | Yes | Yes | Yes |
| `model_project_budget` | Project Budget | Yes | Yes | Yes | Yes |
| `model_research_requirement` | Requirement | Yes | Yes | Yes | Yes |
| `model_research_resource` | Resource | Yes | Yes | Yes | Yes |
| `model_research_experiment` | Experiment | Yes | Yes | Yes | Yes |
| `model_research_experiment_resource` | Experiment Resource | Yes | Yes | Yes | Yes |
| `model_research_output` | Research Output | Yes | Yes | Yes | Yes |
| `model_research_paper` | Research Paper | Yes | Yes | Yes | Yes |
| `model_research_sample_data_wizard` | Sample Data Wizard | Yes | Yes | Yes | Yes |

### 3. Record-Level Rules & Privacy Guardrails
- **Project Visibility Rule**: Public projects (`visibility='public'`) are visible across all authenticated users. Private projects (`visibility='private'`) are strictly restricted to assigned team members (`researcher_line_ids`) and Research Managers.
- **Experiment Ownership Rule**: Users can modify experiments where `owner_id = user.id`. Research Managers bypass ownership restrictions.
- **Controller Input Whitelisting**: REST endpoints sanitize all parameter inputs against explicit field allow-lists (`PROJECT_SEARCH_FIELDS`, `PROJECT_CREATE_FIELDS`), preventing domain injection probes and mass-assignment vulnerabilities.

---

## Key Design & Integrity Patterns

1. **Automatic Reference Sequence (`ir.sequence`)**:
   Projects automatically pull unique identifiers (e.g., `PRJ00001`) via `@api.model_create_multi` hooks in [`research_project.py`](file:///d:/Center/Github_Profile/Research-Supply-Chain/addons/research_supply_chain/models/research_project.py).

2. **Bidirectional Stored Computes & Inverse Handlers**:
   Monetary budget fields (`total_budget_amount`, `total_spent_amount`, `remaining_budget_amount`) use `@api.depends` stored computations alongside `@inverse` handlers, allowing seamless updates from parent projects or direct budget line items.

3. **Strict Validation & SQL Constraints**:
   - `CHECK(start_date IS NULL OR end_date IS NULL OR end_date >= start_date)` across projects, budgets, and experiments.
   - `UNIQUE(code)` on project codes and `UNIQUE(name)` on project tags.
   - Objective requirement constraints before moving experiments to `running` or `completed` states.

4. **Audit Logging & System Event Decoupling**:
   Abstract mixin [`ResearchAuditMixin`](file:///d:/Center/Github_Profile/Research-Supply-Chain/addons/research_supply_chain/models/mixins.py) integrates automated audit history tracking (`audit_notes`) and chatter post integration (`message_post`).
