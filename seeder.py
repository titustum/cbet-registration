from models import db, Department, Course

def seed_data(app):
    with app.app_context():
        db.drop_all()
        db.create_all()

        # Sample departments
        departments = ['ICT', 'Cosmetology', 'Electrical', 'Hospitality', 
                       'Agriculture', 'Fashion', 'Mechanical', 'Building'
                       ]
        courses = {
            'ICT': ['ICT Technician', 'Cybersecurity'],
            'Cosmetology': [],
            'Electrical': ['Power Systems', 'Control Systems'],
            'Hospitality': [], 
            'Agriculture': [], 
            'Fashion': [], 
            'Mechanical': [], 
            'Building': [], 
        }

        for dept_name in departments:
            dept = Department(name=dept_name)
            db.session.add(dept)
            db.session.flush()  # Get dept.id before commit

            for course_name in courses[dept_name]:
                course = Course(name=course_name, department_id=dept.id)
                db.session.add(course)

        db.session.commit()
        print("Database seeded successfully.")
