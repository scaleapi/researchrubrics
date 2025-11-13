# Research Rubrics - Package Summary

## 📦 Package Overview

**Project Name**: Research Rubrics  
**Version**: 1.0.0  
**Purpose**: Evaluate AI-generated research documents against structured rubric criteria using LLMs  
**License**: MIT

## 🎯 What This Package Does

Research Rubrics is a Python-based evaluation framework that:

1. **Evaluates** markdown-formatted research reports against detailed rubric criteria
2. **Uses** Gemini 2.5 Pro (via LiteLLM) for intelligent, context-aware evaluation
3. **Provides** binary grading (Satisfied/Not Satisfied) with confidence scores
4. **Calculates** weighted compliance scores based on rubric importance
5. **Handles** large documents through automatic chunking and synthesis
6. **Supports** batch processing with concurrent API calls

## 📁 Package Contents

### Total Files

- **Documentation**: 8 markdown files
- **Configuration**: 3 files (requirements.txt, setup.py, .gitignore)
- **Source Code**: 4 Python files
- **Prompt Templates**: 4 text files
- **Data**: 1 JSONL file + 3 sample markdown files

### Documentation Files (Root Directory)

| File | Purpose | Size |
|------|---------|------|
| README.md | Main documentation | ~15 KB |
| QUICKSTART.md | Quick start guide | ~8 KB |
| INSTALLATION.md | Installation instructions | ~10 KB |
| DATA_FORMAT.md | Data format specifications | ~11 KB |
| FOLDER_STRUCTURE.md | Directory organization | ~12 KB |
| FILE_MANIFEST.md | Complete file index | ~9 KB |
| SETUP_GUIDE.md | Step-by-step setup | ~8 KB |
| PACKAGE_SUMMARY.md | This file | ~5 KB |

### Configuration Files

| File | Purpose |
|------|---------|
| requirements.txt | Python dependencies (pandas, litellm, tqdm) |
| setup.py | Package installation configuration |
| .gitignore | Git exclusions |

### Source Code (`src/` directory)

```
src/
├── __init__.py
├── evaluate_rubrics/
│   ├── evaluate_single_report.py   (~640 lines)
│   └── evaluate_reports_batch.py   (~155 lines)
├── calculate_metrics/
│   └── calculate_compliance_score.py (~52 lines)
└── prompts/
    ├── system_prompt.txt
    ├── user_prompt.txt
    ├── chunk_prompt_template.txt
    └── synthesis_prompt_template.txt
```

**Total Source Code**: ~850 lines of Python

### Data Files

```
data/researchrubrics/
├── processed_data.jsonl       (5 sample tasks)
└── README.md                   (Dataset template)

agent_responses/
├── 683a58c9a7e7fe4e7695846f.md
├── 683a58c9a7e7fe4e7695848b.md
└── 683a58c9a7e7fe4e7695848e.md
```

## 🔧 Core Components

### 1. Rubric Evaluator (`evaluate_single_report.py`)

**Main Class**: `RubricEvaluator`

**Key Features**:
- Async LLM API calls with retry logic
- Automatic document chunking for large files
- Configurable concurrency (default: 20 concurrent requests)
- Token usage and cost tracking
- Confidence scoring

**Key Functions**:
- `evaluate_task_rubrics()` - Evaluate one markdown file
- `evaluate_single_rubric()` - Evaluate one rubric
- `chunk_document()` - Split large documents
- `synthesize_verdicts()` - Combine chunk results

### 2. Batch Evaluator (`evaluate_reports_batch.py`)

**Main Function**: `evaluate_all_reports()`

**Features**:
- Processes all markdown files in `agent_responses/`
- Generates timestamped JSONL output
- Tracks total cost and token usage
- Displays progress with tqdm

### 3. Compliance Calculator (`calculate_compliance_score.py`)

**Main Function**: `calculate_compliance_score()`

**Features**:
- Calculates weighted compliance scores
- Handles negative-weight (penalty) rubrics
- Displays per-sample and aggregate scores

### 4. Prompt Templates

- **system_prompt.txt**: System-level instructions for the LLM
- **user_prompt.txt**: Template for rubric evaluation requests
- **chunk_prompt_template.txt**: Template for chunk-level evaluation
- **synthesis_prompt_template.txt**: Template for synthesizing results

