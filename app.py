import json
from functools import wraps
from pathlib import Path

from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from cloud_data import (
    aggregate_costs,
    filter_rows_by_team,
    get_budget_alerts,
    get_optimization_recommendations,
    get_provider_percentages,
    load_mock_cost_data,
    load_users,
    monthly_costs,
    parse_csv_rows,
    save_users,
    TEAMS,
)

app = Flask(__name__)
app.secret_key = 'finops-demo-secret-key'

DATA_DIR = Path(__file__).resolve().parent / 'data'
USER_FILE = DATA_DIR / 'users.json'


def get_current_user():
    username = session.get('username')
    if not username:
        return None

    users = load_users(USER_FILE)
    return users.get(username)


def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if get_current_user() is None:
            flash('Please log in to view your team dashboard.', 'error')
            return redirect(url_for('login'))
        return view(**kwargs)

    return wrapped_view


def render_dashboard(rows, title, team_name=None):
    summary = aggregate_costs(rows)
    recommendations = get_optimization_recommendations(rows)
    alerts = get_budget_alerts(rows)
    monthly_labels, monthly_values = monthly_costs(rows)
    provider_labels, provider_values = get_provider_percentages(rows)
    current_user = get_current_user()

    return render_template(
        'dashboard.html',
        page_title=title,
        total_cost=summary['total_cost'],
        cost_by_provider=summary['cost_by_provider'],
        cost_by_project=summary['cost_by_project'],
        top_resources=summary['top_resources'],
        recommendations=recommendations,
        alerts=alerts,
        monthly_labels=monthly_labels,
        monthly_values=monthly_values,
        provider_labels=provider_labels,
        provider_values=provider_values,
        current_user=current_user,
        team_name=team_name,
    )


@app.route('/', methods=['GET'])
def dashboard():
    rows = load_mock_cost_data()
    return render_dashboard(rows, 'Global Multi-Cloud FinOps Dashboard')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        users = load_users(USER_FILE)
        user = users.get(username)

        if user and user['password'] == password:
            session['username'] = username
            flash(f'Logged in as {username}.', 'success')
            return redirect(url_for('team_dashboard'))

        flash('Invalid username or password.', 'error')

    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        team = request.form.get('team', '')

        if not username or not password or not team:
            flash('All fields are required.', 'error')
            return redirect(url_for('register'))

        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('register'))

        users = load_users(USER_FILE)
        if username in users:
            flash('Username already exists. Please choose another username.', 'error')
            return redirect(url_for('register'))

        if team not in TEAMS:
            flash('Please select a valid team.', 'error')
            return redirect(url_for('register'))

        users[username] = {'password': password, 'team': team}
        save_users(USER_FILE, users)
        session['username'] = username
        flash(f'Registered and logged in as {username}.', 'success')
        return redirect(url_for('team_dashboard'))

    return render_template('register.html', teams=TEAMS)


@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Logged out successfully.', 'success')
    return redirect(url_for('dashboard'))


@app.route('/team')
@login_required
def team_dashboard():
    user = get_current_user()
    rows = load_mock_cost_data()
    team_rows = filter_rows_by_team(rows, user['team'])
    title = f"Team Dashboard: {user['team']}"
    return render_dashboard(team_rows, title, team_name=user['team'])


@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        file = request.files.get('billing_csv')
        if not file or file.filename == '':
            flash('Please select a CSV file to upload.', 'error')
            return redirect(url_for('upload'))

        if not file.filename.lower().endswith('.csv'):
            flash('Only CSV files are supported. Please upload a valid billing CSV.', 'error')
            return redirect(url_for('upload'))

        try:
            rows = parse_csv_rows(file)
        except ValueError as exc:
            flash(str(exc), 'error')
            return redirect(url_for('upload'))

        return render_dashboard(rows, 'Uploaded Billing Data Dashboard')

    return render_template('upload.html')


if __name__ == '__main__':
    app.run(debug=True)
