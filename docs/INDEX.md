# Research Supply Chain - Technical Documentation Index

Welcome to the central technical documentation suite for the **Research Supply Chain** module (built for Odoo 19.0 Enterprise / Community ecosystem).

This repository provides an enterprise-grade ERP solution tailored for managing the full lifecycle of scientific research projects, researcher allocations, resource constraints, budgets, experiment execution, biological/technological outputs, and academic publication tracking.

---

## Technical Documentation Hub

| Document Guide | Description | Primary Target Audience |
| :--- | :--- | :--- |
| **[Architecture & System Design](file:///d:/Center/Github_Profile/Research-Supply-Chain/docs/ARCHITECTURE.md)** | System architecture layers, entity-relationship (ER) diagrams, security model, and key design patterns. | System Architects, Lead Developers, Code Reviewers |
| **[Data Models Specification](file:///d:/Center/Github_Profile/Research-Supply-Chain/docs/DATA_MODELS.md)** | Exhaustive field-by-field reference for all 11 custom Odoo models, abstract mixins, constraints, and business logic. | Backend Developers, Integrators, Database Administrators |
| **[Advanced Python Concepts Guide](file:///d:/Center/Github_Profile/Research-Supply-Chain/docs/PYTHON_CONCEPTS_GUIDE.md)** | Complete guide to Python OOP, abstract mixins, custom decorators (`@system_audit_log`, `@validate_regex_pattern`), regex validation, generators, itertools, and error handling. | Python Developers, Code Auditors |
| **[API Specification & Reference](file:///d:/Center/Github_Profile/Research-Supply-Chain/docs/API_DOCUMENTATION.md)** | REST & JSON-RPC endpoint reference, parameters, input sanitization rules, and response payloads. | API Integrators, Web/Mobile Developers |
| **[Postman API Testing Guide](file:///d:/Center/Github_Profile/Research-Supply-Chain/docs/POSTMAN_API_GUIDE.md)** | Step-by-step Postman collection guide, authentication, and endpoint test suite execution. | QA Engineers, System Integrators |
| **[Testing & Synthetic Data](file:///d:/Center/Github_Profile/Research-Supply-Chain/docs/TESTING_AND_DATA_GENERATION.md)** | Automated test runner commands, Python synthetic data generator script (`scripts/generate_fake_data.py`), and interactive UI wizard. | QA Engineers, Automation Testers |
| **[Getting Started & Operations](file:///d:/Center/Github_Profile/Research-Supply-Chain/docs/GETTING_STARTED.md)** | Installation guide, environment prerequisites, database update workflows, and troubleshooting. | DevOps, System Administrators |

---

## Executive Summary & Core Capabilities

The **Research Supply Chain** platform models research as an end-to-end operational supply network across 6 main domain pillars:

1. **Researcher Governance**: Profile tracking, expertise indexing, principal investigator tagging, user synchronization, and team effort percentage allocations.
2. **Project Planning & Visibility**: Project code auto-generation (`PRJ00001`), lifecycle stage management (`proposed` ➔ `approved` ➔ `in_progress` ➔ `completed` ➔ `archived`), tags, and public/private visibility security controls.
3. **Financial Control & Budgets**: Multi-currency project budgets, computed monetary balances (`total_amount - spent_amount`), budget utilization percentages, and strict fiscal constraints.
4. **Requirement & Resource Management**: Procurement requests for hardware, compute, software, and services linked with shared resource catalog allocations.
5. **Experimentation & Execution Tracking**: Experiment objectives, procedures, real-time resource consumption, owner-based execution security, and automated state transitions.
6. **Outputs & Academic Publications**: Associating deliverables to academic preprints, DOIs, GitHub code repositories, and public citation endpoints.

---

## Codebase Structure Quick Reference

```
Research-Supply-Chain/
├── README.md                                    # Repository overview
├── odools.toml                                  # Odoo toolchain configuration
├── addons/
│   └── research_supply_chain/
│       ├── __manifest__.py                      # Odoo module manifest
│       ├── controllers/
│       │   └── main.py                          # REST/JSON-RPC API controllers
│       ├── models/                              # ORM business models & mixins
│       │   ├── research_project.py
│       │   ├── researcher.py
│       │   ├── research_project_researcher.py
│       │   ├── project_budget.py
│       │   ├── research_requirement.py
│       │   ├── research_resource.py
│       │   ├── experiment.py
│       │   ├── experiment_resource.py
│       │   ├── research_output.py
│       │   ├── research_paper.py
│       │   ├── project_tag.py
│       │   ├── mixins.py                        # Audit & export abstract mixins
│       │   └── sample_data_wizard.py            # Synthetic data wizard
│       ├── security/                            # Groups, ACL, and record rules
│       ├── views/                               # XML views & menu structure
│       ├── data/                                # Default data & cron definitions
│       ├── demo/                                # Demo data XML files
│       └── tests/                               # Unit test suite
├── docs/                                        # Complete 8-guide documentation suite
└── scripts/
    └── generate_fake_data.py                    # Standalone Python synthetic data script
```
