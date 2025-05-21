#!/usr/bin/env python3
import os
import argparse
import multiprocessing

# Function to get processed files (by their base name) from the output directory
def get_processed_files(output_dir):
    processed = set()
    for file in os.listdir(output_dir):
        if file.lower().endswith(".md"):
            base, _ = os.path.splitext(file)
            processed.add(base)
    return processed

# Function to convert a single PDF file to Markdown
def process_file(task):
    input_dir, output_dir, pdf_filename = task
    # Import Docling modules locally inside the worker function
    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode
    from docling.datamodel.base_models import InputFormat

    input_path = os.path.join(input_dir, pdf_filename)
    base, _ = os.path.splitext(pdf_filename)
    output_path = os.path.join(output_dir, base + ".md")

    # Setup Docling converter with fast mode for table extraction
    pipeline_options = PdfPipelineOptions(do_table_structure=True)
    pipeline_options.table_structure_options.mode = TableFormerMode.FAST
    converter = DocumentConverter(format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    })
    try:
        result = converter.convert(input_path)
        markdown_text = result.document.export_to_markdown()
        with open(output_path, "w", encoding="utf-8") as f_out:
            f_out.write(markdown_text)
        return (pdf_filename, "success", output_path)
    except Exception as e:
        return (pdf_filename, "error", str(e))

def main():
    parser = argparse.ArgumentParser(
        description="Convert PDF files in an input directory to Markdown using Docling (fast table mode) with multiprocessing."
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to the input directory containing PDF files."
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to the output directory where Markdown files will be saved."
    )
    parser.add_argument(
        "--batch_size",
        type=int,
        default=100,
        help="Number of PDF files to process in a single run (default: 100)."
    )
    parser.add_argument(
        "--num_processes",
        type=int,
        default=1,
        help="Number of parallel processes to use (default: 1). Use a higher number for parallel conversion."
    )
    args = parser.parse_args()

    input_dir = args.input
    output_dir = args.output
    batch_size = args.batch_size
    num_processes = args.num_processes

    if not os.path.exists(input_dir):
        print(f"Input directory '{input_dir}' does not exist.")
        return
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # Build cache of processed files (Markdown files already in output)
    processed_files = get_processed_files(output_dir)
    print(f"Found {len(processed_files)} processed files in the output directory.")

    # List all PDF files in the input directory
    pdf_files = [f for f in os.listdir(input_dir) if f.lower().endswith(".pdf")]
    print(f"Found {len(pdf_files)} PDF files in the input directory.")

    # Filter out files that have already been processed
    files_to_process = [f for f in pdf_files if os.path.splitext(f)[0] not in processed_files]
    total_to_process = min(len(files_to_process), batch_size)
    print(f"Scheduling {total_to_process} unprocessed file(s) for conversion using {num_processes} process(es).")

    # Prepare tasks for multiprocessing: each task is a tuple (input_dir, output_dir, pdf_filename)
    tasks = [(input_dir, output_dir, f) for f in files_to_process[:total_to_process]]

    # Create a multiprocessing Pool and distribute work among the processes
    with multiprocessing.Pool(processes=num_processes) as pool:
        results = pool.map(process_file, tasks)

    # Log the processing outcome for each file
    processed_count = 0
    for filename, status, info in results:
        if status == "success":
            print(f"Converted: {filename} --> {info}")
            processed_count += 1
        else:
            print(f"Error processing {filename}: {info}")

    print(f"Conversion complete. Processed {processed_count} file(s).")

if __name__ == "__main__":
    main()
