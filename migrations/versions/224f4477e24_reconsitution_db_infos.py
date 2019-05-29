"""reconsitution db infos

Revision ID: 224f4477e24
Revises: None
Create Date: 2017-09-18 22:56:10.118054

"""

# revision identifiers, used by Alembic.
revision = '224f4477e24'
down_revision = None

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('alarm_levels',
    sa.Column('level_id', sa.Integer(), nullable=False),
    sa.Column('level_name', sa.String(length=20), nullable=True),
    sa.Column('level_desc', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('level_id')
    )
    op.create_table('check_items',
    sa.Column('check_id', sa.Integer(), nullable=False),
    sa.Column('check_name', sa.String(length=100), nullable=True),
    sa.Column('frequency', sa.SmallInteger(), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('class_of_log', sa.String(length=50), nullable=True),
    sa.PrimaryKeyConstraint('check_id')
    )
    op.create_table('dbtypes',
    sa.Column('db_type_id', sa.Integer(), nullable=False),
    sa.Column('db_type_name', sa.String(length=20), nullable=False),
    sa.PrimaryKeyConstraint('db_type_id'),
    sa.UniqueConstraint('db_type_name')
    )
    op.create_table('ip_addresses',
    sa.Column('ip_id', sa.Integer(), nullable=False),
    sa.Column('ip_address', mysql.INTEGER(display_width=11, unsigned=True), nullable=True),
    sa.PrimaryKeyConstraint('ip_id')
    )
    op.create_table('roles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('default', sa.Boolean(), nullable=True),
    sa.Column('permissions', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_index('ix_roles_default', 'roles', ['default'], unique=False)
    op.create_table('db_arches',
    sa.Column('db_arch_id', sa.SmallInteger(), nullable=False),
    sa.Column('db_type_id', sa.Integer(), nullable=True),
    sa.Column('db_arch_name', sa.String(length=100), nullable=True),
    sa.ForeignKeyConstraint(['db_type_id'], ['dbtypes.db_type_id'], ),
    sa.PrimaryKeyConstraint('db_arch_id')
    )
    op.create_table('dbinst_roles',
    sa.Column('dbinst_role_id', sa.SmallInteger(), nullable=False),
    sa.Column('db_type_id', sa.Integer(), nullable=True),
    sa.Column('dbinst_role_name', sa.String(length=100), nullable=True),
    sa.ForeignKeyConstraint(['db_type_id'], ['dbtypes.db_type_id'], ),
    sa.PrimaryKeyConstraint('dbinst_role_id')
    )
    op.create_table('hosts',
    sa.Column('host_id', sa.Integer(), nullable=False),
    sa.Column('host_name', sa.String(length=100), nullable=True),
    sa.Column('host_ip_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['host_ip_id'], ['ip_addresses.ip_id'], ),
    sa.PrimaryKeyConstraint('host_id')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=64), nullable=True),
    sa.Column('username', sa.String(length=64), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=True),
    sa.Column('confirmed', sa.Boolean(), nullable=True),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('location', sa.String(length=64), nullable=True),
    sa.Column('about_me', sa.Text(), nullable=True),
    sa.Column('member_since', sa.DateTime(), nullable=True),
    sa.Column('last_seen', sa.DateTime(), nullable=True),
    sa.Column('avatar_hash', sa.String(length=32), nullable=True),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_username', 'users', ['username'], unique=True)
    op.create_table('dbinfos',
    sa.Column('db_id', sa.Integer(), nullable=False),
    sa.Column('dbname', sa.String(length=100), nullable=True),
    sa.Column('db_type_id', sa.Integer(), nullable=True),
    sa.Column('db_arch_id', sa.SmallInteger(), nullable=True),
    sa.Column('add_time', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['db_arch_id'], ['db_arches.db_arch_id'], ),
    sa.ForeignKeyConstraint(['db_type_id'], ['dbtypes.db_type_id'], ),
    sa.PrimaryKeyConstraint('db_id')
    )
    op.create_index('ix_dbinfos_add_time', 'dbinfos', ['add_time'], unique=False)
    op.create_table('posts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('body', sa.Text(), nullable=True),
    sa.Column('body_html', sa.Text(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('author_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_posts_timestamp', 'posts', ['timestamp'], unique=False)
    op.create_table('alarm_logs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('db_id', sa.Integer(), nullable=True),
    sa.Column('alarm_message', sa.Text(), nullable=True),
    sa.Column('level_name', sa.String(length=20), nullable=True),
    sa.Column('level_id', sa.Integer(), nullable=True),
    sa.Column('check_id', sa.Integer(), nullable=True),
    sa.Column('create_time', sa.DateTime(), nullable=True),
    sa.Column('status', sa.SmallInteger(), nullable=True),
    sa.Column('finish_time', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['check_id'], ['check_items.check_id'], ),
    sa.ForeignKeyConstraint(['db_id'], ['dbinfos.db_id'], ),
    sa.ForeignKeyConstraint(['level_id'], ['alarm_levels.level_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_alarm_logs_create_time', 'alarm_logs', ['create_time'], unique=False)
    op.create_table('alarm_thresholds',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('db_id', sa.Integer(), nullable=True),
    sa.Column('check_id', sa.Integer(), nullable=True),
    sa.Column('level_id', sa.Integer(), nullable=True),
    sa.Column('threshold', sa.Numeric(precision=3, scale=2), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['check_id'], ['check_items.check_id'], ),
    sa.ForeignKeyConstraint(['db_id'], ['dbinfos.db_id'], ),
    sa.ForeignKeyConstraint(['level_id'], ['alarm_levels.level_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('check_connect_num_logs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('db_id', sa.Integer(), nullable=True),
    sa.Column('connect_num', sa.Integer(), nullable=True),
    sa.Column('max_num', sa.Integer(), nullable=True),
    sa.Column('check_time', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['db_id'], ['dbinfos.db_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_check_connect_num_logs_check_time', 'check_connect_num_logs', ['check_time'], unique=False)
    op.create_table('check_connectivity_logs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('db_id', sa.Integer(), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('check_time', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['db_id'], ['dbinfos.db_id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_check_connectivity_logs_check_time', 'check_connectivity_logs', ['check_time'], unique=False)
    op.create_table('comments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('body', sa.Text(), nullable=True),
    sa.Column('body_html', sa.Text(), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('disabled', sa.Boolean(), nullable=True),
    sa.Column('author_id', sa.Integer(), nullable=True),
    sa.Column('post_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['author_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['post_id'], ['posts.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_comments_timestamp', 'comments', ['timestamp'], unique=False)
    op.create_table('follows',
    sa.Column('follower_id', sa.Integer(), nullable=False),
    sa.Column('db_id', sa.Integer(), nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['db_id'], ['dbinfos.db_id'], ),
    sa.ForeignKeyConstraint(['follower_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('follower_id', 'db_id')
    )
    op.create_table('instances',
    sa.Column('instance_id', sa.Integer(), nullable=False),
    sa.Column('instance_name', sa.String(length=100), nullable=True),
    sa.Column('access_ip_id', sa.Integer(), nullable=True),
    sa.Column('access_port', sa.Integer(), nullable=True),
    sa.Column('dbinst_role_id', sa.SmallInteger(), nullable=True),
    sa.Column('db_id', sa.Integer(), nullable=True),
    sa.Column('host_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['access_ip_id'], ['ip_addresses.ip_id'], ),
    sa.ForeignKeyConstraint(['db_id'], ['dbinfos.db_id'], ),
    sa.ForeignKeyConstraint(['dbinst_role_id'], ['dbinst_roles.dbinst_role_id'], ),
    sa.ForeignKeyConstraint(['host_id'], ['hosts.host_id'], ),
    sa.PrimaryKeyConstraint('instance_id')
    )
    op.create_table('schemas',
    sa.Column('schema_id', sa.Integer(), nullable=False),
    sa.Column('schame_name', sa.String(length=100), nullable=True),
    sa.Column('db_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['db_id'], ['dbinfos.db_id'], ),
    sa.PrimaryKeyConstraint('schema_id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('schemas')
    op.drop_table('instances')
    op.drop_table('follows')
    op.drop_index('ix_comments_timestamp', 'comments')
    op.drop_table('comments')
    op.drop_index('ix_check_connectivity_logs_check_time', 'check_connectivity_logs')
    op.drop_table('check_connectivity_logs')
    op.drop_index('ix_check_connect_num_logs_check_time', 'check_connect_num_logs')
    op.drop_table('check_connect_num_logs')
    op.drop_table('alarm_thresholds')
    op.drop_index('ix_alarm_logs_create_time', 'alarm_logs')
    op.drop_table('alarm_logs')
    op.drop_index('ix_posts_timestamp', 'posts')
    op.drop_table('posts')
    op.drop_index('ix_dbinfos_add_time', 'dbinfos')
    op.drop_table('dbinfos')
    op.drop_index('ix_users_username', 'users')
    op.drop_index('ix_users_email', 'users')
    op.drop_table('users')
    op.drop_table('hosts')
    op.drop_table('dbinst_roles')
    op.drop_table('db_arches')
    op.drop_index('ix_roles_default', 'roles')
    op.drop_table('roles')
    op.drop_table('ip_addresses')
    op.drop_table('dbtypes')
    op.drop_table('check_items')
    op.drop_table('alarm_levels')
    ### end Alembic commands ###
