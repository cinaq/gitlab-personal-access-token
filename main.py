import base64
import hashlib
import psycopg2
import os

default_scopes = """---
- api
- read_user
- read_api
- read_repository
- write_repository
- read_registry
- write_registry
- sudo
"""
db_key_base = os.environ.get('DB_KEY_BASE')
pg_host = os.environ.get('PG_HOST')
pg_dbname = os.environ.get('PG_DBNAME')
pg_port = os.environ.get('PG_PORT')
pg_username = os.environ.get('PG_USERNAME')
pg_password = os.environ.get('PG_PASSWORD')
api_key = os.environ.get('API_KEY')
user_id = int(os.environ.get('USER_ID', 1))
user_scopes = os.environ.get('USER_SCOPES', default_scopes)
api_name = os.environ.get('API_NAME', "Managed by CINAQ gitlab-personal-access-token")

token_digest = base64.b64encode(hashlib.sha256((api_key + db_key_base[:32]).encode('utf-8')).digest()).decode('utf-8')


def get_id(conn, user_id, token_digest):
    with conn.cursor() as cursor:
        cursor.execute(
            """SELECT id FROM personal_access_tokens WHERE user_id = %s and token_digest = %s""",
            (user_id, token_digest,)
        )
        row = cursor.fetchone()
        if row:
            return row[0]
        else:
            return None

def create_pat(conn, user_id, user_scopes, token_digest):
    with conn.cursor() as cursor:
        cursor.execute(
            """INSERT INTO personal_access_tokens 
                (name, impersonation, scopes, revoked, user_id, token_digest)
                VALUES  (%s, %s, %s, %s, %s, %s)""",
            (api_name, False, user_scopes, False, user_id, token_digest)
        )

connect_str = f"dbname='{pg_dbname}' user='{pg_username}' host='{pg_host}' password='{pg_password}' port='{pg_port}'"
conn = psycopg2.connect(connect_str)

current_id = get_id(conn, user_id, token_digest)
if not current_id:
    create_pat(conn, user_id, user_scopes, token_digest)
new_id = get_id(conn, user_id, token_digest)
if not new_id:
    raise Exception("Failed to create PAT")
else:
    print("PAT ID: " + str(new_id))
conn.commit()
conn.close()