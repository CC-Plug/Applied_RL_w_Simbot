import sqlalchemy
import pandas as pd
pd.set_option("display.max_rows", None, "display.max_columns", None)
import time
engine = sqlalchemy.create_engine('sqlite:///Q_TableStream.db')

while True:
    print("Try to Connect DB")
    try:
        conn = engine.connect()
    #     result = engine.execute('SELECT * FROM Q_table')
        print(pd.read_sql('SELECT * FROM Q_table', conn))
        conn.close()
    except:
        print("Waitting Next")
        time.sleep(1)
    print("Close Connection")
    time.sleep(5)