# Intelligent Multi-Cloud FinOps Demo


## Features

- Simulates AWS, Azure, and GCP billing data
- Normalizes cloud cost rows into a unified dashboard
- Shows total spend, provider breakdown, project spend, and top-cost resources
- Includes monthly trend and provider share charts
- Provides budget alerts and optimization recommendations
- Supports CSV upload for real billing datasets

## Run locally

1. Create a virtual environment:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Start the app:
   ```bash
   python app.py
   ```
4. Open `http://127.0.0.1:5000`

## Upload billing data

- Open `http://127.0.0.1:5000/upload`
- Upload a CSV with this exact header row:
  `provider,account,resource,service,cost,usage_hours,project,environment,date`
- A sample file is available at `data/sample_billing.csv`

## Project files

- `app.py` - Flask web app and routes
- `cloud_data.py` - data normalization, aggregation, charts, and alert logic
- `templates/dashboard.html` - dashboard UI with charts
- `templates/upload.html` - file upload form
- `static/style.css` - page styling
- `data/sample_billing.csv` - CSV example for upload testing

## How to extend this project

- Replace mock data with real cloud billing APIs for AWS, Azure, and GCP
- Add user authentication and per-team dashboards
- Add cost allocation for tags, departments, and chargeback rules
- Add a scheduler for auto-shutdown recommendations and policy enforcement
- Store uploaded billing runs in a database for historical analysis
- Use the sample CSV file in `data/sample_billing.csv` to test the upload flow.
