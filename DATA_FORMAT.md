# Data Format Specification

This document describes the data formats used throughout the Research Rubrics evaluation pipeline.

## Table of Contents

- [Input Formats](#input-formats)
  - [Processed Data JSONL](#processed-data-jsonl)
  - [Markdown Reports](#markdown-reports)
- [Output Formats](#output-formats)
  - [Evaluation Results JSONL](#evaluation-results-jsonl)
  - [Compliance Scores](#compliance-scores)

## Input Formats

### Processed Data JSONL

File: `data/researchrubrics/processed_data.jsonl`

This file contains one JSON object per line, with each object representing a research task and its evaluation rubrics.

#### Structure

Each line is a JSON object with the following fields:

| Field | Type | Description |
|-------|------|-------------|
| prompt | string | The research task/question given to the AI |
| sample_id | string | Unique identifier for the task (used as markdown filename) |
| domain | string | Domain category (e.g., "AI & ML", "Historical Analysis") |
| conceptual_breadth | string | Task complexity: "Simple", "Moderate", "Complex" |
| logical_nesting | string | Reasoning depth: "Simple", "Intermediate", "Complex" |
| exploration | string | Research scope: "Low", "Medium", "High" |
| rubrics | array | List of evaluation criteria (see Rubric Format below) |

#### Rubric Format

Each rubric in the `rubrics` array contains:

| Field | Type | Description |
|-------|------|-------------|
| criterion | string | The evaluation criterion description |
| weight | float | Weight of this criterion (can be positive or negative) |
| axis | string | Category (e.g., "Explicit Criteria", "Communication Quality") |

#### Example

```json
{
  "prompt": "Write a synthesis report on the applications of AI in drug discovery for a technical audience unfamiliar with biology...",
  "sample_id": "6847465956a0f6376a605355",
  "domain": "AI & ML",
  "conceptual_breadth": "Moderate",
  "logical_nesting": "Intermediate",
  "exploration": "Medium",
  "rubrics": [
    {
      "criterion": "The response describes at least one specific AI application for each drug-discovery stage...",
      "weight": 5.0,
      "axis": "Explicit Criteria"
    },
    {
      "criterion": "The response provides brief (≤20 words) definitions for specialized terms...",
      "weight": 5.0,
      "axis": "Instruction Following"
    },
    {
      "criterion": "The response uses deterministic language for speculative claims...",
      "weight": -4.0,
      "axis": "Implicit Criteria"
    }
  ]
}
```

**Note**: Negative weights indicate penalty rubrics (failures that should NOT occur).

### Markdown Reports

File location: `agent_responses/[sample_id].md`

These are the AI-generated research reports to be evaluated. Each markdown file should:
- Be named with its corresponding `sample_id` from `processed_data.jsonl`
- Contain the complete text of the AI-generated research report
- Be in markdown format (plain text with markdown formatting)

#### Example Filename

For a task with `sample_id: "6847465956a0f6376a605355"`, the markdown file should be:
```
agent_responses/6847465956a0f6376a605355.md
```

#### Content Example

```markdown
# AI Applications in Drug Discovery

## Introduction

Artificial Intelligence (AI) has revolutionized the drug discovery process...

## Target Identification

AI models such as Convolutional Neural Networks (CNNs) can analyze...

## Conclusion

The integration of AI into drug discovery pipelines represents...
```

## Output Formats

### Evaluation Results JSONL

File location: `results/batch_evaluation_YYYYMMDD_HHMMSS.jsonl`

After evaluation, results are saved as JSONL with one evaluation record per line.

#### Structure

Each line represents a single rubric evaluation:

| Field | Type | Description |
|-------|------|-------------|
| sample_id | string | Task identifier matching the markdown filename |
| rubric_title | string | The rubric criterion that was evaluated |
| verdict | string | "Satisfied" or "Not Satisfied" |
| score | float | 1.0 for Satisfied, 0.0 for Not Satisfied |
| confidence | float | Model's confidence (0.0 to 1.0) |
| reasoning | string | Detailed explanation for the verdict |
| tokens_used | integer | Number of tokens consumed |
| cost | float | API cost for this evaluation (in USD) |
| success | boolean | Whether evaluation completed successfully |
| weight | float | Weight of this rubric from input data |

#### Example

```json
{
  "sample_id": "683a58c9a7e7fe4e7695846f",
  "rubric_title": "The response ensures all acronyms are expanded...",
  "verdict": "Not Satisfied",
  "score": 0.0,
  "confidence": 1.0,
  "reasoning": "The document fails to meet the criterion because it does not expand any of the acronyms it uses (AMC, AIME, USA J MO, IMO)...",
  "tokens_used": 4567,
  "cost": 0.024739999999999998,
  "success": true,
  "weight": 4.0
}
```

### Compliance Scores

Calculated from evaluation results using the formula:

```
Compliance Score = Σ(weight × score) / Σ(positive weights)
```

Where:
- Only positive-weight rubrics are included in the denominator
- Negative-weight rubrics (penalties) subtract from the numerator
- Final score is typically between 0.0 and 1.0 (but can be negative if penalties exceed gains)

#### Console Output Example

```
Compliance Scores:
==================
Sample 683a58c9a7e7fe4e7695846f: 0.65 (65%)
Sample 683a58c9a7e7fe4e7695848b: 0.82 (82%)
Sample 683a58c9a7e7fe4e7695848e: 0.71 (71%)

Average Compliance: 0.73 (73%)
```

## Validation Rules

### Required Fields

#### Input Data (processed_data.jsonl)
Each JSON object must include:
- Non-empty `prompt` string
- Valid `sample_id` string  
- Non-empty `rubrics` array with at least one rubric
- Each rubric must have `criterion`, `weight`, and `axis` fields

#### Markdown Reports
- File must exist in `agent_responses/` directory
- Filename must match a `sample_id` from `processed_data.jsonl`
- File must contain readable markdown text

### Value Constraints

- **Verdict values**: Must be one of:
  - "Satisfied"
  - "Not Satisfied"
- **Weights**: Float values (can be positive or negative)
  - Positive weights: Typical values are 1.0 to 5.0
  - Negative weights: Penalties, typically -1.0 to -5.0
- **Scores**: 
  - Binary: 0.0 or 1.0
- **Confidence**: Float between 0.0 and 1.0

### Data Integrity

- Each markdown file in `agent_responses/` should have a corresponding entry in `processed_data.jsonl`
- Number of evaluation results should match the number of rubrics for each sample
- All JSON lines must be valid and parseable

## File Formats

### JSONL Files

- Encoding: UTF-8
- One JSON object per line
- Each line must be valid JSON
- Line endings: Unix (LF) preferred, Windows (CRLF) acceptable
- No trailing commas
- Use double quotes for all strings

### Markdown Files

- Encoding: UTF-8
- Standard markdown syntax
- Line endings: Unix (LF) preferred, Windows (CRLF) acceptable

## Example Complete Dataset

See the actual `data/researchrubrics/processed_data.jsonl` file for complete examples with multiple tasks and all required fields.

## Working with JSONL

### Reading JSONL in Python

```python
import json

# Read all entries
data = []
with open('data/researchrubrics/processed_data.jsonl', 'r') as f:
    for line in f:
        data.append(json.loads(line))

# Access first task
first_task = data[0]
print(f"Sample ID: {first_task['sample_id']}")
print(f"Number of rubrics: {len(first_task['rubrics'])}")
```

### Reading Evaluation Results

```python
import json
import pandas as pd

# Read evaluation results into a DataFrame
results = []
with open('results/batch_evaluation_20251113_093457.jsonl', 'r') as f:
    for line in f:
        results.append(json.loads(line))

df = pd.DataFrame(results)

# Group by sample_id to get per-task metrics
by_sample = df.groupby('sample_id').agg({
    'score': 'mean',
    'cost': 'sum',
    'tokens_used': 'sum'
})
```

## Questions?

For questions about data formats, please open an issue or refer to the code documentation.
