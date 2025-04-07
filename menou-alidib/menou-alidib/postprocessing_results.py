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
        return 0

# Current directory (where the script is running) - adjust if needed
db_directory = "./"  # Change this if needed to match your actual directory

# Find all .db files in the directory
db_files = glob.glob(os.path.join(db_directory, "*.db"))

# Sort files into moderated and unmoderated lists
moderated_dbs = []
unmoderated_dbs = []

for db_file in db_files:
    filename = os.path.basename(db_file)
    if "_moderated_" in filename:
        moderated_dbs.append(db_file)
    elif "_unmoderated_" in filename:
        unmoderated_dbs.append(db_file)

# Find matching pairs and keep track of which files have been paired
pairs = []
paired_moderated = set()
paired_unmoderated = set()

for mod_db in moderated_dbs:
    mod_name = os.path.basename(mod_db)
    # Replace the "_moderated_" part to see if a direct match exists
    unmod_name = mod_name.replace("_moderated_", "_unmoderated_")
    unmod_path = os.path.join(db_directory, unmod_name)
    
    if unmod_path in unmoderated_dbs:
        pairs.append((mod_db, unmod_path))
        paired_moderated.add(mod_db)
        paired_unmoderated.add(unmod_path)
    else:
        # Try to find a match by comparing the core parts of the filenames
        mod_core = mod_name.split("_moderated_")[1].split(".db")[0]
        for unmod_db in unmoderated_dbs:
            if unmod_db not in paired_unmoderated:
                unmod_core = os.path.basename(unmod_db).split("_unmoderated_")[1].split(".db")[0]
                if mod_core == unmod_core or mod_core.startswith(unmod_core) or unmod_core.startswith(mod_core):
                    pairs.append((mod_db, unmod_db))
                    paired_moderated.add(mod_db)
                    paired_unmoderated.add(unmod_db)
                    break

# Process matching pairs
for mod_db, unmod_db in pairs:
    print("----------------------------------")
    print(f"Processing pair:\n  Moderated:   {os.path.basename(mod_db)}\n  Unmoderated: {os.path.basename(unmod_db)}")
    
    moder_count = count_rows(mod_db)
    unmoder_count = count_rows(unmod_db)
    total = moder_count + unmoder_count
    
    if total > 0:
        ratio = unmoder_count / total
        print(f"Ratio of allowed to total requests: {ratio:.4f}")
    else:
        print("No valid data found in both databases.")

# Process moderated DBs that don't have a matching unmoderated DB
for mod_db in moderated_dbs:
    if mod_db not in paired_moderated:
        print("----------------------------------")
        print(f"Processing moderated DB only: {os.path.basename(mod_db)}")
        moder_count = count_rows(mod_db)
        if moder_count > 0:
            # With no unmoderated counterpart, all requests are considered not allowed
            print(f"Only moderated DB data found with {moder_count} rows. Ratio (allowed/total): 0.0000")
        else:
            print("No valid data found in the moderated DB.")

# Process unmoderated DBs that don't have a matching moderated DB
for unmod_db in unmoderated_dbs:
    if unmod_db not in paired_unmoderated:
        print("----------------------------------")
        print(f"Processing unmoderated DB only: {os.path.basename(unmod_db)}")
        unmoder_count = count_rows(unmod_db)
        if unmoder_count > 0:
            # With no moderated counterpart, all requests are considered allowed
            print(f"Only unmoderated DB data found with {unmoder_count} rows. Ratio (allowed/total): 1.0000")
        else:
            print("No valid data found in the unmoderated DB.")
