from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_pymongo import PyMongo
from datetime import datetime
from bson.objectid import ObjectId
from datetime import timedelta



app = Flask(__name__, template_folder='application/templates')
app.secret_key = 'your_secret_key'
app.config["MONGO_URI"] = "mongodb://localhost:27017/lifehub"  
mongo = PyMongo(app)
habits_collection = mongo.db.habits

@app.route('/')
def home():
    return redirect(url_for('registration'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        user = mongo.db.users.find_one({'email': email, 'password': password})

        if user:
            session['user_id'] = str(user['_id'])
            session['first_name'] = user['first_name']
            session['last_name'] = user['last_name']
            flash(f"Welcome back, {user['first_name']}!", 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')
        

    return render_template('login.html')


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    if request.method == 'POST':
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if mongo.db.users.find_one({'username': username}):
            flash('Username already exists!', 'danger')
        elif mongo.db.users.find_one({'email': email}):
            flash('Email already exists!', 'danger')
        else:
            mongo.db.users.insert_one({
                'first_name': first_name,
                'last_name': last_name,
                'username': username,
                'email': email,
                'password': password,
                'date_registered': datetime.utcnow()
            })
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))

    return render_template('registration.html')


@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        if mongo.db.users.find_one({'email': email}):
            flash(f"A password reset link has been sent to {email}.", 'info')
        else:
            flash("Email not found in our records.", 'danger')

    return render_template('forgot_password.html')


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for('login'))

    user = {
        "first_name": session.get('first_name', 'Guest'),  # Use `get` to avoid KeyError
        "last_name": session.get('last_name', '')
    }
    return render_template('dashboard.html', user=user)

@app.route('/budget_management', methods=['GET', 'POST'])
def budget_management():
    if request.method == 'POST':
        try:
            income = float(request.form['income'])
            expense = float(request.form['expense'])
            category = request.form['category']

            if income < 0 or expense < 0:
                flash('Income and expense values must be non-negative.', 'danger')
            else:
             
                mongo.db.budget.insert_one({
                    'income': income,
                    'expense': expense,
                    'category': category,
                    'date_added': datetime.utcnow()
                })
                flash('Entry added successfully!', 'success')
        except ValueError:
            flash('Invalid data entered. Please ensure income and expense are numbers.', 'danger')

    budget_data = list(mongo.db.budget.find())
    total_income = sum(item['income'] for item in budget_data)
    total_expenses = sum(item['expense'] for item in budget_data)
    balance = total_income - total_expenses

    return render_template(
        'budget_management.html',
        budget_data=budget_data,
        total_income=total_income,
        total_expenses=total_expenses,
        balance=balance
    )


@app.route('/financial_goals', methods=['GET', 'POST'])
def financial_goals():
    if request.method == 'POST':
        goal_name = request.form['goal_name']
        goal_amount = request.form['goal_amount']
        goal_date = request.form['goal_date']

       
        if not goal_name or not goal_amount or not goal_date:
            flash('All fields are required!', 'danger')
        else:
            try:
                goal_amount = float(goal_amount)
                if goal_amount <= 0:
                    flash('Goal amount must be positive.', 'danger')
                else:
                   
                    mongo.db.goals.insert_one({
                        'goal_name': goal_name,
                        'goal_amount': goal_amount,
                        'goal_date': goal_date,
                        'progress': 0,
                        'date_added': datetime.utcnow()
                    })
                    flash('Financial goal added successfully!', 'success')
            except ValueError:
                flash('Invalid goal amount. Please enter a valid number.', 'danger')

    goals = list(mongo.db.goals.find())
    return render_template('financial_goals.html', goals=goals)



@app.route('/add_todo', methods=['GET', 'POST'])
def add_todo():
    if 'user_id' not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        completed = request.form['completed']
        due_date = request.form['due_date']
        priority = request.form['priority']

        if not name or not description:
            flash('Task name and description are required!', 'danger')
        else:
            mongo.db.todos.insert_one({
                'user_id': session['user_id'],
                'name': name,
                'description': description,
                'completed': completed,
                'due_date': due_date,
                'priority': priority,
                'date_created': datetime.utcnow()
            })
            flash('To-Do item added successfully!', 'success')
            return redirect(url_for('dashboard'))

    return render_template('add_todo.html')

@app.route('/view_todos')
def view_todos():
    if 'user_id' not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for('login'))
    
    todos = list(mongo.db.todos.find({'user_id': session['user_id']}))
    return render_template('view_todos.html', todos=todos)

