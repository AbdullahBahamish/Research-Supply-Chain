# Advanced Python Concepts Guide

This guide provides a detailed technical reference and hands-on explanation of the advanced Python concepts implemented throughout the **Research Supply Chain** module.

---

## 1. Object-Oriented Programming (OOP) & Multiple Inheritance

Odoo models support multiple inheritance via the `_inherit` attribute. The main project model [`ResearchProject`](file:///d:/Center/Github_Profile/Research-Supply-Chain/addons/research_supply_chain/models/research_project.py) inherits from both custom abstract mixins and standard Odoo enterprise mixins:

```python
class ResearchProject(models.Model):
    _name = "research.project"
    _inherit = [
        "research.audit.mixin",       # Custom audit history mixin
        "research.exportable.mixin",  # Custom generator & itertools export mixin
        "mail.thread",                # Odoo chatter thread
        "mail.activity.mixin",        # Odoo activity tracking
    ]
```

### Custom Abstract Mixin Implementation
In [`models/mixins.py`](file:///d:/Center/Github_Profile/Research-Supply-Chain/addons/research_supply_chain/models/mixins.py), abstract mixins define reusable domain capabilities:

```python
class ResearchAuditMixin(models.AbstractModel):
    _name = "research.audit.mixin"
    _description = "System Audit Trail Mixin"

    _protected_audit_counter = 0  # Protected class attribute convention

    audit_notes = fields.Text(
        string="Audit History",
        readonly=True,
        copy=False,
    )

    def _log_system_event(self, event_msg: str):
        """Weakly private method logging audit entries into audit_notes and chatter."""
        for record in self:
            timestamp = fields.Datetime.now()
            new_entry = f"[{timestamp}] {event_msg}"
            if hasattr(record, "message_post"):
                try:
                    record.message_post(body=event_msg, message_type="notification")
                except Exception:
                    pass
            current_log = record.audit_notes or ""
            log_lines = current_log.strip().split("\n") if current_log.strip() else []
            updated_lines = [new_entry] + log_lines[:29]
            record.audit_notes = "\n".join(updated_lines) + "\n"
```

---

## 2. Custom Python Decorators (`functools.wraps`)

The module implements custom decorators in [`models/mixins.py`](file:///d:/Center/Github_Profile/Research-Supply-Chain/addons/research_supply_chain/models/mixins.py) for system auditing and automated field pattern validation:

### System Audit Log Decorator
```python
def system_audit_log(action_name: str):
    """Custom decorator measuring execution time and logging audit events."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            start_t = time.perf_counter()
            try:
                res = func(self, *args, **kwargs)
                elapsed_ms = (time.perf_counter() - start_t) * 1000
                target = res if (res and isinstance(res, models.Model)) else self
                log_msg = f"Action '{action_name}' executed on {target._name} in {elapsed_ms:.2f}ms"
                if hasattr(target, '_log_system_event'):
                    target._log_system_event(log_msg)
                return res
            except Exception as e:
                _logger.error(f"Action '{action_name}' FAILED on {self._name}: {e}")
                raise
        return wrapper
    return decorator
```

---

## 3. Memory-Efficient Generators (`yield`)

In [`ExportableDataMixin`](file:///d:/Center/Github_Profile/Research-Supply-Chain/addons/research_supply_chain/models/mixins.py), data streams are generated lazily using Python generators to avoid storing massive recordsets in RAM:

```python
def generate_record_stream(self, records, field_list: list):
    """Generator function yielding record dictionaries on demand."""
    for rec in records:
        data = {"id": rec.id}
        for field in field_list:
            val = getattr(rec, field, False)
            data[field] = val.name if hasattr(val, "name") else val
        yield data
```

---

## 4. Itertools & Functional Operations (`map`, `filter`, `groupby`)

### Grouping Records by Status (`itertools.groupby`)
In API controllers ([`controllers/main.py`](file:///d:/Center/Github_Profile/Research-Supply-Chain/addons/research_supply_chain/controllers/main.py)) and mixins:

```python
def get_grouped_summary_by_status(self, records, status_field: str = "project_status"):
    sorted_recs = sorted(records, key=lambda r: str(getattr(r, status_field, "")))
    summary = {}
    for status_key, group in itertools.groupby(sorted_recs, key=lambda r: str(getattr(r, status_field, ""))):
        group_list = list(group)
        names = list(map(lambda r: getattr(r, "name", False) or getattr(r, "project_name", "N/A"), group_list))
        summary[status_key] = {
            "count": len(group_list),
            "names": names,
        }
    return summary
```

### Functional Set Operations for Skill Analysis
In [`ResearchProject.action_analyze_team_skills()`](file:///d:/Center/Github_Profile/Research-Supply-Chain/addons/research_supply_chain/models/research_project.py):

```python
all_skill_sets = []
for line in self.researcher_line_ids:
    if line.researcher_id.expertise:
        skills = set(map(str.strip, line.researcher_id.expertise.split(",")))
        all_skill_sets.append(skills)

total_unique = set().union(*all_skill_sets)
shared_core = set.intersection(*all_skill_sets) if len(all_skill_sets) > 1 else total_unique
```

---

## 5. Regular Expressions (`re` Module)

Project code verification uses pre-compiled regular expressions for high-performance pattern checking:

```python
CODE_REGEX = re.compile(r"^(PRJ\d{5}|PRJ-\d{4}-\d{3,5}|New)$")
```

---

## 6. Exception Guardrails & Security Error Handling

All controller routes catch specific Odoo ORM exception hierarchies:

```python
try:
    # Business logic
    pass
except AccessError as e:
    return {'status': 403, 'error': str(e)}
except (ValidationError, UserError) as e:
    return {'status': 422, 'error': str(e)}
except Exception as e:
    _logger.exception("API Error")
    return {'status': 500, 'error': 'Internal server error'}
```
