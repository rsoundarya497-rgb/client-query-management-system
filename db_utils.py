import mysql.connector
from mysql.connector import Error
from datetime import datetime
from config import DB_HOST, DB_USER, DB_PASSWORD, DB_NAME


# ---------------------------
# DATABASE CONNECTION
# ---------------------------
def get_connection():
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return conn
    except Error as e:
        print("Database connection error:", e)
        return None


# ---------------------------
# INSERT QUERY
# ---------------------------
def insert_query(mail_id, mobile_number, query_heading, query_description):
    conn = get_connection()
    if conn is None:
        return False

    try:
        cursor = conn.cursor()
        created = datetime.now()

        sql = """
        INSERT INTO client_queries
        (mail_id, mobile_number, query_heading, query_description, status, query_created_time)
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        cursor.execute(sql, (
            mail_id, mobile_number, query_heading,
            query_description, "Open", created
        ))
        conn.commit()
        return True

    except Error as e:
        print("Insert error:", e)
        return False

    finally:
        cursor.close()
        conn.close()


# ---------------------------
# GET ALL QUERIES
# ---------------------------
def get_all_queries():
    conn = get_connection()
    if conn is None:
        return []

    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM client_queries ORDER BY id DESC")
        rows = cursor.fetchall()
        return rows

    except Error as e:
        print("Fetch error:", e)
        return []

    finally:
        cursor.close()
        conn.close()


# ---------------------------
# GET QUERY STATISTICS
# ---------------------------
def get_query_stats():
    conn = get_connection()
    if conn is None:
        return {}

    try:
        cursor = conn.cursor(dictionary=True)

        # Total queries
        cursor.execute("SELECT COUNT(*) AS total FROM client_queries")
        total = cursor.fetchone()["total"]

        # Total unique users
        cursor.execute("SELECT COUNT(DISTINCT mail_id) AS users FROM client_queries")
        users = cursor.fetchone()["users"]

        # Today
        cursor.execute("""
            SELECT COUNT(*) AS today
            FROM client_queries
            WHERE DATE(query_created_time) = CURDATE()
        """)
        today = cursor.fetchone()["today"]

        # Latest query
        cursor.execute("""
            SELECT MAX(query_created_time) AS last_time
            FROM client_queries
        """)
        last_time = cursor.fetchone()["last_time"]

        return {
            "total": total,
            "users": users,
            "today": today,
            "last_time": last_time
        }

    except Error as e:
        print("Stats error:", e)
        return {}

    finally:
        cursor.close()
        conn.close()


# ---------------------------
# CLOSE QUERY
# ---------------------------
def close_query(query_id):
    conn = get_connection()
    if conn is None:
        return False

    try:
        cursor = conn.cursor()
        now = datetime.now()

        sql = """
        UPDATE client_queries
        SET status = 'Closed',
            query_closed_time = %s
        WHERE id = %s
        """

        cursor.execute(sql, (now, query_id))
        conn.commit()

        return cursor.rowcount > 0

    except Error as e:
        print("Close error:", e)
        return False

    finally:
        cursor.close()
        conn.close()
