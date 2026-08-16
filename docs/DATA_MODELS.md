# Data Models Specification

This document provides a comprehensive technical reference for all custom models, abstract mixins, and wizards in the **Research Supply Chain** module.

---

## 1. `research.researcher` (Researcher Profile)
- **Source File**: [`models/researcher.py`](file:///d:/Center/Github_Profile/Research-Supply-Chain/addons/research_supply_chain/models/researcher.py)
- **Description**: Represents individual research staff, faculty, postdocs, or lab members linked to system user accounts.

### Fields
| Field Name | Type | Properties | Description |
| :--- | :--- | :--- | :--- |
| `user_id` | Many2one (`res.users`) | Required, OnDelete: Cascade | System user account linked to researcher. |
| `name` | Char | Related (`user_id.name`), Stored | Researcher full name. |
| `email` | Char | Related (`user_id.email`), Readonly | Researcher email address. |
| `position` | Char | Optional | Academic title (e.g. Senior Bioinformatician, Postdoc Fellow). |
| `expertise` | Text | Optional | Comma-separated domain competencies and technical skills. |
| `is_principal` | Boolean | Default: `False` | Flags if researcher is qualified as a Principal Investigator (PI). |
| `active` | Boolean | Default: `True` | Archival flag. |
| `project_line_ids` | One2many | `research.project.researcher` | Reverse relation to team allocations. |

### Constraints
- Odoo 19 Constraint: `_user_unique = models.Constraint("UNIQUE(user_id)", "A researcher profile already exists for this user account.")`

---

## 2. `research.project` (Research Project)
- **Source File**: [`models/research_project.py`](file:///d:/Center/Github_Profile/Research-Supply-Chain/addons/research_supply_chain/models/research_project.py)
- **Description**: Primary business unit representing a funded research project or lab initiative.

### Fields
| Field Name | Type | Properties | Description |
| :--- | :--- | :--- | :--- |
| `code` | Char | Readonly, Sequence | System-generated code (e.g., `PRJ00001`). |
| `project_name` | Char | Required, Tracking | Title of the research project. |
| `project_description` | Text | Optional | Abstract and detailed technical scope. |
| `visibility` | Selection | Default: `'public'`, Required, Tracking | Visibility scope: `public` or `private`. |
| `analytic_account_id` | Many2one | `account.analytic.account` | Linked financial analytic accounting record. |
| `lead_researcher_id` | Many2one | `research.researcher`, Tracking | Lead Principal Investigator assigned to project. |
| `start_date` | Date | Tracking | Scheduled project start date. |
| `end_date` | Date | Tracking | Scheduled project end date. |
| `project_status` | Selection | Default: `'proposed'`, Required, Tracking | Lifecycle: `proposed`, `approved`, `in_progress`, `completed`, `archived`. |
| `tag_ids` | Many2many | `research.project.tag` | Categorization tags. |
| `researcher_line_ids` | One2many | `research.project.researcher` | Team members and effort allocation details. |
| `budget_ids` | One2many | `project.budget` | Associated financial budget lines. |
| `requirement_ids` | One2many | `research.requirement` | Supply chain requests & requirements. |
| `resource_ids` | One2many | `research.resource` | Physical and virtual resources owned by project. |
| `experiment_ids` | One2many | `research.experiment` | Experiments executed under project scope. |
| `paper_ids` | One2many | `research.paper` | Academic papers and publications generated. |
| `total_budget_amount` | Monetary | Computed, Stored, Inverse | Aggregate budget funding limit. |
| `total_spent_amount` | Monetary | Computed, Stored, Inverse | Aggregate funding spent to date. |
| `remaining_budget_amount` | Monetary | Computed, Stored, Inverse | Aggregate remaining budget balance. |
| `budget_utilization` | Float | Computed, Stored, Inverse | Budget consumption percentage. |

### Key Methods
- `action_analyze_team_skills()`: Analyzes unique skill sets, shared core competencies, and skills unique to the lead researcher using set operations.
- `action_get_functional_summary()`: Summarizes completed experiment counts and names using Python functional programming (`filter`, `map`).
- `cron_update_project_statuses()`: Scheduled cron job automatically advancing project statuses based on start/end dates.

---

## 3. `research.project.tag` (Project Tag)
- **Source File**: [`models/project_tag.py`](file:///d:/Center/Github_Profile/Research-Supply-Chain/addons/research_supply_chain/models/project_tag.py)
- **Description**: Categorization tags used for project taxonomy and color-coded Kanban filtering.

### Fields
| Field Name | Type | Properties | Description |
| :--- | :--- | :--- | :--- |
| `name` | Char | Required, Unique | Tag name label. |
| `color` | Integer | Default: `0` | Color index for Odoo UI badge display. |

---

## 4. `research.project.researcher` (Project Team Allocation)
- **Source File**: [`models/research_project_researcher.py`](file:///d:/Center/Github_Profile/Research-Supply-Chain/addons/research_supply_chain/models/research_project_researcher.py)
- **Description**: Relational line model representing researcher assignments and effort percentages.

### Fields
| Field Name | Type | Properties | Description |
| :--- | :--- | :--- | :--- |
| `project_id` | Many2one | `research.project`, Required, OnDelete: Cascade | Parent research project. |
| `researcher_id` | Many2one | `research.researcher`, Required, OnDelete: Cascade | Assigned team member. |
| `role` | Char | Optional | Assigned functional role (e.g. Lead Bioinformatician). |
| `allocated_pct` | Float | Default: `100.0` | Percentage of time/effort allocated (`0.0 < allocated_pct <= 100.0`). |
| `join_date` | Date | Optional | Date researcher joined project team. |

---

## 5. `project.budget` (Project Budget)
- **Source File**: [`models/project_budget.py`](file:///d:/Center/Github_Profile/Research-Supply-Chain/addons/research_supply_chain/models/project_budget.py)
- **Description**: Manages financial funding limits, spent capital, and remaining balance per project.

### Fields
| Field Name | Type | Properties | Description |
| :--- | :--- | :--- | :--- |
| `project_id` | Many2one | `research.project`, Required, OnDelete: Cascade | Parent project (1:1 constraint). |
| `currency_id` | Many2one | `res.currency`, Required | Currency denomination. |
| `total_amount` | Monetary | Required, Default: `0.0` | Total approved budget funding. |
| `spent_amount` | Monetary | Default: `0.0` | Total capital spent to date. |
| `remaining_amount` | Monetary | Computed, Stored | `total_amount - spent_amount`. |
| `start_date` | Date | Optional | Budget validity start date. |
| `end_date` | Date | Optional | Budget validity end date. |

---

## 6. `research.requirement` (Research Requirement)
- **Source File**: [`models/research_requirement.py`](file:///d:/Center/Github_Profile/Research-Supply-Chain/addons/research_supply_chain/models/research_requirement.py)
- **Description**: Tracks hardware, software, material, or service requests submitted for a project.

### Fields
| Field Name | Type | Properties | Description |
| :--- | :--- | :--- | :--- |
| `project_id` | Many2one | `research.project`, Required, OnDelete: Cascade | Target project. |
| `category` | Selection | Default: `'hardware'`, Required | Category: `dataset`, `hardware`, `software`, `service`, `expertise`, `other`. |
| `name` | Char | Required | Requirement item title. |
| `description` | Text | Optional | Specifications and technical details. |
| `quantity` | Float | Default: `1.0` | Quantity requested (`quantity > 0`). |
| `priority` | Selection | Default: `'medium'`, Required | Priority level: `low`, `medium`, `high`. |
| `status` | Selection | Default: `'requested'`, Required | Status: `requested`, `approved`, `fulfilled`, `cancelled`. |
| `requested_date` | Date | Default: Today | Date requirement was submitted. |
| `needed_by` | Date | Optional | Target fulfillment date (`needed_by >= requested_date`). |

---

## 7. `research.resource` (Research Resource)
- **Source File**: [`models/research_resource.py`](file:///d:/Center/Github_Profile/Research-Supply-Chain/addons/research_supply_chain/models/research_resource.py)
- **Description**: Shared resource inventory of physical equipment, compute clusters, software, or datasets.

### Fields
| Field Name | Type | Properties | Description |
| :--- | :--- | :--- | :--- |
| `resource_type` | Selection | Default: `'equipment'`, Required | Type: `dataset`, `equipment`, `software`, `service`, `other`. |
| `name` | Char | Required | Resource title/identifier. |
| `description` | Text | Optional | Resource overview. |
| `specification` | Text | Optional | Technical specifications. |
| `availability_status` | Selection | Default: `'available'`, Required | Availability: `available`, `in_use`, `unavailable`. |
| `owner_project_id` | Many2one | `research.project` | Owning/custodian project. |
| `notes` | Text | Optional | Maintenance notes. |

---

## 8. `research.experiment` (Research Experiment)
- **Source File**: [`models/experiment.py`](file:///d:/Center/Github_Profile/Research-Supply-Chain/addons/research_supply_chain/models/experiment.py)
- **Description**: Individual research trial, experimental run, or model training benchmark.

### Fields
| Field Name | Type | Properties | Description |
| :--- | :--- | :--- | :--- |
| `project_id` | Many2one | `research.project`, Required, OnDelete: Cascade | Parent project. |
| `name` | Char | Required | Experiment title. |
| `owner_id` | Many2one | `res.users`, Default: Current User | Responsible user/owner. |
| `objective` | Text | Optional | Research hypothesis or goal. |
| `methodology` | Text | Optional | Experimental procedure setup. |
| `status` | Selection | Default: `'planned'`, Required | Lifecycle: `planned`, `running`, `completed`, `cancelled`. |
| `start_date` | Date | Optional | Execution start date. |
| `end_date` | Date | Optional | Completion date. |
| `experiment_resource_ids` | One2many | `research.experiment.resource` | Resources allocated to experiment. |
| `output_ids` | One2many | `research.output` | Outputs generated. |

### Lifecycle Actions
- `action_start()`: Advances experiment status to `'running'`.
- `action_complete()`: Advances experiment status to `'completed'`.
- `action_cancel()`: Cancels experiment execution.

---

## 9. `research.experiment.resource` (Experiment Resource Allocation)
- **Source File**: [`models/experiment_resource.py`](file:///d:/Center/Github_Profile/Research-Supply-Chain/addons/research_supply_chain/models/experiment_resource.py)
- **Description**: Junction model linking shared resources allocated to a specific experiment.

### Fields
| Field Name | Type | Properties | Description |
| :--- | :--- | :--- | :--- |
| `experiment_id` | Many2one | `research.experiment`, Required, OnDelete: Cascade | Target experiment. |
| `resource_id` | Many2one | `research.resource`, Required, OnDelete: Cascade | Allocated resource. |
| `purpose` | Char | Optional | Purpose of allocation (e.g. Model inference benchmark). |
| `quantity` | Float | Default: `1.0` | Quantity allocated (`quantity > 0`). |

---

## 10. `research.output` (Research Output)
- **Source File**: [`models/research_output.py`](file:///d:/Center/Github_Profile/Research-Supply-Chain/addons/research_supply_chain/models/research_output.py)
- **Description**: Deliverables and outputs produced by an experiment.

### Fields
| Field Name | Type | Properties | Description |
| :--- | :--- | :--- | :--- |
| `experiment_id` | Many2one | `research.experiment`, Required, OnDelete: Cascade | Source experiment. |
| `project_id` | Many2one | Related (`experiment_id.project_id`), Stored | Parent project. |
| `output_type` | Selection | Default: `'paper'`, Required | Type: `paper`, `dataset`, `software`, `report`, `thesis`, `other`. |
| `name` | Char | Required | Deliverable title. |
| `status` | Selection | Default: `'draft'`, Required | State: `draft`, `under_review`, `accepted`, `published`. |

---

## 11. `research.paper` (Research Paper)
- **Source File**: [`models/research_paper.py`](file:///d:/Center/Github_Profile/Research-Supply-Chain/addons/research_supply_chain/models/research_paper.py)
- **Description**: Academic publications, journal submissions, and pre-prints.

### Fields
| Field Name | Type | Properties | Description |
| :--- | :--- | :--- | :--- |
| `paper_name` | Char | Required | Publication title. |
| `paper_author` | Char | Optional | Authors list (comma-separated). |
| `paper_publication_date` | Date | Optional | Publication date. |
| `paper_abstract` | Text | Optional | Paper abstract. |
| `paper_doi` | Char | Optional | Digital Object Identifier (DOI). |
| `paper_status` | Selection | Default: `'draft'`, Required | State: `draft`, `submitted`, `published`, `archived`. |
| `paper_github_url` | Char | Optional | Code repository URL. |
| `project_id` | Many2one | `research.project` | Associated research project. |
| `output_id` | Many2one | `research.output` | Associated output record. |

---

## 12. `research.audit.mixin` (System Audit Mixin)
- **Source File**: [`models/mixins.py`](file:///d:/Center/Github_Profile/Research-Supply-Chain/addons/research_supply_chain/models/mixins.py)
- **Description**: Abstract mixin providing automated system event logging and chatter post integration.

### Fields & Methods
- `audit_notes`: Readonly text log storing timestamped system events.
- `_log_system_event(event_msg)`: Logs audit events into `audit_notes` and posts chatter notifications.

---

## 13. `research.exportable.mixin` (Export Stream Mixin)
- **Source File**: [`models/mixins.py`](file:///d:/Center/Github_Profile/Research-Supply-Chain/addons/research_supply_chain/models/mixins.py)
- **Description**: Abstract mixin providing generator and itertools stream export helpers.

### Methods
- `generate_record_stream(records, field_list)`: Generator function yielding record dictionaries on demand.
- `get_grouped_summary_by_status(records, status_field)`: Groups records by status using `itertools.groupby`.

---

## 14. `research.sample.data.wizard` (Generate Sample Data Wizard)
- **Source File**: [`models/sample_data_wizard.py`](file:///d:/Center/Github_Profile/Research-Supply-Chain/addons/research_supply_chain/models/sample_data_wizard.py)
- **Description**: Transient wizard for 1-click generation of synthetic projects, researchers, budgets, and outputs.

### Fields & Methods
- `num_projects` (Integer, Default: 5): Synthetic projects to generate.
- `num_researchers` (Integer, Default: 5): Synthetic researchers to generate.
- `action_generate_data()`: Generates synthetic records and returns UI success notification.
