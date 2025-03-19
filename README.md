# OneLot

# Car Data Scraper and API

This repository contains a Python-based web scraper that collects car data from [Philkotse](https://philkotse.com) and provides a RESTful API to query the collected data. The data is stored in a PostgreSQL database, and the API is built using Flask.

---

## Features

1. **Web Scraper**:
   - Scrapes car details (name, model, price, date posted) from Philkotse.
   - Handles pagination automatically.
   - Stores data in a PostgreSQL database.

2. **REST API**:
   - Provides endpoints to query car data:
     - Get price range for a specific car model.
     - Get the most common car for a given month.
     - Get the least common car for a given month.

3. **Database**:
   - Uses PostgreSQL for data storage.
   - Prevents duplicate entries using unique constraints.

---

## Requirements

- Python 3.11
- PostgreSQL
- Required Python packages (`requirements.txt`):

Here's the addition to your README.md with the sample endpoints and responses:
Copy- Python 3.11
- PostgreSQL
- Required Python packages (`requirements.txt`):

## Sample Endpoints

### Price Range
GET http://localhost:5000/price-range?model=Vios

[
  {
    "car_name": "Toyota",
    "max_price": 695000.0,
    "min_price": 310000.0,
    "model": "Vios"
  }
]
Most Common Car
CopyGET http://localhost:5000/top-common?month=2025-03
Response:
jsonCopy{
  "car_name": "Toyota",
  "count": 93,
  "model": "Fortuner",
  "month": "2025-03"
}
Least Common Car
CopyGET http://localhost:5000/least-common?month=2025-03
Response:
jsonCopy{
  "car_name": "Audi",
  "count": 1,
  "model": "A3",
  "month": "2025-03"
}