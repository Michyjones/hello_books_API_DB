"""empty message

Revision ID: f98a4ccb480f
Revises: 
Create Date: 2018-06-16 11:55:09.201606

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f98a4ccb480f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('blacklist',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('token', sa.String(length=200), nullable=False),
    sa.Column('valid', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('book',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('serial_no', sa.String(length=20), nullable=True),
    sa.Column('book_name', sa.String(length=100), nullable=True),
    sa.Column('category', sa.String(length=50), nullable=True),
    sa.Column('availabilty', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('user',
    sa.Column('first_name', sa.String(length=30), nullable=True),
    sa.Column('last_name', sa.String(length=30), nullable=True),
    sa.Column('address', sa.String(length=30), nullable=True),
    sa.Column('email', sa.String(length=50), nullable=False),
    sa.Column('password', sa.String(length=128), nullable=True),
    sa.Column('IsAdmin', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('email')
    )
    op.create_table('borrow',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('book_id', sa.Integer(), nullable=True),
    sa.Column('user_email', sa.String(), nullable=True),
    sa.Column('date_borrowed', sa.DateTime(), nullable=False),
    sa.Column('date_returned', sa.DateTime(), nullable=True),
    sa.Column('returned', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['book_id'], ['book.id'], ),
    sa.ForeignKeyConstraint(['user_email'], ['user.email'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('borrow')
    op.drop_table('user')
    op.drop_table('book')
    op.drop_table('blacklist')
    # ### end Alembic commands ###
