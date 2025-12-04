import streamlit as st
import pandas as pd
from db_utils import insert_query, get_all_queries, get_query_stats, close_query

st.set_page_config(page_title="Client Query Submission System", layout="wide")


def main():
    st.title("Client Query Submission Portal")

    # --------- 🔀 Mode selector (Client / Support) ----------
    mode = st.selectbox("Select Mode", ["Client", "Support"])

    # --------- 📊 Summary section ----------
    stats = get_query_stats() or {}

    st.subheader("📊 Query Summary")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Queries", stats.get("total", 0))
    col2.metric("Unique Users", stats.get("users", 0))
    col3.metric("Today's Queries", stats.get("today", 0))
    col4.metric("Latest Query", str(stats.get("last_time", "")))
    st.write("---")

    # ====================== ✉️ CLIENT PAGE ======================
    if mode == "Client":
        st.header("Submit a Query")

        mail_id = st.text_input("Email ID")
        mobile = st.text_input("Mobile Number")
        heading = st.text_input("Query Heading")
        description = st.text_area("Query Description")

        if st.button("Submit Query"):
            if mail_id and mobile and heading and description:
                success = insert_query(mail_id, mobile, heading, description)
                if success:
                    st.success("✅ Query submitted successfully!")
                else:
                    st.error("❌ Failed to submit query.")
            else:
                st.warning("⚠️ Please fill all fields before submitting.")

        st.header("All Submitted Queries")

        data = get_all_queries()
        if data:
            df = pd.DataFrame(data)
            st.dataframe(df)
        else:
            st.info("No queries submitted yet.")

    # ====================== 🛠️ SUPPORT PAGE ======================
    elif mode == "Support":
        st.header("Support Team Dashboard")

        data = get_all_queries()
        if not data:
            st.info("No queries available.")
            return

        df = pd.DataFrame(data)

        # Safe filter by status
        if "status" in df.columns:
            status_filter = st.selectbox("Filter by Status", ["All", "Open", "Closed"])
            if status_filter != "All":
                df = df[df["status"] == status_filter]
        else:
            st.warning("⚠️ 'status' column not found. Showing all queries without status filter.")

        st.subheader("Query List")
        st.dataframe(df)

        # Close query section
        st.subheader("Close a Query")
        qid = st.number_input("Enter Query ID", min_value=1, step=1)

        if st.button("Close This Query"):
            if close_query(int(qid)):
                st.success(f"✅ Query ID {qid} has been closed.")
            else:
                st.error("❌ Failed to close query. Check if ID exists or is already closed.")


if __name__ == "__main__":
    main()
