# System-Integrated Advanced Python & OOP Concepts

This document details how all 17 advanced Python language features, Object-Oriented Programming (OOP) paradigms, functional operations, decorators, regex, and error-handling mechanisms are natively integrated into the **Research Supply Chain** module.

---

## 🏛️ Native System Integration Architecture

No separate concept files exist. All advanced techniques form the functional backbone of the production system across `models/` and `controllers/`:

```
addons/research_supply_chain/
├── models/
│   ├── mixins.py                 # Abstract Mixins, Multiple Inheritance, Data Hiding, Decorators
│   ├── research_project.py       # Regex Validation, Sets & Set Operations, Map/Filter/Lambda
│   ├── project_budget.py         # Operator Overloading (+, ==), Managed Properties, Error Handling
│   ├── research_requirement.py   # Recursive Tree Quantities Calculation
│   └── research_paper.py         # Regex DOI & GitHub Repository Group Parsing
└── controllers/
    └── main.py                   # API Controllers with Itertools (groupby) & Generators (yield)
```

---

## 📋 Comprehensive Concept Mapping Matrix

| Python / OOP Concept | System Implementation | Target System File |
| :--- | :--- | :--- |
| **Classes & Instance Methods** | `ResearchProject`, `ProjectBudget`, `ResearchRequirement`, `ResearchPaper` | [models/research_project.py](file:///d:/Center/Github_Profile/Research-Supply-Chain/addons/research_supply_chain/models/research_project.py) |
| **Inheritance & Subclassing** | Subclassing Odoo `models.Model` and `models.AbstractModel` | [models/mixins.py](file:///d:/Center/Github_Profile/Research-Supply-Chain/addons/research_supply_chain/models/mixins.py) |
| **Multiple Inheritance & Mixins** | `_inherit = ["research.project", "research.audit.mixin", "research.exportable.mixin"]` using cooperative `super()` MRO | [models/research_project.py#L9](file:///d:/Center/Github_Profile/Research-Supply-Chain/addons/research_supply_chain/models/research_project.py#L9) |
| **Data Hiding (Encapsulation)** | Weakly private `_protected_audit_counter` & strongly private `__secret_system_token` (Name Mangling) | [models/mixins.py#L42-L60](file:///d:/Center/Github_Profile/Research-Supply-Chain/addons/research_supply_chain/models/mixins.py#L42-L60) |
| **Class & Static Methods** | `@classmethod` (`increment_audit_counter`) & `@staticmethod` (`format_timestamp`) | [models/mixins.py#L65-L75](file:///d:/Center/Github_Profile/Research-Supply-Chain/addons/research_supply_chain/models/mixins.py#L65-L75) |
| **Operator Overloading** | Overloading `+` (`__add__`), `==` (`__eq__`), and `str()` (`__str__`) on `ProjectBudget` | [models/project_budget.py#L75-L100](file:///d:/Center/Github_Profile/Research-Supply-Chain/addons/research_supply_chain/models/project_budget.py#L75-L100) |
| **Managed Properties** | `@property` getter (`utilization_percentage`), setter, and deleter | [models/project_budget.py#L100-L115](file:///d:/Center/Github_Profile/Research-Supply-Chain/addons/research_supply_chain/models/project_budget.py#L100-L115) |
| **Decorators** | Custom `@system_audit_log` and `@validate_regex_pattern` wrapping Odoo actions | [models/mixins.py#L10-L35](file:///d:/Center/Github_Profile/Research-Supply-Chain/addons/research_supply_chain/models/mixins.py#L10-L35) |
| **Regular Expressions (`re`)** | `re.compile`, `re.match`, `re.search` with named groups `(?P<owner>...)` for codes, DOIs, & repos | [models/research_paper.py#L12-L60](file:///d:/Center/Github_Profile/Research-Supply-Chain/addons/research_supply_chain/models/research_paper.py#L12-L60) |
| **Sets & Set Operations** | Set Union (`\|`), Intersection (`&`), & Difference (`-`) calculating team skill overlaps | [models/research_project.py#L90-L125](file:///d:/Center/Github_Profile/Research-Supply-Chain/addons/research_supply_chain/models/research_project.py#L90-L125) |
| **Functional Programming** | `map()`, `filter()`, and `lambda` expressions in project summaries and API routes | [controllers/main.py#L15-L30](file:///d:/Center/Github_Profile/Research-Supply-Chain/addons/research_supply_chain/controllers/main.py#L15-L30) |
| **Generators & Itertools** | Generator streaming (`yield`) and `itertools.groupby` for API experiment classification | [controllers/main.py#L55-L70](file:///d:/Center/Github_Profile/Research-Supply-Chain/addons/research_supply_chain/controllers/main.py#L55-L70) |
| **Recursion** | `calculate_recursive_total_quantity()` calculating nested requirement tree quantities | [models/research_requirement.py#L75-L95](file:///d:/Center/Github_Profile/Research-Supply-Chain/addons/research_supply_chain/models/research_requirement.py#L75-L95) |
| **Exceptions & Error Handling** | `try...except...else...finally` and `ValidationError` handling in budget & code constraints | [models/project_budget.py#L100-L115](file:///d:/Center/Github_Profile/Research-Supply-Chain/addons/research_supply_chain/models/project_budget.py#L100-L115) |

---

## 💻 System Implementation Highlights

### 1. Sets & Set Operations in Project Team Skills (`models/research_project.py`)

```python
def action_analyze_team_skills(self):
    self.ensure_one()
    all_skill_sets = [set(map(str.strip, l.researcher_id.expertise.split(","))) for l in self.researcher_line_ids]

    # Set Operations: Union, Intersection, Difference
    total_unique = set().union(*all_skill_sets)                             # Union (|)
    shared_core = set.intersection(*all_skill_sets)                         # Intersection (&)
    lead_skills = set(map(str.strip, self.lead_researcher_id.expertise.split(",")))
    unique_to_lead = lead_skills - set().union(*all_skill_sets[1:])       # Difference (-)
```

---

### 2. Operator Overloading in Project Budgets (`models/project_budget.py`)

```python
# Combining two project budget records using overloaded '+' operator
def __add__(self, other: "ProjectBudget") -> dict:
    if not isinstance(other, ProjectBudget):
        return NotImplemented
    return {
        "combined_total": self.total_amount + other.total_amount,
        "combined_spent": self.spent_amount + other.spent_amount,
        "combined_remaining": self.remaining_amount + other.remaining_amount,
    }
```

---

### 3. Recursive Requirement Tree Traversal (`models/research_requirement.py`)

```python
def calculate_recursive_total_quantity(self) -> float:
    self.ensure_one()
    total = self.quantity

    # Base case / Terminating condition
    if not self.child_ids:
        return total

    # Recursive step
    for child in self.child_ids:
        total += child.calculate_recursive_total_quantity()

    return total
```

---

### 4. Custom Decorator & Multiple Inheritance Mixin (`models/mixins.py`)

```python
def system_audit_log(action_name: str):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            start_t = time.perf_counter()
            res = func(self, *args, **kwargs)
            elapsed_ms = (time.perf_counter() - start_t) * 1000
            self._log_system_event(f"Action '{action_name}' executed in {elapsed_ms:.2f}ms")
            return res
        return wrapper
    return decorator

class ResearchAuditMixin(models.AbstractModel):
    _name = "research.audit.mixin"
    _protected_audit_counter = 0            # Weakly private attribute
    __secret_system_token = "RSC-SECKEY"    # Strongly private attribute (Name Mangling)
```
