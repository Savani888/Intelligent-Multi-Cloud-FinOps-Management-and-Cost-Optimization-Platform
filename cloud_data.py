import csv
import json
from collections import defaultdict
from datetime import datetime

SAMPLE_CSV_HEADERS = [
    'provider',
    'account',
    'resource',
    'service',
    'cost',
    'usage_hours',
    'project',
    'environment',
    'date',
]

PROJECT_TEAM_MAP = {
    'Customer Portal': 'Product',
    'Internal Tools': 'Engineering',
    'Operations': 'FinOps',
    'Analytics': 'Analytics',
    'AI Platform': 'Analytics',
}

TEAMS = ['Product', 'Engineering', 'FinOps', 'Analytics']


def save_users(user_file, users):
    with open(user_file, 'w', encoding='utf-8') as handle:
        json.dump(users, handle, indent=2)


def load_mock_cost_data():
    rows = [
        {
            'provider': 'AWS',
            'account': 'aws-prod-001',
            'resource': 'ec2-prod-app-1',
            'service': 'EC2',
            'cost': 860.50,
            'usage_hours': 720,
            'project': 'Customer Portal',
            'environment': 'prod',
            'date': datetime(2026, 7, 1).date(),
        },
        {
            'provider': 'AWS',
            'account': 'aws-dev-001',
            'resource': 'ec2-dev-test',
            'service': 'EC2',
            'cost': 120.75,
            'usage_hours': 60,
            'project': 'Internal Tools',
            'environment': 'dev',
            'date': datetime(2026, 7, 1).date(),
        },
        {
            'provider': 'Azure',
            'account': 'azure-ops-001',
            'resource': 'vm-ops-data',
            'service': 'Virtual Machine',
            'cost': 540.80,
            'usage_hours': 680,
            'project': 'Operations',
            'environment': 'prod',
            'date': datetime(2026, 7, 1).date(),
        },
        {
            'provider': 'Azure',
            'account': 'azure-data-001',
            'resource': 'sql-data-warehouse',
            'service': 'SQL Database',
            'cost': 420.20,
            'usage_hours': 480,
            'project': 'Analytics',
            'environment': 'prod',
            'date': datetime(2026, 7, 1).date(),
        },
        {
            'provider': 'GCP',
            'account': 'gcp-project-001',
            'resource': 'gke-cluster-1',
            'service': 'GKE',
            'cost': 310.40,
            'usage_hours': 720,
            'project': 'AI Platform',
            'environment': 'prod',
            'date': datetime(2026, 7, 1).date(),
        },
        {
            'provider': 'GCP',
            'account': 'gcp-dev-001',
            'resource': 'storage-backup',
            'service': 'Cloud Storage',
            'cost': 95.20,
            'usage_hours': 720,
            'project': 'Internal Tools',
            'environment': 'dev',
            'date': datetime(2026, 7, 1).date(),
        },
        {
            'provider': 'AWS',
            'account': 'aws-prod-002',
            'resource': 'rds-order-db',
            'service': 'RDS',
            'cost': 615.00,
            'usage_hours': 720,
            'project': 'Customer Portal',
            'environment': 'prod',
            'date': datetime(2026, 6, 1).date(),
        },
        {
            'provider': 'Azure',
            'account': 'azure-prod-002',
            'resource': 'app-service-prod',
            'service': 'App Service',
            'cost': 220.35,
            'usage_hours': 720,
            'project': 'Operations',
            'environment': 'prod',
            'date': datetime(2026, 6, 1).date(),
        },
        {
            'provider': 'GCP',
            'account': 'gcp-ops-001',
            'resource': 'compute-engine-1',
            'service': 'Compute Engine',
            'cost': 180.60,
            'usage_hours': 480,
            'project': 'Analytics',
            'environment': 'prod',
            'date': datetime(2026, 6, 1).date(),
        },
        {
            'provider': 'AWS',
            'account': 'aws-test-001',
            'resource': 'ec2-test-1',
            'service': 'EC2',
            'cost': 48.40,
            'usage_hours': 100,
            'project': 'Internal Tools',
            'environment': 'dev',
            'date': datetime(2026, 6, 1).date(),
        },
    ]

    for row in rows:
        row['team'] = PROJECT_TEAM_MAP.get(row['project'], 'Unknown')
    return rows