@app.route('/delete_todo/<id>', methods=['POST', 'GET'])
def delete_todo(id):
    if 'user_id' not in session:
        flash("Please log in first.", "danger")
        return redirect(url_for('login'))

  
    mongo.db.todos.delete_one({'_id': ObjectId(id)})
    flash("Task deleted successfully!", "success")
    return redirect(url_for('view_todos'))
    
    

def test_logout(self):
    with self.app.session_transaction() as session:
        session['user_id'] = self.test_user_id

    response = self.app.get('/logout', follow_redirects=True)
    self.assertEqual(response.status_code, 200)
    self.assertIn(b'You have been logged out.', response.data)


def load_habits():
    return list(habits_collection.find())



def save_habit(habit):
    habits_collection.insert_one(habit)



def update_habit_in_db(habit_id, updated_fields):
    try:
        habits_collection.update_one({"_id": ObjectId(habit_id)}, {"$set": updated_fields})
    except Exception as e:
        print(f"Error updating habit: {e}")



def remove_habit_from_db(habit_id):
    habits_collection.delete_one({"_id": ObjectId(habit_id)})

@app.route("/")
def index():
    habits = load_habits()
    now = datetime.now()
    for habit in habits:
        if "last_updated" not in habit or habit["last_updated"] is None:
            habit["last_updated"] = None
        else:
            last_updated = datetime.fromisoformat(habit["last_updated"])
            if habit["frequency"] == "daily" and now - last_updated >= timedelta(days=1):
                habit["streak"] = 0
            elif habit["frequency"] == "weekly" and now - last_updated >= timedelta(weeks=1):
                habit["streak"] = 0
            update_habit_in_db(habit["_id"], {"streak": habit["streak"]})
    return render_template("index.html", habits=habits)

@app.route("/add_habit", methods=["GET", "POST"])
def add_habit():
    if request.method == "POST":
        habit_name = request.form.get("habit_name")
        frequency = request.form.get("frequency")

        if not habit_name or not frequency:
            error = "Please fill out all fields."
            return render_template("add_habit.html", error=error)

        habit = {"name": habit_name, "frequency": frequency, "streak": 0, "last_updated": None}
        save_habit(habit)
        return redirect(url_for("index"))

    return render_template("add_habit.html")

@app.route("/increase_streak", methods=["POST"])
def increase_streak():
    habit_id = request.form.get("habit_id")
    if not habit_id:
        return redirect(url_for("index"))

    try:
        habit = habits_collection.find_one({"_id": ObjectId(habit_id)})
    except Exception as e:
        print(f"Error fetching habit: {e}")
        return redirect(url_for("index"))

    if not habit:
        print("Habit not found")
        return redirect(url_for("index"))

    now = datetime.now()
    if habit["last_updated"]:
        last_updated = datetime.fromisoformat(habit["last_updated"])
        if habit["frequency"] == "daily" and now - last_updated < timedelta(days=1):
            return redirect(url_for("index"))
        if habit["frequency"] == "weekly" and now - last_updated < timedelta(weeks=1):
            return redirect(url_for("index"))

    habit["streak"] += 1
    habit["last_updated"] = now.isoformat()
    update_habit_in_db(habit["_id"], {"streak": habit["streak"], "last_updated": habit["last_updated"]})
    return redirect(url_for("index"))

@app.route("/remove_habit", methods=["POST"])
def remove_habit():
    habit_id = request.form.get("habit_id")
    if not habit_id:
        return redirect(url_for("index"))

    try:
        remove_habit_from_db(habit_id)
    except Exception as e:
        print(f"Error deleting habit: {e}")
    return redirect(url_for("index"))

@app.route("/update_habit", methods=["GET", "POST"])
def update_habit():
    habit_id = request.args.get("habit_id")
    if not habit_id:
        print("No habit_id provided")
        return redirect(url_for("index"))

    try:
        habit = habits_collection.find_one({"_id": ObjectId(habit_id)})
    except Exception as e:
        print(f"Error fetching habit: {e}")
        return redirect(url_for("index"))

    if not habit:
        print("Habit not found")
        return redirect(url_for("index"))

    if request.method == "POST":
        habit_name = request.form.get("habit_name")
        frequency = request.form.get("frequency")

        if not habit_name or not frequency:
            error = "Please fill out all fields."
            return render_template("update_habit.html", habit=habit, error=error)

        updated_fields = {"name": habit_name, "frequency": frequency}
        update_habit_in_db(habit_id, updated_fields)
        return redirect(url_for("index"))

    return render_template("update_habit.html", habit=habit)





if __name__ == '__main__':
    app.run(debug=True)
