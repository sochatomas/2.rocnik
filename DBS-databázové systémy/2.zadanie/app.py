import flask
from flask import Flask
import os
import psycopg2

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['JSON_SORT_KEYS'] = False

def get_db_connection():

    conn = psycopg2.connect(
        host=os.getenv("DBIP"),
        database=os.getenv("DBNAME"),
        user=os.getenv("DBUSER"),
        password=os.getenv("DBPASS"),
        port=os.getenv("DBPORT"))

    return conn

@app.route('/v1/health', methods=['GET'])
def api():
    conn = get_db_connection()
    cur = conn.cursor()

    prikazy = ("SELECT version();","SELECT pg_database_size('dota2')/1024/1024 as dota2_db_size;")
    vypis = {}

    for prikaz in prikazy:
        cur.execute(prikaz)
        popis = cur.description[0].name
        odpoved = cur.fetchone()
        vypis[popis] = odpoved[0]

    vypis_all = {"pgsql": vypis}

    cur.close()
    conn.close()
    return flask.jsonify(vypis_all)


@app.route('/')
def hello():
    return "fungujem "


@app.route('/v1')
def almost():
    return "pridaj este /health  ;)"


if __name__ == '__main__':
    app.run()