def load_users(user_file):
    with open(user_file, 'r', encoding='utf-8') as handle:
        return json.load(handle)


def get_cost_allocation(rows):
    allocation = {
        'by_tag': defaultdict(float),
        'by_department': defaultdict(float),
    }

    for row in rows:
        cost = row['cost']
        cost_center = row.get('tags', {}).get('cost_center', 'Unknown')
        allocation['by_tag'][cost_center] += cost
        allocation['by_department'][row.get('team', 'Unknown')] += cost

    return {
        'by_tag': dict(sorted(allocation['by_tag'].items(), key=lambda item: item[1], reverse=True)),
        'by_department': dict(sorted(allocation['by_department'].items(), key=lambda item: item[1], reverse=True)),
    }


def get_chargeback_rules(rows):
    chargebacks = defaultdict(float)
    for row in rows:
        chargebacks[row['project']] += row['cost']

    total = sum(chargebacks.values())
    return [
        {
            'project': project,
            'allocated_cost': round(cost, 2),
            'share_percent': round((cost / total) * 100, 1) if total else 0,
        }
        for project, cost in sorted(chargebacks.items(), key=lambda item: item[1], reverse=True)
    ]


def get_scheduler_recommendations(rows):
    recommendations = []
    for row in rows:
        if row['environment'] == 'dev' and row['usage_hours'] > 600:
            recommendations.append(
                f"Schedule {row['resource']} ({row['provider']}) to shut down during off-hours."
            )
        if row['service'] == 'Cloud Storage' and row['usage_hours'] < 200:
            recommendations.append(
                f"Archive {row['resource']} ({row['provider']}) to save storage cost."
            )
    return recommendations if recommendations else ['No scheduler recommendations for current dataset.']


def get_policy_warnings(rows):
    warnings = []
    for row in rows:
        if 'cost_center' not in row.get('tags', {}):
            warnings.append(f"{row['resource']} ({row['provider']}) is missing a cost_center tag.")
        if row['environment'] == 'prod' and row['service'] == 'App Service' and row['cost'] < 150:
            warnings.append(
                f"{row['resource']} ({row['provider']}) is production but cost appears unusually low; check configuration."
            )
        if row['environment'] == 'dev' and row['usage_hours'] > 650:
            warnings.append(
                f"{row['resource']} ({row['provider']}) is dev and highly active; consider more aggressive schedule enforcement."
            )
    return warnings


def get_realtime_series(rows):
    labels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    base_cost = sum(row['cost'] for row in rows) / 7
    values = [round(base_cost * (0.85 + i * 0.03), 2) for i in range(7)]
    return labels, values


def aggregate_costs(rows):
    total_cost = sum(row['cost'] for row in rows)
    cost_by_provider = {}
    cost_by_project = {}

    for row in rows:
        cost_by_provider[row['provider']] = cost_by_provider.get(row['provider'], 0.0) + row['cost']
        cost_by_project[row['project']] = cost_by_project.get(row['project'], 0.0) + row['cost']

    top_resources = sorted(rows, key=lambda row: row['cost'], reverse=True)[:6]

    return {
        'total_cost': round(total_cost, 2),
        'cost_by_provider': cost_by_provider,
        'cost_by_project': cost_by_project,
        'top_resources': top_resources,
    }


def filter_rows_by_team(rows, team_name):
    return [row for row in rows if row.get('team') == team_name]


