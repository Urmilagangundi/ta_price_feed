## DEV env setup

* Install postgresql
* Create user 'tiger_analytics_user' and tiger_analytics database
```bash
$ CREATE USER tiger_analytics_user with PASSWORD '123456';
$ CREATE DATABASE tiger_analytics WITH OWNER tiger_analytics_user;
```
* Clone the project
```
$ git clone https://github.com/Urmilagangundi/tiger_analytics
```
* Change the DB connection string in the app.py file accordingly on line#225
* Install pip requirements   
```bash
$ cd tiger_analytics
$ pip install -r src/requirements.txt
```
* Run below commands
```bash
cd tiger_analytics/src
flask db init
flask db migrate
flask db upgrade
```

* Run the flask app
```bash
flask run --host '0.0.0.0'
```

## How to run test cases
```bash
cd tiger_analytics/src
python -m pytest -k testcases
```

## Assumptions and limitations
* Rows with NULL values will be discarded
* Duplicate records will be ignored
* File to be uploaded not more than 1000 rows
* No queuing system used for asynchronous record dumping
* In the search menu, only the exact matches are retrieved (including for price field)
* In the search menu, all the fields give would be applied as AND conditions while querying the data
* Other than the not null constraints, no other constraints are applied at the DB level
* In the given CSV of data, the first row would be always considered as header.
* In the given CSV of data, order of colums would be: ['Store ID', 'SKU', 'Product Name', 'Price', 'Date']
