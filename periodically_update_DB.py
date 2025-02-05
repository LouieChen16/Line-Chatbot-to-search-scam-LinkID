import time
from datetime import datetime
import sqlite3
import pandas as pd
import requests
from bs4 import BeautifulSoup

def get_csv_url(raw_url):
    response = requests.get(open_gov_url)
    if response.status_code < 300:
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Find the link with the specified attributes
        HTML_tag_with_download_link = soup.find('a', title='CSV下載檔案')
        csv_url = HTML_tag_with_download_link['href']
        return csv_url
    else:
        print("error code: " + response.status_code)

def update_db_from_csv(csv_path, db_path):

    # Load the CSV file into a pandas DataFrame
    df = pd.read_csv(csv_path)
    # print(df)

    #Create or connect DB
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        
        #Create Table if not exist
        create_table = f"""
        CREATE TABLE IF NOT EXISTS scam_line_ID(
        No INTEGER,
        line_ID TEXT,
        Date TEXT
        );
        """
        
        conn.execute(create_table)
        
        # Create a temporary table for the new data
        df.to_sql('temp_table', conn, if_exists='replace', index=False)
        
        table_name = "scam_line_ID"

        # Insert only new rows into the existing table
        insert_query = f"""
        INSERT INTO {table_name}
        SELECT * FROM temp_table
        WHERE NOT EXISTS (
            SELECT 1 FROM {table_name} 
            WHERE {table_name}.No = temp_table.編號
        );
        """

        # Execute the query
        conn.execute(insert_query)
        print(f"DB updated at: {datetime.now()}")

        # Drop the temporary table
        conn.execute("DROP TABLE temp_table")

        # Commit the changes and close the connection
        conn.commit()
        #conn.close()

while True:
    #print("round starts")
    open_gov_url = "https://data.gov.tw/dataset/78432"
    csv_download_url = get_csv_url(open_gov_url)

    # download and save csv
    csv = requests.get(csv_download_url)
    csv_165_path = "/Users/louiechen/Documents/Side-Project/line-chatbot/165_scam_lineID.csv"
    with open(csv_165_path, "wb") as file:
        file.write(csv.content)

    #update DB
    db_165_path = "/Users/louiechen/Documents/Side-Project/line-chatbot/scam_line_ID.db"
    update_db_from_csv(csv_165_path, db_165_path)

    #print("round ends")

    # sleep for "interval" seconds
    time.sleep(24*60*60) 