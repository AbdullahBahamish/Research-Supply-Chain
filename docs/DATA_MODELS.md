# Data Models Specification

This document provides a comprehensive technical reference for all custom models in the **Research Supply Chain** module.

---

## 1. `research.researcher` (Researcher)
- **Source File**: [models/researcher.py](file:///d:/Center/Github_Profile/Research-Supply-Chain/addons/research_supply_chain/models/researcher.py)
- **Description**: Represents individual research staff, faculty, postdocs, or lab members.

### Fields
| Field Name | Type | Properties | Description |
| :--- | :--- | :--- | :--- |
| `user_id` | Many2one (`res.users`) | Required, Cascade, Unique | System user account linked to researcher. |
| `name` | Char | Related (`user_id.name`), Stored | Researcher full name. |
| `email` | Char | Related (`user_id.email`), Readonly | Researcher email address. |
| `position` | Char | Optional | Academic or professional title (e.g. Principal Investigator, Bioinformatician). |
| `expertise` | Text | Optional | Core competencies, research domains, or key skills. |
| `is_principal` | Boolean | Default: `False` | Flags if researcher is qualified as a Principal Investigator (PI). |
| `active` | Boolean | Default: `True` | Archival flag. |
| `project_line_ids` | One2many | `research.project.researcher` | Reverse relation to team allocations. |

---

## 2. `research.project` (Research Project)
- **Source File**: [models/research_project.py](file:///d:/Center/Github_Profile/Research-Supply-Chain/addons/research_supply_chain/models/research_project.py)
- **Description**: The primary business unit representing a funded research grant or project.

### Fields
| Field Name | Type | Properties | Description |
| :--- | :--- | :--- | :--- |
| `code` | Char | Readonly, Sequence | System-generated code (e.g., `PRJ00001`). |
| `project_name` | Char | Required | Title of the research project. |
| `project_description` | Text | Optional | Abstract and scope description. |
| `lead_researcher_id` | Many2one | `research.researcher` | Lead Principal Investigator assigned to project. |
| `start_date` | Date | Optional | Scheduled project start date. |
| `end_date` | Date | Optional | Scheduled project end date. |
| `project_status` | Selection | Default: `'proposed'`, Required | Status: `proposed`, `approved`, `in_progress`, `completed`, `archived`. |
| `researcher_line_ids` | One2many | `research.project.researcher` | Team members and allocation details. |
| `budget_ids` | One2many | `project.budget` | Associated financial budget lines. |
| `requirement_ids` | One2many | `research.requirement` | Supply chain requirements. |
| `resource_ids` | One2many | `research.resource` | Physical and virtual resources owned by project. |
| `experiment_ids` | One2many | `research.experiment` | Experiments executed under project scope. |
| `paper_ids` | One2many | `research.paper` | Academic papers and publications generated. |

---

## 3. `research.project.researcher` (Project Team Allocation)
- **Source File**: [models/research_project_researcher.py](file:///d:/Center/Github_Profile/Research-Supply-Chain/addons/research_supply_chain/models/research_project_researcher.py)
- **Description**: Relational model representing team member allocations and effort percentages.

### Fields
| Field Name | Type | Properties | Description |
| :--- | :--- | :--- | :--- |
| `project_id` | Many2one | `research.project`, Required, Cascade | Parent project. |
| `researcher_id` | Many2one | `research.researcher`, Required, Cascade | Assigned researcher. |
| `role` | Char | Optional | Functional role (e.g. Lead Analyst, Data Engineer). |
| `allocated_pct` | Float | Default: `100.0` | Percentage of time/effort allocated (0.0 < pct <= 100.0). |
| `join_date` | Date | Optional | Date researcher joined project team. |

---

## 4. `project.budget` (Project Budget)
- **Source File**: [models/project_budget.py](file:///d:/Center/Github_Profile/Research-Supply-Chain/addons/research_supply_chain/models/project_budget.py)
- **Description**: Manages financial funding limits, spent capital, and remaining balance.

### Fields
| Field Name | Type | Properties | Description |
| :--- | :--- | :--- | :--- |
| `project_id` | Many2one | `research.project`, Required, Cascade, Unique | Parent project (1:1 constraint). |
| `currency_id` | Many2one | `res.currency`, Required | Currency denomination. |
| `total_amount` | Monetary | Required, Default: `0.0` | Total approved budget funding. |
| `spent_amount` | Monetary | Default: `0.0` | Total capital spent to date. |
| `remaining_amount` | Monetary | Computed, Stored | `total_amount - spent_amount`. |
| `start_date` | Date | Optional | Budget validity start date. |
| `end_date` | Date | Optional | Budget validity end date. |

---

## 5. `research.requirement` (Research Requirement)
- **Source File**: [models/research_requirement.py](file:///d:/Center/Github_Profile/Research-Supply-Chain/addons/research_supply_chain/models/research_requirement.py)
- **Description**: Tracks material, computational, software, or personnel requirements requested by a project.

### Fields
| Field Name | Type | Properties | Description |
| :--- | :--- | :--- | :--- |
| `project_id` | Many2one | `research.project`, Required, Cascade | Target project. |
| `category` | Selection | Default: `'hardware'`, Required | Category: `dataset`, `hardware`, `software`, `service`, `expertise`, `other`. |
| `name` | Char | Required | Requirement title/item name. |
| `description` | Text | Optional | Requirement details and specifications. |
| `quantity` | Float | Default: `1.0`, `> 0` | Quantity requested. |
| `priority` | Selection | Default: `'medium'`, Required | Priority level: `low`, `medium`, `high`. |
| `status` | Selection | Default: `'requested'`, Required | Lifecycle status: `requested`, `approved`, `fulfilled`, `cancelled`. |
| `requested_date` | Date | Default: Today | Date requested. |
| `needed_by` | Date | Optional | Target fulfillment date constraint (`needed_by >= requested_date`). |

---

## 6. `research.resource` (Research Resource)
- **Source File**: [models/research_resource.py](file:///d:/Center/Github_Profile/Research-Supply-Chain/addons/research_supply_chain/models/research_resource.py)
- **Description**: Catalog of physical equipment, compute clusters, software licenses, or datasets available for experiments.

### Fields
| Field Name | Type | Properties | Description |
| :--- | :--- | :--- | :--- |
| `resource_type` | Selection | Default: `'equipment'`, Required | Type: `dataset`, `equipment`, `software`, `service`, `other`. |
| `name` | Char | Required | Resource identifier/name. |
| `description` | Text | Optional | General resource description. |
| `specification` | Text | Optional | Hardware or technical specification. |
| `availability_status` | Selection | Default: `'available'`, Required | Availability: `available`, `in_use`, `unavailable`. |
| `owner_project_id` | Many2one | `research.project` | Owning/custodian project. |
| `notes` | Text | Optional | Maintenance or usage notes. |

---

## 7. `research.experiment` (Research Experiment)
- **Source File**: [models/experiment.py](file:///d:/Center/Github_Profile/Research-Supply-Chain/addons/research_supply_chain/models/experiment.py)
- **Description**: Individual research trial, benchmark, or experiment execution.

### Fields
| Field Name | Type | Properties | Description |
| :--- | :--- | :--- | :--- |
| `project_id` | Many2one | `research.project`, Required, Cascade | Parent project. |
| `name` | Char | Required | Experiment title. |
| `objective` | Text | Optional | Research hypothesis or goal. |
| `methodology` | Text | Optional | Experimental procedure and setup. |
| `status` | Selection | Default: `'planned'`, Required | Status: `planned`, `running`, `completed`, `cancelled`. |
| `start_date` | Date | Optional | Execution start date. |
| `end_date` | Date | Optional | Execution completion date. |
| `created_by` | Many2one | `res.users`, Default: Current User | User who created experiment record. |
| `experiment_resource_ids` | One2many | `research.experiment.resource` | Resources consumed/allocated. |
| `output_ids` | One2many | `research.output` | Outputs generated. |

---

## 8. `research.experiment.resource` (Experiment Resource Allocation)
- **Source File**: [models/experiment_resource.py](file:///d:/Center/Github_Profile/Research-Supply-Chain/addons/research_supply_chain/models/experiment_resource.py)
- **Description**: Junction model linking resources allocated to a specific experiment.

### Fields
| Field Name | Type | Properties | Description |
| :--- | :--- | :--- | :--- |
| `experiment_id` | Many2one | `research.experiment`, Required, Cascade | Target experiment. |
| `resource_id` | Many2one | `research.resource`, Required, Cascade | Allocated resource. |
| `purpose` | Char | Optional | Purpose of allocation (e.g. GPU model training). |
| `quantity` | Float | Default: `1.0`, `> 0` | Quantity allocated. |

---

## 9. `research.output` (Research Output)
- **Source File**: [models/research_output.py](file:///d:/Center/Github_Profile/Research-Supply-Chain/addons/research_supply_chain/models/research_output.py)
- **Description**: Tangible deliverables produced by an experiment (papers, datasets, code repos).

### Fields
| Field Name | Type | Properties | Description |
| :--- | :--- | :--- | :--- |
| `experiment_id` | Many2one | `research.experiment`, Required, Cascade | Source experiment. |
| `project_id` | Many2one | Related (`experiment_id.project_id`), Stored | Associated parent project. |
| `output_type` | Selection | Default: `'paper'`, Required | Type: `paper`, `dataset`, `software`, `report`, `thesis`, `other`. |
| `name` | Char | Required | Deliverable title. |
| `status` | Selection | Default: `'draft'`, Required | State: `draft`, `under_review`, `accepted`, `published`. |

---

## 10. `research.paper` (Research Paper)
- **Source File**: [models/research_paper.py](file:///d:/Center/Github_Profile/Research-Supply-Chain/addons/research_supply_chain/models/research_paper.py)
- **Description**: Academic publications, journal submissions, and pre-prints.

### Fields
| Field Name | Type | Properties | Description |
| :--- | :--- | :--- | :--- |
| `paper_name` | Char | Required | Publication title. |
| `paper_author` | Char | Optional | Author list (comma-separated). |
| `paper_publication_date` | Date | Optional | Publication date. |
| `paper_abstract` | Text | Optional | Paper abstract. |
| `paper_doi` | Char | Optional | Digital Object Identifier (DOI). |
| `paper_status` | Selection | Default: `'draft'`, Required | State: `draft`, `submitted`, `published`, `archived`. |
| `paper_github_url` | Char | Optional | Code repository URL. |
| `project_id` | Many2one | `research.project` | Associated research project. |
| `output_id` | Many2one | `research.output` | Associated output record. |

### Methods
- `action_submit()`: Transitions `paper_status` from `'draft'` to `'submitted'`.

---

## 11. `research.sample.data.wizard` (Generate Sample Data Wizard)
- **Source File**: [models/sample_data_wizard.py](file:///d:/Center/Github_Profile/Research-Supply-Chain/addons/research_supply_chain/models/sample_data_wizard.py)
- **Description**: Transient model enabling 1-click synthetic dataset generation from the Odoo web interface.

### Fields
| Field Name | Type | Default | Description |
| :--- | :--- | :---: | :--- |
| `num_projects` | Integer | `5` | Count of synthetic projects to generate. |
| `num_researchers` | Integer | `5` | Count of synthetic researchers to generate. |

### Methods
- `action_generate_data()`: Generates requested count of projects, researchers, budgets, requirements, resources, experiments, outputs, and papers, returning a UI success notification.
