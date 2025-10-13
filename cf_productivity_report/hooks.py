# -*- coding: utf-8 -*-
from odoo import api, SUPERUSER_ID

COLUMNS = [
    ("res_company", "productivity_reset_minutes", "INTEGER"),
    ("res_company", "cf_user_repair_id", "INTEGER"),
    ("res_company", "cf_user_ticket_id", "INTEGER"),
    ("res_company", "cf_user_order_id",  "INTEGER"),
]

def _ensure_columns(cr):
    # Create columns if not exist (safe for multiple runs)
    for table, col, coltype in COLUMNS:
        cr.execute("""
            SELECT 1
            FROM information_schema.columns
            WHERE table_name=%s AND column_name=%s
        """, (table, col))
        if not cr.fetchone():
            if col.endswith('_id') and coltype == "INTEGER":
                cr.execute(f'ALTER TABLE {table} ADD COLUMN {col} {coltype}')
            else:
                cr.execute(f'ALTER TABLE {table} ADD COLUMN {col} {coltype}')

def pre_init_hook(cr):
    # Runs on fresh install
    _ensure_columns(cr)

def post_init_hook(cr, registry):
    # Runs after install; also safe to call on update via -u
    _ensure_columns(cr)
    env = api.Environment(cr, SUPERUSER_ID, {})
    # Set sane defaults if null
    env['res.company'].search([]).write({
        'productivity_reset_minutes': 120,
    })
