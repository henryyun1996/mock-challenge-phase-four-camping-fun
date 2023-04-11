from flask import Flask, request, make_response, jsonify
from flask_cors import CORS
from flask_migrate import Migrate

from models import db, Camper, Activity, Signup

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

CORS(app)
migrate = Migrate(app, db)

db.init_app(app)

# api = Api(app)


@app.route('/')
def index():
    response = make_response(
        {
            "message": "Hello Campers!"
        },
        200
    )
    return response

@app.route('/campers', methods=['GET', 'POST'])
def get_and_post_campers():
    if request.method == 'GET':
        campers = Camper.query.all()
        return make_response([camper.to_dict() for camper in campers], 200)
    if request.method == 'POST':
        try:
            new_camper = Camper(
                name = request.get_json()['name'],
                age = request.get_json()['age']
            )
            db.session.add(new_camper)
            db.session.commit()
        except ValueError:
            return make_response({"errors": ["validation errors"]}, 404)
        response = make_response(
            new_camper.to_dict(),
            200
        )
        return response

@app.route('/campers/<int:id>', methods=['GET'])
def campers_by_id(id):
    camper = Camper.query.filter_by(id=id).first()
    if not camper:
        return make_response({"error": "Camper not found"}, 404)
    return make_response(camper.to_dict(rules=('activities',)), 200)

@app.route('/activities', methods=['GET'])
def get_activities():
    activities = Activity.query.all()
    return make_response([activity.to_dict() for activity in activities], 200)

@app.route('/activities/<int:id>', methods=['DELETE'])
def delete_activity_by_id(id):
    activity = Activity.query.filter_by(id=id).first()
    if not activity:
        return make_response({"error": "Activity not found"}, 404)
    elif request.method == 'DELETE':
        signups = Signup.query.all()
        for signup in signups:
            if signup.activity_id == id:
                db.session.delete(signup)
                db.session.commit()
        db.session.delete(activity)
        db.session.commit()

        return make_response({"activity successfully delete"}, 200)

@app.route('/signups', methods=['POST'])
def post_signups():
    try:
        new_signup = Signup(
            time = request.get_json()['time'],
            camper_id = request.get_json()['camper_id'],
            activity_id = request.get_json()['activity_id']
        )
        db.session.add(new_signup)
        db.session.commit()

        activity = Activity.query.filter_by(id=new_signup.activity.id).first()
        return make_response(activity.to_dict(), 200)
    except ValueError:
        return make_response({"errors": ["validation errors"]}, 404)


if __name__ == '__main__':
    app.run(port=5555, debug=True)
