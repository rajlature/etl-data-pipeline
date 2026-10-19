# ETL Data Pipeline Using Python, Pandas & MySQL

A Python-based ETL (Extract, Transform, Load) pipeline that extracts sales data from CSV files, validates and cleans the records, calculates revenue, and loads the processed data into a MySQL database.

The project demonstrates core data engineering concepts, including data quality checks, database upserts, logging, and automated testing.

## Project Overview

This pipeline processes sales records through three stages:

1. **Extract:** Read sales data from CSV files.
2. **Transform:** Validate required fields, clean data, identify invalid and duplicate records, and calculate revenue.
3. **Load:** Insert new sales records or update existing records in MySQL.

The pipeline also generates processed and rejected CSV files and records execution events in a log file.

## Architecture

```text
Raw Sales CSV
     |
     v
   Extract
     |
     v
  Transform
     |
     +------> Clean Sales CSV
     |                |
     |                v
     |          MySQL Database
     |
     +------> Rejected Records CSV

Execution Logs ---> logs/pipeline.log
```

## Technologies Used

- Python
- Pandas
- SQLAlchemy
- MySQL
- PyMySQL
- SQLite for automated database tests
- pytest
- python-dotenv
- Python logging

## Features

- CSV data extraction
- Data validation and cleaning
- Required-column validation
- Date and numeric field conversion
- Duplicate order ID detection
- Rejection of invalid records
- Automatic revenue calculation
- MySQL insert-or-update operations
- Environment-based database configuration
- File and console logging
- Unit and end-to-end tests

## Project Structure

```text
etl-data-pipeline/
├── data/
│   ├── raw/
│   │   └── sales.csv
│   ├── processed/
│   └── rejected/
├── logs/
│   └── pipeline.log
├── src/
│   ├── extract.py
│   ├── transform.py
│   ├── load.py
│   ├── pipeline.py
│   └── logging_config.py
├── tests/
│   ├── test_load.py
│   ├── test_pipeline.py
│   └── test_transform.py
├── .env
├── .gitignore
├── requirements.txt
└── README.md
```

## Sample Data

The sample dataset contains sales orders with fields such as:

| Column | Description |
|---|---|
| `order_id` | Unique order identifier |
| `order_date` | Date of the order |
| `product` | Product name |
| `category` | Product category |
| `quantity` | Units sold |
| `unit_price` | Price per unit |
| `revenue` | Calculated as quantity × unit price |

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/etl-data-pipeline.git
cd etl-data-pipeline
```

Replace `YOUR_USERNAME` with your GitHub username and use the repository URL after publishing the project.

### 2. Create and activate a virtual environment

```bash
python -m venv .venv
```

On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure MySQL

Create a MySQL database:

```sql
CREATE DATABASE etl_sales_db;
```

Create a `.env` file in the project root with your local database settings:

```dotenv
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=etl_sales_db
MYSQL_USER=your_mysql_username
MYSQL_PASSWORD=your_mysql_password
```

Replace the example credentials with your own local MySQL settings. Never commit your `.env` file or expose database passwords.

### 5. Run the pipeline

```bash
python -m src.pipeline
```

The pipeline extracts and transforms the input data, saves the relevant CSV outputs, and loads sales records into MySQL.

### 6. Run the tests

```bash
python -m pytest -v
```

## Test Results

The current test suite contains **12 passing tests**, covering:

- Data loading into a database
- Updating existing orders
- Handling empty input
- Missing-column validation
- Duplicate order ID rejection
- Data transformation and revenue calculation
- End-to-end extraction, transformation, and loading

The tests use a temporary SQLite database where appropriate, so database tests do not require writing test records to the production MySQL database.

## Sample Database Verification

After running the pipeline, verify the loaded data using:

```sql
USE etl_sales_db;

SELECT
    COUNT(*) AS total_orders,
    SUM(quantity) AS total_items,
    SUM(revenue) AS total_revenue
FROM sales;
```

For the current sample dataset, the expected results are:

- Total orders: **6**
- Total items: **17**
- Total revenue: **197100.00**

## Logging

The logging configuration records pipeline execution events in:

```text
logs/pipeline.log
```

Logs are written to both the terminal and the log file, helping with troubleshooting and execution monitoring.

## Future Improvements

- Build an interactive Power BI sales dashboard.
- Add automated data-quality reports.
- Support scheduled pipeline execution.
- Add more robust exception handling and retry logic.
- Integrate additional data sources.
- Add CI workflows for automated testing.

## Learning Outcomes

This project demonstrates practical experience with Python data processing, ETL workflow design, relational databases, data quality validation, automated testing, and logging.

## Author

**Channabaswaraj Lature**

GitHub: https://github.com/rajlature

LinkedIn: https://www.linkedin.com/in/channabaswaraj-lature-157517323/
