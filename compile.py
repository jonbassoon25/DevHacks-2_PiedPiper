import csv
import os
import re

def get_last_id(file_path):
    """
    Reads a CSV file and returns the last ID from the first column.
    
    Args:
        file_path (str): The path to the CSV file.
        
    Returns:
        int: The last ID found, or 0 if the file is empty, doesn't exist,
             or contains no valid IDs.
    """
    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        return 0
    
    last_id = 0
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader, None) # Skip the header row
            
            for row in reader:
                if row: # Ensure the row is not empty
                    try:
                        # The ID is in the first column (index 0)
                        current_id = int(row[0])
                        last_id = current_id
                    except (ValueError, IndexError):
                        # This row is malformed or its first column isn't a number. Skip it.
                        continue
    except FileNotFoundError:
        return 0 # File doesn't exist, so first ID will be 1
    except Exception as e:
        print(f"⚠️  An unexpected error occurred while reading the last ID: {e}")
        return 0 # Default to 0 on other errors
        
    return last_id

def clean_activity_name(name):
    """
    Removes leading numbers and periods (e.g., '21. ') from a string.
    
    Args:
        name (str): The activity name to clean.
        
    Returns:
        str: The cleaned activity name.
    """
    pattern = r'^\d+\.\s*'
    return re.sub(pattern, '', name).strip()

def append_to_csv(file_path, data_rows, headers):
    """
    Appends rows to a CSV file. Creates the file and adds headers if it doesn't exist.
    
    Args:
        file_path (str): The path to the CSV file (e.g., 'location_database.csv').
        data_rows (list of lists): The rows of data to append.
        headers (list): The header row for the CSV file.
    """
    file_exists = os.path.exists(file_path)
    is_file_empty = not file_exists or os.path.getsize(file_path) == 0

    with open(file_path, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        if is_file_empty:
            writer.writerow(headers)
            
        writer.writerows(data_rows)

def main():
    """
    Main function to run the continuous input loop.
    """
    file_path = 'location_database.csv'
    # Add "ID" as the first column header
    headers = ["ID", "Name", "Rating", "Reviews", "URL", "Description", "Location"]
    
    # Get the last used ID from the file to know where to start.
    # We add 1 to start with the next available ID.
    next_id_counter = get_last_id(file_path) + 1
    
    print("--- TripAdvisor Custom Data Appender (with Auto-ID) ---")
    print(f"This script will add data to '{file_path}'.")
    print(f"Next entry will start with ID: {next_id_counter}")
    print("It expects data formatted with '$$' between cells and '%%' between rows.")
    print("Type 'exit' or 'quit' at any prompt to close the program.")
    
    while True:
        location = input("\n📍 Please enter the location for the next batch (e.g., Chandler, Arizona): ").strip()
        
        if location.lower() in ['exit', 'quit']:
            print("👋 Exiting the program. Goodbye!")
            return
        
        if not location:
            print("❌ Location cannot be empty. Please try again.")
            continue

        print(f"\n📋 Location set to '{location}'. Now, paste the data from your userscript.")
        print("   (To finish pasting, press Enter on an empty line).")
        
        lines = []
        while True:
            try:
                line = input()
                if line.strip().lower() in ['exit', 'quit']:
                    print("👋 Exiting the program. Goodbye!")
                    return
                if line == "":
                    break
                lines.append(line)
            except EOFError:
                break
        
        if not lines:
            continue
            
        pasted_data = "".join(lines)
        
        new_rows = []
        # The pasted data has columns for everything EXCEPT "ID" and "Location".
        expected_columns = len(headers) - 2
        
        rows_data = pasted_data.strip().split('%%')
        
        for row_str in rows_data:
            if not row_str:
                continue
                
            row = row_str.split('$$')
            
            if len(row) == expected_columns:
                # 1. Clean the name (the first item in the pasted row)
                row[0] = clean_activity_name(row[0])
                
                # 2. Add the location to the end of the row
                row.append(location)
                
                # 3. **NEW**: Insert the new auto-incremented ID at the beginning.
                row.insert(0, next_id_counter)
                
                new_rows.append(row)
                
                # 4. **NEW**: Increment the ID for the next row in this batch.
                next_id_counter += 1
            else:
                print(f"⚠️  Skipping malformed row (expected {expected_columns} columns but got {len(row)}): {row_str[:70]}...")

        if new_rows:
            append_to_csv(file_path, new_rows, headers)
            print(f"✅ Success! Added {len(new_rows)} new rows to '{file_path}' with location '{location}'.")
            print(f"Next entry will start with ID: {next_id_counter}")
        else:
            print("🤔 No valid data rows were found in your paste.")

if __name__ == "__main__":
    main()