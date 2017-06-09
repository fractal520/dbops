"""empty message

Revision ID: a57123178a
Revises: 1cf17229dc4
Create Date: 2017-06-08 23:06:16.920132

"""

# revision identifiers, used by Alembic.
revision = 'a57123178a'
down_revision = '1cf17229dc4'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('dbinfos',
    sa.Column('db_id', sa.Integer(), nullable=False),
    sa.Column('instance_name', sa.String(length=100), nullable=True),
    sa.Column('dbname', sa.String(length=100), nullable=True),
    sa.Column('ip', mysql.INTEGER(unsigned=True), nullable=True),
    sa.Column('port', sa.Integer(), nullable=True),
    sa.Column('schema_name', sa.String(length=100), nullable=True),
    sa.Column('db_type', sa.String(length=20), nullable=True),
    sa.PrimaryKeyConstraint('db_id')
    )
    op.create_table('monitor_levels',
    sa.Column('level_id', sa.Integer(), nullable=False),
    sa.Column('level_name', sa.String(length=20), nullable=True),
    sa.Column('level_desc', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('level_id')
    )
    op.create_table('monitor_logs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('db_id', sa.Integer(), nullable=True),
    sa.Column('monitor_log', sa.Text(), nullable=True),
    sa.Column('monitor_level_name', sa.String(length=20), nullable=True),
    sa.Column('level_id', sa.Integer(), nullable=True),
    sa.Column('create_time', sa.DateTime(), nullable=True),
    sa.Column('status', sa.SmallInteger(), nullable=True),
    sa.Column('finish_time', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['db_id'], ['dbinfos.db_id'], ),
    sa.ForeignKeyConstraint(['level_id'], ['monitor_levels.level_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_monitor_logs_create_time', 'monitor_logs', ['create_time'], unique=False)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_monitor_logs_create_time', 'monitor_logs')
    op.drop_table('monitor_logs')
    op.drop_table('monitor_levels')
    op.drop_table('dbinfos')
    ### end Alembic commands ###