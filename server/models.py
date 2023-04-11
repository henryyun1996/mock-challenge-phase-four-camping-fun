from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy

db = SQLAlchemy()


class Camper(db.Model, SerializerMixin):
    __tablename__ = 'campers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    age = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    signups = db.relationship('Signup', backref='camper')
    activities = association_proxy('signups', 'activity')
    serialize_rules = ('-created_at', '-updated_at', '-signups', '-activities.created_at', '-activities.updated_at', '-activities.campers')

    @validates('name')
    def validates_name(self, key, name):
        if not name:
            raise ValueError('Camper must have a name')
        return name
    
    @validates('age')
    def validates_age(self, key, age):
        if 8 <= age <= 18:
            return age
        else:
            raise ValueError('Age must be between 8 and 18')

    def __repr__(self):
        return f'<Camper: {self.name} />'


class Activity(db.Model, SerializerMixin):
    __tablename__ = 'activities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    difficulty = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    signups = db.relationship('Signup', backref='activity')
    campers = association_proxy('signups', 'camper')
    serialize_rules = ('-signups',
                        '-campers.activities', '-created_at', '-updated_at')
    def __repr__(self):
        return f'<Activity: {self.name} />'


class Signup(db.Model, SerializerMixin):
    __tablename__ = 'signups'

    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, onupdate=db.func.now())

    camper_id = db.Column(db.Integer, db.ForeignKey('campers.id'))
    activity_id = db.Column(db.Integer, db.ForeignKey('activities.id'))

    @validates('time')
    def validates_time(self, key, time):
        if not 0 <= time <= 23:
            raise ValueError("Time must be between 0 and 23")
        return time
