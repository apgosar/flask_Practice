from flask import Flask, render_template, request, redirect, url_for
from bson.objectid import ObjectId
from dotenv import load_dotenv
import certifi
import os
from pymongo import MongoClient

# Load env vars
load_dotenv()

app = Flask(__name__)
mongo_uri = os.getenv("MONGO_URI")
if not mongo_uri:
    raise RuntimeError(
        "MONGO_URI is not configured. Check your .env file and working directory."
    )
app.config["MONGO_URI"] = mongo_uri
mongo_dbname = os.getenv("MONGO_DBNAME")
if not mongo_dbname:
    raise RuntimeError(
        "MONGO_DBNAME is not configured. Set it in .env or include a database name in MONGO_URI."
    )
app.config["MONGO_DBNAME"] = mongo_dbname
app.secret_key = os.getenv("SECRET_KEY")

use_mock_mongo = os.getenv("USE_MOCK_MONGO") == "1"

# Use certifi CA bundle explicitly for cross-platform TLS reliability
# (notably fixes common macOS certificate verification failures).
try:
    if use_mock_mongo:
        import mongomock
        client = mongomock.MongoClient()
    else:
        client = MongoClient(mongo_uri, tlsCAFile=certifi.where(), serverSelectionTimeoutMS=5000)
    db = client[mongo_dbname]
    if not use_mock_mongo:
        db.command("ping")
except Exception as e:
    raise RuntimeError(
        "Unable to connect to MongoDB. Verify MONGO_URI, MONGO_DBNAME, and network connectivity. "
        f"Original error: {e}"
    )

# Home page -> list students
@app.route('/')
def index():
    students = db.students.find()
    return render_template('index.html', students=students)

# Add student
@app.route('/add', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        course = request.form['course']
        db.students.insert_one({
            "name": name,
            "email": email,
            "course": course
        })
        return redirect(url_for('index'))
    return render_template('add_student.html')

# Update student
@app.route('/update/<student_id>', methods=['GET', 'POST'])
def update_student(student_id):
    student = db.students.find_one({"_id": ObjectId(student_id)})
    if request.method == 'POST':
        new_name = request.form['name']
        new_email = request.form['email']
        new_course = request.form['course']
        db.students.update_one(
            {"_id": ObjectId(student_id)},
            {"$set": {"name": new_name, "email": new_email, "course": new_course}}
        )
        return redirect(url_for('index'))
    return render_template('update_student.html', student=student)


# Delete student
@app.route('/delete/<student_id>')
def delete_student(student_id):
    db.students.delete_one({"_id": ObjectId(student_id)})
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True, port=5000)


