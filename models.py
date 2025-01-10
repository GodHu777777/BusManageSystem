from app import db
from datetime import datetime

class Fleet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    captain_id = db.Column(db.Integer, db.ForeignKey('driver.id'), nullable=False)
    routes = db.relationship('Route', backref='fleet', lazy=True)

class Route(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    fleet_id = db.Column(db.Integer, db.ForeignKey('fleet.id'), nullable=False)
    route_captain_id = db.Column(db.Integer, db.ForeignKey('driver.id'), nullable=False)
    vehicles = db.relationship('Vehicle', backref='route', lazy=True)
    drivers = db.relationship('Driver', backref='route', lazy=True)

class Driver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_number = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    is_captain = db.Column(db.Boolean, default=False)
    is_route_captain = db.Column(db.Boolean, default=False)
    route_id = db.Column(db.Integer, db.ForeignKey('route.id'))

    def __repr__(self):
        return f"<Driver {self.name}>"

class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plate_number = db.Column(db.String(20), unique=True, nullable=False)
    seats = db.Column(db.Integer, nullable=False)
    route_id = db.Column(db.Integer, db.ForeignKey('route.id'), nullable=False)

class Violation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable=False)
    violation_type = db.Column(db.String(100), nullable=False)
    time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    location = db.Column(db.String(200))
    
    driver = db.relationship('Driver', backref='violations')
    vehicle = db.relationship('Vehicle', backref='violations')

    __table_args__ = (
        db.CheckConstraint(
            violation_type.in_(['闯红灯', '未礼让斑马线', '压线', '违章停车']),
            name='check_violation_type'
        ),
    )
