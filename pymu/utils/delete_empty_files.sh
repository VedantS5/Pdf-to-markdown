#!/bin/bash

# Input and output files
input_file="your_input_file.txt"  # Replace with your actual input file name
log_file="deleted_empty_files.txt"

# Extract file names from the input file
grep "Error processing" "$input_file" | awk -F"'" '{print $2}' | awk -F'/' '{print $NF}' > "$log_file"

# Delete files and log their names
while read -r filename; do
    filepath="/N/project/fads_ng/analyst_reports_project/data/analyst_reports_pdf/$filename"
    if [ -f "$filepath" ]; then
        rm "$filepath"
        echo "$filename" >> "$log_file"
    else
        echo "File not found: $filepath" >> "$log_file"
    fi
done < "$log_file"

echo "Processing complete. Deleted files are listed in $log_file."

