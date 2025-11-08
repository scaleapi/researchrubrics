# Installation Guide

Detailed installation instructions for the Deep Research Benchmarks codebase.

## System Requirements

### Minimum Requirements
- Python 3.8 or higher
- 4 GB RAM
- 2 GB disk space (for code and dependencies)
- Internet connection (for API calls and PDF downloads)

### Recommended Requirements
- Python 3.10+
- 8 GB RAM (for processing large batches)
- 10 GB disk space (for datasets and results)
- Stable internet connection

## Installation Methods

### Method 1: pip install (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd public_release_experiments

# Install using pip
pip install -r requirements.txt

# Verify installation
python -c "import pandas, litellm, markitdown; print('Installation successful!')"
```

### Method 2: conda environment

```bash
# Create conda environment
conda create -n deep-research python=3.10
conda activate deep-research

# Install dependencies
pip install -r requirements.txt
```

### Method 3: virtualenv

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Unix/macOS:
source venv/bin/activate
# On Windows:
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Method 4: Development install

For contributors who want to modify the code:

```bash
# Clone repository
git clone <repository-url>
cd public_release_experiments

# Install in editable mode with dev dependencies
pip install -e .
pip install pytest pytest-asyncio black flake8
```

## Dependency Details

### Core Dependencies

#### pandas (>=1.3.0)
Data manipulation and analysis
```bash
pip install pandas
```

#### numpy (>=1.20.0)
Numerical computing
```bash
pip install numpy
```

#### litellm (>=1.0.0)
LLM API client for multiple providers
```bash
pip install litellm
```

#### markitdown (>=0.1.0)
PDF to Markdown conversion
```bash
pip install markitdown
```

#### PyPDF2 (>=3.0.0)
Fallback PDF text extraction
```bash
pip install PyPDF2
```

#### scikit-learn (>=1.0.0)
Machine learning metrics
```bash
pip install scikit-learn
```

#### tqdm (>=4.60.0)
Progress bars
```bash
pip install tqdm
```

### Optional Dependencies

#### pyarrow (>=10.0.0)
Parquet file support (recommended)
```bash
pip install pyarrow
```

#### pytest and pytest-asyncio
For running tests
```bash
pip install pytest pytest-asyncio
```

#### black and flake8
Code formatting and linting
```bash
pip install black flake8
```

## Configuration

### 1. API Key Setup

Create a `.env` file from the template:

```bash
cp .env.example .env
```

Edit `.env` and add your API key:

```bash
# Open in your preferred editor
nano .env
# or
vim .env
# or
code .env
```

Add your API key:
```
OPENAI_API_KEY=sk-your-api-key-here
```

### 2. Custom API Endpoint (Optional)

If using a custom LiteLLM proxy or alternative endpoint:

```
OPENAI_API_KEY=your_key
API_BASE_URL=https://your-endpoint.com
```

### 3. Model Configuration (Optional)

```
MODEL_NAME=gpt-5
MAX_CONCURRENT_REQUESTS=20
BINARY_EVALUATION=False
```

## Directory Structure Setup

The installation should create these directories automatically, but you can create them manually if needed:

```bash
mkdir -p data/raw_csvs
mkdir -p data/processed_df
mkdir -p data/PDFs
mkdir -p data/predownloaded_pdfs
mkdir -p results
mkdir -p cache
```

## Verification

### Test Basic Functionality

```bash
# Test extract module (from project root)
python -c "import sys; sys.path.insert(0, 'src/extract_rubrics'); from extract_rubrics_markitdown_onetask import RubricExtractor; print('Extract module OK')"

# Test evaluate module (from project root)
python -c "import sys; sys.path.insert(0, 'src/evaluate_rubrics'); from evaluate_rubrics_markitdown_onetask import RubricEvaluator; print('Evaluate module OK')"

# Test metrics module (from project root)
python -c "import sys; sys.path.insert(0, 'src/calculate_metrics'); from calculate_F1_score import calculate_macro_f1_per_task; print('Metrics module OK')"
```

Or run from their directories:

```bash
cd src/extract_rubrics
python -c "from extract_rubrics_markitdown_onetask import RubricExtractor; print('Extract module OK')"

cd ../evaluate_rubrics
python -c "from evaluate_rubrics_markitdown_onetask import RubricEvaluator; print('Evaluate module OK')"

