# app.py
from pathlib import Path
import duckdb

BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"                 # CSV와 madang.db가 놓일 폴더
DB_PATH  = DATA_DIR / "madang.db"

CSV_CUSTOMER = DATA_DIR / "Customer_madang.csv"
CSV_BOOK     = DATA_DIR / "Book_madang.csv"
CSV_ORDERS   = DATA_DIR / "Orders_madang.csv"

def get_conn():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = duckdb.connect(database=str(DB_PATH))
    return conn

def init_db_if_needed(conn):
    # madang.db가 비어있거나 테이블이 없으면 CSV에서 생성
    tables = set(row[0].lower() for row in conn.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema='main'"
    ).fetchall())
    need_create = not {"customer","book","orders"} <= tables

    if need_create:
        # 기존 있으면 정리
        conn.execute("DROP TABLE IF EXISTS Orders")
        conn.execute("DROP TABLE IF EXISTS Book")
        conn.execute("DROP TABLE IF EXISTS Customer")

        # CSV로부터 테이블 생성
        conn.execute(f"CREATE TABLE Customer AS SELECT * FROM read_csv_auto('{CSV_CUSTOMER.as_posix()}')")
        conn.execute(f"CREATE TABLE Book     AS SELECT * FROM read_csv_auto('{CSV_BOOK.as_posix()}')")
        conn.execute(f"CREATE TABLE Orders   AS SELECT * FROM read_csv_auto('{CSV_ORDERS.as_posix()}')")

def query(conn, sql, return_type="df"):
    if return_type == "df":
        return conn.execute(sql).df()
    return conn.execute(sql).fetchall()

def main():
    conn = get_conn()
    init_db_if_needed(conn)

    # 예시: 조인 조회
    df = query(conn, "SELECT * FROM Customer c JOIN Orders o ON c.custid = o.custid")
    print(df.head())

    # 예시: INSERT/DELETE
    conn.execute("""INSERT INTO Customer (custid,name,address,phone)
                    VALUES (10,'표지훈','청주시 흥덕구','010-2613-6323')""")
    print(query(conn, "SELECT * FROM Customer ORDER BY custid").tail())

    conn.execute("DELETE FROM Customer WHERE custid = 10")
    print(query(conn, "SELECT * FROM Customer ORDER BY custid").tail())

if __name__ == "__main__":
    main()
