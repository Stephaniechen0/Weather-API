# Project 1: Weather Analytics Platform for Data Processing

## Project Description

In this project, you will take on the role of a junior data engineer at a fictional analytics company contracted to build a weather reporting tool for regional operations teams. You will use the **Open-Meteo Historical Weather API** to collect daily weather data across a set of cities of your choosing, clean and profile the data in Python, store it in a normalized relational database, and write SQL queries to answer real operational questions — such as identifying the hottest month of the year, average rainfall by city, or the frequency of extreme temperature days.

This is an individual project due at the **end of Week 5**.

---

## Tools Used

| Tool | Purpose |
|------|---------|
| **Python** (`requests`) | Making parameterized HTTP requests to the Open-Meteo API |
| **Python** (`pandas`) | Profiling, cleaning, and transforming raw JSON responses into structured tabular data |
| **PostgreSQL** | Hosting the normalized relational database |
| **SQL** (DDL / DML / SELECT) | Schema creation, data loading, and analytical querying |
| **Open-Meteo Historical Weather API** | Source of historical daily weather data (no API key required) |
| **Git & GitHub** | Version control and project submission |

> API Base URL: `https://archive-api.open-meteo.com/v1/archive`

---

## Architecture Description

The platform follows a linear **Extract → Profile & Clean → Load → Analyze** pipeline:

```
┌─────────────────────────┐
│   Open-Meteo API        │  Historical daily weather data
│  (REST / JSON)          │  (temperature, precipitation, wind speed)
└────────────┬────────────┘
             │  HTTP GET (requests)
             ▼
┌─────────────────────────┐
│   Python Ingestion      │  Parameterized requests for 3+ cities
│   Layer                 │  Raw JSON saved to file
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│   Profiling & Cleaning  │  Null checks, type validation, range inspection,
│   (pandas)              │  duplicate detection, and transformation
└────────────┬────────────┘
             │  Cleaned DataFrame
             ▼
┌─────────────────────────┐
│   PostgreSQL Database   │  Normalized schema with primary/foreign keys
│   (Normalized Schema)   │  (e.g., cities table + weather_records table)
└────────────┬────────────┘
             │
             ▼
┌─────────────────────────┐
│   SQL Analysis Layer    │  5+ analytical queries answering business questions
│   (SELECT queries)      │  (e.g., hottest month, total monthly precipitation)
└─────────────────────────┘
```

All work is tracked in a **Git repository** with a meaningful, incremental commit history throughout each phase.

---

## Requirements

### Functional Requirements

- [ ] Call the Open-Meteo Historical Weather API using Python's `requests` library to retrieve **daily weather data** (temperature, precipitation, wind speed) for a **minimum of three cities** across a defined date range
- [ ] Flatten and profile the returned JSON payload, inspecting for:
  - Null or missing values
  - Type inconsistencies
  - Unexpected value ranges
  - Duplicate records
- [ ] Clean and transform the raw API response into a structured tabular format using `pandas`
- [ ] Design a **normalized relational schema** appropriate for multi-city time-series weather data (with appropriate primary and foreign key relationships)
- [ ] Write **DDL** to create the schema and **DML** to load the cleaned records into PostgreSQL
- [ ] Write a **minimum of five analytical SQL queries** answering concrete business-style questions, such as:
  - Highest recorded temperature per city
  - Total monthly precipitation
  - Windiest week of the year
  - Average rainfall by city
  - Frequency of extreme temperature days
- [ ] Maintain a **Git repository** with a clear, meaningful commit history throughout the project

### Deliverables

- [ ] A **GitHub repository** containing:
  - All Python scripts used for ingestion, profiling, and loading
  - All SQL files (DDL schema, DML inserts, and SELECT queries)
  - A sample of the raw API JSON response
- [ ] A **populated, normalized PostgreSQL database**
- [ ] A **short written summary** (half to one page) describing:
  - The cities chosen and the date range used
  - Any data quality issues encountered
  - How those issues were resolved