cd ../calculate_metrics
python -c "from calculate_F1_score import calculate_macro_f1_per_task; print('Metrics module OK')"
```

### Test API Connection

```bash
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
if api_key and api_key != 'your_api_key_here':
    print('API key configured ✓')
else:
    print('API key not configured - edit .env file')
"
```

### Run Test Suite (if available)

```bash
pytest tests/
```

## Platform-Specific Instructions

### macOS

```bash
# Install Xcode Command Line Tools (if not already installed)
xcode-select --install

# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python via Homebrew (optional)
brew install python@3.10

# Follow standard installation steps
pip3 install -r requirements.txt
```

### Linux (Ubuntu/Debian)

```bash
# Update package list
sudo apt-get update

# Install Python and pip
sudo apt-get install python3.10 python3-pip python3-venv

# Install system dependencies (if needed)
sudo apt-get install build-essential

# Follow standard installation steps
pip3 install -r requirements.txt
```

### Windows

```powershell
# Install Python from python.org or Microsoft Store
# Ensure pip is included in the installation

# Open PowerShell or Command Prompt as Administrator (if needed)

# Follow standard installation steps
pip install -r requirements.txt
```

#### Windows-Specific Notes

- Use backslashes (`\`) in paths or use raw strings in Python
- Some packages may require Microsoft C++ Build Tools
- Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

## Troubleshooting

### Issue: ImportError for specific package

**Solution**: Install the missing package individually
```bash
pip install package-name
```

### Issue: Permission denied errors

**Solution**: Use `--user` flag or virtual environment
```bash
pip install --user -r requirements.txt
```

### Issue: Conflicting dependencies

**Solution**: Use a fresh virtual environment
```bash
python -m venv clean_env
source clean_env/bin/activate  # Unix
.\clean_env\Scripts\activate   # Windows
pip install -r requirements.txt
```

### Issue: pip is outdated

**Solution**: Upgrade pip
```bash
pip install --upgrade pip
```

### Issue: SSL certificate errors

**Solution**: Update certificates or use trusted host
```bash
pip install --trusted-host pypi.org --trusted-host pypi.python.org -r requirements.txt
```

### Issue: markitdown installation fails

**Solution**: Install system dependencies
```bash
# macOS
brew install poppler

# Ubuntu/Debian
sudo apt-get install poppler-utils

# Then retry
pip install markitdown
```

### Issue: Can't find .env file

**Solution**: Ensure .env is in the project root (public_release_experiments/)
```bash
# From project root
cd public_release_experiments
ls -la .env

# If missing, create from template
cp .env.example .env
# Edit and add your OPENAI_API_KEY
```

**Note**: The evaluation scripts look for `.env` in the project root (`public_release_experiments/.env`), not in the script directory. The code automatically searches up the directory tree from `src/evaluate_rubrics/` to find it.

## Upgrading

To upgrade to the latest version:

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install --upgrade -r requirements.txt

# Clear cache if needed
rm -rf cache/*
```

## Uninstallation

To remove the installation:

```bash
# If using pip directly
pip uninstall -r requirements.txt

# If using virtual environment, just delete it
rm -rf venv/
# or
rm -rf conda_env/
```

## Docker Installation (Alternative)

For a containerized installation (if Dockerfile is provided):

```bash
# Build Docker image
docker build -t deep-research-benchmarks .

# Run container
docker run -v $(pwd)/data:/app/data \
           -v $(pwd)/results:/app/results \
           -e OPENAI_API_KEY=your_key \
           deep-research-benchmarks
```

## Next Steps

After successful installation:

1. Review [QUICKSTART.md](QUICKSTART.md) for usage examples
2. Read [README.md](README.md) for comprehensive documentation
3. Check [DATA_FORMAT.md](DATA_FORMAT.md) for data specifications
4. Run the example workflow to verify everything works

## Getting Help

If you encounter installation issues:

1. Check the [Troubleshooting](#troubleshooting) section above
2. Review existing GitHub issues
3. Open a new issue with:
   - Your OS and Python version
   - Complete error message
   - Steps to reproduce
   - Output of `pip list`

## Version Information

Current version: 1.0.0

To check installed package versions:
```bash
pip list | grep -E "pandas|litellm|markitdown|scikit-learn"
```

## License

This software is distributed under the MIT License. See [LICENSE](LICENSE) for details.
