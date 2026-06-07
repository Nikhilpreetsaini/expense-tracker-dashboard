import os
from flask import Flask, render_template, redirect, url_for, flash, request, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import csv
import io


def create_app(test_config=None):
    """
    Application factory for the expense tracker. This allows the app to be
    configured differently for testing or production environments.
    """
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'very_secret_key')
    # Database configuration: Use SQLite by default. Render provides a postgres
    # database automatically in production, but SQLite is fine for demonstration.
    base_dir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(base_dir, 'expenses.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    @app.before_first_request
    def create_tables():
        db.create_all()

    # Routes
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return redirect(url_for('login'))

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            existing = User.query.filter_by(username=username).first()
            if existing:
                flash('Username already exists. Please log in.', 'warning')
                return redirect(url_for('login'))
            hashed = generate_password_hash(password)
            new_user = User(username=username, password=hashed)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login'))
        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        if request.method == 'POST':
            username = request.form.get('username')
            password = request.form.get('password')
            user = User.query.filter_by(username=username).first()
            if user and check_password_hash(user.password, password):
                login_user(user)
                return redirect(url_for('dashboard'))
            else:
                flash('Invalid username or password.', 'danger')
        return render_template('login.html')

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()
        return redirect(url_for('login'))

    @app.route('/dashboard')
    @login_required
    def dashboard():
        # Gather expense data for the current user
        expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).all()
        total = sum(exp.amount for exp in expenses)
        # Prepare data for charts
        categories = {}
        monthly = {}
        for exp in expenses:
            # Category totals
            categories[exp.category] = categories.get(exp.category, 0) + exp.amount
            # Monthly totals (YYYY-MM)
            month_str = exp.date.strftime('%Y-%m')
            monthly[month_str] = monthly.get(month_str, 0) + exp.amount
        # Sort monthly data by date
        monthly_sorted = dict(sorted(monthly.items()))
        return render_template('dashboard.html', expenses=expenses, total=total,
                               categories=categories, monthly=monthly_sorted)

    @app.route('/add', methods=['GET', 'POST'])
    @login_required
    def add_expense():
        """Create a new expense record for the logged-in user."""
        if request.method == 'POST':
            # Parse form data
            try:
                amount = float(request.form.get('amount'))
            except (TypeError, ValueError):
                flash('Please enter a valid amount.', 'danger')
                # Provide the current date back to the template to preserve state
                return render_template('add_expense.html', current_date=datetime.now().strftime('%Y-%m-%d'))
            category = request.form.get('category')
            description = request.form.get('description')
            date_str = request.form.get('date')
            # Convert date string to datetime object
            date = datetime.strptime(date_str, '%Y-%m-%d') if date_str else datetime.now()
            # Create and save the expense
            new_exp = Expense(amount=amount, category=category, description=description,
                              date=date, user_id=current_user.id)
            db.session.add(new_exp)
            db.session.commit()
            flash('Expense added successfully.', 'success')
            return redirect(url_for('dashboard'))
        # GET request: show form with today's date as default
        return render_template('add_expense.html', current_date=datetime.now().strftime('%Y-%m-%d'))

    @app.route('/delete/<int:expense_id>', methods=['POST'])
    @login_required
    def delete_expense(expense_id):
        exp = Expense.query.get_or_404(expense_id)
        if exp.user_id != current_user.id:
            flash('You are not authorized to delete this expense.', 'danger')
            return redirect(url_for('dashboard'))
        db.session.delete(exp)
        db.session.commit()
        flash('Expense deleted.', 'info')
        return redirect(url_for('dashboard'))

    @app.route('/export', methods=['GET'])
    @login_required
    def export_csv():
        # Export user's expenses to CSV
        expenses = Expense.query.filter_by(user_id=current_user.id).all()
        proxy = io.StringIO()
        writer = csv.writer(proxy)
        writer.writerow(['Date', 'Category', 'Description', 'Amount'])
        for exp in expenses:
            writer.writerow([exp.date.strftime('%Y-%m-%d'), exp.category, exp.description, f"{exp.amount:.2f}"])
        mem = io.BytesIO()
        mem.write(proxy.getvalue().encode('utf-8'))
        mem.seek(0)
        proxy.close()
        return send_file(mem, mimetype='text/csv', as_attachment=True, attachment_filename='expenses.csv')

    return app


db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'login'


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    expenses = db.relationship('Expense', backref='user', lazy=True)


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


if __name__ == '__main__':
    app = create_app()
    port = int(os.environ.get('PORT', 5000))
    # Running with flask's built-in server for local testing; Render will run using gunicorn.
    app.run(debug=True, host='0.0.0.0', port=port)