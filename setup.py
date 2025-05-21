from setuptools import setup, find_packages

# Read the long description from README.md
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except:
    long_description = "A unified interface for PDF to markdown/text conversion"

setup(
    name="pdf-md-toolkit",  # Updated name based on recommendation
    version="0.1.0",
    description="A toolkit for converting PDF documents to markdown/text using multiple methods",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="FADS Team",
    author_email="vedantshah@iu.edu",
    packages=find_packages(),
    install_requires=[
        "pymupdf>=1.22.0",  # Note: PyMuPDF is under GPL license
    ],
    entry_points={
        'console_scripts': [
            'pdf-md-toolkit=pdf_to_markdown:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # This refers to our wrapper code only
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "Topic :: Text Processing :: Markup",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
    python_requires=">=3.8",
    project_urls={
        "Source": "https://github.com/VedantS5/Pdf-to-markdown",
        "Issue Tracker": "https://github.com/VedantS5/Pdf-to-markdown/issues",
    }
)
