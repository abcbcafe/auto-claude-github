#!/usr/bin/env python3
"""Setup script for ClaudeUp."""

from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="claudeup",
    version="1.0.0",
    author="ClaudeUp Contributors",
    description="Automate GitHub repository creation for Claude Code Web",
    long_description=long_description,
    long_description_content_type="text/markdown",
    py_modules=["claudeup"],
    install_requires=[
        "requests>=2.31.0",
    ],
    entry_points={
        "console_scripts": [
            "claudeup=claudeup:main",
        ],
    },
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Version Control :: Git",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
