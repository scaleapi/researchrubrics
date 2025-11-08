# Data Format Specification

This document describes the data formats used throughout the Deep Research Benchmarks pipeline.

## Table of Contents

- [Input Formats](#input-formats)
  - [Raw CSV Format](#raw-csv-format)
- [Intermediate Formats](#intermediate-formats)
  - [Compiled Dataset](#compiled-dataset)
  - [Rubric Format](#rubric-format)
- [Output Formats](#output-formats)
  - [Evaluation Results](#evaluation-results)
  - [Metrics Output](#metrics-output)

## Input Formats

### Raw CSV Format

Raw evaluation CSV files should follow this structure:

#### Structure

| Row | Column | Description |
|-----|--------|-------------|
| 0 | prompt | The original task prompt |
| 1+ | title | Rubric criterion title |
| 1+ | weight | Numerical weight (e.g., 1.0) |
| 1+ | category | Rubric category (e.g., "Accuracy", "Completeness") |
| 1+ | gemini_present | Ground truth for Gemini (Satisfied/Partially Satisfied/Not Satisfied) |
| 1+ | chatgpt_present | Ground truth for ChatGPT |
| 1+ | perplexity_present | Ground truth for Perplexity |

#### Special Rows

- **Row 0**: Task prompt
- **Row 3**: Gemini PDF URL in `prompt` column
- **Row 6**: ChatGPT PDF URL in `prompt` column
- **Row 9**: Perplexity PDF URL in `prompt` column

#### Example

```csv
prompt,title,weight,category,gemini_present,chatgpt_present,perplexity_present
"Analyze the impact of climate change...",,,,,
,Data Sources,1.0,Accuracy,Satisfied,Satisfied,Partially Satisfied
,Citation Quality,1.0,References,Satisfied,Not Satisfied,Satisfied
https://example.com/gemini.pdf,,,,,
,Methodology,1.0,Completeness,Partially Satisfied,Satisfied,Satisfied
,Analysis Depth,1.0,Quality,Satisfied,Satisfied,Not Satisfied
https://example.com/chatgpt.pdf,,,,,
,Conclusion,1.0,Structure,Satisfied,Partially Satisfied,Satisfied
,Visual Elements,0.5,Presentation,Not Satisfied,Satisfied,Satisfied
https://example.com/perplexity.pdf,,,,,
```

## Intermediate Formats

### Compiled Dataset

After extraction, data is compiled into `compiled_dataset.csv`:

#### Columns

| Column | Type | Description |
|--------|------|-------------|
| csv_filename | string | Original CSV filename |
| task_name | string | Unique task identifier (hash) |
| prompt | string | Original task prompt |
| rubrics | JSON string | Array of rubric objects |
| rubrics_count | integer | Number of rubrics |
| pdf_paths | JSON string | Paths to PDFs for each model |
| final_presence | JSON string | Ground truth evaluations |

#### Example Row

```json
{
  "csv_filename": "683a58c9a7e7fe4e7695846f_fixed.csv",
  "task_name": "683a58c9a7e7fe4e7695846f",
  "prompt": "Analyze the impact of climate change on polar bear populations...",
  "rubrics": "[{\"title\": \"Data Sources\", \"weight\": 1.0, \"category\": \"Accuracy\", \"row_index\": 1}, ...]",
  "rubrics_count": 15,
  "pdf_paths": "{\"gemini_pdf\": {\"path\": \"data/PDFs/683.../gemini.pdf\", \"error\": null}, ...}",
  "final_presence": "{\"gemini_present\": {\"values\": [\"Satisfied\", \"Partially Satisfied\", ...], \"null_count\": 0, \"total_count\": 15}, ...}"
}
```

### Rubric Format

Each rubric is a JSON object with the following structure:

```json
{
  "title": "Data Sources",
  "weight": 1.0,
  "category": "Accuracy",
  "row_index": 1
}
```

**Fields**:
- `title` (string): The rubric criterion description
- `weight` (float): Weight for scoring (typically 1.0 or 0.5)
- `category` (string): Category classification (e.g., "Accuracy", "Completeness", "Structure")
- `row_index` (integer): Original row position in CSV

### PDF Paths Format

```json
{
  "gemini_pdf": {
    "path": "data/PDFs/683a58c9a7e7fe4e7695846f/gemini.pdf",
    "error": null
  },
  "chatgpt_pdf": {
    "path": "data/PDFs/683a58c9a7e7fe4e7695846f/chatgpt.pdf",
    "error": null
  },
  "perplexity_pdf": {
    "path": "data/PDFs/683a58c9a7e7fe4e7695846f/perplexity.pdf",
    "error": null
  }
}
```

### Final Presence Format

```json
{
  "gemini_present": {
    "values": ["Satisfied", "Partially Satisfied", "Not Satisfied", ...],
    "null_count": 0,
    "total_count": 15
  },
  "chatgpt_present": {
    "values": ["Satisfied", "Satisfied", "Not Satisfied", ...],
    "null_count": 0,
    "total_count": 15
  },
  "perplexity_present": {
    "values": ["Not Satisfied", "Satisfied", "Satisfied", ...],
    "null_count": 0,
    "total_count": 15
  }
}
```

**Fields**:
- `values` (array): List of verdicts in order of rubrics
- `null_count` (integer): Number of missing/null evaluations
- `total_count` (integer): Total number of rubrics

## Output Formats

### Evaluation Results

After LLM evaluation, results are saved with the same structure as compiled dataset, but with updated `final_presence` containing predicted values.

#### Individual Evaluation Record

During evaluation, each rubric-document pair generates:

```json
{
  "task_name": "683a58c9a7e7fe4e7695846f",
  "pdf": "gemini",
  "rubric_title": "Data Sources",
  "verdict": "Satisfied",
  "score": 1.0,
  "confidence": 0.95,
  "reasoning": "The document cites 5 peer-reviewed sources...",
  "tokens_used": 2453,
  "cost": 0.0123,
  "duration": 2.34,
  "success": true,
  "error": null
}
```

### Metrics Output

#### F1 Scores

Console output format:

```
================================================================================
MACRO F1 SCORE RESULTS
================================================================================

Average F1 Scores across 100 tasks:
  Gemini      : 0.8542
  Chatgpt     : 0.8123
  Perplexity  : 0.7891

Note: F1 scores calculated by comparing ground truth vs predicted presence lists
```

#### Weighted Scores

```
Average Scores across 100 rows:
Gemini:     0.8234
ChatGPT:    0.7956
Perplexity: 0.7723
```

#### Failure Breakdown

```
================================================================================
FAILURE RATE BREAKDOWN BY CATEGORY
================================================================================

MODEL: GEMINI
--------------------------------------------------------------------------------
Tasks with failures: 45 / 100
Total failures across all tasks: 234

Category                                  Avg Ratio    Agg Ratio    Tasks
---------------------------------------- ------------ ------------ --------
Accuracy                                     0.3456       0.3512       32
Completeness                                 0.2789       0.2845       28
Structure                                    0.1923       0.1876       21
References                                   0.1234       0.1198       15
...
```

## Validation Rules

### Required Fields

All datasets must include:
- Non-empty `task_name`
- Valid `prompt` text
- At least one rubric
- PDF paths for all three models
- Complete presence data (null_count = 0)

### Value Constraints

- **Verdict values**: Must be one of:
  - Ternary: "Satisfied", "Partially Satisfied", "Not Satisfied"
  - Binary: "Satisfied", "Not Satisfied"
- **Weights**: Positive float values (typically 0.5 or 1.0)
- **Scores**: 
  - Ternary: 0.0, 0.5, or 1.0
  - Binary: 0.0 or 1.0
- **Confidence**: Float between 0.0 and 1.0

### Data Integrity

- Number of verdicts must match number of rubrics
- All models must have the same number of evaluations
- PDF files must exist at specified paths

## File Formats

### CSV Files

- Encoding: UTF-8
- Delimiter: Comma (`,`)
- Quoting: Minimal (quote fields containing commas)
- Line endings: Unix (LF) or Windows (CRLF)

### Parquet Files

- Compression: Snappy (default)
- Schema: Inferred from pandas DataFrame
- Complex types: Stored as JSON strings

### JSON Fields

Within CSV/Parquet:
- JSON strings must be valid and parseable
- Use double quotes for JSON keys and string values
- Arrays and objects properly nested

## Example Complete Dataset

See `examples/sample_dataset.csv` for a complete example with multiple tasks and all required fields.

## Converting Between Formats

### CSV to Parquet

```python
import pandas as pd

df = pd.read_csv('compiled_dataset.csv')
df.to_parquet('compiled_dataset.parquet', index=False)
```

### Extracting JSON Fields

```python
import json
import pandas as pd

df = pd.read_csv('compiled_dataset.csv')

# Parse rubrics
df['rubrics_parsed'] = df['rubrics'].apply(json.loads)

# Parse presence data
df['presence_parsed'] = df['final_presence'].apply(json.loads)
```

## Schema Validation

Use this JSON schema to validate compiled datasets:

```json
{
  "type": "object",
  "required": ["task_name", "prompt", "rubrics", "final_presence"],
  "properties": {
    "task_name": {"type": "string", "minLength": 1},
    "prompt": {"type": "string", "minLength": 1},
    "rubrics": {"type": "string"},
    "rubrics_count": {"type": "integer", "minimum": 1},
    "final_presence": {"type": "string"}
  }
}
```

## Questions?

For questions about data formats, please open an issue or refer to the code documentation.
