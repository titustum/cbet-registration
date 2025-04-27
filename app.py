from functools import wraps
from flask import Flask, flash, jsonify, render_template, redirect, url_for, request, session
from models import db, Department, Course, Student, UnitRegistration
from forms import AddCourseForm, StudentRegistrationForm, UnitForm, StudentLoginForm
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cbet.db'
db.init_app(app)


app.config['UPLOAD_FOLDER'] = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'student_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
 

@app.route('/', methods=['GET', 'POST'])
def register():
    form = StudentRegistrationForm()
    # Always populate departments
    form.department.choices = [(0, '-- Select Department --')] + [(d.id, d.name) for d in Department.query.order_by('name').all()]

    # Pre-populate courses if a department is already selected (useful for form validation failures)
    if form.department.data:
        form.course.choices = [(c.id, c.name) for c in Course.query.filter_by(department_id=form.department.data).order_by('name').all()]
    else:
        form.course.choices = [(0, '-- Select Course --')]

    if form.validate_on_submit():
        admission_number = form.admission_number.data
        fullname = form.fullname.data
        department_id = form.department.data
        course_id = form.course.data
        level = form.level.data
        classroom = form.classroom.data
        profile_image = form.profile_image.data  # Get the uploaded file

        filename = None
        if profile_image and allowed_file(profile_image.filename):
            filename = secure_filename(profile_image.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            try:
                profile_image.save(filepath)
                image_path_in_db = f"uploads/{filename}" 
            except Exception as e:
                flash(f'Error saving profile image: {e}', 'error')
                image_path_in_db = None
        else:
            image_path_in_db = None

        student = Student(
            admission_number=admission_number,
            fullname=fullname,
            department_id=department_id,
            course_id=course_id,
            classroom=classroom,
            level=level,
            profile_image=image_path_in_db  # Save the image path in the student object
        )
        db.session.add(student)
        try:
            db.session.commit()
            session['student_id'] = student.id
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error registering student: {e}', 'error')

    return render_template('register.html', form=form)


@app.route('/get_courses/<int:department_id>')
def get_courses(department_id):
    courses = Course.query.filter_by(department_id=department_id).all()
    course_list = [{'id': c.id, 'name': c.name} for c in courses]
    return jsonify(course_list)



    

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = StudentLoginForm()
    if form.validate_on_submit():
        student = Student.query.filter_by(admission_number=form.admission_number.data).first()
        if student:
            session['student_id'] = student.id
            return redirect(url_for('dashboard'))
        else:
            flash('No student with that admission number', 'error')
            return redirect(url_for('login'))
    return render_template('login.html', form=form)

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    student = Student.query.get(session.get('student_id'))
    new_units = UnitRegistration.query.filter_by(student_id=student.id, is_reassessment=False).all()
    reassessments = UnitRegistration.query.filter_by(student_id=student.id, is_reassessment=True).all()
    return render_template('dashboard.html', student=student, new_units=new_units, reassessments=reassessments)

@app.route('/add_unit', methods=['POST'])
@login_required
def add_unit():
    unit_name = request.form['unit_name']
    is_reassessment = request.form['is_reassessment'] == 'true'
    student_id = session.get('student_id')
    unit = UnitRegistration(unit_name=unit_name, is_reassessment=is_reassessment, student_id=student_id)
    db.session.add(unit)
    db.session.commit()
    flash("Unit added successfully.", "success")
    return redirect(url_for('dashboard'))


@app.route('/remove_unit/<int:unit_id>', methods=['POST'])
@login_required
def remove_unit(unit_id):
    unit = UnitRegistration.query.get_or_404(unit_id)
    db.session.delete(unit)
    db.session.commit()
    flash("Unit removed successfully.", "success")
    return redirect(url_for('dashboard'))  # Replace 'dashboard' with your actual dashboard route function name

@app.route('/logout')
def logout():
    session.pop('student_id', None)  # Remove the student_id from the session
    flash('Logged out successfully!', 'info')
    return redirect(url_for('login'))  # Redirect to your login page



# @app.route('/students')
# def students_list():
#     students = Student.query.all()
#     return render_template('students_list.html', students=students)

@app.route('/students')
def students_list():
    students = Student.query.order_by(
        Student.department_id,
        Student.course_id,
        Student.level,
        Student.classroom,
        Student.admission_number
    ).all()
    return render_template('students_list.html', students=students)

@app.route('/students/<int:student_id>')
def student_details(student_id):
    student = Student.query.get_or_404(student_id)
    new_units = UnitRegistration.query.filter_by(student_id=student_id, is_reassessment=False).all()
    reassessments = UnitRegistration.query.filter_by(student_id=student_id, is_reassessment=True).all()
    return render_template('student_details.html', student=student, new_units=new_units, reassessments=reassessments)


@app.route('/add_course', methods=['GET', 'POST'])
def add_course():
    form = AddCourseForm()
    form.department.choices = [(d.id, d.name) for d in Department.query.all()]

    if form.validate_on_submit():
        department_id = form.department.data
        course_name = form.coursename.data

        # Check if the course already exists for this department (optional)
        existing_course = Course.query.filter_by(name=course_name, department_id=department_id).first()
        if existing_course:
            flash(f'Course "{course_name}" already exists in this department.', 'warning')
            return render_template('add_course.html', form=form)

        new_course = Course(name=course_name, department_id=department_id)
        db.session.add(new_course)
        try:
            db.session.commit()
            flash(f'Course "{course_name}" added successfully to {form.department.label.text}.', 'success')
            return redirect(url_for('add_course'))  # Redirect to clear the form
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding course: {e}', 'error')

    return render_template('add_course.html', form=form)



@app.route('/admin/dashboard')
def admin_dashboard():
    total_students = Student.query.count()
    total_departments = Department.query.count()
    total_courses = Course.query.count()

    # You can fetch more detailed statistics if needed
    # For example, students per department:
    students_by_department = db.session.query(Department.name, db.func.count(Student.id)).\
        join(Student, Student.department_id == Department.id).\
        group_by(Department.name).\
        all()

    # Or courses per department:
    courses_by_department = db.session.query(Department.name, db.func.count(Course.id)).\
        join(Course, Course.department_id == Department.id).\
        group_by(Department.name).\
        all()

    return render_template(
        'admin_dashboard.html',
        total_students=total_students,
        total_departments=total_departments,
        total_courses=total_courses,
        students_by_department=students_by_department,
        courses_by_department=courses_by_department
    )

from seeder import seed_data
@app.route('/initDB')
def init_db():
    seed_data(app)
    return "Database initialized and seeded."
