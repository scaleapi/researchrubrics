# File Manifest

This document lists all files included in the Deep Research Benchmarks release and their purposes.

## 📋 Core Documentation

### README.md
**Purpose**: Main documentation and entry point  
**Content**: Overview, quick start, usage instructions, repository structure  
**Audience**: All users  
**Read**: START HERE

### QUICKSTART.md
**Purpose**: Quick start guide with practical examples  
**Content**: Step-by-step tutorials, code examples, common use cases  
**Audience**: New users wanting to get started quickly  
**Read**: After README.md

### INSTALLATION.md
**Purpose**: Detailed installation instructions  
**Content**: System requirements, multiple installation methods, troubleshooting  
**Audience**: Users setting up the environment  
**Read**: Before running any code

### DATA_FORMAT.md
**Purpose**: Data format specifications  
**Content**: Input/output formats, schema definitions, validation rules  
**Audience**: Users working with custom datasets  
**Read**: When preparing your own data

## 🛠️ Configuration Files

### requirements.txt
**Purpose**: Python dependencies  
**Content**: List of required packages with version constraints  
**Usage**: `pip install -r requirements.txt`  
**Type**: Installation file

### .env.example
**Purpose**: Environment variables template  
**Content**: API keys, configuration options  
**Usage**: Copy to `.env` and fill in your values  
**Type**: Configuration template

### setup.py
**Purpose**: Package installation configuration  
**Content**: Package metadata, dependencies, entry points  
**Usage**: `pip install -e .` for development install  
**Type**: Python package configuration

### .gitignore
**Purpose**: Git version control exclusions  
**Content**: Files and directories to exclude from version control  
**Usage**: Automatically used by Git  
**Type**: Version control configuration

## 📖 Additional Documentation

### CONTRIBUTING.md
**Purpose**: Contribution guidelines  
**Content**: Development setup, code style, pull request process  
**Audience**: Contributors and developers  
**Read**: Before contributing code

### CHANGELOG.md
**Purpose**: Version history  
**Content**: Changes, additions, and fixes in each version  
**Audience**: Users tracking updates  
**Read**: When upgrading versions

### CITATION.bib
**Purpose**: Academic citation information  
**Content**: BibTeX citation for the paper  
**Audience**: Researchers citing this work  
**Usage**: Copy and paste into your bibliography

### LICENSE
**Purpose**: Software license  
**Content**: MIT License terms  
**Audience**: Anyone using or distributing the code  
**Read**: To understand usage rights

## 🎯 Evaluation Prompts

### prompts/ternary/system_prompt.txt
**Purpose**: System prompt for ternary evaluation  
**Content**: Instructions for evaluating with 3 classes (Satisfied/Partially/Not)  
**Usage**: Loaded automatically by evaluation scripts  
**Type**: LLM prompt template

### prompts/ternary/user_prompt_template.txt
**Purpose**: User prompt template for ternary evaluation  
**Content**: Template for rubric evaluation requests (3 classes)  
**Usage**: Loaded and formatted by evaluation scripts  
**Type**: LLM prompt template

### prompts/binary/system_prompt.txt
**Purpose**: System prompt for binary evaluation  
**Content**: Instructions for evaluating with 2 classes (Satisfied/Not Satisfied)  
**Usage**: Loaded automatically when binary=True  
**Type**: LLM prompt template

### prompts/binary/user_prompt_template.txt
**Purpose**: User prompt template for binary evaluation  
**Content**: Template for rubric evaluation requests (2 classes)  
**Usage**: Loaded and formatted when binary=True  
**Type**: LLM prompt template

## 📂 Directory Structure (Expected)

While not included in this release package, the following directories should be created:

```
public_release_experiments/
├── src/                          # Source code (your codebase)
│   ├── extract_rubrics/          # Rubric extraction scripts
│   ├── evaluate_rubrics/         # LLM evaluation scripts
│   └── calculate_metrics/        # Metrics calculation scripts
├── data/                         # Data directory
│   ├── raw_csvs/                 # Input: Raw CSV files
│   ├── processed_df/             # Output: Compiled datasets
│   ├── PDFs/                     # Downloaded PDFs
│   └── predownloaded_pdfs/       # Optional: Pre-downloaded PDFs
├── results/                      # Evaluation results
├── cache/                        # Cached conversions
└── tests/                        # Test files (optional)
```

## 📊 File Sizes (Approximate)

