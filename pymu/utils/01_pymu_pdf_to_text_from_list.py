#!/usr/bin/env python3
import os
import argparse
import fitz  # PyMuPDF
import multiprocessing
from pathlib import Path

def init_worker(shared_processed):
    """Initialize each worker process with the shared cache."""
    global processed_cache
    processed_cache = shared_processed

def process_pdf(pdf_path, output_dir, pages_to_extract):
    """
    Extract the first 'pages_to_extract' pages from pdf_path and
    write the output to a text file in output_dir.
    Uses the shared cache to avoid duplicate processing.
    """
    try:
        pdf_path = Path(pdf_path)
        key = f"{pdf_path.stem}_pages{pages_to_extract}"
        
        # Check the shared cache
        if key in processed_cache:
            print(f"Skipping {pdf_path.name}: already processed (shared cache).")
            return

        # Construct the output file path
        out_file = Path(output_dir) / f"{key}.txt"
        if out_file.exists():
            print(f"Skipping {pdf_path.name}: output file exists.")
            processed_cache[key] = True  # Update cache so others see it
            return

        # Open the PDF document and extract text
        doc = fitz.open(str(pdf_path))
        total_pages = doc.page_count
        pages = min(pages_to_extract, total_pages)
        extracted_text = []

        for i in range(pages):
            page = doc.load_page(i)
            text = page.get_text("text")
            extracted_text.append(f"Page {i + 1}:\n{text}\n")
        doc.close()

        # Write the extracted text to the output file
        with open(out_file, "w", encoding="utf-8") as f:
            f.write("\n".join(extracted_text))
            
        # Update the shared cache now that processing succeeded
        processed_cache[key] = True
        print(f"Processed {pdf_path.name} -> {out_file.name}")

    except Exception as e:
        print(f"Error processing {pdf_path.name}: {e}")

def process_batch(input_dir, output_dir, pages_to_extract, batch_size, num_processes, shared_processed, file_list=None):
    """
    Process up to batch_size unprocessed PDF files from the input directory.
    If file_list is provided, only files listed in that file are processed.
    """
    input_path = Path(input_dir)
    pdf_files = []

    if file_list:
        # Read the file list and convert each base name to a full PDF path.
        with open(file_list, "r") as f:
            for line in f:
                name = line.strip()
                if name:
                    # Assume the file list names don't include the .pdf extension.
                    pdf_file = input_path / f"{name}.pdf"
                    pdf_files.append(pdf_file)
    else:
        # Otherwise, scan the input_dir for all PDFs.
        pdf_files = sorted([p for p in input_path.iterdir() if p.suffix.lower() == ".pdf"])

    # Filter out files that have been processed already.
    unprocessed_files = []
    for pdf_file in pdf_files:
        key = f"{pdf_file.stem}_pages{pages_to_extract}"
        if key not in shared_processed:
            unprocessed_files.append(pdf_file)

    print(f"Found {len(pdf_files)} PDF files. {len(unprocessed_files)} are unprocessed.")
    files_to_process = unprocessed_files[:batch_size]
    print(f"Processing {len(files_to_process)} unprocessed files with {num_processes} processes.")

    # Create argument tuples for starmap.
    args_list = [(str(pdf_file), output_dir, pages_to_extract) for pdf_file in files_to_process]

    with multiprocessing.Pool(
        processes=num_processes,
        initializer=init_worker,
        initargs=(shared_processed,)
    ) as pool:
        pool.starmap(process_pdf, args_list)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract first N pages from each PDF in a directory (batch mode, multiprocessing enabled)."
    )
    parser.add_argument("input_dir", help="Directory containing PDF files.")
    parser.add_argument("output_dir", help="Directory to store output text files.")
    parser.add_argument(
        "-p", "--pages", type=int, default=1,
        help="Number of pages to extract from each PDF (default: 1)."
    )
    parser.add_argument(
        "-b", "--batch", type=int, default=1000,
        help="Maximum number of files to process for this run (default: 1000)."
    )
    parser.add_argument(
        "-n", "--num_procs", type=int, default=2,
        help="Number of parallel processes to use (default: 2)."
    )
    parser.add_argument(
        "--file_list", type=str, default=None,
        help="Optional file containing list of PDF base names (without extension) to process."
    )
    args = parser.parse_args()

    # Ensure the output directory exists.
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)

    # Build the shared processed-files cache using a Manager.
    with multiprocessing.Manager() as manager:
        shared_processed = manager.dict()

        print("Building initial cache from output directory...")
        # Preload the cache with already processed files.
        for file in Path(args.output_dir).iterdir():
            if file.suffix.lower() == ".txt":
                stem = file.stem.replace(f"_pages{args.pages}", "")
                key = f"{stem}_pages{args.pages}"
                shared_processed[key] = True
        print(f"Found {len(shared_processed)} already processed files in output directory.")

        process_batch(
            args.input_dir,
            args.output_dir,
            args.pages,
            args.batch,
            args.num_procs,
            shared_processed,
            file_list=args.file_list
        )

