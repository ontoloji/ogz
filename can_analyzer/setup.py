"""
CAN Bus Analyzer - Windows Setup Script
"""
from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="can-bus-analyzer",
    version="1.0.0",
    author="CAN Tools Developer",
    description="Windows CAN Bus Data Analysis Tool with Kvaser Support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/ontoloji/ogz",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Embedded Systems",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: Microsoft :: Windows :: Windows 10",
        "Operating System :: Microsoft :: Windows :: Windows 11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "python-can>=4.3.1",
        "cantools>=39.4.0",
        "PyQt5>=5.15.10",
        "pandas>=2.1.4",
        "numpy>=1.26.2",
        "matplotlib>=3.8.2",
        "pyqtgraph>=0.13.3",
        "openpyxl>=3.1.2",
        "xlsxwriter>=3.1.9",
        "pywin32>=306",
        "python-dateutil>=2.8.2",
    ],
    entry_points={
        "console_scripts": [
            "can-analyzer=can_analyzer.main:main",
        ],
    },
    package_data={
        "can_analyzer": ["resources/icons/*"],
    },
)
