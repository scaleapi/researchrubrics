# Quick Start Guide

This guide will help you get started with the Research Rubrics codebase in minutes.

## Prerequisites

- Python 3.8+
- LiteLLM API key (for accessing Gemini 2.5 Pro)

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd researchrubrics

# Install dependencies
pip install -r requirements.txt

# Set up environment
echo "LITELLM_API_KEY=your_api_key_here" > .env
```

## Basic Workflow

### Step 1: Prepare Your Data

Ensure you have:
1. `data/researchrubrics/processed_data.jsonl` - Contains rubrics and prompts
2. Markdown files in `agent_responses/` - Named with sample IDs (e.g., `683a58c9a7e7fe4e7695846f.md`)

### Step 2: Evaluate Reports

```bash
cd src/evaluate_rubrics
python evaluate_reports_batch.py
```

This will:
- Process all `.md` files in `agent_responses/`
- Evaluate each report against its rubrics
- Save results to `results/batch_evaluation_YYYYMMDD_HHMMSS.jsonl`

### Step 3: Calculate Compliance Scores

```bash
cd ../calculate_metrics
python calculate_compliance_score.py
```

This will display compliance scores for each evaluated report.

## Example: Single Report Evaluation

For testing or debugging, evaluate a single report:

```python
import asyncio
from pathlib import Path
import sys

# Add src directory to path if running from project root
sys.path.insert(0, 'src/evaluate_rubrics')

from evaluate_single_report import evaluate_task_rubrics

async def main():
    # Evaluate a specific markdown file
    markdown_file = "agent_responses/683a58c9a7e7fe4e7695846f.md"
    results_df, compliance_score = await evaluate_task_rubrics(markdown_file)
    
    # Display results
    print(f"\nCompliance Score: {compliance_score:.2%}")
    print(f"Evaluated {len(results_df)} rubrics")
    print(f"Average confidence: {results_df['confidence'].mean():.2f}")
    print(f"Total tokens used: {results_df['tokens_used'].sum()}")
    print(f"Total cost: ${results_df['cost'].sum():.4f}")
    
    # Show some rubric results
    print("\nSample Results:")
    for idx, row in results_df.head(3).iterrows():
        print(f"\n{idx+1}. {row['rubric_title'][:60]}...")
        print(f"   Verdict: {row['verdict']}")
        print(f"   Score: {row['score']}")
        print(f"   Confidence: {row['confidence']}")

asyncio.run(main())
```

**Note**: When running scripts from their directories (e.g., `cd src/evaluate_rubrics && python evaluate_reports_batch.py`), imports work automatically.

## Example: Custom Configuration

Customize evaluation parameters:

```python
import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, 'src/evaluate_rubrics')

from evaluate_single_report import RubricEvaluator

async def main():
    # Initialize with custom settings
    evaluator = RubricEvaluator(
        api_key=os.getenv("LITELLM_API_KEY"),
        model="litellm_proxy/gemini/gemini-2.5-pro-preview-06-05",
        max_concurrent=10  # Reduce concurrent requests if hitting rate limits
    )
    
    # Evaluate manually
    markdown_content = Path("agent_responses/683a58c9a7e7fe4e7695846f.md").read_text()
    rubrics = [...]  # Load from processed_data.jsonl
    
    results = []
    for rubric in rubrics:
        result = await evaluator.evaluate_single_rubric(
            document_content=markdown_content,
            rubric_criterion=rubric['criterion']
        )
        results.append(result)
    
    print(f"Completed {len(results)} evaluations")

asyncio.run(main())
```

## Example: Analyzing Results

Process evaluation results:

```python
import json
import pandas as pd

# Read evaluation results
results = []
with open('results/batch_evaluation_20251113_093457.jsonl', 'r') as f:
    for line in f:
        results.append(json.loads(line))

df = pd.DataFrame(results)

# Group by sample_id
by_sample = df.groupby('sample_id').agg({
    'score': 'mean',
    'cost': 'sum',
    'tokens_used': 'sum',
    'confidence': 'mean'
})

print("\nResults by Sample:")
print(by_sample)

# Analyze by rubric axis
with open('data/researchrubrics/processed_data.jsonl', 'r') as f:
    data = [json.loads(line) for line in f]

# Find which rubric axes have the lowest scores
axis_scores = {}
for _, row in df.iterrows():
    # Find the rubric's axis
    for task in data:
        if task['sample_id'] == row['sample_id']:
            for rubric in task['rubrics']:
                if rubric['criterion'] == row['rubric_title']:
                    axis = rubric['axis']
                    if axis not in axis_scores:
                        axis_scores[axis] = []
                    axis_scores[axis].append(row['score'])
                    break

print("\nAverage Scores by Axis:")
for axis, scores in axis_scores.items():
    print(f"{axis}: {sum(scores)/len(scores):.2%}")
```

## Troubleshooting

### API Rate Limits
If you hit rate limits, reduce concurrency:
```python
evaluator = RubricEvaluator(max_concurrent=5)
```

### Missing Input Data
Ensure `data/researchrubrics/processed_data.jsonl` exists:
```bash
ls data/researchrubrics/processed_data.jsonl
```

### Missing Markdown Files
Check that markdown files exist in `agent_responses/`:
```bash
ls agent_responses/*.md
```

### API Key Issues
Verify `.env` file is in project root with correct key:
```bash
cat .env
# Should show: LITELLM_API_KEY=your_actual_key
```

## Common Configurations

### Using Custom Model

```python
evaluator = RubricEvaluator(
    model="litellm_proxy/gemini/gemini-2.5-pro-preview-06-05"  # Change model here
)
```

### Adjusting Concurrency

```python
# Conservative (for rate limit sensitive APIs)
evaluator = RubricEvaluator(max_concurrent=5)

# Aggressive (for higher throughput)
evaluator = RubricEvaluator(max_concurrent=30)
```

### Custom Output Location

```python
# In evaluate_reports_batch.py
await evaluate_all_reports(
    agent_responses_dir="agent_responses",
    output_file="results/my_custom_results.jsonl"
)
```

## Expected Performance

Typical performance metrics:
- **Single rubric evaluation**: ~5-15 seconds (depends on document length)
- **Batch processing**: 20 reports concurrently by default
- **Token usage**: 3,000-10,000 tokens per rubric evaluation
- **Cost**: ~$0.01-$0.05 per rubric evaluation (Gemini 2.5 Pro pricing)

## Next Steps

- Read the full [README.md](README.md) for comprehensive documentation
- Check [DATA_FORMAT.md](DATA_FORMAT.md) for data format details
- Review [INSTALLATION.md](INSTALLATION.md) for detailed setup
- See [FOLDER_STRUCTURE.md](FOLDER_STRUCTURE.md) for project organization

## Getting Help

- Check existing issues on GitHub
- Open a new issue with your question
- Include error messages and relevant code snippets

Happy evaluating! 🚀
