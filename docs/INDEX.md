# Research Supply Chain - Technical Documentation Index

Welcome to the official technical documentation for the **Research Supply Chain** module (Odoo 19.0 Enterprise / Community ecosystem).

This repository provides an enterprise-grade ERP solution tailored for managing the full lifecycle of scientific research projects, researcher allocations, resource constraints, budgets, experiment execution, biological/technological outputs, and academic publication tracking.

---

## 📚 Documentation Directory

| Document | Description | Target Audience |
| :--- | :--- | :--- |
| **[Architecture & Design](file:///d:/Center/Github_Profile/Research-Supply-Chain/docs/ARCHITECTURE.md)** | Core system architecture, entity-relationship (ER) diagrams, security model, and design patterns. | System Architects, Lead Developers, Technical Reviewers |
| **[Data Models Specification](file:///d:/Center/Github_Profile/Research-Supply-Chain/docs/DATA_MODELS.md)** | Exhaustive reference for all 10 custom Odoo models, fields, constraints, and business logic. | Backend Developers, Integrators, Database Administrators |
| **[Advanced Python Concepts Guide](file:///d:/Center/Github_Profile/Research-Supply-Chain/docs/PYTHON_CONCEPTS_GUIDE.md)** | Complete tutorial & reference for OOP, decorators, regex, recursion, generators, itertools, and error handling. | Python Developers, Learners, Code Auditors |
| **[API Specification & Reference](file:///d:/Center/Github_Profile/Research-Supply-Chain/docs/API_DOCUMENTATION.md)** | Complete REST & JSON-RPC endpoint reference, parameters, payloads, and response structures. | API Developers, Integrators, Frontend Engineers |
| **[Postman API Testing Guide](file:///d:/Center/Github_Profile/Research-Supply-Chain/docs/POSTMAN_API_GUIDE.md)** | Step-by-step Postman collection guide, authentication, and endpoint testing. | API Developers, QA Engineers, System Integrators |
| **[Testing & Synthetic Data](file:///d:/Center/Github_Profile/Research-Supply-Chain/docs/TESTING_AND_DATA_GENERATION.md)** | Manual for artificial data generation via XML, Python Odoo Shell, and the interactive UI Wizard. | QA Engineers, Testers, Operations Teams |
| **[Getting Started & Operations](file:///d:/Center/Github_Profile/Research-Supply-Chain/docs/GETTING_STARTED.md)** | Installation guide, environment prerequisites, database update workflows, and troubleshooting. | DevOps, System Administrators, New Contributors |

---

## 🎯 Executive Summary & Capabilities

The **Research Supply Chain** platform models research as an end-to-end operational supply network:

1. **Researcher Management**: Profile tracking, expertise indexing, principal investigator tagging, and user synchronization.
2. **Project Planning & Governance**: Project coding, lifecycle stage management (`proposed` ➔ `approved` ➔ `in_progress` ➔ `completed` ➔ `archived`), and multi-researcher allocation percentages.
3. **Financial Control & Budgets**: Multi-currency project budgets, real-time monetary spent vs. remaining tracking, and strict fiscal constraints.
4. **Supply Chain Requirements & Resource Allocation**: Material, equipment, and compute requirements linked with physical hardware, datasets, and cloud service allocations.
5. **Experimentation & Execution Tracking**: Experiment objectives, methodologies, real-time resource consumption, and status tracking.
6. **Outputs & Academic Publications**: Association of experiments to papers, datasets, software repositories, DOIs, and submission pipeline state transitions.
