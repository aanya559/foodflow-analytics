# FoodFlow Analytics

FoodFlow Analytics is a synthetic, portfolio-ready food delivery operations dashboard built with Python, SQLite, pandas, Plotly, and Streamlit. It investigates late deliveries, restaurant prep bottlenecks, delivery-zone performance, cancellation behavior, and the business impact of delay-related issues.

## Project overview

This project answers questions such as:

- Why are food orders delivered late?
- Which restaurants have the highest late-delivery rates?
- Which delivery zones are most affected by delays?
- How do order volume and delay patterns vary by hour and day?
- What is the relationship between preparation time and total delivery time?
- Which factors are associated with cancellations?
- Which operational changes would likely reduce delays?
- How much estimated order value is tied to cancelled or late orders?

The dashboard is designed for a local analytics workflow and uses a reproducible synthetic dataset, not real customer data. All findings should be treated as operational evidence from the generated dataset.

## Synthetic data disclaimer

This project uses a synthetic food delivery dataset generated with a fixed random seed. It is intended for analytics demos, dashboard prototyping, and portfolio presentation.

Important notes:

- The dataset is not sourced from a real food delivery provider.
- Any performance numbers and business recommendations are based on the generated data only.
- The UI labels the dataset as synthetic.
- Findings should be treated as illustrative operational patterns rather than real-world observations.

## Business problem

Food delivery operations teams need to understand the root causes of late deliveries and cancellations. Common operational questions include:

- Are delays concentrated in certain zones or peak hours?
- Are restaurant preparation times driving downstream miss-rates?
- Are weather and traffic conditions linked to poor customer outcomes?
- Do cancellations represent a major revenue issue?
- Which segments deserve investigation first?

This project creates an interactive dashboard and SQL-based analysis to answer these questions using structured evidence rather than assumptions.

## Features

- Synthetic data generation with reproducible seed and business-consistent relationships
- SQLite database creation and structured SQL analysis scripts
- KPI calculations for completed, cancelled, and late-order performance
- Multi-page Streamlit dashboard with filtering and downloadable exports
- Delay analysis, restaurant ranking, cancellation analysis, and recommendation engine
- Automated tests for KPI logic, validation rules, and analytics outputs

## Technology stack

- Python 3.11+
- pandas and NumPy
- SQLite
- SQL
- Streamlit
- Plotly
- Seaborn and Matplotlib
- pytest

## Dataset schema

The generated dataset includes the following fields:

- order_id
- order_date
- order_time
- restaurant_id
- restaurant_name
- delivery_zone
- order_value
- preparation_time_minutes
- estimated_delivery_minutes
- actual_delivery_minutes
- delivery_distance_km
- weather_condition
- traffic_level
- order_status
- cancellation_reason
- delivery_partner_id
- customer_rating
- discount_amount

## KPI definitions

All KPI formulas are documented in code and used consistently in the dashboard. Key metrics include:

- Total orders = count of all rows in the filtered dataset
- Completed orders = rows with order_status = 'Completed'
- Cancelled orders = rows with order_status = 'Cancelled'
- Cancellation rate = cancelled orders / total orders
- Late deliveries = completed orders where actual_delivery_minutes > estimated_delivery_minutes
- Late-delivery rate = late deliveries / completed deliveries with valid delivery times
- On-time delivery rate = 1 - late-delivery rate
- Average actual delivery time = mean actual_delivery_minutes among completed rows
- Average preparation time = mean preparation_time_minutes across all valid rows
- Average delivery distance = mean delivery_distance_km
- Average order value = mean order_value
- Average customer rating = mean customer_rating for completed rows
- Estimated gross order value = sum of order_value across all rows
- Estimated value of cancelled orders = sum of order_value for cancelled rows

Important note: revenue and order value are not the same as profit. Profit is intentionally not claimed because costs are unavailable.

## SQL techniques demonstrated

The project includes SQL scripts under [sql/schema.sql](sql/schema.sql) and [sql/analytics_queries.sql](sql/analytics_queries.sql). The queries demonstrate:

- CREATE TABLE statements and indexes
- GROUP BY summaries
- CASE WHEN logic
- JOIN patterns
- CTE-based transformations
- Window-style operational ranking logic where suitable
- Readable, business-focused analysis for operations dashboards

## Project architecture

- [app.py](app.py) — Streamlit entry point and multi-page navigation
- [pages/](pages/) — dedicated dashboard sections
- [src/](src/) — reusable business logic, analytics, validation, and database helpers
- [sql/](sql/) — database schema and analytical SQL
- [scripts/initialize_database.py](scripts/initialize_database.py) — dataset and database creation
- [tests/](tests/) — automated validation and KPI checks
- [data/](data/) — generated CSV + SQLite database
- [reports/](reports/) — export and reporting folder

## Installation and setup

### Windows PowerShell

```powershell
cd "C:\Users\acer\Desktop\foodflow-analytics"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python scripts/initialize_database.py
streamlit run app.py
```

### macOS / Linux

```bash
cd /path/to/foodflow-analytics
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python scripts/initialize_database.py
streamlit run app.py
```

## Generate data and initialize the database

To regenerate the synthetic dataset and populate SQLite:

```bash
python scripts/initialize_database.py
```

This creates:

- [data/foodflow_orders.csv](data/foodflow_orders.csv)
- [data/foodflow.db](data/foodflow.db)

## Launch the app

```bash
streamlit run app.py
```



## Testing

Run the automated tests with:

```bash
pytest -q
```

The test suite covers:

- KPI formulas and denominator correctness
- Late-delivery logic
- Cancelled-order exclusion from completed-delivery metrics
- Empty-dataset safety
- Duplicate and missing-value validation
- Database initialization and analytics output shapes

## Dashboard screenshots

Screenshot placeholders will be added here once a local capture is available.

- Executive Overview: pending screenshot
- Delay Investigation: pending screenshot
- Restaurant & Zone Performance: pending screenshot
- Cancellation Analysis: pending screenshot
- Recommendations: pending screenshot

## Limitations and future improvements

- The data is synthetic, so all findings are illustrative and should not be used as real production intelligence.
- The analysis focuses on descriptive operations analytics rather than causal modeling.
- Additional improvements could include:
  - richer SQL parameterized reporting modules
  - real CSV download actions with user-selected export filters
  - scoring models for segment prioritization
  - improved integration with external operational datasets

## License

This project is distributed under the MIT License. See [LICENSE](LICENSE) for details.
