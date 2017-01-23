"""Initial db, before import of old db.

Revision ID: 47683b299022
Revises:
Create Date: 2016-07-19 15:54:59.599369

"""

# revision identifiers, used by Alembic.
revision = '47683b299022'
down_revision = None
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('skin',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('title', sa.VARCHAR(length=80), autoincrement=False, nullable=True),
    sa.Column('fname', sa.VARCHAR(length=80), autoincrement=False, nullable=True),
    sa.Column('orders', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='skin_pkey')
    )
    op.create_table('users',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(length=80), autoincrement=False, nullable=True),
    sa.Column('email', sa.VARCHAR(length=80), autoincrement=False, nullable=True),
    sa.Column('passwd', sa.VARCHAR(length=80), autoincrement=False, nullable=True),
    sa.Column('title', sa.VARCHAR(length=80), autoincrement=False, nullable=True),
    sa.Column('disabled', sa.INTEGER(), server_default=sa.text('0'), autoincrement=False, nullable=True),
    sa.Column('super', sa.INTEGER(), server_default=sa.text('0'), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='users_pkey')
    )
    op.create_table('docscomment',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('link', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('users_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('datetimeon', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('content', sa.TEXT(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='docscomment_pkey')
    )
    op.create_table('node',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('title', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('keywords', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('type', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('content', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('summary', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('orders', sa.INTEGER(), server_default=sa.text('0'), autoincrement=False, nullable=False),
    sa.Column('parentid', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('link', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('hidden', sa.INTEGER(), server_default=sa.text('0'), autoincrement=False, nullable=True),
    sa.Column('target', sa.VARCHAR(length=80), autoincrement=False, nullable=True),
    sa.Column('custom', postgresql.BYTEA(), autoincrement=False, nullable=True),
    sa.Column('skin_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('uri', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('users_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('groups_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('mods', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('folderid', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('folder', sa.INTEGER(), server_default=sa.text('0'), autoincrement=False, nullable=True),
    sa.Column('modules_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('image', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='node_pkey')
    )
    op.create_table('wikicomment',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('link', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('users_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('datetimeon', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('content', sa.TEXT(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='wikicomment_pkey')
    )
    op.create_table('news',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('title', sa.VARCHAR(length=80), autoincrement=False, nullable=True),
    sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('datetimeon', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('submit_users_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='news_pkey')
    )
    op.create_table('modules',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(length=80), autoincrement=False, nullable=True),
    sa.Column('title', sa.VARCHAR(length=80), autoincrement=False, nullable=True),
    sa.Column('orders', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='modules_pkey')
    )
    op.create_table('project',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('users_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('node_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('title', sa.VARCHAR(length=80), autoincrement=False, nullable=True),
    sa.Column('summary', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('uri', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('datetimeon', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('image', sa.VARCHAR(length=80), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='project_pkey')
    )
    op.create_table('projectcomment',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('project_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('users_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('datetimeon', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('content', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('rating', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='projectcomment_pkey')
    )
    op.create_table('groups',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('name', sa.VARCHAR(length=80), autoincrement=False, nullable=True),
    sa.Column('title', sa.VARCHAR(length=80), autoincrement=False, nullable=True),
    sa.Column('orders', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='groups_pkey')
    )
    op.create_table('tags',
    sa.Column('project_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('value', sa.VARCHAR(length=32), autoincrement=False, nullable=True)
    )
    op.create_table('wiki',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('link', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('summary', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('content', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('datetimeon', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('fname', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('changes', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('users_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('latest', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('name', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('title', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('parent', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('keywords', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='wiki_pkey')
    )
    op.create_table('users_groups',
    sa.Column('users_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('groups_id', sa.INTEGER(), autoincrement=False, nullable=True)
    )
    op.create_table('release',
    sa.Column('id', sa.INTEGER(), nullable=False),
    sa.Column('project_id', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('datetimeon', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('description', sa.TEXT(), autoincrement=False, nullable=True),
    sa.Column('srcuri', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('winuri', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('macuri', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('title', sa.VARCHAR(length=80), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name='release_pkey')
    )
    ### end Alembic commands ###

def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('release')
    op.drop_table('users_groups')
    op.drop_table('wiki')
    op.drop_table('tags')
    op.drop_table('groups')
    op.drop_table('projectcomment')
    op.drop_table('project')
    op.drop_table('modules')
    op.drop_table('news')
    op.drop_table('wikicomment')
    op.drop_table('node')
    op.drop_table('docscomment')
    op.drop_table('users')
    op.drop_table('skin')
    ### end Alembic commands ###