"""empty message

Revision ID: 3e283b664d0
Revises: 3125e3fd49a
Create Date: 2017-09-25 23:26:53.158447

"""

# revision identifiers, used by Alembic.
revision = '3e283b664d0'
down_revision = '3125e3fd49a'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('db_schemas', sa.Column('schema_name', sa.String(length=100), nullable=True))
    op.drop_column('db_schemas', 'schame_name')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('db_schemas', sa.Column('schame_name', mysql.VARCHAR(length=100), nullable=True))
    op.drop_column('db_schemas', 'schema_name')
    ### end Alembic commands ###
