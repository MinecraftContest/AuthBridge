from flask import Flask, request, Response
from db import get_db
from emails import get_smtp, send_email
import json
import random
import string
import hashlib
import smtplib

PASSWORD_LENGTH = 6

with open('email_template.html') as f:
    EMAIL_TEMPLATE = f.read()

app = Flask(__name__)

def generate_password(length):
    result = ''.join([random.choice(string.ascii_lowercase) for x in range(length)])
    return result


@app.route('/create-team', methods=['POST'])
def create_team():
    # TODO: check secret
    print(request.args.get('secret'))

    data = request.get_json()

    conn = get_db()
    smtp = get_smtp()
    cur = conn.cursor()
    cur.execute('INSERT INTO teams(title_name) VALUES(%s) RETURNING id', (data['name'],))
    team_id = cur.fetchone()[0]
    for user in data['users']:
        password = generate_password(PASSWORD_LENGTH)
        password_hash = hashlib.sha256()
        password_hash.update(password.encode('ascii'))
        cur.execute('INSERT INTO mc_users(external_id, full_name, email, password_hash, team_id) VALUES(%s,%s,%s,%s,%s) RETURNING id', (user['id'], user['name'], user['email'], password_hash.hexdigest(), team_id))
        user_id = cur.fetchone()[0]
        send_email(smtp, user['email'], 'Данные для подключения',
            EMAIL_TEMPLATE.replace('{{login}}', "{:03d}".format(user_id)).replace('{{password}}', password))

    conn.commit()
    conn.close()
    smtp.quit()
    return Response(status=200)