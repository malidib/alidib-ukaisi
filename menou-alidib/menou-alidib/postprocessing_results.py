import os
import sqlite3
import glob

def count_rows(db_name: str):
    """
    Counts and returns the number of rows in the specified SQLite database (db_name).
    """
    try:
        conn = sqlite3.connect(db_name)
        c = conn.cursor()
        c.execute("SELECT COUNT(*) FROM logs")
        row_count = c.fetchone()[0]
        conn.close()
        return row_count
    except sqlite3.Error as e:
     #   print(f"Error accessing {db_name}: {e}")
        return 0

# Current directory (where the script is running) - adjust if needed
db_directory = "./databases/"  # Change this if needed to match your actual directory

# Print current directory for debugging
#print(f"Looking for .db files in: {os.path.abspath(db_directory)}")

# Find all .db files in the directory
db_files = glob.glob(os.path.join(db_directory, "*.db"))
#print(f"Total .db files found: {len(db_files)}")

# Sort files into moderated and unmoderated lists
moderated_dbs = []
unmoderated_dbs = []

for db_file in db_files:
    filename = os.path.basename(db_file)
  #  print(f"Examining file: {filename}")
    if "_moderated_" in filename:
        moderated_dbs.append(db_file)
    elif "_unmoderated_" in filename:
        unmoderated_dbs.append(db_file)

#print(f"Found {len(moderated_dbs)} moderated DBs and {len(unmoderated_dbs)} unmoderated DBs")

# Find matching pairs
pairs = []
for mod_db in moderated_dbs:
    mod_name = os.path.basename(mod_db)
    
    # Replace moderated with unmoderated to find potential match
    unmod_name = mod_name.replace("_moderated_", "_unmoderated_")
    unmod_path = os.path.join(db_directory, unmod_name)
    
    if unmod_path in unmoderated_dbs:
        pairs.append((mod_db, unmod_path))
     #   print(f"Direct match: {mod_name} with {unmod_name}")
    else:
        # Try to find a match by core parts
        mod_core = mod_name.split("_moderated_")[1].split(".db")[0]
        for unmod_db in unmoderated_dbs:
            unmod_core = os.path.basename(unmod_db).split("_unmoderated_")[1].split(".db")[0]
            # If the cores are identical or very similar
            if mod_core == unmod_core or (
                mod_core.startswith(unmod_core) or unmod_core.startswith(mod_core)
            ):
                pairs.append((mod_db, unmod_db))
            #    print(f"Core match: {mod_name} with {os.path.basename(unmod_db)}")
                break

#print(f"Total pairs found: {len(pairs)}")

# Process matching pairs
for mod_db, unmod_db in pairs:
    print("----------------------------------")
   # print(f"Processing pair:\n  Moderated:   {os.path.basename(mod_db)}\n  Unmoderated: {os.path.basename(unmod_db)}")

    moder_count = count_rows(mod_db)
    unmoder_count = count_rows(unmod_db)

    if moder_count + unmoder_count > 0:
        ratio = unmoder_count / (moder_count + unmoder_count)
        print(f"Ratio of allowed to total requests: {ratio:.4f}")
    else:
        print("No valid data found in both databases.")