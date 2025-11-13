# File Manifest

This document lists all files included in the Research Rubrics release and their purposes.

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
**Content**: System requirements, installation methods, troubleshooting  
**Audience**: Users setting up the environment  
**Read**: Before running any code

### DATA_FORMAT.md
**Purpose**: Data format specifications  
**Content**: Input/output formats, JSONL structure, validation rules  
**Audience**: Users working with the data  
**Read**: When preparing or analyzing data

### FOLDER_STRUCTURE.md
**Purpose**: Directory organization guide  
**Content**: Complete directory tree, setup instructions, path references  
**Audience**: Users setting up the project  
**Read**: During initial setup

### FILE_MANIFEST.md
**Purpose**: File index (this document)  
**Content**: List and description of all files  
**Audience**: Users wanting a complete overview  
**Read**: For reference

### SETUP_GUIDE.md
**Purpose**: Step-by-step setup instructions  
**Content**: Complete setup workflow from scratch  
**Audience**: New users  
**Read**: First time setup

### PACKAGE_SUMMARY.md
**Purpose**: Package overview  
**Content**: Summary of package contents and structure  
**Audience**: All users  
**Read**: For a high-level overview

## 🛠️ Configuration Files

### requirements.txt
**Purpose**: Python dependencies  
**Content**: List of required packages (pandas, litellm, tqdm, etc.)  
**Usage**: `pip install -r requirements.txt`  
**Type**: Installation file

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

### .env (user-created)
**Purpose**: API credentials  
**Content**: LITELLM_API_KEY=your_key_here  
**Usage**: Created by user, never committed  
**Type**: Configuration file

## 📖 Additional Documentation

### LICENSE
**Purpose**: Software license  
**Content**: MIT License terms  
**Audience**: Anyone using or distributing the code  
**Read**: To understand usage rights

### CITATION.bib
**Purpose**: Academic citation information  
**Content**: BibTeX citation for the paper  
**Audience**: Researchers citing this work  
**Usage**: Copy and paste into your bibliography

## 🎯 Evaluation Prompts

### src/prompts/system_prompt.txt
**Purpose**: System prompt for rubric evaluation  
**Content**: Instructions for the LLM evaluator  
**Usage**: Loaded automatically by evaluation scripts  
**Type**: LLM prompt template

### src/prompts/user_prompt.txt
**Purpose**: User prompt template for evaluation  
**Content**: Template for rubric evaluation requests  
**Usage**: Loaded and formatted by evaluation scripts  
**Type**: LLM prompt template

### src/prompts/chunk_prompt_template.txt
**Purpose**: Prompt for evaluating document chunks  
**Content**: Template for chunk-level evaluation  
**Usage**: Used when documents exceed token limits  
**Type**: LLM prompt template

### src/prompts/synthesis_prompt_template.txt
**Purpose**: Prompt for synthesizing chunk evaluations  
**Content**: Template for combining chunk results  
**Usage**: Used to create final verdict from chunks  
**Type**: LLM prompt template

## 📂 Source Code Files

### src/evaluate_rubrics/evaluate_single_report.py
**Purpose**: Single report evaluation  
**Content**: `RubricEvaluator` class and `evaluate_task_rubrics` function  
**Usage**: Evaluate one markdown file against its rubrics  
**Type**: Python module

### src/evaluate_rubrics/evaluate_reports_batch.py
**Purpose**: Batch evaluation script  
**Content**: Process all markdown files in `agent_responses/`  
**Usage**: `python evaluate_reports_batch.py`  
**Type**: Python script

### src/calculate_metrics/calculate_compliance_score.py
**Purpose**: Compliance score calculation  
**Content**: Calculate weighted compliance scores from evaluation results  
**Usage**: `python calculate_compliance_score.py`  
**Type**: Python script

### src/__init__.py
**Purpose**: Package marker  
**Content**: (typically empty)  
**Type**: Python package file

### tests/__init__.py
**Purpose**: Test package marker  
**Content**: (typically empty)  
**Type**: Python package file

## 📊 Data Files (Expected Structure)

### data/researchrubrics/processed_data.jsonl
**Purpose**: Input data with rubrics and metadata  
**Content**: One JSON object per line with prompts, sample IDs, and rubrics  
**Format**: JSONL (JSON Lines)  
**Type**: Input data file

### data/researchrubrics/README.md
**Purpose**: Dataset documentation template  
**Content**: Hugging Face dataset card template  
**Type**: Documentation

### agent_responses/[sample_id].md
**Purpose**: AI-generated research reports to evaluate  
**Content**: Markdown-formatted research documents  
**Format**: Markdown  
**Type**: Input files

### results/batch_evaluation_YYYYMMDD_HHMMSS.jsonl
**Purpose**: Evaluation results  
**Content**: One evaluation result per line  
**Format**: JSONL  
**Type**: Output file

## 📝 File Count Summary

**Total Documentation**: 8 files  
**Total Configuration**: 3 files  
**Total Prompts**: 4 files  
**Total Source Code**: 4 Python files  
**Total Package Markers**: 2 files  
**Expected Data Files**: Variable (3 sample markdown files in current repo)

## 🔍 Finding Information

**"How do I install?"** → `INSTALLATION.md`  
**"How do I run it?"** → `QUICKSTART.md`  
**"What's the data format?"** → `DATA_FORMAT.md`  
**"What's this project?"** → `README.md`  
**"How do I set up?"** → `SETUP_GUIDE.md` or `FOLDER_STRUCTURE.md`  
**"What's the license?"** → `LICENSE`  
**"How do I cite?"** → `CITATION.bib`  
**"What files are there?"** → This file (`FILE_MANIFEST.md`)

## 📦 Distribution

When distributing this code release:

### Include:
- ✅ All documentation files (8 files)
- ✅ All configuration templates (requirements.txt, setup.py, .gitignore)
- ✅ All source code (src/ directory)
- ✅ All prompt templates (src/prompts/)
- ✅ Empty directory structure (data/, agent_responses/, results/, cache/, tests/)
- ✅ LICENSE and CITATION.bib

### Do NOT Include:
- ❌ `.env` (with actual API keys)
- ❌ Actual data files (unless publicly shareable)
- ❌ `cache/` contents
- ❌ `results/` with actual evaluation outputs
- ❌ `__pycache__/` directories
- ❌ `.pyc` files

## ✅ Verification Checklist

After setup, ensure:
- [ ] All 8 documentation files present in root
- [ ] requirements.txt, setup.py, .gitignore in root
- [ ] All 4 prompt files in `src/prompts/`
- [ ] 2 evaluation scripts in `src/evaluate_rubrics/`
- [ ] 1 metrics script in `src/calculate_metrics/`
- [ ] `.env` created with LITELLM_API_KEY
- [ ] `data/researchrubrics/processed_data.jsonl` exists
- [ ] Markdown files in `agent_responses/`
- [ ] Dependencies installed

---

**Last Updated**: 2025-11-13  
**Version**: 1.0.0
