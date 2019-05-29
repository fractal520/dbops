"""empty message

Revision ID: 348d0b49ec5
Revises: 1517ab92cfd
Create Date: 2017-07-05 20:03:32.517242

"""

# revision identifiers, used by Alembic.
revision = '348d0b49ec5'
down_revision = '1517ab92cfd'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('check_items', sa.Column('class_of_log', sa.String(length=50), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('check_items', 'class_of_log')
    ### end Alembic commands ###