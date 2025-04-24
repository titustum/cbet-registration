from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Department(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    courses = db.relationship('Course', backref='department', lazy=True)
    students = db.relationship('Student', backref='department', lazy=True)

class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'), nullable=False)
    students = db.relationship('Student', backref='course', lazy=True)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admission_number = db.Column(db.String(20), unique=True)
    fullname = db.Column(db.String(100))
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    classroom = db.Column(db.String(50))
    level = db.Column(db.String(50))
    profile_image = db.Column(db.String(250), nullable=True)

class UnitRegistration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    unit_name = db.Column(db.String(100))
    is_reassessment = db.Column(db.Boolean, default=False)
