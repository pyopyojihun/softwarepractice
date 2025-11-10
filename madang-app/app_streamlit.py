import streamlit as st
import duckdb
from pathlib import Path

# 경로: 리포 기준 상대경로
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH  = DATA_DIR / "madang.db"
CSV_CUSTOMER = DATA_DIR / "Customer_madang.csv"
CSV_BOOK     = DATA_DIR / "Book_madang.csv"
CSV_ORDERS   = DATA_DIR / "Orders_madang.csv"

@st.cache_resource
def get_conn():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = duckdb.connect(database=str(DB_PATH))
    ensure_tables(conn)  # 테이블 없으면 CSV로 초기화
    return conn

def ensure_tables(conn):
    tables = {r[0].lower() for r in conn.execute(
        "select table_name from information_schema.tables where table_schema='main'"
    ).fetchall()}
    if {"customer","book","orders"} <= tables:
        return
    # CSV가 없으면 중지(배포 환경 디버깅이 쉬움)
    for p, label in [(CSV_CUSTOMER,"Customer CSV"), (CSV_BOOK,"Book CSV"), (CSV_ORDERS,"Orders CSV")]:
        if not p.exists():
            st.error(f"{label} not found: {p}")
            st.stop()
    conn.execute("drop table if exists Orders")
    conn.execute("drop table if exists Book")
    conn.execute("drop table if exists Customer")
    conn.execute(f"create table Customer as select * from read_csv_auto('{CSV_CUSTOMER.as_posix()}')")
    conn.execute(f"create table Book     as select * from read_csv_auto('{CSV_BOOK.as_posix()}')")
    conn.execute(f"create table Orders   as select * from read_csv_auto('{CSV_ORDERS.as_posix()}')")

def run_query(sql: str):
    return conn.execute(sql).df()

st.set_page_config(page_title="Madang (DuckDB + Streamlit)", layout="wide")

st.title("📚 Madang DB")
st.caption(f"DB Path: {DB_PATH}")
st.caption(f"Data Dir: {DATA_DIR}")

conn = get_conn()

tab1, tab2, tab3 = st.tabs(["👀 조회", "➕ Customer 추가", "🗑️ Customer 삭제"])

with tab1:
    c1, c2, c3 = st.columns(3)
    with c1:
        st.subheader("Customer")
        st.dataframe(conn.sql("select * from Customer").df(), use_container_width=True)
    with c2:
        st.subheader("Book")
        st.dataframe(conn.sql("select * from Book").df(), use_container_width=True)
    with c3:
        st.subheader("Orders")
        st.dataframe(conn.sql("select * from Orders").df(), use_container_width=True)

with tab2:
    st.subheader("Insert into Customer")
    with st.form("insert_customer"):
        custid = st.number_input("custid", min_value=0, step=1)
        name = st.text_input("name")
        address = st.text_input("address")
        phone = st.text_input("phone")
        submitted = st.form_submit_button("추가")
        if submitted:
            try:
                conn.execute(
                    "insert into Customer (custid,name,address,phone) values (?,?,?,?)",
                    [int(custid), name, address, phone]
                )
                st.success("INSERT 성공")
            except Exception as e:
                st.error(f"INSERT 실패: {e}")

with tab3:
    st.subheader("Delete from Customer")
    ids = conn.sql("select custid from Customer order by custid").df()["custid"].tolist()
    target = st.selectbox("삭제할 custid", ids) if ids else None
    if st.button("삭제", disabled=(target is None)):
        try:
            conn.execute("delete from Customer where custid = ?", [int(target)])
            st.success(f"custid={target} 삭제 완료")
        except Exception as e:
            st.error(f"DELETE 실패: {e}")

st.divider()
st.caption("Tip: data/madang.db가 없으면 CSV로 초기화합니다.")
