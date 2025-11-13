# Research Rubrics - Folder Structure

This document describes the complete folder structure for the Research Rubrics project.

## 📁 Complete Directory Structure

```
researchrubrics/
│
├── 📄 Documentation Files (root level)
│   ├── README.md                      # Main documentation
│   ├── QUICKSTART.md                  # Quick start guide
│   ├── INSTALLATION.md                # Installation guide
│   ├── DATA_FORMAT.md                 # Data format specifications
│   ├── FOLDER_STRUCTURE.md            # This file
│   ├── FILE_MANIFEST.md               # File index
│   ├── SETUP_GUIDE.md                 # Setup instructions
│   ├── PACKAGE_SUMMARY.md             # Package summary
│   ├── LICENSE                        # MIT License
│   └── CITATION.bib                   # BibTeX citation
│
├── ⚙️ Configuration Files (root level)
│   ├── requirements.txt               # Python dependencies
│   ├── setup.py                       # Package configuration
│   ├── .env                           # Your API key (DO NOT COMMIT)
│   └── .gitignore                     # Git exclusions
│
├── 📦 src/                            # Source code
│   │
│   ├── __init__.py                    # Package marker
│   │
│   ├── evaluate_rubrics/              # Rubric evaluation module
│   │   ├── evaluate_single_report.py  # Single report evaluator
│   │   └── evaluate_reports_batch.py  # Batch evaluation script
│   │
│   ├── calculate_metrics/             # Metrics calculation module
│   │   └── calculate_compliance_score.py  # Compliance score calculation
│   │
│   └── prompts/                       # Evaluation prompt templates
│       ├── system_prompt.txt          # System prompt for evaluator
│       ├── user_prompt.txt            # User prompt template
│       ├── chunk_prompt_template.txt  # Prompt for chunk evaluation
│       └── synthesis_prompt_template.txt  # Prompt for synthesizing chunks
│
├── 📊 data/                           # Data directory
│   └── researchrubrics/               # Input data
│       ├── processed_data.jsonl       # Rubrics and task metadata (JSONL)
│       └── README.md                  # Dataset documentation template
│
├── 📝 agent_responses/                # Input: Markdown reports to evaluate
│   ├── 683a58c9a7e7fe4e7695846f.md   # AI-generated report (sample 1)
│   ├── 683a58c9a7e7fe4e7695848b.md   # AI-generated report (sample 2)
│   └── 683a58c9a7e7fe4e7695848e.md   # AI-generated report (sample 3)
│
├── 📈 results/                        # Evaluation results (JSONL format)
│   └── batch_evaluation_YYYYMMDD_HHMMSS.jsonl  # Timestamped results
│
├── 💾 cache/                          # Reserved for future use
│
└── 🧪 tests/                          # Test files
    └── __init__.py                    # Package marker
```

## 📋 Setup Instructions

### Step 1: Create Base Structure

```bash
# Navigate to your project root
cd researchrubrics

# Create all required directories
mkdir -p src/evaluate_rubrics
mkdir -p src/calculate_metrics
mkdir -p src/prompts
mkdir -p data/researchrubrics
mkdir -p agent_responses
mkdir -p results
mkdir -p cache
mkdir -p tests
```

### Step 2: Create .env File

```bash
# In researchrubrics/ root
echo "LITELLM_API_KEY=your_api_key_here" > .env
```

### Step 3: Install Dependencies

```bash
# In researchrubrics/ root
pip install -r requirements.txt
```

### Step 4: Verify Data Files

Ensure your input data is in place:

```bash
# Check that processed_data.jsonl exists
ls data/researchrubrics/processed_data.jsonl

# Check that markdown reports exist
ls agent_responses/*.md
```

### Step 5: Test the Installation

```bash
# Test evaluation module (from project root)
cd src/evaluate_rubrics
python -c "from evaluate_single_report import RubricEvaluator; print('✓ Module OK')"
cd ../..
```

## 🎯 Key Directory Purposes

### Documentation (Root Level)
All user-facing documentation lives at the root level for easy discovery.

### src/
Contains all Python source code, organized by functionality:
- **evaluate_rubrics/**: LLM-based rubric evaluation scripts
- **calculate_metrics/**: Compliance score calculation
- **prompts/**: Evaluation prompt templates (system, user, chunk, synthesis)

### data/
Input data directory:
- **researchrubrics/**: Contains `processed_data.jsonl` with rubrics and task metadata

### agent_responses/
Markdown reports to be evaluated:
- Each file named with its `sample_id` (e.g., `683a58c9a7e7fe4e7695846f.md`)

### results/
Evaluation outputs in JSONL format:
- Format: `batch_evaluation_YYYYMMDD_HHMMSS.jsonl`
- One JSON object per line, each representing a rubric evaluation

### cache/
Reserved for future use (currently unused)

## 🔍 Path References in Code

The code uses these path patterns:

```python
# From any script in src/[module]/
base_dir = Path(__file__).parent.parent.parent  # Goes to researchrubrics/

# Common paths used in code:
data_file = base_dir / 'data' / 'researchrubrics' / 'processed_data.jsonl'
agent_responses = base_dir / 'agent_responses'
results = base_dir / 'results'
cache = base_dir / 'cache'

# For prompts (from evaluate_rubrics/):
prompts_dir = Path(__file__).parent.parent / 'prompts'
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
echo "LITELLM_API_KEY=your_key_here" > .env

# 3. Run batch evaluation
cd src/evaluate_rubrics
python evaluate_reports_batch.py

# 4. Calculate compliance scores
cd ../calculate_metrics
python calculate_compliance_score.py
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
