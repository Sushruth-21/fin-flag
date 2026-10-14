# Fin-Flag
#### Video Demo:  <[URL HERE](https://youtu.be/IL2Sp32asUw)>


## Description
Fin-Flag refers to Finance Flag is a project based on identifying the outliers in the transaction of any finance releated sector. It utilizes a custom algorithmic anomaly detection for checking velocity and statistical outliers.

**Velocity Outlier :** It flags outliers (anomaly transactions) based on the timestamp of the transaction takes place. Example: It doesn't make sense if a users purchase 2 different things at a same time.

**Statistical Outlier :** It flags outliers (anomaly transactions) based on the spikes calculated via Z-score. Example: A transaction from user spending amount higher than usual like if he has a range of $10 to $20, it would be suspicious of him to spend $500 or $1000. (Well there are exceptions on counting if a user is intended to spend, thats why there is a delete button present beside transactions)


## Core Features
1. **Admin Authentication :** Users can register and log in using password hashing and Flask sessions. The system stores administrators separately from transaction users. The admins table stores login accounts, while the users table stores transaction subjects. Each transaction references both the user associated with the transaction and the administrator who submitted it.

2. **Data Ingestion (Bulk and Manual) :** Users can upload and process multiple transactions from a CSV file or can enter single transaction manually in form.

3. **Filtering and Deletion :** The Security Operation Center (SOC) Dashboard contains input to minimun and maximum value filter to search within its range. If user feels some transactions are unnecessary, then it can be deleted by a delete button

4. **SOC Dashboard :** Security Operation Center (SOC) Dashboard consist list of transaction that user have entered and found any anomaly in any transaction. So, it has the record of the outliers in transaction.


## Architecture and File Structure
The Application is made up on Python(Flask), HTML/CSS, SQLITE FOR DATABASE and Javascript for frontend.

Fin-Flag/
│
├── README.md
├── app.py
├── engine.py
├── requirements.txt
├── finflag.db
├── .env.example
├── .gitignore
│
├── tests/
│   └── test_engine.py
│
├── static/
│   ├── dashboard.js
│   └── styles.css
│
├── templates/
│   ├── index.html
│   ├── layout.html
│   ├── login.html
│   ├── register.html
│   └── soc_feed.html
│
└── sample datasets/
    ├── dataset.csv
    ├── dataset_anomaly.csv
    ├── dataset_anomaly_2.csv
    └── test_data.csv

**app.py :** Contains Python flask and SQL, which route to functions and html pages, So it is the main file for the project where all the function like login, logout, register, reading CSV files, submitting transaction(process transaction), SQL query are present.

**engine.py :** Backbone of the project containing mathematical algorithms to check the outliers. The anomaly logic of transaction is calculated based of z-score and slide time window.

**finflag.db :** It is database consisting table of users, admins, transactions.

**static/dashboard.js :** Present in static folder, it fetchs alerts asynchronously, checks/handles minimum and maximum values for filtering, functions for next and previous pages, delete transactions.


## Setup Instructions
### Root folder :
cd Fin-Flag

### Set up a virtual environment :
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
PowerShell: .\venv\Scripts\Activate.ps1

### Install requirements :
pip install -r requirements.txt

### Run the server :
flask --app app run


## Test Instructions
### Root folder :
cd Fin-Flag

### Set up a virtual environment :
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate

### Install requirements :
pip install -r requirements.txt

### Run test file :
pytest tests\test_engine.py
It should display 7 passed.


## Database Setup(Only if database is not present)
The application uses a SQLite database named finflag.db. The current database contains the admins, users, and transactions tables.

### Creating the Database
If the finflag.db file does not exist, you can Open or create an empty database file by running the following command:
sqlite3 finflag.db

The repository includes an initialized development database. A missing database currently requires manually applying the documented schema.

### Schema
Schema for the database is as follows:
```sql
CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT);

CREATE TABLE admins (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT NOT NULL, hash TEXT NOT NULL);

CREATE TABLE transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT, 
        user_id INTEGER REFERENCES users(id), 
        amount NUMERIC,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, 
        is_flagged BOOLEAN DEFAULT 0, 
        flag_type TEXT, 
        admin_id INTEGER REFERENCES admins(id)
    );
```

## Environment Variables
.env.example documents the required variables for the application. You can create a .env file in the root directory and set the following variables:
FINFLAG_SECRET_KEY=replace-with-a-long-random-value-for-flask-session-security


## Running with Docker

### Prerequisite
Install and start Docker Desktop for Windows. Verify that the Docker Engine is running:
```powershell
docker info
```

### Configure the environment variable
Create a private .env file in the project root using .env.example as a reference:
```text
FINFLAG_SECRET_KEY=replace-with-a-long-random-value
```
Do not commit .env; it is ignored by .gitignore.

### Build the Docker image
Run this command from the project root:
```powershell
docker build -t fin-flag .
```
This creates a Docker image named `fin-flag`.

### Run the container
```powershell
docker run --name fin-flag-app --publish 5000:5000 --env-file .env --volume "D:\Fin-Flag\finflag.db:/app/finflag.db" fin-flag
```
For another computer, replace the host-side path with that computer's project path. 
D:\Fin-Flag\finflag.db to your actual path on current computer

### Open the application
Visit: Open [http://localhost:5000/login](http://localhost:5000/login)

### Stop the container
If the container is running in the current PowerShell window, press: `Ctrl+C`

Alternatively, You can also stop it from another PowerShell window:
```powershell 
docker stop fin-flag-app
```

### Start the existing container again
```powershell 
docker start -a fin-flag-app
```

### Remove the container
Stop it first, then remove it:
```powershell
docker rm fin-flag-app
```
Removing the container does not remove the host finflag.db file because it is mounted from the project folder

If the image needs to be rebuilt after changing the Dockerfile:
```powershell
docker build -t fin-flag .
```

## FAQs
#### What is purpose of this project?
This Project is based on intent for a user who has list of transaction in CSV and want to know if there is an anomaly in transaction.

#### What algorithm does Velocity and Statistical Outlier use?
Velocity Outlier used Sliding Time Window and Statistical Outlier uses Z-score.

#### How does the system ensure data isolation between different administrators?
The transactions table references admins(id) through admin_id. This associates each transaction with the logged-in administrator who submitted it. It separately references users(id) through user_id.

#### What happens if I didn't enter time stamp is CSV file?
It just mark the time of submission, so you would likely to get an velocity outlier.

#### How is the timestamp in manually enter form stored?
It stores time on based of submission.

#### Why flask over other alternatives?
It is minimal, easy to implement, lightweight and best for small apps.

#### How is password stores in tables?
Passwords are stored as hashes using Werkzeug’s generate_password_hash() function. Plain-text passwords are not stored in the database.


## Design Choice
- Used Limit in SOC Dashboard so the browser won't crash because of multiple transaction in single page

- Implemented two completely different detection algorithms: Z-score math and sliding time window

- Used URLSearchParams in javascript to append URL queries

- Most of the function has built-in type casting to specific datatype and made sure to avoid or handle NULL values (But would cause internal server error if NULL values on CSV file) which is how real financial systems work—they reject bad data.

- Avoided Zombie Processes (setInterval(fetchAlerts, 3000)), So my dashboard page doesn't get overwrite because of running loop



