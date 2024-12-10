"""Initial Data Models Creation

Revision ID: 51495ee82278
Revises: 
Create Date: 2024-11-22 12:40:19.000995

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '51495ee82278'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('departments',
    sa.Column('department_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('department_id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('item_categories',
    sa.Column('category_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('category_id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('permissions',
    sa.Column('permission_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('description', sa.String(length=255), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('permission_id'),
    sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_permissions_permission_id'), 'permissions', ['permission_id'], unique=False)
    op.create_table('roles',
    sa.Column('role_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('description', sa.String(length=255), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('role_id'),
    sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_roles_role_id'), 'roles', ['role_id'], unique=False)
    op.create_table('unit_of_measures',
    sa.Column('uom_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('abbreviation', sa.String(length=10), nullable=False),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('uom_id'),
    sa.UniqueConstraint('abbreviation'),
    sa.UniqueConstraint('name')
    )
    op.create_table('vendors',
    sa.Column('vendor_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('vendor_id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('employees',
    sa.Column('employee_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('employee_number', sa.String(length=8), nullable=False),
    sa.Column('first_name', sa.String(length=50), nullable=False),
    sa.Column('middle_name', sa.String(length=50), nullable=True),
    sa.Column('last_name', sa.String(length=50), nullable=False),
    sa.Column('department_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['department_id'], ['departments.department_id'], ),
    sa.PrimaryKeyConstraint('employee_id'),
    sa.UniqueConstraint('employee_number')
    )
    op.create_table('items',
    sa.Column('item_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('item_code', sa.String(length=20), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('category', sa.Integer(), nullable=False),
    sa.Column('vendor_id', sa.Integer(), nullable=True),
    sa.Column('owner_department', sa.Integer(), nullable=False),
    sa.Column('has_barcode', sa.Boolean(), nullable=True),
    sa.Column('barcode', sa.String(length=13), nullable=True),
    sa.Column('image_path', sa.String(length=255), nullable=True),
    sa.Column('unit_of_measure', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('low_stock_threshold', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['category'], ['item_categories.category_id'], ),
    sa.ForeignKeyConstraint(['owner_department'], ['departments.department_id'], ),
    sa.ForeignKeyConstraint(['unit_of_measure'], ['unit_of_measures.uom_id'], ),
    sa.ForeignKeyConstraint(['vendor_id'], ['vendors.vendor_id'], ),
    sa.PrimaryKeyConstraint('item_id')
    )
    op.create_index(op.f('ix_items_description'), 'items', ['description'], unique=False)
    op.create_index(op.f('ix_items_item_code'), 'items', ['item_code'], unique=False)
    op.create_index(op.f('ix_items_name'), 'items', ['name'], unique=False)
    op.create_table('roles_permissions',
    sa.Column('role_id', sa.Integer(), nullable=False),
    sa.Column('permission_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['permission_id'], ['permissions.permission_id'], ),
    sa.ForeignKeyConstraint(['role_id'], ['roles.role_id'], ),
    sa.PrimaryKeyConstraint('role_id', 'permission_id')
    )
    op.create_table('checkout_transactions',
    sa.Column('transaction_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('employee_id', sa.Integer(), nullable=False),
    sa.Column('department_id', sa.Integer(), nullable=False),
    sa.Column('total_items', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['department_id'], ['departments.department_id'], ),
    sa.ForeignKeyConstraint(['employee_id'], ['employees.employee_id'], ),
    sa.PrimaryKeyConstraint('transaction_id')
    )
    op.create_table('scanned_invoices',
    sa.Column('scan_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('invoice_number', sa.String(length=100), nullable=False),
    sa.Column('vendor_id', sa.Integer(), nullable=False),
    sa.Column('scanned_by', sa.Integer(), nullable=False),
    sa.Column('image_file_path', sa.String(length=255), nullable=True),
    sa.Column('total_items', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['scanned_by'], ['employees.employee_id'], ),
    sa.ForeignKeyConstraint(['vendor_id'], ['vendors.vendor_id'], ),
    sa.PrimaryKeyConstraint('scan_id')
    )
    op.create_table('users',
    sa.Column('user_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_name', sa.String(length=50), nullable=False),
    sa.Column('hashed_password', sa.String(length=255), nullable=False),
    sa.Column('enabled', sa.Boolean(), nullable=True),
    sa.Column('employee_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['employee_id'], ['employees.employee_id'], ),
    sa.PrimaryKeyConstraint('user_id'),
    sa.UniqueConstraint('user_name')
    )
    op.create_index(op.f('ix_users_user_id'), 'users', ['user_id'], unique=False)
    op.create_table('checkout_items',
    sa.Column('checkout_item_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('transaction_id', sa.Integer(), nullable=False),
    sa.Column('line_number', sa.Integer(), nullable=False),
    sa.Column('item_id', sa.Integer(), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.Column('unit_of_measure', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['item_categories.category_id'], ),
    sa.ForeignKeyConstraint(['item_id'], ['items.item_id'], ),
    sa.ForeignKeyConstraint(['transaction_id'], ['checkout_transactions.transaction_id'], ),
    sa.ForeignKeyConstraint(['unit_of_measure'], ['unit_of_measures.uom_id'], ),
    sa.PrimaryKeyConstraint('checkout_item_id'),
    sa.UniqueConstraint('transaction_id', 'line_number', name='uq_transaction_line')
    )
    op.create_table('scanned_invoice_items',
    sa.Column('scanned_invoice_item_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('scan_id', sa.Integer(), nullable=False),
    sa.Column('line_number', sa.Integer(), nullable=False),
    sa.Column('item_id', sa.Integer(), nullable=False),
    sa.Column('item_code', sa.String(length=20), nullable=False),
    sa.Column('quantity', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['item_id'], ['items.item_id'], ),
    sa.ForeignKeyConstraint(['scan_id'], ['scanned_invoices.scan_id'], ),
    sa.PrimaryKeyConstraint('scanned_invoice_item_id'),
    sa.UniqueConstraint('scan_id', 'line_number', name='uq_scan_line')
    )
    op.create_table('users_roles',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('role_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['role_id'], ['roles.role_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ),
    sa.PrimaryKeyConstraint('user_id', 'role_id')
    )
    op.create_table('inventory_adjustment_logs',
    sa.Column('log_id', sa.Integer(), nullable=False),
    sa.Column('item_id', sa.Integer(), nullable=False),
    sa.Column('old_quantity', sa.Integer(), nullable=False),
    sa.Column('new_quantity', sa.Integer(), nullable=False),
    sa.Column('quantity_changed', sa.Integer(), nullable=False),
    sa.Column('adjustment_type', sa.String(), nullable=False),
    sa.Column('adjusted_at', sa.DateTime(), nullable=False),
    sa.Column('scanned_invoice_item_id', sa.Integer(), nullable=True),
    sa.Column('checkout_item_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['checkout_item_id'], ['checkout_items.checkout_item_id'], ),
    sa.ForeignKeyConstraint(['item_id'], ['items.item_id'], ),
    sa.ForeignKeyConstraint(['scanned_invoice_item_id'], ['scanned_invoice_items.scanned_invoice_item_id'], ),
    sa.PrimaryKeyConstraint('log_id')
    )
    op.create_index(op.f('ix_inventory_adjustment_logs_log_id'), 'inventory_adjustment_logs', ['log_id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_inventory_adjustment_logs_log_id'), table_name='inventory_adjustment_logs')
    op.drop_table('inventory_adjustment_logs')
    op.drop_table('users_roles')
    op.drop_table('scanned_invoice_items')
    op.drop_table('checkout_items')
    op.drop_index(op.f('ix_users_user_id'), table_name='users')
    op.drop_table('users')
    op.drop_table('scanned_invoices')
    op.drop_table('checkout_transactions')
    op.drop_table('roles_permissions')
    op.drop_index(op.f('ix_items_name'), table_name='items')
    op.drop_index(op.f('ix_items_item_code'), table_name='items')
    op.drop_index(op.f('ix_items_description'), table_name='items')
    op.drop_table('items')
    op.drop_table('employees')
    op.drop_table('vendors')
    op.drop_table('unit_of_measures')
    op.drop_index(op.f('ix_roles_role_id'), table_name='roles')
    op.drop_table('roles')
    op.drop_index(op.f('ix_permissions_permission_id'), table_name='permissions')
    op.drop_table('permissions')
    op.drop_table('item_categories')
    op.drop_table('departments')
    # ### end Alembic commands ###
