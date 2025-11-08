# Quick Start Guide

This guide will help you get started with the Deep Research Benchmarks codebase in minutes.

## Prerequisites

- Python 3.8+
- OpenAI API key (or compatible endpoint)

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd public_release_experiments

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

## Basic Workflow

### Step 1: Extract Rubrics

Process your raw CSV files to extract rubrics and ground truth:

```bash
cd src/extract_rubrics
python extract_rubrics_batch.py
```

**Output**: `data/processed_df/compiled_dataset.csv` and `compiled_dataset.parquet`

### Step 2: Evaluate with LLMs

Evaluate documents against rubric criteria:

```bash
cd ../evaluate_rubrics
python evaluate_rubrics_batch.py
```

**Output**: `results/<date>/<timestamp>/processed_df/compiled_dataset.csv`

### Step 3: Calculate Metrics

Compare ground truth vs predictions:

```bash
cd ../calculate_metrics

# Calculate F1 scores
python calculate_F1_score.py

# Calculate weighted scores
python calculate_final_score.py

# Analyze failure patterns
python calculate_failure_breakdown.py
```

## Example: Single Task Evaluation

For testing or debugging, evaluate a single task:

```python
import asyncio
import sys
from pathlib import Path

# Add src directory to path if running from project root
sys.path.insert(0, str(Path(__file__).parent / 'src' / 'evaluate_rubrics'))

from evaluate_rubrics_markitdown_onetask import evaluate_task_rubrics

async def main():
    # Evaluate a specific task
    results_df = await evaluate_task_rubrics(
        task_name="683a58c9a7e7fe4e7695846f",
        binary=False  # Use ternary evaluation
    )
    
    # Display results
    print(f"Evaluated {len(results_df)} rubrics")
    print(f"Average score: {results_df['score'].mean():.3f}")
    print(f"Total cost: ${results_df['cost'].sum():.4f}")

asyncio.run(main())
```

**Note**: When running scripts from their directories (e.g., `cd src/evaluate_rubrics && python evaluate_rubrics_batch.py`), imports work automatically.

## Example: Custom Configuration

Customize evaluation parameters:

```python
import asyncio
import os
import sys
from pathlib import Path

# Add src directory to path if needed
sys.path.insert(0, str(Path(__file__).parent / 'src' / 'evaluate_rubrics'))

from evaluate_rubrics_markitdown_onetask import RubricEvaluator

# Initialize with custom settings
evaluator = RubricEvaluator(
    api_key=os.getenv("OPENAI_API_KEY"),
    base_url="https://example.com",  # Custom endpoint
    model="gpt-4o",           # Use GPT-4o instead of GPT-5
    binary=True,              # Binary evaluation mode
    max_concurrent=10         # Limit concurrent requests
)

# Process documents
async def main():
    results = await evaluator.evaluate_all_rubrics(
        rubrics=rubrics,
        pdf_paths=pdf_paths,
        save_results=True
    )
    print(f"Evaluation complete: {len(results)} results")

asyncio.run(main())
```

## Example: Binary vs Ternary Evaluation

**Ternary Mode** (default - 3 classes):
```python
results = await evaluate_task_rubrics(
    task_name="your_task",
    binary=False  # Satisfied / Partially Satisfied / Not Satisfied
)
```

**Binary Mode** (strict pass/fail):
```python
results = await evaluate_task_rubrics(
    task_name="your_task",
    binary=True  # Satisfied / Not Satisfied
)
```

## Example: Batch Processing with Progress

Monitor progress during batch processing:

```python
from tqdm import tqdm
import pandas as pd

# Load all tasks
df = pd.read_csv("data/processed_df/compiled_dataset.csv")

results = []
for idx, task_row in tqdm(df.iterrows(), total=len(df)):
    result = await evaluate_task_rubrics(
        task_row=task_row,
        save_results=False
    )
    results.append(result)
```

## Example: Calculate Custom Metrics

Calculate metrics on your results:

```python
import sys
from pathlib import Path

# Add src directory to path if needed
sys.path.insert(0, str(Path(__file__).parent / 'src' / 'calculate_metrics'))

from calculate_F1_score import (
    load_data, 
    calculate_model_f1_scores,
    calculate_average_f1_scores
)

# Define paths relative to project root
base_dir = Path(__file__).parent
ground_truth_path = base_dir / "data" / "processed_df" / "compiled_dataset.parquet"
predicted_path = base_dir / "results" / "11_04" / "20251104_034416" / "processed_df" / "compiled_dataset.parquet"

# Load ground truth and predictions
ground_truth_df = load_data(ground_truth_path)
predicted_df = load_data(predicted_path)

# Calculate F1 scores
f1_scores = calculate_model_f1_scores(
    ground_truth_df, 
    predicted_df,
    binary=False  # Ternary evaluation
)

# Get averages
avg_f1 = calculate_average_f1_scores(f1_scores)

# Display results
for model, score in avg_f1.items():
    print(f"{model}: {score:.4f}")
```

**Note**: When running from `src/calculate_metrics/` directory, the scripts handle paths automatically.

## Troubleshooting

### API Rate Limits
If you hit rate limits, reduce concurrency:
```python
evaluator = RubricEvaluator(max_concurrent=5)  # Lower concurrency
```

### Missing PDFs
If PDFs fail to download, place them manually in:
```
data/predownloaded_pdfs/<task_name>/
├── gemini.pdf
├── chatgpt.pdf
└── perplexity.pdf
```

### Memory Issues
For large batches, process in smaller chunks:
```python
# Process first 10 tasks
limited_df = df.head(10)
results = await evaluate_batch(limited_df)
```

## Common Configurations

### Using Custom API Endpoint
```python
evaluator = RubricEvaluator(
    api_key="your_key",
    base_url="https://your-endpoint.com",
    model="your-model"
)
```

### Adjusting File Paths
```python
from pathlib import Path

# Set custom paths
base_path = Path("/custom/path")
ground_truth = base_path / "data" / "compiled_dataset.parquet"
predicted = base_path / "results" / "compiled_dataset.parquet"
```

### Saving Intermediate Results
```python
# Save after each task
for task in tasks:
    result = await evaluate_task_rubrics(
        task_name=task,
        save_results=True  # Save detailed results
    )
```

## Next Steps

- Read the full [README.md](README.md) for comprehensive documentation
- Check [CONTRIBUTING.md](CONTRIBUTING.md) to contribute
- Review the code in `src/` for implementation details
- Explore example notebooks (if available)

## Getting Help

- Open an issue on GitHub
- Check existing issues and discussions
- Contact the maintainers

Happy benchmarking! 🚀
