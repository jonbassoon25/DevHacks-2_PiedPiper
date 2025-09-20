import csv
import os
import re
import io

def clean_activity_name(name):
    """
    Removes leading numbers and periods (e.g., '21. ') from a string.
    
    Args:
        name (str): The activity name to clean.
        
    Returns:
        str: The cleaned activity name.
    """
    # This regular expression looks for:
    # ^     - the beginning of the string
    # \d+   - one or more digits (like 21)
    # \.    - a literal period
    # \s* - zero or more whitespace characters
    pattern = r'^\d+\.\s*'
    return re.sub(pattern, '', name).strip()

def append_to_csv(file_path, data_rows, headers):
    """
    Appends rows to a CSV file. Creates the file and adds headers if it doesn't exist.
    
    Args:
        file_path (str): The path to the CSV file (e.g., 'result.csv').
        data_rows (list of lists): The rows of data to append.
        headers (list): The header row for the CSV file.
    """
    # Check if the file is new or empty. If so, we'll need to write headers.
    file_exists = os.path.exists(file_path)
    is_file_empty = not file_exists or os.path.getsize(file_path) == 0

    # 'a' mode is for append. newline='' is important to prevent extra blank rows.
    with open(file_path, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # If the file is new/empty, write the header row first.
        if is_file_empty:
            writer.writerow(headers)
            
        # Write all the new data rows.
        writer.writerows(data_rows)

def main():
    """
    Main function to run the continuous input loop.
    """
    file_path = 'result.csv'
    # Add "Location" to the headers
    headers = ["Name", "Rating", "Reviews", "URL", "Description", "Location"]
    
    print("--- TripAdvisor CSV Appender ---")
    print("This script will add data to 'result.csv'.")
    print("Type 'exit' or 'quit' at any prompt to close the program.")
    
    while True:
        # First, ask for the location for the upcoming batch of data.
        location = input("\n📍 Please enter the location for the next batch (e.g., Chandler, Arizona): ").strip()
        
        if location.lower() in ['exit', 'quit']:
            print("👋 Exiting the program. Goodbye!")
            return
        
        if not location:
            print("❌ Location cannot be empty. Please try again.")
            continue

        print(f"\n📋 Location set to '{location}'. Now, paste the CSV data from your userscript.")
        print("   (To finish pasting, press Enter on an empty line).")
        
        lines = []
        # Loop to capture multi-line pasted input
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
                break # Handles Ctrl+D/Ctrl+Z
        
        # If no input was provided, loop again
        if not lines:
            continue
            
        csv_text = "\n".join(lines)
        
        # Use io.StringIO to treat the input string as a file for the csv reader
        string_io = io.StringIO(csv_text)
        reader = csv.reader(string_io)
        
        try:
            # The first row from the pasted data is its header, which we can ignore
            pasted_header = next(reader)
        except StopIteration:
            print("❌ Error: Pasted data was empty. Please try again.")
            continue
            
        new_rows = []
        # The pasted data will have one less column than our new headers list
        expected_columns = len(headers) - 1
        for row in reader:
            # Basic validation to ensure the row has the correct number of columns from the paste
            if len(row) == expected_columns:
                # Clean the name (the first item in the row)
                row[0] = clean_activity_name(row[0])
                # Add the location to the end of the row
                row.append(location)
                new_rows.append(row)
            else:
                print(f"⚠️  Skipping malformed row (expected {expected_columns} columns): {row}")

        if new_rows:
            append_to_csv(file_path, new_rows, headers)
            print(f"✅ Success! Added {len(new_rows)} new rows to '{file_path}' with location '{location}'.")
        else:
            print("🤔 No valid data rows were found in your paste.")

# This makes the script runnable from the command line
if __name__ == "__main__":
    main()