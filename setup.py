"""
Setup configuration for refib.
"""
from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="refib",
    version="0.1.0",
    author="David Li",
    author_email="uncorrelited@fastmail.com",
    description="A simple Python retry library using Fibonacci sequence delays",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/uncorrelited/refib",
    packages=find_packages(exclude=["tests*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.6",
    install_requires=[],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "pytest-timeout>=1.4",
            "black>=22.0",
            "flake8>=4.0",
            "mypy>=0.910",
            "tox>=3.24",
        ],
    },
)