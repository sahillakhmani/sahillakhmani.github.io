from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, login_required, logout_user, LoginManager, current_user

# Initialize app
app = Flask(__name__)

# Secret key for session management
app.config['SECRET_KEY'] = 'your-secret-key'

# Configure database (use SQLite for simplicity)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database and login manager
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Create a User model (with tokens field and role field)
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    tokens = db.Column(db.Integer, default=0)
    role = db.Column(db.String(50), default='user')  # Add a role field to indicate user type

    def is_admin(self):
        return self.role == 'admin'  # Method to check if the user is an admin

# Initialize the database
with app.app_context():
    db.create_all()
    
    # Check if the default admin user exists
    admin_user = User.query.filter_by(username='sahil').first()
    if not admin_user:
        # Create the default admin user
        default_admin = User(username='sahil', password='123', role='admin')
        db.session.add(default_admin)
        db.session.commit()
        print("Default admin 'Sahil' created successfully.")

# Login manager function
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Home route (redirect to login if not logged in)
@app.route('/')
@login_required
def home():
    if current_user.role == 'admin':
        return render_template('home.html', admin=True)  # Pass 'admin' as True to the template
    return render_template('home.html', admin=False)  # Pass 'admin' as False


# Signup route (user registration)
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists!', 'error')
            return redirect(url_for('signup'))

        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()

        flash('User created successfully! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

# Login route (user authentication)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and user.password == password:
            login_user(user)
            return redirect(url_for('home'))
        
        flash('Invalid login credentials. Contact Agastya or Arjun in case of forgotten password', 'error')

    return render_template('login.html')

# Token purchase route (add tokens to user account)
@app.route('/buy_tokens', methods=['POST'])
@login_required
def buy_tokens():
    tokens = request.form['tokens']
    current_user.tokens += int(tokens)  # Add tokens to current user's balance
    db.session.commit()
    flash(f'You have successfully bought {tokens} tokens!', 'success')
    return redirect(url_for('home'))

# Route to check token balance
@app.route('/check_balance')
@login_required
def check_balance():
    return render_template('balance.html', balance=current_user.tokens)

# Logout route (logout user)
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

# Users route (admin-only access to see the list of all users)
@app.route('/users')
@login_required
def users():
    if not current_user.is_admin():  # Check if the current user is an admin
        flash('You do not have access to this page!', 'error')
        return redirect(url_for('home'))  # Redirect to the home page if not an admin

    all_users = User.query.all()  # Query all users
    return render_template('users.html', users=all_users)

# Admin Dashboard route
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.role == 'admin':
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('home'))

    # Get all users from the database
    users = User.query.all()

    # Debugging: Print users to console
    print(users)

    return render_template('admin_dashboard.html', users=users)


from werkzeug.security import generate_password_hash

@app.route('/admin/update_user/<int:user_id>', methods=['GET', 'POST'])
@login_required
def update_user(user_id):
    if not current_user.role == 'admin':
        flash('You do not have permission to access this page.', 'error')
        return redirect(url_for('home'))

    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        # Handle the updated tokens
        new_token_balance = request.form['tokens']
        user.tokens = new_token_balance

        # Handle password change
        if request.form.get('password'):
            new_password = request.form['password']
            user.password = generate_password_hash(new_password)

        # Handle email or username change (if needed)
        if request.form.get('email'):
            user.email = request.form['email']
        
        db.session.commit()
        flash(f'User details for {user.username} updated successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('update_user.html', user=user)


if __name__ == '__main__':
    app.run(debug=True)
