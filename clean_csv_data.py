import csv
from datetime import datetime
import re

def clean_organ_donation_csv(input_csv_path, output_csv_path):
    """
    Cleans the Organ Donation CSV file by anonymizing names and
    reformatting timestamps, and saves the cleaned data to a new CSV.
    """
    cleaned_data = []
    
    try:
        with open(input_csv_path, mode='r', encoding='utf-8') as infile:
            reader = csv.DictReader(infile)
            fieldnames = reader.fieldnames # Get original headers
            
            for row in reader:
                cleaned_row = row.copy() # Start with a copy of the original row

                # 1. Anonymize Name
                name = cleaned_row.get('Name', '').strip()
                if name:
                    name_parts = name.split()
                    initials = ''.join([part[0].upper() for part in name_parts if part])
                    cleaned_row['Name'] = initials if initials else 'Donor'
                else:
                    cleaned_row['Name'] = 'Anonymous Donor'

                # 2. Reformat Timestamp
                timestamp_str = cleaned_row.get('Timestamp')
                if timestamp_str:
                    try:
                        # Remove ' GMT' and colon from timezone offset for strptime compatibility
                        gmt_match = re.search(r'\sGMT([+-]\d{1,2}):?(\d{2})', timestamp_str)
                        if gmt_match:
                            date_time_part = timestamp_str[:gmt_match.start()]
                            tz_offset = f"{gmt_match.group(1)}{gmt_match.group(2)}"
                            clean_timestamp_str = f"{date_time_part} {tz_offset}"
                            # Use %z for timezone, then convert to naive datetime for simpler CSV output
                            dt_object = datetime.strptime(clean_timestamp_str, '%Y/%m/%d %I:%M:%S %p %z')
                            # Convert to a simple string without timezone for CSV
                            cleaned_row['Timestamp'] = dt_object.strftime('%Y-%m-%d %H:%M:%S')
                        else:
                            # Fallback for timestamps without ' GMT' if they exist, or if initial regex fails
                            # This might raise ValueError if format is inconsistent, which will be caught below
                            dt_object = datetime.strptime(timestamp_str, '%Y/%m/%d %I:%M:%S %p')
                            cleaned_row['Timestamp'] = dt_object.strftime('%Y-%m-%d %H:%M:%S')
                    except ValueError as ve:
                        print(f"⚠️ Warning: Could not parse timestamp '{timestamp_str}': {ve}. Keeping original or setting empty.")
                        cleaned_row['Timestamp'] = timestamp_str # Keep original problematic string
                
                cleaned_data.append(cleaned_row)
        
        # Write the cleaned data to a new CSV file
        with open(output_csv_path, mode='w', encoding='utf-8', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(cleaned_data)
        
        print(f"✅ Successfully cleaned '{input_csv_path}' and saved to '{output_csv_path}'.")
        print(f"   Anonymized names and reformatted timestamps.")

    except FileNotFoundError:
        print(f"❌ Error: Input CSV file not found at '{input_csv_path}'. Please ensure the file is in the correct directory.")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    # Specify your input and output file paths here
    input_file = 'Organ Donation.csv'
    output_file = 'Organ Donation_cleaned.csv'
    clean_organ_donation_csv(input_file, output_file) 