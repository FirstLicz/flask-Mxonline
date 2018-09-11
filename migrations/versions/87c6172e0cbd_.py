"""empty message

Revision ID: 87c6172e0cbd
Revises: 
Create Date: 2018-08-30 10:23:54.933558

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '87c6172e0cbd'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('banners',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('title', sa.String(length=128), nullable=True),
    sa.Column('url', sa.String(length=256), nullable=True),
    sa.Column('image', sa.String(length=256), nullable=True),
    sa.Column('index', sa.Integer(), nullable=False),
    sa.Column('add_time', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_index(op.f('ix_banners_title'), 'banners', ['title'], unique=False)
    op.create_table('courses',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=128), nullable=False),
    sa.Column('add_time', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_index(op.f('ix_courses_name'), 'courses', ['name'], unique=False)
    op.create_table('roles',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('add_time', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_index(op.f('ix_roles_name'), 'roles', ['name'], unique=False)
    op.create_table('users',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('username', sa.String(length=128), nullable=False),
    sa.Column('name', sa.String(length=128), nullable=True),
    sa.Column('password_hash', sa.String(length=256), nullable=False),
    sa.Column('image', sa.String(length=128), nullable=True),
    sa.Column('gender', sa.Boolean(), nullable=False),
    sa.Column('address', sa.String(length=200), nullable=True),
    sa.Column('mobile', sa.String(length=11), nullable=True),
    sa.Column('birthday', sa.Date(), nullable=True),
    sa.Column('add_time', sa.DateTime(), nullable=True),
    sa.Column('last_login', sa.DateTime(), nullable=True),
    sa.Column('last_logout', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_index(op.f('ix_users_name'), 'users', ['name'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=False)
    op.create_table('verify_codes',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('email', sa.String(length=128), nullable=False),
    sa.Column('code', sa.String(length=32), nullable=False),
    sa.Column('code_type', sa.String(length=2), nullable=False),
    sa.Column('send_time', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_index(op.f('ix_verify_codes_code'), 'verify_codes', ['code'], unique=False)
    op.create_index(op.f('ix_verify_codes_email'), 'verify_codes', ['email'], unique=False)
    op.create_table('messages',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('message', sa.String(length=256), nullable=False),
    sa.Column('add_time', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_index(op.f('ix_messages_message'), 'messages', ['message'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_messages_message'), table_name='messages')
    op.drop_table('messages')
    op.drop_index(op.f('ix_verify_codes_email'), table_name='verify_codes')
    op.drop_index(op.f('ix_verify_codes_code'), table_name='verify_codes')
    op.drop_table('verify_codes')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_name'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_roles_name'), table_name='roles')
    op.drop_table('roles')
    op.drop_index(op.f('ix_courses_name'), table_name='courses')
    op.drop_table('courses')
    op.drop_index(op.f('ix_banners_title'), table_name='banners')
    op.drop_table('banners')
    # ### end Alembic commands ###
