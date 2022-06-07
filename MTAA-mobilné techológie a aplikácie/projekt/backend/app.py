import flask
from flask import Flask, request, jsonify, make_response
import os
import psycopg2
from flask_restful import Resource, reqparse
from functools import wraps
import jwt
import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['JSON_SORT_KEYS'] = False
app.config['SECRET_KEY'] = os.urandom(12).hex()


def token_required(f):
    @wraps(f)
    def decorated(*args,**kwargs):
        token = request.headers.get('token')
        # token = request.args.get('token')
        if not token:
            return jsonify({'message': 'Token is missing'}), 403

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms="HS256")
        except:
            return jsonify({'message': 'Token is invalid'}), 403

        return f(*args,**kwargs)

    return decorated


user_login_args = reqparse.RequestParser()
user_login_args.add_argument("name", type=str, required=True)
user_login_args.add_argument("password", type=str, required=True)


@app.route('/login',methods=['POST'])
def login():
    args = user_login_args.parse_args()
    name = args["name"]
    password = args["password"]
    prikaz = ("select * from users where name = \'" + name +  "\' and password = \'" + password + "\'")

    popis,odpoved,cur,conn = pripojenie(prikaz)
    cur.close()
    conn.close()

    if len(odpoved) == 1:
        token = jwt.encode({'user': name, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, app.config['SECRET_KEY'],algorithm="HS256")

        delete("delete from call_history where now()-time > interval '1 month'")
        delete("delete from events where now()-time > interval '1 week' and now()>time")

        return jsonify({'token': token, "user_id": odpoved[0][0]}),200

    return jsonify({'message':'Incorrect login information'}),401


def get_db_connection():

    conn = psycopg2.connect(
        host=os.getenv("DBIP-MTAA"),
        database=os.getenv("DBNAME-MTAA"),
        user=os.getenv("DBUSER-MTAA"),
        password=os.getenv("DBPASS-MTAA"),
        port=os.getenv("DBPORT"))

    return conn


def pripojenie(prikaz):                         # pripojenie sa na databazu
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(prikaz)
    popis = cur.description
    odpoved = cur.fetchall()

    return popis,odpoved,cur,conn


def get_method(prikaz,string,start,end):

    popis,odpoved,cur,conn = pripojenie(prikaz)
    list = []
    vypis_all = {string: list}

    while len(odpoved) > 0:
        akt_zaznam = odpoved.pop(0)
        element_of_list = {}

        for index in range(start, end):  # naplnenie hodnot v dict. pre akt.element
            key = popis[index].name
            element_of_list[key] = akt_zaznam[index]

        list.append(element_of_list)

    cur.close()
    conn.close()
    return flask.jsonify(vypis_all)


# GET endpointy
@app.route('/get/calls/<user_id>', methods=["GET"])
@token_required
def get_calls(user_id):

    prikaz = ("select * from call_history where caller_id = " + user_id +" or receiver_id = " + user_id)

    return get_method(prikaz,"calls", 1, 5)


@app.route('/get/user/events/<user_id>', methods=["GET"])
@token_required
def get_user_events(user_id):

    prikaz = ("select id as event_id,title,description,time,file,contact_id from events where user_id = " + user_id)
    return get_method(prikaz, "events", 0, 6)


@app.route('/get/user/events/today/<user_id>', methods=["GET"])
@token_required
def get_user_events_today(user_id):

    prikaz = ("select id as event_id,title,description,time,file,contact_id from events where (EXTRACT(day from now()) = EXTRACT(day from time) and now()-time < interval '1 day' and user_id = " + user_id + ") order by time")

    return get_method(prikaz, "events", 0, 6)


# POST endpointy
user_post_args = reqparse.RequestParser()
user_post_args.add_argument("name", type=str, help="name of new user is required", required=True)
user_post_args.add_argument("password", type=str, help="password of new user is required", required=True)
user_post_args.add_argument("ip_address", type=str, help="ip_address of new user is required",required=True)


def post_method(prikaz):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(prikaz)
    conn.commit()
    cur.close()
    conn.close()


@app.route('/register', methods=["POST"])
def register():

    args = user_post_args.parse_args()
    name = args["name"]
    passwd = args["password"]
    ipaddress = args["ip_address"]
    prikaz = ("insert into users(name,password,ip_address) values(\'" + name + "\',\'" + passwd + "\',\'" + ipaddress + "\')")

    try:
        post_method(prikaz)
    except psycopg2.errors.UniqueViolation:
        return jsonify({"message":"422 The user already exists"}), 422
    except:
        return jsonify({"message": "Fail"}), 400

    return jsonify({"message": "Success"}), 201


event_post_args = reqparse.RequestParser()
event_post_args.add_argument("user_id", type=int, required=True)
event_post_args.add_argument("title", type=str, required=True)
event_post_args.add_argument("description", type=str)
event_post_args.add_argument("time", type=str,required=True)
event_post_args.add_argument("file", type=str)
event_post_args.add_argument("contact_id", type=int)


@app.route('/add/event', methods=["POST"])
@token_required
def add_event():
    args = event_post_args.parse_args()
    # name = request.form["name"]
    user_id = args["user_id"].__str__()
    title = args["title"]
    description = args["description"]
    time = args["time"]
    file = args["file"]
    contact_id = args["contact_id"].__str__()

    prikaz = "insert into events(user_id,title"
    if description is not None:
        prikaz += ",description"
    prikaz += ",time"
    if file is not None:
        prikaz += ",file"

    if contact_id is not None:
        prikaz += ",contact_id"

    prikaz += ") values(\'" + user_id + "\',\'" + title + "\'"

    if description is not None:
        prikaz += ",\'" + description + "\'"
    prikaz += ",\'" + time + "\'"
    if file is not None:
        prikaz += ",\'" + file + "\'"
    if contact_id is not None:
        prikaz += ",\'" + contact_id + "\'"
    prikaz += ")"

    try:
        post_method(prikaz)
    except:
        return jsonify({"message": "Fail"}), 400

    return jsonify({"message": "Success"}), 201


call_post_args = reqparse.RequestParser()
call_post_args.add_argument("caller_id", type=int, required=True)
call_post_args.add_argument("receiver_id", type=int, required=True)
call_post_args.add_argument("call_length", type=int, required=True)
call_post_args.add_argument("time", type=str, required=True)


@app.route('/add/call', methods=["POST"])
@token_required
def add_call():

    args = call_post_args.parse_args()
    # name = request.form["name"]
    caller_id = args["caller_id"].__str__()
    receiver_id = args["receiver_id"].__str__()
    call_length = args["call_length"].__str__()
    time = args["time"]

    prikaz = ("insert into call_history(caller_id,receiver_id,call_length,time) values(\'" + caller_id + "\',\'" + receiver_id +"\',\'" + call_length + "\',\'" + time + "\')")

    if caller_id == receiver_id:
        return jsonify({"message": "Fail"}), 400
    try:
        post_method(prikaz)
    except:
        return jsonify({"message": "Fail"}),400

    return jsonify({"message": "Success"}), 201


# DELETE endpointy
def delete(prikaz):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(prikaz)
    conn.commit()

    cur.close()
    conn.close()
    return jsonify({"message": "Success"}), 200


@app.route('/delete/user/<user_id>', methods=["DELETE"])
@token_required
def delete_user(user_id):
    prikaz1 =("select from users where id =" + user_id)
    popis, odpoved, cur, conn = pripojenie(prikaz1)

    if len(odpoved) == 0:
        return jsonify({"message": "Fail"}),404

    prikaz = ("delete from users where id = " + user_id)
    return delete(prikaz)


@app.route('/delete/event/<event_id>', methods=["DELETE"])
@token_required
def delete_event(event_id):
    prikaz1 =("select from events where id =" + event_id)
    popis, odpoved, cur, conn = pripojenie(prikaz1)

    if len(odpoved) == 0:
        return jsonify({"message": "Fail"}),404

    prikaz = ("delete from events where id = " + event_id)
    return delete(prikaz)


event_put_args = reqparse.RequestParser()
event_put_args.add_argument("title", type=str)
event_put_args.add_argument("description", type=str)
event_put_args.add_argument("time", type=str)
event_put_args.add_argument("file", type=str)
event_put_args.add_argument("contact_id", type=int)


# PUT endpointy
@app.route('/update/event/<event_id>', methods=["PUT"])
@token_required
def update_event(event_id):
    args = event_put_args.parse_args()
    title = args["title"]
    description = args["description"]
    time = args["time"]
    file = args["file"]
    contact_id = args["contact_id"]


    valid_request = False       # ak nevyplnil ziadne pole tak nema zmysel volat query
    comma_required = False
    prikaz = "update events set"
    if title is not None:
        prikaz += " title = \'" + title + "\'"
        comma_required = True
        valid_request = True
    if description is not None:
        if comma_required:
            prikaz += ','

        prikaz += " description = \'" + description + "\'"
        comma_required = True
        valid_request = True
    if time is not None:
        if comma_required:
            prikaz += ','

        prikaz += " time = \'" + time + "\'"
        comma_required = True
        valid_request = True
    if file is not None:
        if comma_required:
            prikaz += ','

        prikaz += " file = \'" + file + "\'"
        comma_required = True
        valid_request = True
    if contact_id is not None:
        contact_id = str(contact_id)
        if comma_required:
            prikaz += ','
        prikaz += " contact_id = \'" + contact_id + "\'"

        valid_request = True

    prikaz += " where id = " + event_id

    if valid_request:
        try:
            prikaz1 = ("select from events where id =" + event_id)
            popis, odpoved, cur, conn = pripojenie(prikaz1)

            if len(odpoved) == 0:
                return jsonify({"message": "Fail"}), 404

            post_method(prikaz)
            return jsonify({"message": "Success"}), 200
        except :
            return jsonify({"message": "Fail"}),400
    else:
        return jsonify({"message": "Fail"}), 400



@app.errorhandler(404)
def page_not_found(e):
    return jsonify({"message":"404 Page not found"}),404


@app.errorhandler(500)
def page_not_found(e):
    return jsonify({"message": "500 Internal server error"}),500


@app.errorhandler(409)
def page_not_found(e):
    return jsonify({"message": "Conflict"}),409

@app.errorhandler(400)
def page_not_found(e):
    return jsonify({"message": "Fail"}),400

if __name__ == '__main__':
    app.run()
