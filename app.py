from flask import Flask, render_template, request, redirect, url_for, flash
from cloud_data import (
    load_mock_cost_data,
    aggregate_costs,
    get_optimization_recommendations,
    get_budget_alerts,
    monthly_costs,
    provider_percentages,
    parse_csv_rows,
)

app = Flask(__name__)
app.secret_key = 'finops-demo-secret-key'


def render_dashboard(rows, title):
    summary = aggregate_costs(rows)
    recommendations = get_optimization_recommendations(rows)
    alerts = get_budget_alerts(rows)
    monthly_labels, monthly_values = monthly_costs(rows)
    provider_labels, provider_values = provider_percentages(rows)

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
    )


@app.route('/', methods=['GET'])
def dashboard():
    rows = load_mock_cost_data()
    return render_dashboard(rows, 'Demo Multi-Cloud FinOps Dashboard')


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
