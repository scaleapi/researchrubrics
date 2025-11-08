# Deep Research Benchmarks

Official code release for the ICLR paper on Deep Research Benchmarks. This repository contains tools for extracting rubrics from evaluation datasets, evaluating documents against rubric criteria using Large Language Models (LLMs), and calculating comprehensive metrics.

## Overview

This codebase provides a complete pipeline for evaluating AI-generated research documents against structured rubric criteria:

1. **Rubric Extraction**: Process raw CSV files to extract evaluation rubrics, prompts, and ground truth annotations
2. **Rubric Evaluation**: Use LLMs to evaluate whether documents satisfy specific rubric criteria
3. **Metrics Calculation**: Compute F1 scores, failure breakdowns, and weighted scores

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Repository Structure](#repository-structure)
- [Usage](#usage)
  - [Extracting Rubrics](#extracting-rubrics)
  - [Evaluating Rubrics](#evaluating-rubrics)
  - [Calculating Metrics](#calculating-metrics)
- [Data Format](#data-format)
- [Configuration](#configuration)
- [Citation](#citation)
- [License](#license)

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd public_release_experiments
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure API credentials:
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

## Quick Start

```bash
# Navigate to project root
cd public_release_experiments

# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure API key
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# 3. Extract rubrics from raw CSV files
cd src/extract_rubrics
python extract_rubrics_batch.py

# 4. Evaluate rubrics using LLMs
cd ../evaluate_rubrics
python evaluate_rubrics_batch.py

# 5. Calculate metrics
cd ../calculate_metrics
python calculate_F1_score.py
python calculate_final_score.py
python calculate_failure_breakdown.py
```

## Repository Structure

```
public_release_experiments/
├── src/
│   ├── extract_rubrics/           # Rubric extraction from CSV files
│   │   ├── extract_rubrics_batch.py
│   │   └── extract_rubrics_markitdown_onetask.py
│   ├── evaluate_rubrics/          # LLM-based rubric evaluation
│   │   ├── evaluate_rubrics_batch.py
│   │   ├── evaluate_rubrics_markitdown_onetask.py
│   │   └── prompts/               # Evaluation prompts
│   │       ├── binary/            # Binary classification prompts
│   │       │   ├── system_prompt.txt
│   │       │   └── user_prompt_template.txt
│   │       └── ternary/           # Ternary classification prompts
│   │           ├── system_prompt.txt
│   │           └── user_prompt_template.txt
│   └── calculate_metrics/         # Metrics computation
│       ├── calculate_F1_score.py
│       ├── calculate_final_score.py
│       └── calculate_failure_breakdown.py
├── data/
│   ├── raw_csvs/                  # Input: Raw evaluation CSV files
│   ├── processed_df/              # Output: Compiled datasets
│   ├── PDFs/                      # Downloaded/processed PDFs
│   │   └── [task_name]/           # PDFs organized by task
│   │       ├── gemini.pdf
│   │       ├── chatgpt.pdf
│   │       └── perplexity.pdf
│   └── predownloaded_pdfs/        # Optional: Pre-downloaded PDFs
├── results/                       # Evaluation results by date/timestamp
│   └── [mm_dd]/[timestamp]/processed_df/
├── cache/                         # Cached markdown conversions
├── requirements.txt
├── .env.example
├── .gitignore
├── setup.py
├── LICENSE
├── CITATION.bib
└── README.md
```

## Usage

### Extracting Rubrics

Extract rubrics, prompts, and ground truth annotations from raw CSV files:

#### Single Task
```python
from extract_rubrics_markitdown_onetask import RubricExtractor

extractor = RubricExtractor()
results = extractor.process_task("data/raw_csvs/task_file.csv")
```

#### Batch Processing
```bash
cd src/extract_rubrics
python extract_rubrics_batch.py
```

**Output**: `data/processed_df/compiled_dataset.csv` and `compiled_dataset.parquet`

**Output Format**:
- `task_name`: Unique task identifier
- `prompt`: Original task prompt
- `rubrics`: List of rubric criteria (JSON)
- `pdf_paths`: Paths to model-generated PDFs
- `final_presence`: Ground truth annotations

### Evaluating Rubrics

Evaluate documents against rubric criteria using LLMs:

#### Single Task
```python
from evaluate_rubrics_markitdown_onetask import evaluate_task_rubrics

# Evaluate a specific task
results_df = await evaluate_task_rubrics(
    task_name="683a58c9a7e7fe4e7695846f",
    binary=False  # Use ternary prompts (Satisfied/Partially Satisfied/Not Satisfied)
)
```

#### Batch Processing
```bash
cd src/evaluate_rubrics
python evaluate_rubrics_batch.py
```

**Configuration Options**:
- `binary`: Set to `True` for binary evaluation (Satisfied/Not Satisfied), `False` for ternary (Satisfied/Partially Satisfied/Not Satisfied)
- `model`: LLM model to use (default: "gpt-5")
- `max_concurrent`: Maximum concurrent API calls (default: 20)

**Output**: Results saved to `results/<mm_dd>/<timestamp>/processed_df/`

### Calculating Metrics

#### F1 Scores
Compare ground truth vs. predicted evaluations:

```bash
cd src/calculate_metrics
python calculate_F1_score.py
```

**Configuration**:
- Set `binary = True/False` for binary or ternary evaluation
- Update file paths for ground truth and predicted datasets

**Output**: Macro F1 scores for each model (Gemini, ChatGPT, Perplexity)

#### Weighted Scores
Calculate weighted scores based on rubric weights:

```bash
python calculate_final_score.py
```

**Scoring**:
- Satisfied: 1.0
- Partially Satisfied: 0.5
- Not Satisfied: 0.0

Score = Σ(weight × score) / Σ(positive weights)

#### Failure Breakdown
Analyze failure patterns by rubric category:

```bash
python calculate_failure_breakdown.py
```

**Output**:
- Per-task average failure ratios by category
- Aggregate failure distribution across all tasks
- Identification of common failure patterns

## Data Format

### Input CSV Format

Raw CSV files should contain:
- Row 0: Task prompt
- Rows 1+: Rubric evaluations with columns:
  - `title`: Rubric criterion title
  - `weight`: Rubric weight (numeric)
  - `category`: Rubric category
  - `gemini_present`: Ground truth for Gemini
  - `chatgpt_present`: Ground truth for ChatGPT
  - `perplexity_present`: Ground truth for Perplexity

### Compiled Dataset Format

The compiled dataset (`compiled_dataset.csv`) contains:

```
csv_filename,task_name,prompt,rubrics,rubrics_count,pdf_paths,final_presence
```

- `rubrics`: JSON array of rubric objects
- `pdf_paths`: JSON object with paths to PDFs for each model
- `final_presence`: JSON object with ground truth evaluations

## Configuration

### Environment Variables

Create a `.env` file from the template:

```bash
cp .env.example .env
```

Required variables:
```
OPENAI_API_KEY=your_api_key_here
```

Optional variables:
```
API_BASE_URL=https://your-custom-endpoint.com
MODEL_NAME=gpt-5
```

### API Configuration

The evaluation scripts support:
- **OpenAI API**: Set `OPENAI_API_KEY`
- **Custom endpoints**: Set both `OPENAI_API_KEY` and `API_BASE_URL`
- **LiteLLM proxy**: Supported via custom base URL

### Model Support

Supported models (configurable in evaluation scripts):
- `gpt-5` (default)
- `gpt-4o`
- `gpt-4.1`
- `litellm_proxy/gemini/gemini-2.5-pro-preview-06-05`

## Advanced Features

### Document Chunking

For large documents exceeding token limits, the evaluator automatically:
1. Splits documents into chunks
2. Evaluates each chunk independently
3. Synthesizes findings into final verdict

### Caching

- **Markdown Conversion**: Cached in `cache/` directory
- **Document Content**: Cached in memory during batch processing

### Parallel Processing

Batch evaluation uses asynchronous processing with configurable concurrency:
```python
evaluator = RubricEvaluator(max_concurrent=20)
```

## Evaluation Modes

### Binary Mode
- **Classes**: Satisfied, Not Satisfied
- **Use Case**: Strict pass/fail evaluation
- **Configuration**: Set `binary=True`

### Ternary Mode (Default)
- **Classes**: Satisfied, Partially Satisfied, Not Satisfied
- **Use Case**: Nuanced evaluation with partial credit
- **Configuration**: Set `binary=False`

## Troubleshooting

### Common Issues

1. **API Rate Limits**: Reduce `max_concurrent` in evaluation scripts
2. **Missing PDFs**: Check `pdf_paths` errors in extraction output
3. **Empty Results**: Verify CSV format matches expected structure
4. **Markdown Conversion Fails**: Install `markitdown` or check PDF file validity

### Logging

Adjust logging level in scripts:
```python
logging.basicConfig(level=logging.DEBUG)  # For detailed output
```

## Performance

Typical performance on a standard dataset:
- **Extraction**: ~1-2 seconds per task
- **Evaluation**: ~5-10 seconds per task (depends on document size and API latency)
- **Metrics**: <1 second for full dataset

## Citation

If you use this code in your research, please cite:

```bibtex
@inproceedings{deepresearch2025,
  title={Deep Research Benchmarks},
  author={[Authors]},
  booktitle={International Conference on Learning Representations (ICLR)},
  year={2025}
}
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For questions or issues, please open an issue on GitHub or contact [contact email].

## Acknowledgments

This research was conducted as part of [institution/project name]. We thank the contributors and reviewers for their valuable feedback.
