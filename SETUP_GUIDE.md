# Research Rubrics - Complete Setup Guide

This guide will walk you through setting up Research Rubrics from scratch.

## 📦 Prerequisites

Before you begin, ensure you have:
- Python 3.8 or higher installed
- Git installed (for cloning the repository)
- A LiteLLM API key (for accessing Gemini 2.5 Pro)
- Command line access (Terminal/PowerShell/Command Prompt)

## 🚀 Complete Setup Instructions

### Step 1: Clone the Repository

```bash
# Clone the repository
git clone <repository-url>
cd researchrubrics
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Create a virtual environment
python -m venv venv

# Activate it
# On Unix/macOS:
source venv/bin/activate
# On Windows:
.\venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt

# Verify installation
python -c "import pandas, litellm, tqdm; print('✓ All dependencies installed')"
```

### Step 4: Configure API Credentials

```bash
# Create .env file with your API key
echo "LITELLM_API_KEY=your_actual_api_key_here" > .env

# Verify .env file was created
cat .env
```

**Important**: Replace `your_actual_api_key_here` with your real API key!

### Step 5: Verify Directory Structure

```bash
# Check that all necessary directories exist
ls -d src/*/
ls -d data/
ls -d agent_responses/
ls -d results/
```

Expected output:
```
src/calculate_metrics/
src/evaluate_rubrics/
src/prompts/
data/
agent_responses/
results/
```

### Step 6: Prepare Input Data

Ensure you have:

1. **Rubrics data file**: `data/researchrubrics/processed_data.jsonl`
2. **Markdown reports**: Files in `agent_responses/` directory

```bash
# Check data file exists
ls data/researchrubrics/processed_data.jsonl

# Check markdown files exist
ls agent_responses/*.md
```

### Step 7: Test the Installation

```bash
# Test the evaluation module
cd src/evaluate_rubrics
python -c "from evaluate_single_report import RubricEvaluator; print('✓ Evaluate module OK')"

# Test the metrics module
cd ../calculate_metrics
python -c "from calculate_compliance_score import calculate_compliance_score; print('✓ Metrics module OK')"

# Return to project root
cd ../..
```

### Step 8: Run a Test Evaluation (Optional)

```bash
# Run evaluation on all reports (if you have data ready)
cd src/evaluate_rubrics
python evaluate_reports_batch.py
```

This will evaluate all markdown files in `agent_responses/` and save results to `results/`.

## 📊 Understanding the Data Flow

```
Input Data:
  data/researchrubrics/processed_data.jsonl  (rubrics + metadata)
  agent_responses/*.md                       (markdown reports)
           ↓
       Evaluation
    (evaluate_reports_batch.py)
           ↓
       Results:
  results/batch_evaluation_YYYYMMDD_HHMMSS.jsonl
           ↓
       Metrics:
    (calculate_compliance_score.py)
           ↓
       Compliance Scores
```

## 🎯 Quick Start After Setup

Once setup is complete:

```bash
# 1. Evaluate all reports
cd src/evaluate_rubrics
python evaluate_reports_batch.py

# 2. Calculate compliance scores
cd ../calculate_metrics
python calculate_compliance_score.py
```

## 🔧 Customization Options

### Adjusting Concurrency

Edit `src/evaluate_rubrics/evaluate_single_report.py`:

```python
# Find this line (around line 78)
def __init__(self, api_key: str = None, base_url: str = None, 
             model: str = "litellm_proxy/gemini/gemini-2.5-pro-preview-06-05", 
             max_concurrent: int = 20):  # Change this number

# Examples:
# max_concurrent=5   # Conservative (avoid rate limits)
# max_concurrent=10  # Moderate
# max_concurrent=30  # Aggressive (higher throughput)
```

### Using a Different Model

In the same file, change the `model` parameter:

```python
model: str = "litellm_proxy/gemini/gemini-2.5-pro-preview-06-05"  # Change this
```

### Custom Output Location

In `src/evaluate_rubrics/evaluate_reports_batch.py`, modify:

```python
await evaluate_all_reports(
    agent_responses_dir="agent_responses",  # Change input directory
    output_file="results/my_custom_results.jsonl"  # Change output file
)
```

## 📋 Verification Checklist

After setup, verify:

- [ ] Python 3.8+ installed (`python --version`)
- [ ] All dependencies installed (`pip list | grep -E "pandas|litellm|tqdm"`)
- [ ] `.env` file created with LITELLM_API_KEY
- [ ] `data/researchrubrics/processed_data.jsonl` exists
- [ ] Markdown files in `agent_responses/`
- [ ] Source code files in `src/` directory
- [ ] Prompt templates in `src/prompts/`
- [ ] Test imports work (Step 7)

## 🆘 Troubleshooting

### Issue: "No module named 'litellm'"

**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: "FileNotFoundError: processed_data.jsonl"

**Solution**: Ensure data file exists in the correct location
```bash
ls data/researchrubrics/processed_data.jsonl
```

If missing, obtain the data file from the appropriate source.

### Issue: "No markdown files found"

**Solution**: Add markdown files to `agent_responses/`
```bash
# Files should be named with sample IDs
# Example: 683a58c9a7e7fe4e7695846f.md
```

### Issue: "API key not found"

**Solution**: Verify `.env` file
```bash
# Check .env exists
ls .env

# Check contents
cat .env

# Should contain: LITELLM_API_KEY=your_key_here
```

### Issue: Rate limit errors

**Solution**: Reduce concurrency
```python
# In evaluate_single_report.py
evaluator = RubricEvaluator(max_concurrent=5)
```

## 🔄 Updating the Code

To update to the latest version:

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install --upgrade -r requirements.txt
```

## 📖 Next Steps

Now that setup is complete:

1. **Read Documentation**:
   - [README.md](README.md) - Project overview
   - [QUICKSTART.md](QUICKSTART.md) - Quick examples
   - [DATA_FORMAT.md](DATA_FORMAT.md) - Data format details

2. **Run Evaluations**:
   - Start with a small batch to test
   - Monitor API costs and token usage
   - Adjust concurrency based on rate limits

3. **Analyze Results**:
   - Review evaluation results in `results/`
   - Calculate compliance scores
   - Identify patterns in rubric performance

## 💡 Tips for Success

1. **Start Small**: Test with 1-2 markdown files before processing large batches
2. **Monitor Costs**: Check token usage and API costs regularly
3. **Adjust Concurrency**: Balance between speed and rate limits
4. **Save Results**: Keep evaluation results for later analysis
5. **Version Control**: Don't commit `.env` file or results to Git

## 📞 Getting Help

If you need assistance:

1. Check the troubleshooting section above
2. Review [INSTALLATION.md](INSTALLATION.md) for detailed setup help
3. Check existing GitHub issues
4. Open a new issue with:
   - Your setup (OS, Python version)
   - Error message (full traceback)
   - Steps to reproduce

## ✅ Setup Complete!

Once all checks pass, you're ready to:
- ✅ Evaluate markdown reports against rubrics
- ✅ Calculate compliance scores
- ✅ Analyze evaluation results
- ✅ Customize the evaluation pipeline

**Happy evaluating! 🚀**

---

**Setup Guide Version**: 1.0  
**Last Updated**: 2025-11-13  
**Estimated Setup Time**: 10-15 minutes
