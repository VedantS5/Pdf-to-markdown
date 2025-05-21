# PDF to Markdown Converter

A versatile toolkit for converting PDF documents to markdown/text formats using multiple conversion methods. This project offers three different conversion approaches, each with its own strengths and use cases.

## Features

- **Multiple Conversion Methods**: Choose between three different PDF conversion approaches:
  - **Docling**: Advanced document structure recognition with table support
  - **Marker**: Good formatting preservation with GPU acceleration
  - **PyMuPDF**: Simple, fast text extraction (best for basic needs)

- **Batch Processing**: Process large collections of PDFs efficiently
- **Parallel Processing**: Utilize multiple CPUs/GPUs for faster conversion
- **Skip Processing**: Automatically skip files that have already been processed
- **Flexible Output**: Choose which pages to extract (first N pages or all)

## Quick Start

```bash
# Install the requirements
pip install -r requirements.txt

# Run a simple conversion with PyMuPDF (fastest)
python pdf_to_markdown.py --converter pymu --input /path/to/pdfs --output /path/to/output

# Run with Docling for better document structure recognition
python pdf_to_markdown.py --converter docling --input /path/to/pdfs --output /path/to/output

# Run with Marker (requires marker to be installed separately)
python pdf_to_markdown.py --converter marker --input /path/to/pdfs --output /path/to/output
```

## Installation

### Prerequisites

- Python 3.8+
- For GPU acceleration (Marker only): CUDA 11.7+ and compatible GPU

### Basic Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/VedantS5/Pdf-to-markdown.git
   cd Pdf-to-markdown
   ```

2. Install the base requirements:
   ```bash
   pip install -r requirements.txt
   ```

### Converter-Specific Requirements

#### PyMuPDF (Default)
The base installation includes PyMuPDF. No additional steps required.

#### Docling
```bash
pip install docling
```

#### Marker
Marker requires a separate installation:

1. Install Marker following instructions at: https://github.com/marker-doc/marker
2. Ensure `marker_chunk_convert` is in your PATH

## Usage

### Basic Usage

```bash
python pdf_to_markdown.py --converter [docling|marker|pymu] --input /path/to/pdfs --output /path/to/output
```

### Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--converter` | Conversion method to use (`docling`, `marker`, or `pymu`) | `pymu` |
| `--input` | Directory containing PDF files | (Required) |
| `--output` | Directory to save output files | (Required) |
| `--batch_size` | Number of files to process in a batch | 100 |
| `--num_processes` | Number of parallel processes to use | 4 |
| `--pages` | Number of pages to extract (PyMuPDF only, -1 for all) | -1 |
| `--num_devices` | Number of GPU devices to use (Marker only) | 1 |
| `--num_workers` | Number of workers per device (Marker only) | 16 |

### Conversion Method Comparison

| Method | Strengths | Limitations | Output Format | Speed |
|--------|-----------|-------------|--------------|-------|
| PyMuPDF | Fast, minimal dependencies | Basic text extraction only | Text (.txt) | ★★★★★ |
| Docling | Table structure recognition, good formatting | Slower, more dependencies | Markdown (.md) | ★★★☆☆ |
| Marker | Good formatting, GPU acceleration | Requires separate installation | Markdown (.md) | ★★★★☆ |

### Example Commands

#### Process 50 PDFs with PyMuPDF, extracting only the first 2 pages:

```bash
python pdf_to_markdown.py --converter pymu --input /path/to/pdfs --output /path/to/output --batch_size 50 --pages 2
```

#### Process PDFs with Docling using 8 parallel processes:

```bash
python pdf_to_markdown.py --converter docling --input /path/to/pdfs --output /path/to/output --num_processes 8
```

#### Process PDFs with Marker using 2 GPUs and 32 workers:

```bash
python pdf_to_markdown.py --converter marker --input /path/to/pdfs --output /path/to/output --num_devices 2 --num_workers 32
```

## Implementation Details

### PyMuPDF Converter

The PyMuPDF converter is a simple but fast text extractor based on the PyMuPDF library. It extracts raw text from PDF documents with minimal formatting. It's the fastest option and works well for simple PDFs where structure isn't critical.

Key features:
- Parallel processing with multiprocessing
- Page selection (first N pages or all)
- Fastest conversion method

### Docling Converter

The Docling converter uses the Docling library for document understanding. It preserves document structure better and can handle tables. This method produces higher quality markdown output but is slower.

Key features:
- Table structure recognition
- Better handling of document structure
- Outputs to Markdown format

### Marker Converter

The Marker converter uses the Marker document conversion system, which offers GPU acceleration. It's a middle ground in terms of speed and quality.

Key features:
- GPU acceleration for faster processing
- Good formatting preservation
- Requires separate installation

## Contributing

Contributions are welcome! Here are ways you can contribute:

1. Report bugs and issues
2. Add new conversion methods
3. Improve documentation
4. Optimize existing code

## License Notice

This wrapper code is licensed under the MIT License - see the LICENSE file for details. However, this project depends on several tools that have their own licenses:

- **PyMuPDF**: GNU GPL v3 license - [PyMuPDF License](https://github.com/pymupdf/PyMuPDF/blob/master/COPYING)
- **Docling**: Proprietary license - Commercial use may require a license
- **Marker**: Open-source license - [Marker License](https://github.com/marker-doc/marker/blob/main/LICENSE)

Users must comply with all relevant licenses when using this software. This is especially important if you're using this software for commercial purposes.

## Disclaimer

This project is a wrapper that provides a unified interface to existing tools. The authors of this wrapper are not affiliated with the creators of the underlying tools. Use at your own risk and ensure you comply with the licenses of all underlying dependencies.

## Acknowledgments

- [PyMuPDF](https://github.com/pymupdf/PyMuPDF) for the fast PDF processing capabilities
- [Docling](https://github.com/docling) for document structure analysis
- [Marker](https://github.com/marker-doc/marker) for GPU-accelerated conversion
