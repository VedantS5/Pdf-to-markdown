#!/usr/bin/env python3
import os
import argparse
import fitz  # PyMuPDF
import multiprocessing
from pathlib import Path

def init_worker(shared_processed):
    """Initialize worker process with shared cache"""
    global processed_cache
    processed_cache = shared_processed

def process_pdf(pdf_path, output_dir, pages_to_extract):
    """
    Extract the first 'pages_to_extract' pages from pdf_path and
    write the output to a text file in output_dir.
    Uses shared cache to track processed files.
    """
    try:
        pdf_path = Path(pdf_path)
        # Create key for cache
        pages_label = "all" if pages_to_extract < 0 else str(pages_to_extract)
        key = f"{pdf_path.stem}_pages{pages_label}"

        
        # Check shared cache first
        if key in processed_cache:
            print(f"Skipping {pdf_path.name}: already processed (shared cache).")
            return

        # Construct output file name
        out_file = Path(output_dir) / f"{key}.txt"
        if out_file.exists():
            print(f"Skipping {pdf_path.name}: output file exists.")
            processed_cache[key] = True  # Update cache
            return

        # Open the PDF document
        doc = fitz.open(str(pdf_path))
        total_pages = doc.page_count
        if pages_to_extract < 0:
            pages = total_pages
        else:
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
        
        # Update shared cache after successful processing
        processed_cache[key] = True
        print(f"Processed {pdf_path.name} -> {out_file.name}")
        
    except Exception as e:
        print(f"Error processing {pdf_path.name}: {e}")

def process_batch(input_dir, output_dir, pages_to_extract, batch_size, num_processes, shared_processed):
    """
    Process up to batch_size unprocessed PDF files from input_dir using multiple processes.
    Uses shared cache to track processed files.
    """
    input_path = Path(input_dir)
    # Gather and sort all PDF files in input directory
    pdf_files = sorted([p for p in input_path.iterdir() if p.suffix.lower() == ".pdf"])

    # Create a list of unprocessed PDFs using shared cache
    unprocessed_files = []
    for pdf_file in pdf_files:
        key = f"{pdf_file.stem}_pages{pages_to_extract}"
        if key not in shared_processed:
            unprocessed_files.append(pdf_file)

    print(f"Found {len(pdf_files)} PDF files. {len(unprocessed_files)} are unprocessed.")
    files_to_process = unprocessed_files[:batch_size]
    print(f"Processing {len(files_to_process)} unprocessed files with {num_processes} processes.")

    # Prepare argument tuples for each file
    args_list = [(str(pdf_file), output_dir, pages_to_extract) for pdf_file in files_to_process]
    
    # Create a pool of worker processes with shared cache
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
        "-p", "--pages", type=int, default=-1,
        help="Number of pages to extract from each PDF. Use 1 to extract only the first page; default (-1) processes the entire PDF."
    )
    parser.add_argument(
        "-b", "--batch", type=int, default=1000,
        help="Maximum number of files to process for this run (default: 1000)."
    )
    parser.add_argument(
        "-n", "--num_procs", type=int, default=2,
        help="Number of parallel processes to use (default: 2)."
    )
    args = parser.parse_args()

    # Ensure output directory exists
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)
    
    # Create a manager to hold our shared processed files cache
    with multiprocessing.Manager() as manager:
        shared_processed = manager.dict()
        
        # Preload the shared cache with existing processed files
        print("Building initial cache from output directory...")
        for file in Path(args.output_dir).iterdir():
            if file.suffix.lower() == ".txt":
                # Extract the original stem without the _pagesN suffix
                stem = file.stem.replace(f"_pages{args.pages}", "")
                key = f"{stem}_pages{args.pages}"
                shared_processed[key] = True
        print(f"Found {len(shared_processed)} already processed files in output directory.")
        
        # Process the batch with shared cache
        process_batch(
            args.input_dir,
            args.output_dir,
            args.pages,
            args.batch,
            args.num_procs,
            shared_processed
        )

