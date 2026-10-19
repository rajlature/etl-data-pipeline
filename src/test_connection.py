
import os

from dotenv import load_dotenv
from sqlalchemy import URL, create_engine, text

load_dotenv()

connection_url = URL.create(
    drivername="mysql+pymysql",
    username=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    host=os.getenv("MYSQL_HOST", "localhost"),
    port=int(os.getenv("MYSQL_PORT", "3306")),
    database=os.getenv("MYSQL_DATABASE", "etl_sales_db"),
)

engine = create_engine(connection_url, pool_pre_ping=True)

try:
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT DATABASE(), VERSION()")
        )
        database_name, mysql_version = result.fetchone()

        print("Connection successful!")
        print("Database:", database_name)
        print("MySQL version:", mysql_version)

except Exception as error:
    print("Database connection failed.")
    print("Error type:", type(error).__name__)
    print("Check your .env settings and MySQL Server status.")

finally:
    engine.dispose()
