import argparse
import requests
import pyodbc

def main():
    parser = argparse.ArgumentParser(description="Data ETL Script")
    parser.add_argument('--src-url', type=str, required=True, help='Url to pull data')
    parser.add_argument('--inserted-by', type=str, required=True, help='Name of person inserting data to the database')
    parser.add_argument('--dest-sqlserver-connstr', type=str,  required=True, help='Connection string of the destination SQL Server')

    args = parser.parse_args()

    print(args.src_url)

    res = requests.get(args.src_url)
    json_data = res.json()

    
    SQL_STATEMENT = """
    INSERT dbo.etl_data (
    inserted_by,
    json_data,
    created_at
    ) OUTPUT INSERTED.id 
    VALUES (?, ?, CURRENT_TIMESTAMP)
    """
    print("Connecting to SQL Server.")
    conn = pyodbc.connect(args.dest_sqlserver_connstr) 
    cursor = conn.cursor()
    print("Inserting ETL Data.")
    cursor.execute(
        SQL_STATEMENT,
        args.inserted_by,
        json_data
    )
    resultId = cursor.fetchval()
    print(f"Inserted ETL Data ID : {resultId}")
    conn.commit()
    cursor.close()
    conn.close()
    print("ETL Data inserted!")


if __name__ == "__main__":
    main()