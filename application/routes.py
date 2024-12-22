from application import app, db
from flask import render_template, request, redirect, url_for, flash, session
from bson import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from .forms import TodoForm


@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = db.users.find_one({'username': username})

        if user and check_password_hash(user['password'], password):
            session['user_id'] = str(user['_id'])  
            return redirect(url_for('add_todo'))  
        else:
            flash('Invalid username or password', 'danger')

    return render_template('login.html')

@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        if db.users.find_one({'username': username}):
            flash('Username already exists!', 'danger')
        else:
            db.users.insert_one({'username': username, 'email': email, 'password': hashed_password})
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))

    return render_template('registration.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route("/add_todo", methods=['POST', 'GET'])
def add_todo():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    form = TodoForm()
    if request.method == 'POST' and form.validate():
        todo_name = form.name.data
        todo_description = form.description.data
        completed = form.completed.data

        db.todos_flask.insert_one({
            "name": todo_name,
            "description": todo_description,
            "completed": completed,
            "date_created": datetime.utcnow(),
            "user_id": session['user_id']  
        })
        flash("To-Do successfully added", "success")
        return redirect(url_for('get_todos'))

    return render_template("add_todo.html", form=form)

@app.route("/get_todos")
def get_todos():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    todos = []
    for todo in db.todos_flask.find({"user_id": session['user_id']}).sort("date_created", -1):
        todo["_id"] = str(todo["_id"])
        todo["date_created"] = todo["date_created"].strftime("%b %d %Y %H:%M:%S")
        todos.append(todo)

    return render_template("view_todos.html", todos=todos)

@app.route("/delete_todo/<id>")
def delete_todo(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    db.todos_flask.find_one_and_delete({"_id": ObjectId(id), "user_id": session['user_id']})
    flash("To-Do successfully deleted", "success")
    return redirect(url_for('get_todos'))

@app.route("/update_todo/<id>", methods=['POST', 'GET'])
def update_todo(id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    todo = db.todos_flask.find_one({"_id": ObjectId(id), "user_id": session['user_id']})
    if not todo:
        flash("To-Do not found", "danger")
        return redirect(url_for('get_todos'))

    form = TodoForm()
    if request.method == 'POST' and form.validate():
        db.todos_flask.find_one_and_update({"_id": ObjectId(id)}, {
            "$set": {
                "name": form.name.data,
                "description": form.description.data,
                "completed": form.completed.data,
                "date_created": datetime.utcnow()
            }
        })
        flash("To-Do successfully updated", "success")
        return redirect(url_for('get_todos'))

    form.name.data = todo.get("name")
    form.description.data = todo.get("description")
    form.completed.data = todo.get("completed")
    return render_template("add_todo.html", form=form)
