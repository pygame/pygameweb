"""Added unique constraints to users.name and users.email

Revision ID: c25a81c43821
Revises: 31d24cc4f46b
Create Date: 2017-03-08 15:15:03.329654

"""

# revision identifiers, used by Alembic.
revision = 'c25a81c43821'
down_revision = '31d24cc4f46b'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###

    # Deduplicate users with the same email.
    duplicate_users_q = """
    select id, email from users where email in (select email from (
      SELECT email, id,
      ROW_NUMBER() OVER(PARTITION BY email ORDER BY id asc) AS Row
      FROM users
    ) dups
    where
    dups.Row > 1) ORDER BY email, id"""

    table_sql = sa.text(duplicate_users_q)
    connection = op.get_bind()
    rows = connection.execute(duplicate_users_q)


    # We reset all of their content to be owned by the first user added.

    # id_user = {user_id: email}
    # email_users = {email: [id, ...]}
    id_email = {}
    email_ids = {}
    for r in rows:
        id, email = r
        id_email[id] = email
        if email not in email_ids:
            email_ids[email] = []
        email_ids[email].append(id)

    for email in email_ids:
        first_user = email_ids[email][0]
        other_users = email_ids[email][1:]

        for ouser in other_users:
            queries = [
                f'UPDATE wiki set users_id={first_user} where users_id={ouser}',
                f'UPDATE project set users_id={first_user} where users_id={ouser}',
                f'UPDATE projectcomment set users_id={first_user} where users_id={ouser}',
                f'UPDATE docscomment set users_id={first_user} where users_id={ouser}',
                f'DELETE from users_groups where users_id={ouser}',
                f'DELETE from users where id={ouser}',
            ]
            for query in queries:
                op.execute(query)

    op.create_unique_constraint(None, 'users', ['email'])
    op.create_unique_constraint(None, 'users', ['name'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'users', type_='unique')
    op.drop_constraint(None, 'users', type_='unique')
    # ### end Alembic commands ###