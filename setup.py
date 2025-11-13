from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding="utf-8")

setup(
    name="research-rubrics",
    version="1.0.0",
    author="Manasi Sharma et al.",
    author_email="manasi.sharma@scale.com",
    description="ResearchRubrics: A Benchmark of Prompts and Rubrics For Evaluating Deep Research Agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/scaleapi/researchrubrics",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas>=1.3.0",
        "numpy>=1.20.0",
        "litellm>=1.0.0",
        "markitdown>=0.1.0",
        "PyPDF2>=3.0.0",
        "scikit-learn>=1.0.0",
        "tqdm>=4.60.0",
        "requests>=2.25.0",
        "pyarrow>=10.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.20.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "extract-rubrics=extract_rubrics.extract_rubrics_batch:main",
            "evaluate-rubrics=evaluate_rubrics.evaluate_rubrics_batch:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
