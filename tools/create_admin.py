from getpass import getpass

from argon2 import PasswordHasher
import psycopg


conn = psycopg.connect(
    "postgresql://metabase:shallN#v3rL34k@10.174.7.177:5432/endrix"
)

username = input("Username: ")
password = getpass("Password: ")

ph = PasswordHasher()

password_hash = ph.hash(password)

with conn.cursor() as cur:
    cur.execute(
        """
        INSERT INTO users
            (username, password_hash, active)
        VALUES
            (%s, %s, TRUE)
        """,
        (username, password_hash)
    )

conn.commit()

print("User created.")