| File | Size | Type |
|------|------|------|
| README.md | ~9 KB | Markdown |
| QUICKSTART.md | ~5 KB | Markdown |
| INSTALLATION.md | ~8 KB | Markdown |
| DATA_FORMAT.md | ~9 KB | Markdown |
| CONTRIBUTING.md | ~3 KB | Markdown |
| requirements.txt | ~0.5 KB | Text |
| setup.py | ~2 KB | Python |
| .env.example | ~0.4 KB | Text |
| LICENSE | ~1 KB | Text |
| CHANGELOG.md | ~2 KB | Markdown |
| CITATION.bib | ~0.3 KB | BibTeX |
| .gitignore | ~0.9 KB | Text |
| Prompts (all) | ~2 KB | Text |
| **Total** | **~43 KB** | - |

## 🔄 File Dependencies

### Installation Flow
1. Read `README.md`
2. Follow `INSTALLATION.md`
3. Configure `.env` from `.env.example`
4. Install using `requirements.txt` or `setup.py`

### Usage Flow
1. Read `QUICKSTART.md`
2. Prepare data according to `DATA_FORMAT.md`
3. Run scripts (which use `prompts/`)
4. Analyze results

### Development Flow
1. Read `CONTRIBUTING.md`
2. Setup dev environment from `requirements.txt` + dev tools
3. Follow code style in `CONTRIBUTING.md`
4. Update `CHANGELOG.md` with changes

## 📝 Customization Guide

### Which Files to Modify

**For Your Institution/Project**:
- `README.md`: Update author information, contact details, repository URL
- `CITATION.bib`: Add actual authors and publication details
- `LICENSE`: Update copyright holder and year
- `setup.py`: Update package metadata and URLs

**For Configuration**:
- `.env`: Add your actual API keys (don't commit this!)
- `requirements.txt`: Add or update dependencies as needed

**For Custom Evaluation**:
- `prompts/`: Modify prompts to match your evaluation criteria
- `DATA_FORMAT.md`: Document any custom data formats

**Don't Modify** (unless necessary):
- `.gitignore`: Standard exclusions work for most cases
- `CONTRIBUTING.md`: Generic guidelines applicable to most projects

## 🔍 Finding Information

**"How do I install?"** → `INSTALLATION.md`  
**"How do I run it?"** → `QUICKSTART.md`  
**"What's the data format?"** → `DATA_FORMAT.md`  
**"How do I contribute?"** → `CONTRIBUTING.md`  
**"What's the license?"** → `LICENSE`  
**"How do I cite?"** → `CITATION.bib`  
**"What changed?"** → `CHANGELOG.md`  
**"What's this project?"** → `README.md`

## ✅ Pre-Release Checklist

Before releasing, ensure:

- [ ] Update `README.md` with correct repository URL
- [ ] Fill in actual authors in `CITATION.bib`
- [ ] Update copyright year in `LICENSE`
- [ ] Verify all URLs in documentation
- [ ] Update contact information
- [ ] Set correct version in `setup.py` and `CHANGELOG.md`
- [ ] Test installation instructions
- [ ] Verify all example code works
- [ ] Remove any sensitive information
- [ ] Update `.env.example` with correct variables

## 📞 Support

For questions about specific files:
- **Installation issues**: See `INSTALLATION.md` troubleshooting section
- **Usage questions**: Check `QUICKSTART.md` examples
- **Data format**: Refer to `DATA_FORMAT.md`
- **Contributing**: Read `CONTRIBUTING.md`
- **Other**: Open an issue or contact maintainers

## 📦 Distribution

When distributing this code release:

1. **Include all files listed above**
2. **Do NOT include**:
   - `.env` (with actual keys)
   - `data/` directories with actual data
   - `cache/` directory
   - `results/` directory
   - `__pycache__/` directories
3. **Optional to include**:
   - Sample datasets (if license permits)
   - Example notebooks
   - Test files

## 🔗 Related Files (Not in This Package)

These files are part of your codebase but documented separately:

- `src/extract_rubrics/*.py`: Rubric extraction scripts
- `src/evaluate_rubrics/*.py`: Evaluation scripts
- `src/calculate_metrics/*.py`: Metrics calculation scripts

See the source code documentation and README.md for details on these files.

---

**Last Updated**: 2025-01-XX  
**Version**: 1.0.0  
**Maintained By**: [Maintainer Name/Team]
