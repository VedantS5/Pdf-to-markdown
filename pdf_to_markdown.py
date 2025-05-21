#!/usr/bin/env python3
"""
PDF to Markdown Converter Tool

This script provides a unified interface to convert PDF files to markdown/text
using different conversion methods: Docling, Marker, or PyMuPDF.

Each method has different strengths and capabilities:
- docling: Advanced document structure recognition with table support
- marker: Marker-based conversion with good formatting preservation
- pymu: Simple text extraction using PyMuPDF (fastest option)
"""

import os
import argparse
import sys
import subprocess
from pathlib import Path


def check_dependencies(converter):
    """Check if the required dependencies are installed for the selected converter"""
    if converter == "docling":
        try:
            import docling
            return True
        except ImportError:
            print("Docling is not installed. Install it with: pip install docling")
            return False
    elif converter == "marker":
        try:
            # Check if marker_chunk_convert is available in PATH
            subprocess.run(["marker_chunk_convert", "--help"], 
                          stdout=subprocess.PIPE, 
                          stderr=subprocess.PIPE)
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            print("Marker is not installed or not in PATH.")
            print("Install it following instructions at: https://github.com/VedantS5/Pdf-to-markdown")
            return False
    elif converter == "pymu":
        try:
            import fitz
            return True
        except ImportError:
            print("PyMuPDF is not installed. Install it with: pip install pymupdf")
            return False
    return False


def run_docling_converter(input_path, output_path, batch_size, num_processes):
    """Run the Docling PDF to Markdown converter"""
    # We'll import the module dynamically later in the function

    # Make sure paths are absolute
    input_abs = os.path.abspath(input_path)
    output_abs = os.path.abspath(output_path)
    
    # Create args object similar to what argparse would create
    class Args:
        input = input_abs
        output = output_abs
        batch_size = batch_size
        num_processes = num_processes
    
    # Call the docling main function with our args
    print(f"Running Docling converter with {num_processes} processes")
    print(f"Input: {input_abs}")
    print(f"Output: {output_abs}")
    print(f"Batch size: {batch_size}")
    
    # Run the converter using importlib for modules with numeric prefixes
    import importlib.util
    module_path = os.path.join(os.path.dirname(__file__), "docling/01_docling_pdf_to_md.py")
    spec = importlib.util.spec_from_file_location("docling_module", module_path)
    docling_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(docling_module)
    docling_main = docling_module.main
    
    # Save original argv and restore after
    original_argv = sys.argv
    sys.argv = [
        "docling_converter",
        "--input", input_abs,
        "--output", output_abs,
        "--batch_size", str(batch_size),
        "--num_processes", str(num_processes)
    ]
    
    try:
        docling_main()
    finally:
        sys.argv = original_argv


def run_marker_converter(input_path, output_path, batch_size, num_devices, num_workers):
    """Run the Marker PDF to Markdown converter"""
    # Make sure paths are absolute
    input_abs = os.path.abspath(input_path)
    output_abs = os.path.abspath(output_path)
    
    print(f"Running Marker converter with {num_devices} devices and {num_workers} workers")
    print(f"Input: {input_abs}")
    print(f"Output: {output_abs}")
    print(f"Batch size: {batch_size}")
    
    # Import marker module using importlib
    import importlib.util
    module_path = os.path.join(os.path.dirname(__file__), "marker/01_marker_pdf_to_md_wrapper.py")
    spec = importlib.util.spec_from_file_location("marker_module", module_path)
    marker_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(marker_module)
    marker_main = marker_module.main
    
    # Save original argv and restore after
    original_argv = sys.argv
    sys.argv = [
        "marker_wrapper",
        "--input_dir", input_abs,
        "--output_dir", output_abs,
        "--batch_size", str(batch_size),
        "--num_devices", str(num_devices),
        "--num_workers", str(num_workers)
    ]
    
    try:
        marker_main()
    finally:
        sys.argv = original_argv


def run_pymu_converter(input_path, output_path, pages, batch_size, num_processes):
    """Run the PyMuPDF PDF to Text converter"""
    # Make sure paths are absolute
    input_abs = os.path.abspath(input_path)
    output_abs = os.path.abspath(output_path)
    
    print(f"Running PyMuPDF converter with {num_processes} processes")
    print(f"Input: {input_abs}")
    print(f"Output: {output_abs}")
    print(f"Pages to extract: {pages}")
    print(f"Batch size: {batch_size}")
    
    # Import pymu module using importlib
    import importlib.util
    module_path = os.path.join(os.path.dirname(__file__), "pymu/01_pymu_pdf_to_text.py")
    spec = importlib.util.spec_from_file_location("pymu_module", module_path)
    pymu_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(pymu_module)
    pymu_main = pymu_module.main
    
    # Save original argv and restore after
    original_argv = sys.argv
    sys.argv = [
        "pymu_converter",
        input_abs,
        output_abs,
        "--pages", str(pages),
        "--batch", str(batch_size),
        "--num_procs", str(num_processes)
    ]
    
    try:
        pymu_main()
    finally:
        sys.argv = original_argv


def main():
    parser = argparse.ArgumentParser(
        description="Convert PDF files to markdown or text using various methods."
    )
    parser.add_argument(
        "--converter",
        choices=["docling", "marker", "pymu"],
        default="pymu",
        help="Converter to use (default: pymu)"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to input directory containing PDF files"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to output directory for markdown/text files"
    )
    parser.add_argument(
        "--batch_size",
        type=int,
        default=100,
        help="Number of files to process in a batch (default: 100)"
    )
    parser.add_argument(
        "--num_processes",
        type=int,
        default=4,
        help="Number of parallel processes to use (default: 4)"
    )
    parser.add_argument(
        "--pages",
        type=int,
        default=-1,
        help="Number of pages to extract (pymu only, -1 for all pages, default: -1)"
    )
    parser.add_argument(
        "--num_devices",
        type=int,
        default=1,
        help="Number of devices to use (marker only, default: 1)"
    )
    parser.add_argument(
        "--num_workers",
        type=int,
        default=16,
        help="Number of workers per device (marker only, default: 16)"
    )
    
    args = parser.parse_args()
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output, exist_ok=True)
    
    # Check that the converter's dependencies are installed
    if not check_dependencies(args.converter):
        return 1
    
    # Run the selected converter
    if args.converter == "docling":
        run_docling_converter(args.input, args.output, args.batch_size, args.num_processes)
    elif args.converter == "marker":
        run_marker_converter(args.input, args.output, args.batch_size, args.num_devices, args.num_workers)
    elif args.converter == "pymu":
        run_pymu_converter(args.input, args.output, args.pages, args.batch_size, args.num_processes)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
