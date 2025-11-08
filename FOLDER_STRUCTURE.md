# Deep Research Benchmarks - Folder Structure

This document describes the complete folder structure for the Deep Research Benchmarks release.

## 📁 Complete Directory Structure

```
public_release_experiments/
│
├── 📄 Documentation Files (root level)
│   ├── README.md                      # Main documentation
│   ├── QUICKSTART.md                  # Quick start guide
│   ├── INSTALLATION.md                # Installation guide
│   ├── DATA_FORMAT.md                 # Data format specifications
│   ├── CONTRIBUTING.md                # Contribution guidelines
│   ├── CHANGELOG.md                   # Version history
│   ├── FILE_MANIFEST.md               # File index
│   ├── LICENSE                        # MIT License
│   └── CITATION.bib                   # BibTeX citation
│
├── ⚙️ Configuration Files (root level)
│   ├── requirements.txt               # Python dependencies
│   ├── setup.py                       # Package configuration
│   ├── .env.example                   # Environment template
│   ├── .env                           # Your API keys (DO NOT COMMIT)
│   └── .gitignore                     # Git exclusions
│
├── 📦 src/                            # Source code
│   │
│   ├── extract_rubrics/               # Rubric extraction module
│   │   ├── __init__.py                # Package marker (optional)
│   │   ├── extract_rubrics_batch.py   # Batch extraction script
│   │   └── extract_rubrics_markitdown_onetask.py  # Single task extractor
│   │
│   ├── evaluate_rubrics/              # Rubric evaluation module
│   │   ├── __init__.py                # Package marker (optional)
│   │   ├── evaluate_rubrics_batch.py  # Batch evaluation script
│   │   ├── evaluate_rubrics_markitdown_onetask.py  # Single task evaluator
│   │   └── prompts/                   # Evaluation prompts
│   │       ├── binary/                # Binary evaluation prompts
│   │       │   ├── system_prompt.txt
│   │       │   └── user_prompt_template.txt
│   │       └── ternary/               # Ternary evaluation prompts
│   │           ├── system_prompt.txt
│   │           └── user_prompt_template.txt
│   │
│   └── calculate_metrics/             # Metrics calculation module
│       ├── __init__.py                # Package marker (optional)
│       ├── calculate_F1_score.py      # F1 score calculation
│       ├── calculate_final_score.py   # Weighted score calculation
│       └── calculate_failure_breakdown.py  # Failure analysis
│
├── 📊 data/                           # Data directory
│   ├── raw_csvs/                      # Input: Raw CSV files
│   │   └── [your_csv_files.csv]
│   ├── processed_df/                  # Output: Compiled datasets
│   │   ├── compiled_dataset.csv
│   │   └── compiled_dataset.parquet
│   ├── PDFs/                          # Downloaded/generated PDFs
│   │   └── [task_name]/               # One directory per task
│   │       ├── gemini.pdf
│   │       ├── chatgpt.pdf
│   │       └── perplexity.pdf
│   └── predownloaded_pdfs/           # Optional: Pre-downloaded PDFs
│       └── [task_name]/
│           ├── gemini.pdf
│           ├── chatgpt.pdf
│           └── perplexity.pdf
│
├── 📈 results/                        # Evaluation results
│   └── [mm_dd]/                       # Results by date
│       └── [timestamp]/               # Results by timestamp
│           └── processed_df/
│               ├── compiled_dataset.csv
│               └── compiled_dataset.parquet
│
├── 💾 cache/                          # Cached conversions
│   └── [hash].md                      # Cached markdown conversions
│
└── 🧪 tests/                          # Test files (optional)
    ├── __init__.py
    ├── test_extract_rubrics.py
    ├── test_evaluate_rubrics.py
    └── test_calculate_metrics.py
```

## 📋 Setup Instructions

### Step 1: Create Base Structure

```bash
# Navigate to your project root
cd public_release_experiments

# Create all required directories
mkdir -p src/extract_rubrics
mkdir -p src/evaluate_rubrics/prompts/binary
mkdir -p src/evaluate_rubrics/prompts/ternary
mkdir -p src/calculate_metrics
mkdir -p data/raw_csvs
mkdir -p data/processed_df
mkdir -p data/PDFs
mkdir -p data/predownloaded_pdfs
mkdir -p results
mkdir -p cache
mkdir -p tests
```

### Step 2: Place Documentation Files

All documentation files go in the root `public_release_experiments/` directory:

```bash
# In public_release_experiments/
cp /path/to/README.md .
cp /path/to/QUICKSTART.md .
cp /path/to/INSTALLATION.md .
cp /path/to/DATA_FORMAT.md .
cp /path/to/CONTRIBUTING.md .
cp /path/to/CHANGELOG.md .
cp /path/to/FILE_MANIFEST.md .
cp /path/to/LICENSE .
cp /path/to/CITATION.bib .
```

### Step 3: Place Configuration Files

```bash
# In public_release_experiments/
cp /path/to/requirements.txt .
cp /path/to/setup.py .
cp /path/to/.gitignore .
cp /path/to/.env.example .

# Create your .env file
cp .env.example .env
# Edit .env and add your API key
```

### Step 4: Place Source Code

Your existing code files go in their respective directories:

