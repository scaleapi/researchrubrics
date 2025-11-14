# ResearchRubrics

Official code release for the ResearchRubrics project. This repository contains tools for evaluating AI-generated research documents against structured rubric criteria using Large Language Models (LLMs).

## Overview

This codebase provides a complete pipeline for evaluating AI-generated research reports (in markdown format) against structured rubric criteria:

1. **Rubric-Based Evaluation**: Use LLMs to evaluate whether markdown documents satisfy specific rubric criteria
2. **Batch Processing**: Evaluate multiple research reports efficiently with concurrent processing
3. **Compliance Scoring**: Calculate compliance scores based on weighted rubric evaluations

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Repository Structure](#repository-structure)
- [Usage](#usage)
  - [Evaluating Single Reports](#evaluating-single-reports)
  - [Batch Evaluation](#batch-evaluation)
  - [Calculating Compliance Scores](#calculating-compliance-scores)
- [Data Format](#data-format)
- [Configuration](#configuration)
- [Citation](#citation)
- [License](#license)

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- LiteLLM API key (for accessing Gemini 2.5 Pro)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd researchrubrics
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Download the dataset:
```bash
mkdir -p data/researchrubrics
huggingface-cli download ScaleAI/researchrubrics processed_data.jsonl --local-dir data/researchrubrics
```

4. Configure API credentials:
```bash
# Create .env file in project root
echo "LITELLM_API_KEY=your_api_key_here" > .env
```

## Quick Start

```bash
# Navigate to project root
cd researchrubrics

# 1. Install dependencies
pip install -r requirements.txt

# 2. Download the dataset
mkdir -p data/researchrubrics
huggingface-cli download ScaleAI/researchrubrics processed_data.jsonl --local-dir data/researchrubrics

# 3. Configure API key
echo "LITELLM_API_KEY=your_api_key_here" > .env

# 4. Place markdown reports in agent_responses/ directory
# (Reports should be named with task IDs, e.g., 683a58c9a7e7fe4e7695846f.md)

# 5. Evaluate all reports
cd src/evaluate_rubrics
python evaluate_reports_batch.py

# 6. Calculate compliance scores
cd ../calculate_metrics
python calculate_compliance_score.py
```

## Repository Structure

```
researchrubrics/
├── src/
│   ├── __init__.py
│   ├── evaluate_rubrics/          # LLM-based rubric evaluation
│   │   ├── evaluate_single_report.py  # Single markdown evaluation
│   │   └── evaluate_reports_batch.py  # Batch evaluation script
│   ├── calculate_metrics/         # Metrics computation
│   │   └── calculate_compliance_score.py
│   └── prompts/                   # Evaluation prompt templates
│       ├── system_prompt.txt
│       ├── user_prompt.txt
│       ├── chunk_prompt_template.txt
│       └── synthesis_prompt_template.txt
├── data/
│   └── researchrubrics/           # Input data
│       ├── processed_data.jsonl   # Rubrics and metadata (JSONL format)
│       └── README.md              # Dataset documentation
├── agent_responses/               # Input: Markdown reports to evaluate
│   └── [task_id].md               # One file per task
├── results/                       # Evaluation results (JSONL format)
│   └── batch_evaluation_YYYYMMDD_HHMMSS.jsonl
├── cache/                         # Cached markdown conversions
├── tests/
│   └── __init__.py
├── requirements.txt
├── .env                           # Your API key (DO NOT COMMIT)
├── .gitignore
├── setup.py
├── LICENSE
├── CITATION.bib
└── README.md
```

## Usage

### Evaluating Single Reports

Evaluate a single markdown report against its rubrics:

```python
import asyncio
from pathlib import Path
from evaluate_single_report import evaluate_task_rubrics

async def main():
    # Evaluate a specific markdown file
    markdown_file = "agent_responses/683a58c9a7e7fe4e7695846f.md"
    results_df, compliance_score = await evaluate_task_rubrics(markdown_file)
    
    # Display results
    print(f"Compliance Score: {compliance_score:.2%}")
    print(f"Evaluated {len(results_df)} rubrics")
    print(f"Total cost: ${results_df['cost'].sum():.4f}")

asyncio.run(main())
```

**Output**: Returns a DataFrame with evaluation results and a compliance score.

### Batch Evaluation

Evaluate all markdown reports in the `agent_responses/` directory:

```bash
cd src/evaluate_rubrics
python evaluate_reports_batch.py
```

**Features**:
- Processes all `.md` files in `agent_responses/`
- Uses binary grading (Satisfied/Not Satisfied)
- Powered by Gemini 2.5 Pro via LiteLLM
- Concurrent processing (default: 20 concurrent requests)
- Automatic retry logic with exponential backoff

**Output**: Results saved to `results/batch_evaluation_YYYYMMDD_HHMMSS.jsonl`

**Configuration Options**:
- `model`: LLM model to use (default: "litellm_proxy/gemini/gemini-2.5-pro-preview-06-05")
- `max_concurrent`: Maximum concurrent API calls (default: 20)
- `agent_responses_dir`: Directory containing markdown files (default: "agent_responses/")
- `output_file`: Custom output file path (optional)

### Calculating Compliance Scores

Calculate compliance scores from evaluation results:

```bash
cd src/calculate_metrics
python calculate_compliance_score.py
```

**Scoring**:
- Binary grading: Satisfied = 1.0, Not Satisfied = 0.0
- Compliance Score = Σ(weight × score) / Σ(positive weights)
- Excludes negative-weight rubrics from denominator

**Output**: Displays compliance scores for each evaluated report

## Data Format

### Input Data (processed_data.jsonl)

The input data file `data/researchrubrics/processed_data.jsonl` should be downloaded from the [ScaleAI/researchrubrics](https://huggingface.co/datasets/ScaleAI/researchrubrics) HuggingFace dataset and placed in the `data/researchrubrics/` directory. The file contains one JSON object per line:

```json
{
  "prompt": "Task description...",
  "sample_id": "683a58c9a7e7fe4e7695846f",
  "domain": "AI & ML",
  "conceptual_breadth": "Moderate",
  "logical_nesting": "Intermediate",
  "exploration": "Medium",
  "rubrics": [
    {
      "criterion": "Rubric description...",
      "weight": 4.0,
      "axis": "Explicit Criteria"
    }
  ]
}
```

**Fields**:
- `prompt`: The research task/question
- `sample_id`: Unique identifier matching markdown filename
- `domain`: Domain category
- `conceptual_breadth`, `logical_nesting`, `exploration`: Task complexity metrics
- `rubrics`: Array of evaluation criteria with weights and categories

### Markdown Reports (agent_responses/)

Input markdown files should be named with their `sample_id` (e.g., `683a58c9a7e7fe4e7695846f.md`) and contain the AI-generated research report to evaluate.

### Evaluation Results (results/*.jsonl)

Output JSONL file with one evaluation result per line:

```json
{
  "sample_id": "683a58c9a7e7fe4e7695846f",
  "rubric_title": "Rubric description...",
  "verdict": "Satisfied",
  "score": 1.0,
  "confidence": 0.95,
  "reasoning": "Detailed explanation...",
  "tokens_used": 4567,
  "cost": 0.0247,
  "success": true,
  "weight": 4.0
}
```

## Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
echo "LITELLM_API_KEY=your_api_key_here" > .env
```

Required variables:
```
LITELLM_API_KEY=your_api_key_here
```

Optional variables (only needed if using a custom LiteLLM proxy):
```
API_BASE_URL=https://your-custom-endpoint.com
```

### API Configuration

The evaluation scripts use **LiteLLM** to access Gemini 2.5 Pro:
- Set `LITELLM_API_KEY` in your `.env` file
- Default model: `litellm_proxy/gemini/gemini-2.5-pro-preview-06-05`
- Custom base URL supported via `API_BASE_URL` environment variable

### Model Configuration

In `evaluate_single_report.py`, you can customize:

```python
evaluator = RubricEvaluator(
    model="litellm_proxy/gemini/gemini-2.5-pro-preview-06-05",
    max_concurrent=20  # Adjust based on rate limits
)
```

## Advanced Features

### Document Chunking

For large documents exceeding token limits, the evaluator automatically:
1. Splits documents into manageable chunks (8000 tokens per chunk)
2. Evaluates each chunk independently using chunk-specific prompts
3. Synthesizes chunk findings into a final verdict
4. Uses separate prompt templates for chunking and synthesis

### Caching

- **Markdown Parsing**: Internal caching to avoid redundant parsing
- The `cache/` directory is reserved for future use

### Parallel Processing

Batch evaluation uses asynchronous processing with configurable concurrency:
```python
evaluator = RubricEvaluator(max_concurrent=20)
```

Adjust `max_concurrent` based on your API rate limits.

### Retry Logic

Automatic retry with exponential backoff:
- Maximum 3 retries per request
- Exponential backoff: 2^retry_count seconds
- Handles rate limits and transient errors gracefully

## Evaluation Mode

### Binary Grading (Current Implementation)
- **Classes**: Satisfied, Not Satisfied
- **Scoring**: 1.0 for Satisfied, 0.0 for Not Satisfied
- **Use Case**: Clear pass/fail evaluation
- **Prompts**: Uses prompts from `src/prompts/` directory

## Troubleshooting

### Common Issues

1. **API Rate Limits**: Reduce `max_concurrent` in `RubricEvaluator` initialization
   ```python
   evaluator = RubricEvaluator(max_concurrent=5)
   ```

2. **Missing Input Data**: Ensure `data/researchrubrics/processed_data.jsonl` exists
3. **Missing Markdown Files**: Check that markdown files exist in `agent_responses/` with matching `sample_id` names
4. **API Key Issues**: Verify `.env` file is in project root with correct `LITELLM_API_KEY`

### Logging

The scripts use Python's logging module. Adjust logging level:
```python
logging.basicConfig(level=logging.DEBUG)  # For detailed output
logging.basicConfig(level=logging.INFO)   # For standard output
logging.basicConfig(level=logging.WARNING) # For minimal output
```

## Performance

Typical performance metrics:
- **Single Report Evaluation**: ~10-30 seconds (depends on document length and rubric count)
- **Batch Processing**: Processes 20 reports concurrently (configurable)
- **Token Usage**: Varies by document length; typically 3,000-10,000 tokens per rubric evaluation
- **Cost**: Approximately $0.01-$0.05 per rubric evaluation (Gemini 2.5 Pro pricing)

## Citation

If you use this code in your research, please cite:

```bibtex
@misc{sharma2025researchrubricsbenchmarkpromptsrubrics,
  title={ResearchRubrics: A Benchmark of Prompts and Rubrics For Evaluating Deep Research Agents}, 
  author={Manasi Sharma and Chen Bo Calvin Zhang and Chaithanya Bandi and Clinton Wang and Ankit Aich and Huy Nghiem and Tahseen Rabbani and Ye Htet and Brian Jang and Sumana Basu and Aishwarya Balwani and Denis Peskoff and Marcos Ayestaran and Sean M. Hendryx and Brad Kenstler and Bing Liu},
  year={2025},
  eprint={2511.07685},
  archivePrefix={arXiv},
  primaryClass={cs.AI},
  url={https://arxiv.org/abs/2511.07685}
}
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For questions or issues, please open an issue on GitHub.

## Acknowledgments

We thank the contributors and reviewers for their valuable feedback.
