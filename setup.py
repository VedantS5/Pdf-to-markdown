from setuptools import setup, find_packages

setup(
    name="pdf-to-markdown",
    version="0.1.0",
    description="A toolkit for converting PDF documents to markdown/text using multiple methods",
    author="FADS Team",
    author_email="vedantshah@iu.edu",
    packages=find_packages(),
    install_requires=[
        "pymupdf>=1.22.0",
    ],
    entry_points={
        'console_scripts': [
            'pdf-to-markdown=pdf_to_markdown:main',
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
)
