# Client Query Management System

This is a simple end-to-end project built using **Python**, **Streamlit**, and **MySQL**.  
It allows clients to submit support queries and the support team to manage and close them.

---

## 🚀 Features

### ✔ Client Page
- Submit a new query (email, mobile, heading, description)
- Query is saved into MySQL with **status = Open**
- All queries are displayed in a table

### ✔ Support Page
- View all queries from database
- Filter by **All, Open, Closed**
- Close a query → Updates status to **Closed** and saves closed timestamp

### ✔ Dashboard Summary
- Total queries
- Unique users
- Today’s queries
- Latest query submitted time

---

## 🗃 Database Table (MySQL)

```sql
CREATE TABLE client_queries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    mail_id VARCHAR(255),
    mobile_number VARCHAR(50),
    query_heading VARCHAR(255),
    query_description TEXT,
    status VARCHAR(20),
    query_created_time DATETIME,
    query_closed_time DATETIME NULL
);
🛠 Technologies Used

Python

Streamlit

MySQL

Pandas

Datetime


How to Run

Install dependencies:

pip install streamlit mysql-connector-python pandas


Update database credentials in config.py, then run:

python -m streamlit run app.py

📁 Files Included

app.py – Streamlit App (Client + Support)

db_utils.py – Database operations

config.py – MySQL connection details

client_queries_sample.csv – Sample data

.gitignore

🙌 Author

Soundarya raju

Project submitted for GUVI Python + SQL Course.


---

# 🎉 Done!
