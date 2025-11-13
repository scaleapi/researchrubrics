# Installation Guide

Detailed installation instructions for the Research Rubrics codebase.

## System Requirements

### Minimum Requirements
- Python 3.8 or higher
- 4 GB RAM
- 2 GB disk space (for code and dependencies)
- Internet connection (for API calls)

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
cd researchrubrics

# Install using pip
pip install -r requirements.txt

# Verify installation
python -c "import pandas, litellm, tqdm; print('Installation successful!')"
```

### Method 2: conda environment

```bash
# Create conda environment
conda create -n researchrubrics python=3.10
conda activate researchrubrics

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
cd researchrubrics

# Install in editable mode with dev dependencies
pip install -e .
pip install pytest pytest-asyncio
```

## Dependency Details

### Core Dependencies

#### pandas (>=2.0.0)
Data manipulation and analysis
```bash
pip install pandas
```

#### litellm (>=1.0.0)
LLM API client for accessing Gemini 2.5 Pro
```bash
pip install litellm
```

#### tqdm (>=4.60.0)
Progress bars for batch processing
```bash
pip install tqdm
```

### Optional Dependencies

#### pytest and pytest-asyncio
For running tests
```bash
pip install pytest pytest-asyncio
```

## Configuration

### 1. API Key Setup

Create a `.env` file in the project root:

```bash
# From project root
echo "LITELLM_API_KEY=your_api_key_here" > .env
```

Or manually create `.env`:
```bash
nano .env
# Add: LITELLM_API_KEY=your_api_key_here
```

### 2. Verify API Key

```python
import os
from pathlib import Path

# Load .env file
env_file = Path('.env')
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            if line.startswith('LITELLM_API_KEY='):
                print('API key configured ✓')
else:
    print('No .env file found - create one with LITELLM_API_KEY')
```

## Directory Structure Setup

The installation should create these directories automatically if they don't exist, but you can create them manually if needed:

```bash
mkdir -p data/researchrubrics
mkdir -p agent_responses
mkdir -p results
mkdir -p cache
```

## Verification

### Test Basic Functionality

```bash
# Test evaluate module (from project root)
cd src/evaluate_rubrics
python -c "from evaluate_single_report import RubricEvaluator; print('Evaluate module OK')"

# Test metrics module
cd ../calculate_metrics
python -c "from calculate_compliance_score import calculate_compliance_score; print('Metrics module OK')"

cd ../..  # Back to project root
```

### Test API Connection

```python
import os
from pathlib import Path

# Try to load API key
env_file = Path('.env')
if not env_file.exists():
    print('ERROR: .env file not found')
    exit(1)

with open(env_file) as f:
    for line in f:
        if 'LITELLM_API_KEY=' in line:
            key = line.split('=')[1].strip()
            if key and key != 'your_api_key_here':
                print('✓ API key configured')
            else:
                print('ERROR: API key not set in .env file')
            break
    else:
        print('ERROR: LITELLM_API_KEY not found in .env file')
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

# Open PowerShell or Command Prompt

# Follow standard installation steps
pip install -r requirements.txt
```

#### Windows-Specific Notes

- Use backslashes (`\`) in paths or use raw strings in Python
- Ensure Python is added to PATH during installation

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

### Issue: Can't find .env file

**Solution**: Ensure .env is in the project root
```bash
# From project root
ls -la .env

# If missing, create it
echo "LITELLM_API_KEY=your_api_key_here" > .env
```

**Note**: The evaluation scripts look for `.env` in the project root (`researchrubrics/.env`), not in the script directory.

### Issue: litellm import error

**Solution**: Ensure litellm is installed with correct version
```bash
pip install --upgrade litellm
```

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

## Next Steps

After successful installation:

1. Review [QUICKSTART.md](QUICKSTART.md) for usage examples
2. Read [README.md](README.md) for comprehensive documentation
3. Check [DATA_FORMAT.md](DATA_FORMAT.md) for data specifications
4. Follow [SETUP_GUIDE.md](SETUP_GUIDE.md) for complete setup

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
pip list | grep -E "pandas|litellm|tqdm"
```

## License

This software is distributed under the MIT License. See [LICENSE](LICENSE) for details.
