import psycopg2
import os

def get_db():
    conn = psycopg2.connect(
        host=os.environ.get('DATABASE_HOST'),
        database=os.environ.get('DATABASE_NAME'),
        user=os.environ.get('DATABASE_USER'),
        password=os.environ.get('DATABASE_PASSWORD'))
    return conn