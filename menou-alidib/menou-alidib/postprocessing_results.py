import subprocess
import os
import sqlite3
import glob



def show_logs(db_name: str):
    """
    Fetches and prints all records from the specified SQLite database (db_name).
    """
    conn = sqlite3.connect(db_name)
    c = conn.cursor()
    c.execute("SELECT id, content, timestamp FROM logs")
    rows = c.fetchall()
    conn.close()

    if not rows:
        print(f"No entries found in {db_name}.")
    else:
        print(f"-- Entries in {db_name} --")
        for (log_id, content, timestamp) in rows:
            print(f"ID: {log_id}, Timestamp: {timestamp}, Content: {content}")

def count_rows(db_name: str):
    """
    Counts and prints the number of rows in the specified SQLite database (db_name).
    """
    try:
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM logs")
        row_count = c.fetchone()[0]
        conn.close()
        #print(f"Total rows in {db_name}: {row_count}")
        return row_count
    except sqlite3.Error as e:
        #print(f"Error accessing {db_name}: {e}")
        return 0


allfolders = glob.glob('./all_modified_codes/*/')

for foldername in allfolders: 
    try:
        completions_moderated = foldername+"/completions_moderated.db"
        completions_unmoderated = foldername+"/completions_unmoderated.db"
        #print (completions_moderated,completions_unmoderated)
        print ("----------------------------------")
        moder = count_rows(completions_moderated)
        unmoder = count_rows(completions_unmoderated)
        print (foldername)
        print ("Ratio of allowed to total requests: ", unmoder/(moder+unmoder))
    except:
        continue
        



