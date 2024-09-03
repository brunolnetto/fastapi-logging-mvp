"""auto_generated_migration_20240902_154301

Revision ID: 57ccd08e7414
Revises: e466b066b2c5
Create Date: 2024-09-02 15:43:02.154555

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '57ccd08e7414'
down_revision: Union[str, None] = 'e466b066b2c5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_task_log_talo_id', table_name='task_log')
    op.drop_index('ix_task_log_talo_name', table_name='task_log')
    op.drop_index('ix_task_log_talo_status', table_name='task_log')
    op.drop_table('task_log')
    op.drop_index('ix_request_log_relo_id', table_name='request_log')
    op.drop_index('ix_request_log_relo_method', table_name='request_log')
    op.drop_index('ix_request_log_relo_url', table_name='request_log')
    op.drop_table('request_log')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('request_log',
    sa.Column('relo_id', postgresql.UUID(), autoincrement=False, nullable=False),
    sa.Column('relo_method', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('relo_url', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('relo_headers', postgresql.JSONB(astext_type=sa.Text()), autoincrement=False, nullable=True),
    sa.Column('relo_body', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('relo_status_code', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('relo_ip_address', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('relo_device_info', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('relo_absolute_path', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('relo_request_duration', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('relo_response_size', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('relo_inserted_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('relo_id', name='request_log_pkey')
    )
    op.create_index('ix_request_log_relo_url', 'request_log', ['relo_url'], unique=False)
    op.create_index('ix_request_log_relo_method', 'request_log', ['relo_method'], unique=False)
    op.create_index('ix_request_log_relo_id', 'request_log', ['relo_id'], unique=False)
    op.create_table('task_log',
    sa.Column('talo_id', postgresql.UUID(), autoincrement=False, nullable=False),
    sa.Column('talo_name', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('talo_status', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('talo_type', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.Column('talo_details', postgresql.JSONB(astext_type=sa.Text()), autoincrement=False, nullable=True),
    sa.Column('talo_start_time', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('talo_end_time', postgresql.TIMESTAMP(timezone=True), autoincrement=False, nullable=True),
    sa.Column('talo_success', sa.BOOLEAN(), autoincrement=False, nullable=True),
    sa.Column('talo_error_message', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('talo_error_trace', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('talo_inserted_at', postgresql.TIMESTAMP(timezone=True), server_default=sa.text('now()'), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('talo_id', name='task_log_pkey')
    )
    op.create_index('ix_task_log_talo_status', 'task_log', ['talo_status'], unique=False)
    op.create_index('ix_task_log_talo_name', 'task_log', ['talo_name'], unique=False)
    op.create_index('ix_task_log_talo_id', 'task_log', ['talo_id'], unique=False)
    # ### end Alembic commands ###