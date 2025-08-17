from sqlalchemy import create_engine, text
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://app_user:app_passw0rd@localhost/simple_test_db")
engine = create_engine(DATABASE_URL, echo=True)

with engine.begin() as c:  # This auto-commits
    # Drop table if exists and create new one
    c.execute(text("DROP TABLE IF EXISTS test_table1"))
    c.execute(text("CREATE TABLE test_table1 (id SERIAL PRIMARY KEY, name TEXT)"))
    c.execute(text("INSERT INTO test_table1 (name) VALUES ('test row')"))
    print("Table created and data inserted")

# Verify it exists
with engine.connect() as c:
    result = c.execute(text("SELECT * FROM test_table1"))
    rows = result.fetchall()
    print("Data in test_table:", rows)
    
    # Check table exists in information_schema
    result2 = c.execute(text("""
        SELECT table_name, table_schema 
        FROM information_schema.tables 
        WHERE table_name = 'test_table1'
    """))
    table_info = result2.fetchall()
    print("Table info:", table_info)