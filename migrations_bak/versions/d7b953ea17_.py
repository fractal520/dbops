"""empty message

Revision ID: d7b953ea17
Revises: 1c8d9a4510d
Create Date: 2017-06-08 23:19:17.805422

"""

# revision identifiers, used by Alembic.
revision = 'd7b953ea17'
down_revision = '1c8d9a4510d'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('dbinfos', sa.Column('ip', mysql.INTEGER(display_width=11, unsigned=True), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('dbinfos', 'ip')
    ### end Alembic commands ###
