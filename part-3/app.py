from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import joinedload
import os

app = Flask(__name__)
app.secret_key = "secret-key"

# ================= DATABASE CONFIG (FIXED) =================
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = (
    'sqlite:///' + os.path.join(BASE_DIR, 'school.db')
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ================= MODELS =================

# -------- Exercise 1: Teacher Model --------
class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    courses = db.relationship('Course', backref='teacher', lazy=True)

    def __repr__(self):
        return f"<Teacher {self.name}>"


class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)

    students = db.relationship('Student', backref='course', lazy=True)

    def __repr__(self):
        return f"<Course {self.name}>"


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

    def __repr__(self):
        return f"<Student {self.name}>"

# ================= ROUTES =================

# -------- Exercise 2: order_by() --------
@app.route('/')
def index():
    students = Student.query.options(
        joinedload(Student.course)
    ).order_by(Student.name.asc()).all()
    return render_template('index.html', students=students)


# -------- filter() --------
@app.route('/courses')
def courses():
    courses = Course.query.options(
        joinedload(Course.students)
    ).all()
    return render_template('courses.html', courses=courses)


# -------- limit() --------
@app.route('/top-students')
def top_students():
    students = Student.query.limit(3).all()
    return render_template('index.html', students=students)


@app.route('/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        student = Student(
            name=request.form['name'],
            email=request.form['email'],
            course_id=request.form['course_id']
        )
        db.session.add(student)
        db.session.commit()
        flash('Student added successfully!', 'success')
        return redirect(url_for('index'))

    courses = Course.query.all()
    return render_template('add.html', courses=courses)


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    student = Student.query.get_or_404(id)

    if request.method == 'POST':
        student.name = request.form['name']
        student.email = request.form['email']
        student.course_id = request.form['course_id']
        db.session.commit()
        flash('Student updated!', 'success')
        return redirect(url_for('index'))

    courses = Course.query.all()
    return render_template('edit.html', student=student, courses=courses)


@app.route('/delete/<int:id>')
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    flash('Student deleted!', 'danger')
    return redirect(url_for('index'))


@app.route('/add-course', methods=['GET', 'POST'])
def add_course():
    if request.method == 'POST':
        course = Course(
            name=request.form['name'],
            description=request.form.get('description', ''),
            teacher_id=request.form['teacher_id']
        )
        db.session.add(course)
        db.session.commit()
        flash('Course added!', 'success')
        return redirect(url_for('courses'))

    teachers = Teacher.query.all()
    return render_template('add_course.html', teachers=teachers)

# ================= INIT DATABASE =================

def init_db():
    with app.app_context():
        db.create_all()

        if Teacher.query.count() == 0:
            t1 = Teacher(name='Dr. Sharma', email='sharma@gmail.com')
            t2 = Teacher(name='Prof. Mehta', email='mehta@gmail.com')
            db.session.add_all([t1, t2])
            db.session.commit()

        if Course.query.count() == 0:
            c1 = Course(name='Python Basics', description='Intro to Python', teacher_id=1)
            c2 = Course(name='Web Development', description='Flask & HTML', teacher_id=2)
            db.session.add_all([c1, c2])
            db.session.commit()


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
