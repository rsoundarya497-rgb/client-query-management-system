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
# INSERT SINGLE QUERY (Client submission)
# ---------------------------
def insert_query(mail_id, mobile_number, query_heading, query_description):
    conn = get_connection()
    if conn is None:
        return False

    cursor = None
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
        if cursor is not None:
            cursor.close()
        conn.close()


# ---------------------------
# GET ALL QUERIES (Support view)
# ---------------------------
def get_all_queries():
    conn = get_connection()
    if conn is None:
        return []

    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM client_queries ORDER BY id DESC")
        return cursor.fetchall()

    except Error as e:
        print("Fetch error:", e)
        return []

    finally:
        if cursor is not None:
            cursor.close()
        conn.close()


# ---------------------------
# GET QUERIES BY CLIENT EMAIL (Client view)
# ---------------------------
def get_queries_by_email(mail_id):
    conn = get_connection()
    if conn is None:
        return []

    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)
        sql = """
        SELECT *
        FROM client_queries
        WHERE mail_id = %s
        ORDER BY id DESC
        """
        cursor.execute(sql, (mail_id,))
        return cursor.fetchall()

    except Error as e:
        print("Fetch by email error:", e)
        return []

    finally:
        if cursor is not None:
            cursor.close()
        conn.close()


# ---------------------------
# GET QUERY STATISTICS
# ---------------------------
def get_query_stats():
    conn = get_connection()
    if conn is None:
        return {}

    cursor = None
    try:
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT COUNT(*) AS total FROM client_queries")
        total = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS open_count FROM client_queries WHERE status = 'Open'")
        open_count = cursor.fetchone()["open_count"]

        cursor.execute("SELECT COUNT(*) AS closed_count FROM client_queries WHERE status = 'Closed'")
        closed_count = cursor.fetchone()["closed_count"]

        cursor.execute("""
            SELECT AVG(TIMESTAMPDIFF(SECOND, query_created_time, query_closed_time)) AS avg_seconds
            FROM client_queries
            WHERE status = 'Closed'
              AND query_closed_time IS NOT NULL
              AND query_created_time IS NOT NULL
        """)
        avg_seconds = cursor.fetchone()["avg_seconds"]

        avg_resolution_hrs = None
        if avg_seconds is not None:
            avg_resolution_hrs = float(avg_seconds) / 3600

        return {
            "total": total,
            "open": open_count,
            "closed": closed_count,
            "avg_resolution_hrs": avg_resolution_hrs
        }

    except Error as e:
        print("Stats error:", e)
        return {}

    finally:
        if cursor is not None:
            cursor.close()
        conn.close()


# ---------------------------
# CLOSE QUERY
# ---------------------------
def close_query(query_id):
    conn = get_connection()
    if conn is None:
        return False

    cursor = None
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
        if cursor is not None:
            cursor.close()
        conn.close()


# =========================================================
# ADMIN FUNCTIONS (FOR REPLACING OLD HISTORY)
# =========================================================

# ---------------------------
# DELETE ALL QUERIES (Hard reset history)
# ---------------------------
def delete_all_queries():
    conn = get_connection()
    if conn is None:
        return False

    cursor = None
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM client_queries")
        conn.commit()
        return True

    except Error as e:
        print("Delete error:", e)
        return False

    finally:
        if cursor is not None:
            cursor.close()
        conn.close()


# ---------------------------
# INSERT BULK QUERIES (from DataFrame)
# ---------------------------
def insert_bulk_queries(df):
    """
    Expected columns (case-sensitive):
    - mail_id
    - mobile_number
    - query_heading
    - query_description
    Optional columns:
    - status (default Open)
    - query_created_time (default now)
    - query_closed_time (default None)
    """
    conn = get_connection()
    if conn is None:
        return False

    cursor = None
    try:
        cursor = conn.cursor()

        required_cols = {"mail_id", "mobile_number", "query_heading", "query_description"}
        missing = required_cols - set(df.columns)
        if missing:
            print(f"Bulk insert error: Missing columns in CSV/DataFrame: {missing}")
            return False

        sql = """
        INSERT INTO client_queries
        (mail_id, mobile_number, query_heading, query_description, status, query_created_time, query_closed_time)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        rows = []
        for _, r in df.iterrows():
            status = r["status"] if "status" in df.columns and str(r["status"]).strip() else "Open"
            created = r["query_created_time"] if "query_created_time" in df.columns and str(r["query_created_time"]).strip() else datetime.now()
            closed = r["query_closed_time"] if "query_closed_time" in df.columns and str(r["query_closed_time"]).strip() else None

            rows.append((
                r["mail_id"],
                r["mobile_number"],
                r["query_heading"],
                r["query_description"],
                status,
                created,
                closed
            ))

        cursor.executemany(sql, rows)
        conn.commit()
        return True

    except Error as e:
        print("Bulk insert error:", e)
        return False

    finally:
        if cursor is not None:
            cursor.close()
        conn.close()


# Optional debug (comment out for evaluator)
# print("db_utils loaded successfully")

print("USING db_utils FROM:", __file__)
