from flask_wtf import FlaskForm
from wtforms import FileField, StringField, SelectField, SubmitField
from wtforms.validators import DataRequired

class StudentRegistrationForm(FlaskForm):
    admission_number = StringField("Admission Number", validators=[DataRequired()])
    fullname = StringField("Full Name", validators=[DataRequired()])
    department = SelectField("Department", coerce=int, validators=[DataRequired()])
    course = SelectField("Course", coerce=int, validators=[DataRequired()])
    level = SelectField("Level", choices=['Level 3', 'Level 4', 'Level 5', 'Level 6'], default='Level 4', validators=[DataRequired()])
    classroom = StringField("Classroom Name", validators=[DataRequired()])
    profile_image = FileField("Profile Image")  # Add the FileField for image upload
    submit = SubmitField("Register")

class StudentLoginForm(FlaskForm):
    admission_number = StringField("Admission Number", validators=[DataRequired()]) 
    submit = SubmitField("Login")

class UnitForm(FlaskForm):
    unit_name = StringField("Unit Name", validators=[DataRequired()])
    submit = SubmitField("Add Unit")

class AddCourseForm(FlaskForm):
    department = SelectField("Department", coerce=int, validators=[DataRequired()])
    coursename = StringField("Course Name", validators=[DataRequired()])
    submit = SubmitField("Add Course")