```bash
# Extract rubrics module
cp /path/to/extract_rubrics_batch.py src/extract_rubrics/
cp /path/to/extract_rubrics_markitdown_onetask.py src/extract_rubrics/

# Evaluate rubrics module
cp /path/to/evaluate_rubrics_batch.py src/evaluate_rubrics/
cp /path/to/evaluate_rubrics_markitdown_onetask.py src/evaluate_rubrics/

# Prompts
cp /path/to/prompts/binary/system_prompt.txt src/evaluate_rubrics/prompts/binary/
cp /path/to/prompts/binary/user_prompt_template.txt src/evaluate_rubrics/prompts/binary/
cp /path/to/prompts/ternary/system_prompt.txt src/evaluate_rubrics/prompts/ternary/
cp /path/to/prompts/ternary/user_prompt_template.txt src/evaluate_rubrics/prompts/ternary/

# Calculate metrics module
cp /path/to/calculate_F1_score.py src/calculate_metrics/
cp /path/to/calculate_final_score.py src/calculate_metrics/
cp /path/to/calculate_failure_breakdown.py src/calculate_metrics/
```

### Step 5: Add __init__.py Files (Optional)

For proper Python package structure:

```bash
touch src/__init__.py
touch src/extract_rubrics/__init__.py
touch src/evaluate_rubrics/__init__.py
touch src/calculate_metrics/__init__.py
```

## 🎯 Key Directory Purposes

### Documentation (Root Level)
All user-facing documentation lives at the root level for easy discovery.

### src/
Contains all Python source code, organized by functionality:
- **extract_rubrics/**: CSV processing and rubric extraction
- **evaluate_rubrics/**: LLM-based evaluation
  - **prompts/binary/**: Binary evaluation prompts (2 classes)
  - **prompts/ternary/**: Ternary evaluation prompts (3 classes)
- **calculate_metrics/**: Metric computation and analysis

### data/
All data files, organized by stage:
- **raw_csvs/**: Your input CSV files
- **processed_df/**: Compiled datasets after extraction
- **PDFs/**: PDFs organized by task name (task_name/gemini.pdf, chatgpt.pdf, perplexity.pdf)
- **predownloaded_pdfs/**: Optional backup PDFs in same structure

### results/
Evaluation outputs, automatically organized by date and timestamp:
- Format: `results/MM_DD/YYYYMMDD_HHMMSS/processed_df/`

### cache/
Temporary cached files (markdown conversions):
- Auto-generated, can be deleted safely
- Improves performance on repeated evaluations

## 🔍 Path References in Code

The code uses these path patterns:

```python
# From any script in src/[module]/
base_dir = Path(__file__).parent.parent.parent  # Goes to public_release_experiments/

# Common paths used in code:
csv_path = base_dir / 'data' / 'raw_csvs' / 'file.csv'
compiled = base_dir / 'data' / 'processed_df' / 'compiled_dataset.csv'
pdf_dir = base_dir / 'data' / 'PDFs' / task_name
results = base_dir / 'results' / date / timestamp
cache = base_dir / 'cache'

# For prompts (from evaluate_rubrics/):
prompts_dir = Path(__file__).parent / 'prompts' / prompt_type
```

## ✅ Verification

After setting up, verify the structure:

```bash
# Check structure
tree -L 3 -I '__pycache__|*.pyc|.git'

# Verify all documentation is present
ls -1 *.md *.txt LICENSE CITATION.bib

# Verify source code structure
find src/ -name "*.py" | head -10

# Verify prompts are in place
find src/evaluate_rubrics/prompts/ -name "*.txt"

# Check data directories exist
ls -d data/*/
```

Expected output:
```
README.md
QUICKSTART.md
INSTALLATION.md
DATA_FORMAT.md
CONTRIBUTING.md
CHANGELOG.md
FILE_MANIFEST.md
requirements.txt
...
```

## 🚀 Quick Start After Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure API key
cp .env.example .env
# Edit .env and add OPENAI_API_KEY

# 3. Run extraction
cd src/extract_rubrics
python extract_rubrics_batch.py

# 4. Run evaluation
cd ../evaluate_rubrics
python evaluate_rubrics_batch.py

# 5. Calculate metrics
cd ../calculate_metrics
python calculate_F1_score.py
```

## 📦 For Distribution

When packaging for release:

### Include:
- All documentation files
- All configuration templates
- All source code in `src/`
- Empty directory structure (`data/`, `results/`, `cache/`)
- Prompts in `src/evaluate_rubrics/prompts/`

### Exclude:
- `.env` (with actual keys)
- Populated `data/` directories with actual data
- `cache/` contents
- `results/` contents
- `__pycache__/` directories
- `.pyc` files

### Create .gitkeep Files

To preserve empty directories in git:

```bash
touch data/raw_csvs/.gitkeep
touch data/processed_df/.gitkeep
touch data/PDFs/.gitkeep
touch data/predownloaded_pdfs/.gitkeep
touch results/.gitkeep
touch cache/.gitkeep
```

## 🔧 Customization

### Adding New Modules

```bash
# Create new module
mkdir -p src/new_module
touch src/new_module/__init__.py
touch src/new_module/new_script.py

# Update documentation
# - Add to README.md
# - Update FILE_MANIFEST.md
```

### Adding New Data Directories

```bash
# Create new data directory
mkdir -p data/new_data_type

# Update .gitignore if needed
echo "data/new_data_type/*" >> .gitignore
echo "!data/new_data_type/.gitkeep" >> .gitignore
touch data/new_data_type/.gitkeep
```

## 📞 Support

If structure issues arise:
1. Check path references in Python files match this structure
2. Verify all `Path(__file__).parent` calculations
3. Ensure prompts are in correct location
4. Check that data directories are properly created

## 🔗 Related Documentation

- **README.md**: Overview and usage
- **INSTALLATION.md**: Setup instructions
- **QUICKSTART.md**: First steps
- **FILE_MANIFEST.md**: Complete file listing

---

**Last Updated**: 2025-01-XX  
**Version**: 1.0.0
