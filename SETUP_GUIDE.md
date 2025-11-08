# Deep Research Benchmarks - Complete Setup Guide

This guide will walk you through setting up your Deep Research Benchmarks release from scratch.

## 📦 What You Have

Your release package contains **21 files**:

### 📄 Documentation (9 files)
1. **README.md** - Main documentation
2. **QUICKSTART.md** - Quick start guide  
3. **INSTALLATION.md** - Installation instructions
4. **DATA_FORMAT.md** - Data format specifications
5. **FOLDER_STRUCTURE.md** - Directory organization guide
6. **FILE_MANIFEST.md** - File index
7. **CONTRIBUTING.md** - Contribution guidelines
8. **CHANGELOG.md** - Version history
9. **RELEASE_CHECKLIST.md** - Pre-publication checklist

### ⚙️ Configuration (5 files)
10. **requirements.txt** - Python dependencies
11. **setup.py** - Package configuration
12. **.env.example** - Environment variables template
13. **.gitignore** - Git exclusions
14. **LICENSE** - MIT License

### 📝 Other (2 files)
15. **CITATION.bib** - BibTeX citation
16. **setup_structure.sh** - Unix setup script
17. **setup_structure.bat** - Windows setup script

### 🎯 Prompts (4 files in prompts/ directory)
18-19. **prompts/binary/** - Binary evaluation prompts (2 files)
20-21. **prompts/ternary/** - Ternary evaluation prompts (2 files)

## 🚀 Complete Setup Instructions

### Step 1: Organize Your Files

Create your project directory structure:

```bash
# Create project directory
mkdir -p public_release_experiments
cd public_release_experiments

# Move all documentation files to root
mv /path/to/README.md .
mv /path/to/QUICKSTART.md .
mv /path/to/INSTALLATION.md .
mv /path/to/DATA_FORMAT.md .
mv /path/to/FOLDER_STRUCTURE.md .
mv /path/to/FILE_MANIFEST.md .
mv /path/to/CONTRIBUTING.md .
mv /path/to/CHANGELOG.md .
mv /path/to/RELEASE_CHECKLIST.md .

# Move configuration files to root
mv /path/to/requirements.txt .
mv /path/to/setup.py .
mv /path/to/.env.example .
mv /path/to/.gitignore .
mv /path/to/LICENSE .
mv /path/to/CITATION.bib .

# Move setup scripts to root
mv /path/to/setup_structure.sh .
mv /path/to/setup_structure.bat .
```

### Step 2: Run Setup Script

Run the appropriate setup script for your OS:

**Unix/Linux/macOS:**
```bash
chmod +x setup_structure.sh
./setup_structure.sh
```

**Windows:**
```batch
setup_structure.bat
```

This creates all necessary directories:
- `src/extract_rubrics/`
- `src/evaluate_rubrics/prompts/binary/` and `prompts/ternary/`
- `src/calculate_metrics/`
- `data/raw_csvs/`, `data/processed_df/`, `data/PDFs/`, `data/predownloaded_pdfs/`
- `results/`, `cache/`, `tests/`

### Step 3: Place Your Source Code

Copy your existing Python files to the correct locations:

```bash
# Extract rubrics module
cp /path/to/your/extract_rubrics_batch.py src/extract_rubrics/
cp /path/to/your/extract_rubrics_markitdown_onetask.py src/extract_rubrics/

# Evaluate rubrics module  
cp /path/to/your/evaluate_rubrics_batch.py src/evaluate_rubrics/
cp /path/to/your/evaluate_rubrics_markitdown_onetask.py src/evaluate_rubrics/

# Calculate metrics module
cp /path/to/your/calculate_F1_score.py src/calculate_metrics/
cp /path/to/your/calculate_final_score.py src/calculate_metrics/
cp /path/to/your/calculate_failure_breakdown.py src/calculate_metrics/
```

### Step 4: Place Prompt Files

Move the prompt files to their correct locations:

```bash
# Binary prompts
mv prompts/binary/system_prompt.txt src/evaluate_rubrics/prompts/binary/
mv prompts/binary/user_prompt_template.txt src/evaluate_rubrics/prompts/binary/

# Ternary prompts
mv prompts/ternary/system_prompt.txt src/evaluate_rubrics/prompts/ternary/
mv prompts/ternary/user_prompt_template.txt src/evaluate_rubrics/prompts/ternary/

# Remove the now-empty prompts directory from root
rm -rf prompts/
```

### Step 5: Configure Environment

```bash
# Create your .env file
cp .env.example .env

# Edit .env and add your API key
nano .env  # or vim .env, or code .env
# Add: OPENAI_API_KEY=your_actual_api_key_here
```

### Step 6: Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Verify installation
python -c "import pandas, litellm, markitdown, sklearn; print('✓ All dependencies installed')"
```

### Step 7: Verify Setup

```bash
# Check folder structure
tree -L 3 -I '__pycache__|*.pyc'

# Or use ls to verify key directories
ls -d src/*/
ls -d data/*/
```

Expected output:
```
src/extract_rubrics/
src/evaluate_rubrics/
src/calculate_metrics/
data/raw_csvs/
data/processed_df/
data/PDFs/
data/predownloaded_pdfs/
```

### Step 8: Test Your Setup

```bash
# Test imports
cd src/extract_rubrics
python -c "from extract_rubrics_markitdown_onetask import RubricExtractor; print('✓ Extract module OK')"

cd ../evaluate_rubrics  
python -c "from evaluate_rubrics_markitdown_onetask import RubricEvaluator; print('✓ Evaluate module OK')"

cd ../calculate_metrics
python -c "from calculate_F1_score import calculate_macro_f1_per_task; print('✓ Metrics module OK')"

cd ../..  # Back to project root
```

## 📂 Final Folder Structure

After setup, your directory should look like this:

```
public_release_experiments/
├── README.md
├── QUICKSTART.md
├── INSTALLATION.md
├── DATA_FORMAT.md
├── FOLDER_STRUCTURE.md
├── FILE_MANIFEST.md
├── CONTRIBUTING.md
├── CHANGELOG.md
├── RELEASE_CHECKLIST.md
├── LICENSE
├── CITATION.bib
├── requirements.txt
├── setup.py
├── .env.example
├── .env (your API key - DO NOT COMMIT)
├── .gitignore
├── setup_structure.sh
├── setup_structure.bat
├── src/
│   ├── __init__.py
│   ├── extract_rubrics/
│   │   ├── __init__.py
│   │   ├── extract_rubrics_batch.py
│   │   └── extract_rubrics_markitdown_onetask.py
│   ├── evaluate_rubrics/
│   │   ├── __init__.py
│   │   ├── evaluate_rubrics_batch.py
│   │   ├── evaluate_rubrics_markitdown_onetask.py
│   │   └── prompts/
│   │       ├── binary/
│   │       │   ├── system_prompt.txt
│   │       │   └── user_prompt_template.txt
│   │       └── ternary/
│   │           ├── system_prompt.txt
│   │           └── user_prompt_template.txt
│   └── calculate_metrics/
│       ├── __init__.py
│       ├── calculate_F1_score.py
│       ├── calculate_final_score.py
│       └── calculate_failure_breakdown.py
├── data/
│   ├── raw_csvs/
│   ├── processed_df/
│   ├── PDFs/
│   └── predownloaded_pdfs/
├── results/
├── cache/
└── tests/
```

## 🎯 Running Your First Workflow

Once setup is complete:

```bash
# 1. Place your CSV files in data/raw_csvs/
# (You need to do this manually with your data)

# 2. Extract rubrics
cd src/extract_rubrics
python extract_rubrics_batch.py

# 3. Evaluate rubrics
cd ../evaluate_rubrics
python evaluate_rubrics_batch.py

# 4. Calculate metrics
cd ../calculate_metrics
python calculate_F1_score.py
python calculate_final_score.py
python calculate_failure_breakdown.py
```

## 📋 Before Publishing

Before you push to GitHub, complete the **RELEASE_CHECKLIST.md**:

1. **Update placeholders**:
   - Replace `[Authors]` with actual names
   - Replace `<repository-url>` with your GitHub URL
   - Replace `[username]` in links
   - Update contact information

2. **Review security**:
   - Remove any API keys from code
   - Verify `.env` is in `.gitignore`
   - Check for sensitive information

3. **Test everything**:
   - Fresh install in new environment
   - Run complete workflow
   - Verify all documentation

4. **Initialize Git**:
```bash
git init
git add .
git commit -m "Initial release: Deep Research Benchmarks v1.0.0"
git remote add origin <your-github-url>
git push -u origin main
```

## 📖 Documentation Overview

- **Start here**: README.md
- **Quick examples**: QUICKSTART.md  
- **Installation help**: INSTALLATION.md
- **Data formats**: DATA_FORMAT.md
- **File organization**: FOLDER_STRUCTURE.md
- **Before release**: RELEASE_CHECKLIST.md

## 🆘 Troubleshooting

### "Module not found" errors
**Solution**: Make sure you're running scripts from their directories or add to Python path.

### "Can't find .env" errors  
**Solution**: Ensure `.env` is in project root (`public_release_experiments/.env`), not in `src/`.

### Prompt files not found
**Solution**: Verify prompts are in `src/evaluate_rubrics/prompts/binary/` and `.../ternary/`, not in project root.

### Import errors between modules
**Solution**: `__init__.py` files should be present in all `src/` subdirectories.

## ✅ Setup Complete!

Your Deep Research Benchmarks codebase is now ready for:
- ✅ Development and testing
- ✅ Running experiments
- ✅ Publishing to GitHub
- ✅ Sharing with collaborators
- ✅ Paper submission

## 📞 Need Help?

- Check **INSTALLATION.md** for detailed installation troubleshooting
- Review **FOLDER_STRUCTURE.md** for directory organization
- See **QUICKSTART.md** for usage examples
- Consult **RELEASE_CHECKLIST.md** before publishing

---

**Setup Guide Version**: 1.0  
**Last Updated**: 2025-01-XX  
**Estimated Setup Time**: 10-15 minutes