def get_optimization_recommendations(rows):
    suggestions = []

    for row in rows:
        if row['service'] in ('EC2', 'Virtual Machine', 'GKE', 'RDS') and row['cost'] > 500:
            suggestions.append(
                f"Check rightsizing for {row['resource']} ({row['provider']}) because it costs ${row['cost']:.2f}."
            )
        if row['service'] == 'Cloud Storage' and row['usage_hours'] < 200:
            suggestions.append(
                f"Review {row['resource']} in {row['provider']} for archive or lower-cost storage tier."
            )
        if row['environment'] == 'dev' and row['usage_hours'] > 600:
            suggestions.append(
                f"Consider scheduling {row['resource']} in {row['provider']} to shut down during off-hours."
            )
        if row['environment'] == 'prod' and row['cost'] < 100 and row['service'] == 'App Service':
            suggestions.append(
                f"Confirm {row['resource']} in {row['provider']} is right-sized for production use."
            )

    return suggestions if suggestions else ['All mock resources look healthy for this demo.']


def get_budget_alerts(rows, budgets=None):
    if budgets is None:
        budgets = {
            'AWS': 1800,
            'Azure': 1200,
            'GCP': 700,
        }

    alerts = []
    provider_totals = defaultdict(float)

    for row in rows:
        provider_totals[row['provider']] += row['cost']

    for provider, limit in budgets.items():
        spent = provider_totals.get(provider, 0.0)
        if spent >= limit:
            alerts.append(f"{provider} spend is above the budget of ${limit:.2f}: current spend is ${spent:.2f}.")
        elif spent >= limit * 0.8:
            alerts.append(f"{provider} spend is close to budget: ${spent:.2f} of ${limit:.2f}.")

    return alerts


def monthly_costs(rows):
    monthly = defaultdict(float)
    for row in rows:
        label = row['date'].strftime('%b %Y')
        monthly[label] += row['cost']

    sorted_months = sorted(monthly.items(), key=lambda item: datetime.strptime(item[0], '%b %Y'))
    labels = [label for label, _ in sorted_months]
    values = [round(value, 2) for _, value in sorted_months]
    return labels, values


def get_provider_percentages(rows):
    provider_totals = defaultdict(float)
    for row in rows:
        provider_totals[row['provider']] += row['cost']

    total = sum(provider_totals.values())
    labels = []
    values = []
    for provider, amount in provider_totals.items():
        labels.append(provider)
        values.append(round((amount / total) * 100, 1) if total else 0)

    return labels, values


def parse_csv_rows(file):
    try:
        sample = file.read()
        if isinstance(sample, bytes):
            sample = sample.decode('utf-8')
        file.seek(0)
    except Exception:
        raise ValueError('Unable to read CSV file.')

    reader = csv.DictReader(sample.splitlines())
    if not reader.fieldnames or not set(SAMPLE_CSV_HEADERS).issubset(set(reader.fieldnames)):
        raise ValueError('CSV must include headers: ' + ', '.join(SAMPLE_CSV_HEADERS))

    rows = [normalize_row(row) for row in reader if row.get('provider')]
    if not rows:
        raise ValueError('CSV file contains no valid cost rows.')

    for row in rows:
        row['team'] = PROJECT_TEAM_MAP.get(row['project'], 'Unknown')
    return rows


def normalize_row(row):
    try:
        return {
            'provider': row['provider'].strip(),
            'account': row['account'].strip(),
            'resource': row['resource'].strip(),
            'service': row['service'].strip(),
            'cost': float(row['cost']),
            'usage_hours': float(row['usage_hours']),
            'project': row['project'].strip(),
            'environment': row['environment'].strip(),
            'date': parse_date(row['date']),
        }
    except Exception as exc:
        raise ValueError(f'Invalid CSV row values: {exc}')


def parse_date(value):
    for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y', '%b %Y'):
        try:
            return datetime.strptime(value.strip(), fmt).date()
        except Exception:
            continue
    raise ValueError('Date must use YYYY-MM-DD, DD/MM/YYYY, MM/DD/YYYY or Mon YYYY format.')
