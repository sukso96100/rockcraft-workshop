import argparse
import requests

def main():
    parser = argparse.ArgumentParser(description="Data ETL Script")
    parser.add_argument('--src-url', type=str, required=True, help='Url to pull data')
    parser.add_argument('--dest-sqlserver-conn-str', type=str,  required=True, help='Connection string of the destination SQL Server')

    args = parser.parse_args()

    print(args.src_url)
    print(args.dest_sqlserver_conn_str)

    res = requests.get(args.src_url)
    print(res.json())

if __name__ == "__main__":
    main()