## 📊 Data Flow

```
Input:
  processed_data.jsonl (rubrics)
  agent_responses/*.md (reports)
         ↓
   Evaluation Process
    (Gemini 2.5 Pro)
         ↓
Output:
  batch_evaluation_*.jsonl (results)
         ↓
   Metrics Calculation
         ↓
  Compliance Scores
```

## 🎓 Key Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| pandas | >=2.0.0 | Data manipulation |
| litellm | >=1.0.0 | LLM API access |
| tqdm | >=4.60.0 | Progress bars |

## 💾 Storage Requirements

- **Code**: ~1 MB
- **Dependencies**: ~50 MB (pandas, litellm, etc.)
- **Data**: Variable (depends on number of reports)
- **Results**: ~1 KB per rubric evaluation
- **Cache**: Minimal (reserved for future use)

## 🚀 Performance Characteristics

- **Single Rubric Evaluation**: ~5-15 seconds
- **Batch Processing**: 20 reports concurrently (default)
- **Token Usage**: 3,000-10,000 tokens per evaluation
- **Cost**: ~$0.01-$0.05 per rubric (Gemini 2.5 Pro)

## 📈 Scalability

- **Reports**: Can handle 100+ reports in one batch
- **Rubrics per Report**: Tested with 20+ rubrics per report
- **Concurrent Requests**: Configurable (5-30 recommended)
- **Document Length**: Automatic chunking for large documents

## 🔐 Security Considerations

- **API Key**: Stored in `.env` file (not committed to Git)
- **Data Privacy**: All processing local except LLM API calls
- **No Data Persistence**: Evaluation happens in memory
- **.gitignore**: Protects sensitive files from version control

## 🎯 Use Cases

1. **Research Paper Evaluation**: Grade AI-generated research reports
2. **Content Quality Assessment**: Evaluate content against criteria
3. **Automated Grading**: Batch process student submissions
4. **Benchmark Testing**: Compare different AI models' outputs

## 📖 Documentation Structure

```
Start Here:
  README.md
     ↓
Quick Start:
  QUICKSTART.md
  SETUP_GUIDE.md
     ↓
Reference:
  DATA_FORMAT.md
  FOLDER_STRUCTURE.md
  FILE_MANIFEST.md
     ↓
Detailed Setup:
  INSTALLATION.md
```

## ✅ Quality Assurance

- **Code Quality**: Well-structured, documented functions
- **Error Handling**: Comprehensive try-catch blocks
- **Logging**: Detailed logging for debugging
- **Retry Logic**: Exponential backoff for API failures
- **Validation**: Input validation for data files

## 🔄 Extensibility

Easy to extend:
- **New Models**: Change `model` parameter
- **Custom Prompts**: Modify prompt templates
- **Different Grading**: Modify verdict logic
- **Additional Metrics**: Add to `calculate_metrics/`

## 📦 Distribution Checklist

When distributing:

✅ **Include**:
- All documentation files
- Configuration templates
- Source code
- Prompt templates
- LICENSE and CITATION.bib
- Empty directory structure

❌ **Exclude**:
- `.env` file with real API keys
- Actual evaluation results
- Cache files
- `__pycache__` directories

## 🎓 Educational Value

This package demonstrates:
- Async Python programming
- LLM API integration
- Batch processing patterns
- Document chunking strategies
- Error handling best practices
- Configuration management

## 📞 Support

**Documentation**: See all `.md` files in root directory  
**Issues**: GitHub Issues  
**Updates**: Git pull from main branch  

## 🔗 Related Resources

- LiteLLM Documentation: https://docs.litellm.ai/
- Pandas Documentation: https://pandas.pydata.org/
- Python AsyncIO: https://docs.python.org/3/library/asyncio.html

## 📊 Package Statistics

- **Total Lines of Code**: ~850 (Python)
- **Total Lines of Documentation**: ~2,000 (Markdown)
- **Test Coverage**: Minimal (ready for expansion)
- **Python Version**: 3.8+
- **Platform**: Cross-platform (Windows, macOS, Linux)

---

**Package Version**: 1.0.0  
**Release Date**: 2025-11-13  
**Maintained By**: Research Team  
**Status**: Production Ready

**Next Steps**: Read [README.md](README.md) to get started!
