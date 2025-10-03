from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cinestyle",
    version="0.1.0",
    author="David Burton",
    author_email="",
    description="Create stylized data visualizations inspired by iconic film aesthetics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Burton-David/cinematic-matplotlib",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "matplotlib>=3.3.0",
        "numpy>=1.19.0",
    ],
)
