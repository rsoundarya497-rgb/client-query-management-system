import streamlit as st
import pandas as pd
from db_utils import insert_query, get_all_queries, get_query_stats, close_query
import io

st.set_page_config(page_title="Client Query Submission System", layout="wide")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = None

# --------- Login Page ----------
def login_page():
    st.title("🔐 Login")

    role = st.selectbox("Select Role", ["Client", "Support"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        # Demo credentials
        if role == "Client" and username == "client" and password == "client123":
            st.session_state.logged_in = True
            st.session_state.role = "Client"
            st.success("Login successful")
            st.rerun()

        elif role == "Support" and username == "admin" and password == "admin123":
            st.session_state.logged_in = True
            st.session_state.role = "Support"
            st.success("Login successful")
            st.rerun()

        else:
            st.error("Invalid username or password")


def main():
    st.title("Client Query Submission Portal")

    # Logout
    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.role = None
        st.rerun()

    mode = st.session_state.role

    # ================= CLIENT =================
    if mode == "Client":
        st.header("Submit a Query")

        mail_id = st.text_input("Email ID")
        mobile = st.text_input("Mobile Number")
        heading = st.text_input("Query Heading")
        description = st.text_area("Query Description")

        if st.button("Submit Query"):
            if mail_id and mobile and heading and description:
                insert_query(mail_id, mobile, heading, description)
                st.success("✅ Query submitted successfully!")
            else:
                st.warning("⚠️ Please fill all fields")

        data = get_all_queries()
        if data:
            st.subheader("All Submitted Queries")
            st.dataframe(pd.DataFrame(data))

    # ================= SUPPORT =================
    elif mode == "Support":
        st.header("Support Team Dashboard")

        data = get_all_queries()
        if not data:
            st.info("No queries available.")
            return

        df = pd.DataFrame(data)

        status_filter = st.selectbox("Filter by Status", ["All", "Open", "Closed"])
        if status_filter != "All" and "status" in df.columns:
            df = df[df["status"] == status_filter]

        st.subheader("Query List")
        st.dataframe(df)

        st.subheader("⬇️ Export Queries")
        st.download_button(
            "Download Queries as CSV",
            df.to_csv(index=False).encode("utf-8"),
            "client_queries_export.csv",
            "text/csv"
        )

        st.subheader("📊 Query Analytics")
        if "status" in df.columns:
            st.bar_chart(df["status"].value_counts())

        if "query_created_time" in df.columns:
            df["query_created_time"] = pd.to_datetime(df["query_created_time"], errors="coerce")
            daily = df.groupby(df["query_created_time"].dt.date).size()
            st.line_chart(daily)

        st.subheader("Close a Query")
        qid = st.number_input("Enter Query ID", min_value=1, step=1)
        if st.button("Close This Query"):
            close_query(int(qid))
            st.success("Query closed successfully")





if __name__ == "__main__":
    if not st.session_state.logged_in:
        login_page()
    else:
        main()
