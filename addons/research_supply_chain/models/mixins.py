import functools
import itertools
import re
import time
import logging
from odoo import models, fields, api  # type: ignore  # pyfly: ignore [missing-import]
from odoo.exceptions import ValidationError  # type: ignore  # pyfly: ignore [missing-import]

# ==============================================================================
# DECORATORS
# ==============================================================================
_logger = logging.getLogger(__name__)

def system_audit_log(action_name: str):
    """Custom decorator for logging method execution in system models."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            start_t = time.perf_counter()
            try:
                res = func(self, *args, **kwargs)
                elapsed_ms = (time.perf_counter() - start_t) * 1000

                target = res if (res and isinstance(res, models.Model)) else self
                target_ids = getattr(target, 'ids', [])
                log_msg = f"Action '{action_name}' executed on {target._name} (IDs: {target_ids}) in {elapsed_ms:.2f}ms"

                if hasattr(target, '_log_system_event'):
                    try:
                        target._log_system_event(log_msg)
                    except Exception as log_err:
                        _logger.warning(f"Failed to record internal audit log: {log_err}")
                else:
                    _logger.info(log_msg)

                return res

            except Exception as e:
                elapsed_ms = (time.perf_counter() - start_t) * 1000
                _logger.error(
                    f"Action '{action_name}' FAILED on {self._name} (IDs: {self.ids}) after {elapsed_ms:.2f}ms. Error: {e}"
                )
                raise

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

    audit_notes = fields.Text(
        string="Audit History",
        readonly=True,
        copy=False,
    )

    def _log_system_event(self, event_msg: str):
        """Weakly private method logging audit entries cleanly and efficiently."""
        for record in self:
            timestamp = fields.Datetime.now()
            new_entry = f"[{timestamp}] {event_msg}"
            
            # 1. Post to chatter if model supports mail.thread
            if hasattr(record, "message_post"):
                try:
                    record.message_post(body=event_msg, message_type="notification")
                except Exception:
                    pass

            # 2. Store in audit_notes field (capped at latest 30 entries to prevent performance degradation)
            current_log = record.audit_notes or ""
            log_lines = current_log.strip().split("\n") if current_log.strip() else []
            updated_lines = [new_entry] + log_lines[:29]
            # record.audit_notes = "\n".join(updated_lines) + "\n"
            super(ResearchAuditMixin, record).write({
                "audit_notes": "\n".join(updated_lines) + "\n"  # type: ignore
            })
    

    def write(self, vals):
        # Exclude internal audit logging updates from triggering recursive audit trails
        if set(vals.keys()) == {"audit_notes"}:
            return super().write(vals)

        tracked_fields = [k for k in vals.keys() if k != "audit_notes"]
        res = super().write(vals)

        if tracked_fields:
            user_name = self.env.user.name
            mutated_keys = ", ".join(tracked_fields)
            for record in self:
                msg = f"Record mutated by {user_name}. Altered fields: [{mutated_keys}]"
                record._log_system_event(msg)

        return res

    def unlink(self):
        user_name = self.env.user.name
        for record in self:
            rec_identifier = getattr(record, "display_name", f"ID {record.id}")
            _logger.info(
                f"Permanent deletion executed by {user_name} on model {record._name}: {rec_identifier}"
            )
        return super().unlink()
        
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


