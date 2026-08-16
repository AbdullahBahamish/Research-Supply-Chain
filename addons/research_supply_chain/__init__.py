from . import models
from . import controllers


def post_init_hook(env):
    """
    Runs once after module install/upgrade.
    Sets the home action for all users without one so they land on
    Research Projects instead of Discuss after login.
    """
    try:
        action = env.ref('research_supply_chain.action_research_project')
        users = env['res.users'].search([
            ('action_id', '=', False),
            ('active', '=', True),
            ('share', '=', False),  # internal users only
        ])
        if users:
            users.write({'action_id': action.id})
    except Exception:
        pass  # Non-fatal: don't break install if action not found yet
