import functools
import itertools
import re
import time
from odoo import models, fields, api  # type: ignore  # pyfly: ignore [missing-import]
from odoo.exceptions import ValidationError  # type: ignore  # pyfly: ignore [missing-import]

# ==============================================================================
# DECORATORS
# ==============================================================================

def system_audit_log(action_name: str):
    """Custom decorator for logging method execution in system models."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            start_t = time.perf_counter()
            res = func(self, *args, **kwargs)
            elapsed_ms = (time.perf_counter() - start_t) * 1000
            # Record log internally if model supports logging
            if hasattr(self, '_log_system_event'):
                self._log_system_event(f"Action '{action_name}' completed in {elapsed_ms:.2f}ms")
            return res
        return wrapper
    return decorator


def validate_regex_pattern(pattern_str: str, field_name: str):
    """Custom decorator for regex field validation."""
    regex_compiled = re.compile(pattern_str)
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            res = func(self, *args, **kwargs)
            for record in self:
                val = getattr(record, field_name, False)
                if val and not regex_compiled.match(str(val)):
                    raise ValidationError(f"Field '{field_name}' with value '{val}' fails regex pattern '{pattern_str}'")
            return res
        return wrapper
    return decorator


# ==============================================================================
# ABSTRACT MIXIN MODELS (MULTIPLE INHERITANCE)
# ==============================================================================

class ResearchAuditMixin(models.AbstractModel):
    """
    Abstract Mixin demonstrating:
    - Multiple Inheritance in Odoo
    - Data Hiding (Weakly & Strongly Private fields)
    - Class & Static Methods
    - Properties
    """
    _name = "research.audit.mixin"
    _description = "System Audit Trail Mixin"

    # Weakly private attribute convention
    _protected_audit_counter = 0

    # Strongly private attribute (Name Mangling active)
    __secret_system_token = "RSC-SECURE-KEY-2026"

    audit_notes = fields.Text(
        string="Audit History",
        readonly=True,
        copy=False,
    )

    def _log_system_event(self, event_msg: str):
        """Weakly private method logging audit entries."""
        for record in self:
            timestamp = fields.Datetime.now()
            current_log = record.audit_notes or ""
            new_entry = f"[{timestamp}] {event_msg}\n"
            record.audit_notes = new_entry + current_log

    def get_security_token(self) -> str:
        """Data hiding method accessing strongly private attribute."""
        return self.__secret_system_token

    @classmethod
    def increment_audit_counter(cls):
        """Class method accessing class-level state."""
        cls._protected_audit_counter += 1
        return cls._protected_audit_counter

    @staticmethod
    def format_timestamp(dt_val) -> str:
        """Static method: Pure helper function."""
        if not dt_val:
            return "N/A"
        return dt_val.strftime("%Y-%m-%d %H:%M:%S")


class ExportableDataMixin(models.AbstractModel):
    """
    Abstract Mixin demonstrating:
    - Generators (yield)
    - Itertools (groupby, chain)
    - Functional programming (map, filter, lambda)
    """
    _name = "research.exportable.mixin"
    _description = "Data Stream Export Mixin"

    def generate_record_stream(self, records, field_list: list):
        """Generator function using 'yield' to stream record data on demand."""
        for rec in records:
            data = {"id": rec.id}
            for field in field_list:
                val = getattr(rec, field, False)
                data[field] = val.name if hasattr(val, "name") else val
            yield data

    def get_grouped_summary_by_status(self, records, status_field: str = "project_status"):
        """Demonstrates itertools.groupby and itertools.chain."""
        # Sort first for itertools.groupby
        sorted_recs = sorted(records, key=lambda r: str(getattr(r, status_field, "")))
        
        summary = {}
        for status_key, group in itertools.groupby(sorted_recs, key=lambda r: str(getattr(r, status_field, ""))):
            group_list = list(group)
            # Use map & lambda to extract names
            names = list(map(lambda r: getattr(r, "name", False) or getattr(r, "project_name", "N/A"), group_list))
            summary[status_key] = {
                "count": len(group_list),
                "names": names,
            }
        return summary
