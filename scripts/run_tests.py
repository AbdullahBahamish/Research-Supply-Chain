#!/usr/bin/env python3
"""
Fast Odoo Module Test Runner
Executes Odoo test suites via odoo-bin CLI harness using fast test tags.
"""

import sys
import os
import argparse
import configparser
import subprocess

DEFAULT_ODOO_PATH = r"D:\Program Files D\Odoo 19.0.20260810\server"
DEFAULT_PYTHON_PATH = r"D:\Program Files D\Odoo 19.0.20260810\python\python.exe"
DEFAULT_MODULE = "research_supply_chain"

def get_db_from_conf(conf_path):
    if os.path.exists(conf_path):
        config = configparser.ConfigParser()
        try:
            config.read(conf_path)
            if 'options' in config and 'db_name' in config['options']:
                return config['options']['db_name']
        except Exception:
            pass
    return None

def run_tests():
    workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    conf_path = os.path.join(workspace_root, "odoo.conf")
    default_db = get_db_from_conf(conf_path) or "research_test_db"

    parser = argparse.ArgumentParser(description="Run Odoo module tests cleanly and quickly.")
    parser.add_argument("--db", "-d", default=default_db, help=f"Database name (default: {default_db})")
    parser.add_argument("--module", "-m", default=DEFAULT_MODULE, help=f"Module name (default: {DEFAULT_MODULE})")
    parser.add_argument("--tag", "-t", help="Specific test tag (default: /<module_name>)")
    parser.add_argument("--update", "-u", action="store_true", help="Force update module before running tests (slower)")
    parser.add_argument("--odoo-path", default=DEFAULT_ODOO_PATH, help="Path to Odoo server directory")
    parser.add_argument("--python-path", default=DEFAULT_PYTHON_PATH, help="Path to Odoo python interpreter")
    
    args = parser.parse_args()

    addons_path = os.path.join(workspace_root, "addons")
    odoo_addons_path = os.path.join(args.odoo_path, "odoo", "addons")
    combined_addons = f"{odoo_addons_path},{addons_path}"
    
    odoo_bin = os.path.join(args.odoo_path, "odoo-bin")
    if not os.path.exists(odoo_bin):
        odoo_bin_py = os.path.join(args.odoo_path, "odoo-bin.py")
        if os.path.exists(odoo_bin_py):
            odoo_bin = odoo_bin_py
        else:
            print(f"[ERROR] Could not find odoo-bin at: {odoo_bin}", file=sys.stderr)
            sys.exit(1)

    tag = args.tag or f"/{args.module}"

    log_file_path = os.path.join(workspace_root, "test_run.log")

    cmd = [
        args.python_path,
        odoo_bin,
        "-c", conf_path,
        f"--addons-path={combined_addons}",
        "-d", args.db,
        "--test-tags", tag,
        "--stop-after-init",
        "--log-level=info",
        f"--logfile={log_file_path}",
    ]

    if args.update:
        cmd.extend(["-u", args.module])

    print("=" * 60)
    print(f"Fast Odoo Test Execution: {args.module}")
    print(f"Target Database: {args.db}")
    print(f"Test Tag: {tag}")
    print(f"Mode: {'Update & Test' if args.update else 'Fast Execution (No Reinstall)'}")
    print(f"Log File: {log_file_path}")
    print(f"Command: {' '.join(cmd)}")
    print("=" * 60)

    try:
        res = subprocess.run(cmd)
        sys.exit(res.returncode)
    except Exception as e:
        print(f"[ERROR] Failed to run test command: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    run_tests()
