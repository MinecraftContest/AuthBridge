from flask import Flask, request, Response
from db import get_db
from emails import get_smtp, send_email
from psycopg2.errors import UniqueViolation
import random
import string
import hashlib
import os

PASSWORD_LENGTH = 6
AUTH_SECRET = os.environ.get('AUTH_SECRET')

with open('email_template.html') as f:
    EMAIL_TEMPLATE = f.read()

app = Flask(__name__)

def generate_password(length):
    result = ''.join([random.choice(string.ascii_lowercase) for x in range(length)])
    return result

@app.route('/hello')
def hello():
    return 'Hello world!'


@app.route('/create-team', methods=['POST'])
def create_team():
    data = request.get_json()

    if 'secret' not in data:
        return Response(status=401)

    if data['secret'] != AUTH_SECRET:
        return Response(status=401)

    conn = None
    smtp = None
    try:
        conn = get_db()
        smtp = get_smtp()
        cur = conn.cursor()
        try:
            cur.execute(
                'INSERT INTO teams(external_id, title_name) VALUES(%s, %s) RETURNING id',
                (data['id'], data['name'],))
            team_id = cur.fetchone()[0]
        except UniqueViolation as e:
            return Response(status=201)

        leader = data['leader']
        users = data['users']
        users.append(leader)

        for user in users:
            password = generate_password(PASSWORD_LENGTH)
            password_hash = hashlib.sha256()
            password_hash.update(password.encode('ascii'))
            cur.execute('INSERT INTO mc_users(external_id, full_name, email, password_hash, team_id) VALUES(%s,%s,%s,%s,%s) RETURNING id', (user['id'], user['name'], user['email'], password_hash.hexdigest(), team_id))
            user_id = cur.fetchone()[0]
            send_email(smtp, user['email'], 'Данные для подключения',
                EMAIL_TEMPLATE.replace('{{login}}', "{:03d}".format(user_id)).replace('{{password}}', password))
            user['generated_id'] = user_id

        cur.execute(
            'UPDATE teams SET leader_id = %s WHERE external_id = %s',
            (leader['generated_id'], data['id'])
        )
        conn.commit()
    finally:
        if conn is not None:
            conn.close()
        if smtp is not None:
            smtp.quit()
    return Response(status=200)

