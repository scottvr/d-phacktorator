from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="dphackt",
    version="0.1.0",
    author="Scott VanRavenswaay",
    author_email="scottvr@gmail.com",
    description="A flexible data analysis library for handling various datasets and performing analyses. Developed in supprt of the D-phacktorator.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/scottvr/d-phacktorator",
    packages=find_packages(exclude=["tests", "examples"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers, Data Scientists, Digital Humorists",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pandas>=1.0.0",
        "numpy>=1.18.0",
        "matplotlib>=3.0.0",
    ],
)