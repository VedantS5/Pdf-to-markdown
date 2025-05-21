#!/usr/bin/env python3
import os
import argparse
import subprocess
import glob
import shutil

def main():
    parser = argparse.ArgumentParser(description="Wrapper for marker_chunk_convert with batch functionality")
    parser.add_argument("--input_dir", default="/N/project/fads_ng/analyst_reports_project/data/analyst_reports_pdf", help="Directory containing PDF files")
    parser.add_argument("--output_dir", required=True, help="Directory for Markdown output")
    parser.add_argument("--batch_size", type=int, required=True, help="Number of PDF files to process in this batch")
    parser.add_argument("--num_devices", default="1", help="Number of devices to use (default: 1)")
    parser.add_argument("--num_workers", default="16", help="Number of workers to use (default: 16)")
    parser.add_argument("--marker_command", default="marker_chunk_convert", help="Marker command name (default: marker_chunk_convert)")
    args = parser.parse_args()

    # Gather PDF files that have not yet been converted.
    batch_files = []
    pdf_files = sorted(glob.glob(os.path.join(args.input_dir, "*.pdf")))
    for pdf_file in pdf_files:
        base = os.path.basename(pdf_file)
        # Assumes the output file uses the same base name with a '.md' extension.
        output_file = os.path.join(args.output_dir, os.path.splitext(base)[0] + ".md")
        if not os.path.exists(output_file):
            batch_files.append(pdf_file)
            if len(batch_files) >= args.batch_size:
                break

    if not batch_files:
        print("No new PDF files to process.")
        return

    # Create a temporary directory for the batch.
    tmp_input = os.path.join(args.input_dir, "tmp_batch")
    os.makedirs(tmp_input, exist_ok=True)

    # Instead of copying, we create symbolic links to the files in the batch.
    for f in batch_files:
        basename = os.path.basename(f)
        link_path = os.path.join(tmp_input, basename)
        if not os.path.exists(link_path):
            os.symlink(os.path.abspath(f), link_path)

    # Build and run the marker conversion command.
    cmd = [args.marker_command, tmp_input, args.output_dir]
    env = os.environ.copy()
    env["NUM_DEVICES"] = str(args.num_devices)
    env["NUM_WORKERS"] = str(args.num_workers)
    print("Executing command: " + " ".join(cmd))
    subprocess.run(cmd, env=env)

    # Clean up the temporary directory.
    shutil.rmtree(tmp_input)
    print("Batch processing complete.")

if __name__ == "__main__":
    main()
