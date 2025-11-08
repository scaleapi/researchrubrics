#!/usr/bin/env python3
"""
Enhanced rubric evaluation script with improved prompts and PDF processing.
Key improvements:
- Uses markdown conversion for better text processing
- Chunking strategy for large documents
- Improved prompts with better structure
- Retry logic and error handling
- Token optimization
- Comprehensive logging
"""

import os
import sys
import json
import time
import logging
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import pandas as pd
import numpy as np
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import LiteLLM client
try:
    import litellm
    from tqdm import tqdm
    litellm.suppress_debug_info = True
    litellm.set_verbose = False
    # Suppress LiteLLM and httpx logging
    logging.getLogger('LiteLLM').setLevel(logging.ERROR)
    logging.getLogger('httpx').setLevel(logging.ERROR)
    logging.getLogger('openai').setLevel(logging.ERROR)
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.error("LiteLLM library not available. Install with: pip install litellm")

# Import sklearn for metrics
try:
    from sklearn.metrics import f1_score, classification_report, confusion_matrix
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("scikit-learn not available for metrics calculation")

@dataclass
class EvaluationResult:
    """Data class for evaluation results"""
    rubric_title: str
    pdf_name: str
    verdict: str
    score: float
    confidence: float
    reasoning: str
    tokens_used: int
    cost: float
    duration: float
    success: bool
    error: Optional[str] = None

class ImprovedPromptTemplates:
    """Improved prompt templates for rubric evaluation"""
    
    def __init__(self, prompt_type):
        prompts_dir = Path(__file__).parent / 'prompts' / prompt_type
        self.SYSTEM_PROMPT = (prompts_dir / 'system_prompt.txt').read_text(encoding='utf-8')
        self.USER_PROMPT_TEMPLATE = (prompts_dir / 'user_prompt_template.txt').read_text(encoding='utf-8')

    CHUNK_PROMPT_TEMPLATE = """You are evaluating a large document in chunks. This is chunk {chunk_num} of {total_chunks}.

## Previous Context Summary
{context_summary}

## Current Chunk Content
{chunk_content}

## Rubric Criterion
**Title**: {rubric_title}
**Category**: {rubric_category}

Please evaluate this chunk for evidence related to the rubric criterion. Your response should be in JSON format:

```json
{{
  "relevant_evidence": ["Evidence point 1", "Evidence point 2", ...],
  "partial_satisfaction": true/false,
  "confidence_for_chunk": [0.0-1.0],
  "notes": "Any important observations"
}}
```"""

class RubricEvaluator:
    """Enhanced rubric evaluation system"""
    
    def __init__(self, api_key: str = None, base_url: str = None, model: str = "gpt-4o", binary: bool = False, max_concurrent: int = 20):
        """Initialize the evaluator
        
        Args:
            api_key: OpenAI API key
            base_url: API base URL
            model: Model to use
            binary: If True, use binary prompts; if False, use ternary prompts (default: False)
            max_concurrent: Maximum number of concurrent API calls (default: 20)
        """
        if not OPENAI_AVAILABLE:
            raise ImportError("LiteLLM library required")
            
        self.model = model
        self.max_concurrent = max_concurrent
        self.semaphore = None  # Will be initialized when needed in async context
        prompt_type = 'binary' if binary else 'ternary'
        self.prompts = ImprovedPromptTemplates(prompt_type=prompt_type)
        
        # Load .env file if api_key not provided and OPENAI_API_KEY not in environment
        if not api_key and not os.getenv("OPENAI_API_KEY"):
            # Try to find .env file in public_release_experiments directory
            # Script is at: src/evaluate_rubrics/evaluate_rubrics_markitdown_onetask.py
            env_file = Path(__file__).parent.parent.parent / '.env'
            if env_file.exists():
                # logger.info(f"Loading environment variables from: {env_file}")
                with open(env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            os.environ[key.strip()] = value.strip()
        
        # Store API configuration for LiteLLM
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url
        
        # Token limits by model
        self.token_limits = {
            "gpt-5": 200000,
            "litellm_proxy/gemini/gemini-2.5-pro-preview-06-05": 200000,
            "gpt-4o": 128000,
            "gpt-4.1": 128000,
        }
        
        # Pricing per 1M tokens
        self.pricing = {
            "gpt-5": {"input": 1.25, "output": 10.0},
            "litellm_proxy/gemini/gemini-2.5-pro-preview-06-05": {"input": 1.25, "output": 10.0},
            "gpt-4o": {"input": 2.5, "output": 10.0},
            "gpt-4.1": {"input": 2.0, "output": 8.0},
        }
        
        # Cache for processed documents
        self.document_cache = {}
        
    def load_document(self, file_path: Path, use_cache: bool = True) -> str:
        """Load document content (markdown or PDF)
        
        Args:
            file_path: Path to document
            use_cache: Whether to use cached content
            
        Returns:
            Document content as string
        """
        # Check cache
        cache_key = str(file_path)
        if use_cache and cache_key in self.document_cache:
            # logger.info(f"Using cached content for {file_path.name}")
            return self.document_cache[cache_key]
            
        # Try markdown version first
        markdown_path = file_path.with_suffix('.md')
        if markdown_path.exists():
            # logger.info(f"Loading markdown: {markdown_path}")
            content = markdown_path.read_text(encoding='utf-8')
        else:
            # Fallback to PDF text extraction
            # logger.warning(f"Markdown not found, attempting PDF extraction: {file_path}")
            content = self._extract_pdf_text(file_path)
            
        # Cache the content
        if use_cache:
            self.document_cache[cache_key] = content
            
        return content
        
    def _extract_pdf_text(self, pdf_path: Path) -> str:
        """Extract text from PDF using fallback method
        
        Args:
            pdf_path: Path to PDF
            
        Returns:
            Extracted text
        """
        try:
            import PyPDF2
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except ImportError:
            logger.error("PyPDF2 not available for PDF extraction")
            return ""
        except Exception as e:
            logger.error(f"Failed to extract PDF text: {e}")
            return ""
            
    def chunk_document(self, content: str, max_tokens: int = 100000) -> List[str]:
        """Split document into chunks for processing
        
        Args:
            content: Document content
            max_tokens: Maximum tokens per chunk
            
        Returns:
            List of content chunks
        """
        # Rough estimate: 1 token ≈ 4 characters
        max_chars = max_tokens * 4
        
        if len(content) <= max_chars:
            return [content]
            
        # Split by paragraphs first
        paragraphs = content.split('\n\n')
        
        chunks = []
        current_chunk = ""
        
        for para in paragraphs:
            if len(current_chunk) + len(para) < max_chars:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"
                
        if current_chunk:
            chunks.append(current_chunk.strip())
            
        # logger.info(f"Document split into {len(chunks)} chunks")
        return chunks
        
    async def evaluate_rubric(self, rubric: Dict[str, Any], document_content: str, 
                       use_chunking: bool = True) -> EvaluationResult:
        """Evaluate a single rubric against document content
        
        Args:
            rubric: Rubric information
            document_content: Document content
            use_chunking: Whether to use chunking for large documents
            
        Returns:
            EvaluationResult object
        """
        start_time = time.time()
        
        # Use semaphore to limit concurrent API calls
        async with self.semaphore:
            try:
                # Check if chunking is needed
                estimated_tokens = len(document_content) // 4
                context_limit = self.token_limits.get(self.model) - 4096  # Reserve tokens for response
                
                if use_chunking and estimated_tokens > context_limit:
                    result = await self._evaluate_with_chunks(rubric, document_content)
                else:
                    result = await self._evaluate_single(rubric, document_content)
                    
                result.duration = time.time() - start_time
                return result
                
            except Exception as e:
                logger.error(f"Evaluation failed: {e}")
                return EvaluationResult(
                    rubric_title=rubric.get('title', 'Unknown'),
                    pdf_name='',
                    verdict='Error',
                    score=0.0,
                    confidence=0.0,
                    reasoning=f"Evaluation failed: {str(e)}",
                    tokens_used=0,
                    cost=0.0,
                    duration=time.time() - start_time,
                    success=False,
                    error=str(e)
                )
            
    async def _evaluate_single(self, rubric: Dict[str, Any], content: str) -> EvaluationResult:
        """Evaluate rubric on single content (no chunking)
        
        Args:
            rubric: Rubric information
            content: Document content
            
        Returns:
            EvaluationResult
        """
        # Prepare prompt
        user_prompt = self.prompts.USER_PROMPT_TEMPLATE.format(
            document_content=content,
            rubric_title=rubric.get('title', ''),
            rubric_category=rubric.get('category', 'General'),
            rubric_weight=rubric.get('weight', 1.0)
        )
        
        # Make API call with retry logic
        for attempt in range(3):
            try:
                response = await litellm.acompletion(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": self.prompts.SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt}
                    ],
                    # temperature=0.1,  # Low temperature for consistency
                    max_tokens=4096,
                    response_format={"type": "json_object"},  # Ensure JSON response
                    api_key=self.api_key,
                    base_url=self.base_url
                )
                
                # Parse response
                response_text = response.choices[0].message.content
                result_data = json.loads(response_text)
                
                # Calculate cost
                tokens_used = response.usage.total_tokens if response.usage else 0
                cost = self._calculate_cost(response.usage)
                
                return EvaluationResult(
                    rubric_title=rubric.get('title', ''),
                    pdf_name='',
                    verdict=result_data.get('verdict', 'Unknown'),
                    score=float(result_data.get('score', 0.0)),
                    confidence=float(result_data.get('confidence', 0.0)),
                    reasoning=result_data.get('reasoning', ''),
                    tokens_used=tokens_used,
                    cost=cost,
                    duration=0,
                    success=True
                )
                
            except json.JSONDecodeError as e:
                logger.warning(f"JSON decode error on attempt {attempt + 1}: {e}")
                if attempt == 2:
                    raise
            except Exception as e:
                logger.warning(f"API call failed on attempt {attempt + 1}: {e}")
                if attempt == 2:
                    raise
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
                
    async def _evaluate_with_chunks(self, rubric: Dict[str, Any], content: str) -> EvaluationResult:
        """Evaluate rubric using document chunks
        
        Args:
            rubric: Rubric information
            content: Full document content
            
        Returns:
            EvaluationResult
        """
        chunks = self.chunk_document(content)
        # logger.info(f"Evaluating rubric across {len(chunks)} chunks")
        
        # Process chunks and collect evidence
        all_evidence = []
        chunk_results = []
        total_tokens = 0
        total_cost = 0.0
        
        for i, chunk in enumerate(chunks, 1):
            # logger.info(f"Processing chunk {i}/{len(chunks)}")
            
            # Evaluate chunk
            chunk_prompt = self.prompts.CHUNK_PROMPT_TEMPLATE.format(
                chunk_num=i,
                total_chunks=len(chunks),
                context_summary="Previous chunks evaluated" if i > 1 else "First chunk",
                chunk_content=chunk,
                rubric_title=rubric.get('title', ''),
                rubric_category=rubric.get('category', 'General')
            )
            
            response = await litellm.acompletion(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are evaluating document chunks for rubric criteria."},
                    {"role": "user", "content": chunk_prompt}
                ],
                # temperature=0.1,
                max_tokens=4096,
                response_format={"type": "json_object"},
                api_key=self.api_key,
                base_url=self.base_url
            )
            
            chunk_data = json.loads(response.choices[0].message.content)
            chunk_results.append(chunk_data)
            
            if chunk_data.get('relevant_evidence'):
                all_evidence.extend(chunk_data['relevant_evidence'])
                
            total_tokens += response.usage.total_tokens if response.usage else 0
            total_cost += self._calculate_cost(response.usage)
            
        # Synthesize final evaluation
        synthesis_prompt = f"""Based on the following evidence collected from the document:

Evidence points:
{json.dumps(all_evidence, indent=2)}

Evaluate whether the document satisfies the rubric criterion:
**Title**: {rubric.get('title', '')}
**Category**: {rubric.get('category', 'General')}

Provide your final evaluation in JSON format:
{{
  "verdict": "[Not Satisfied/Partially Satisfied/Satisfied]",
  "score": [0.0/0.5/1.0],
  "confidence": [0.0-1.0],
  "reasoning": "Synthesis of evidence"
}}"""

        final_response = await litellm.acompletion(
            model=self.model,
            messages=[
                {"role": "system", "content": self.prompts.SYSTEM_PROMPT},
                {"role": "user", "content": synthesis_prompt}
            ],
            # temperature=0.1,
            max_tokens=4096,
            response_format={"type": "json_object"},
            api_key=self.api_key,
            base_url=self.base_url
        )
        
        final_data = json.loads(final_response.choices[0].message.content)
        total_tokens += final_response.usage.total_tokens if final_response.usage else 0
        total_cost += self._calculate_cost(final_response.usage)
        
        return EvaluationResult(
            rubric_title=rubric.get('title', ''),
            pdf_name='',
            verdict=final_data.get('verdict', 'Unknown'),
            score=float(final_data.get('score', 0.0)),
            confidence=float(final_data.get('confidence', 0.0)),
            reasoning=final_data.get('reasoning', ''),
            tokens_used=total_tokens,
            cost=total_cost,
            duration=0,
            success=True
        )
        
    def _calculate_cost(self, usage: Any) -> float:
        """Calculate API call cost
        
        Args:
            usage: Usage information from API
            
        Returns:
            Cost in USD
        """
        if not usage:
            return 0.0
            
        model_pricing = self.pricing.get(self.model)
        
        input_tokens = getattr(usage, 'prompt_tokens', 0)
        output_tokens = getattr(usage, 'completion_tokens', 0)
        
        input_cost = (input_tokens / 1_000_000) * model_pricing["input"]
        output_cost = (output_tokens / 1_000_000) * model_pricing["output"]
        
        return input_cost + output_cost
        
    async def evaluate_all_rubrics(self, rubrics: List[Dict], pdf_paths: Dict[str, Path],
                            save_results: bool = True) -> pd.DataFrame:
        """Evaluate all rubrics against all PDFs (with parallelization)
        
        Args:
            rubrics: List of rubric dictionaries
            pdf_paths: Dictionary mapping PDF names to paths
            save_results: Whether to save results to file
            
        Returns:
            Results dataframe
        """
        # Initialize semaphore for concurrent request limiting
        self.semaphore = asyncio.Semaphore(self.max_concurrent)
        
        results = []
        
        # Track overall progress
        total_evaluations = len(rubrics) * len(pdf_paths)
        # logger.info(f"Starting evaluation: {len(rubrics)} rubrics × {len(pdf_paths)} PDFs = {total_evaluations} evaluations")
        
        for pdf_name, pdf_path in pdf_paths.items():
            # logger.info(f"\nProcessing PDF: {pdf_name}")
            
            # Load document once
            document_content = self.load_document(pdf_path)
            
            if not document_content:
                logger.error(f"Failed to load content for {pdf_name}")
                continue
                
            # logger.info(f"Document loaded: {len(document_content)} characters")
            
            # Evaluate all rubrics in parallel for this PDF
            pbar = tqdm(total=len(rubrics), desc=f"Evaluating {pdf_name}")
            
            # Create tasks for parallel evaluation
            async def evaluate_and_update(rubric):
                result = await self.evaluate_rubric(rubric, document_content)
                result.pdf_name = pdf_name
                pbar.update(1)
                pbar.set_postfix({'verdict': result.verdict, 'score': result.score})
                return result
            
            # Run all rubric evaluations in parallel
            evaluation_results = await asyncio.gather(*[evaluate_and_update(rubric) for rubric in rubrics])
            pbar.close()
            
            # Add all results
            for result in evaluation_results:
                results.append({
                    'pdf': pdf_name,
                    'rubric_title': result.rubric_title,
                    'verdict': result.verdict,
                    'score': result.score,
                    'confidence': result.confidence,
                    'reasoning': result.reasoning[:500],  # Truncate for dataframe
                    'tokens_used': result.tokens_used,
                    'cost': result.cost,
                    'duration': result.duration,
                    'success': result.success,
                    'error': result.error
                })
                
        # Create dataframe
        results_df = pd.DataFrame(results)
        
        # Save results
        if save_results:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = Path(f"evaluation_results_{timestamp}.csv")
            results_df.to_csv(results_file, index=False)
            logger.info(f"\nResults saved to: {results_file}")
            
        return results_df

async def evaluate_task_rubrics(task_name: str = None, save_results: bool = False, task_row: pd.Series = None, compiled_df: pd.DataFrame = None, binary: bool = False) -> pd.DataFrame:
    """Evaluate rubrics for a specific task (async with parallelization)
    
    Args:
        task_name: Name of the task to evaluate (hash string like "683a58c9a7e7fe4e7695846f")
        save_results: Whether to save detailed results to file
        task_row: Optional pandas Series with task data (for efficiency)
        compiled_df: Optional compiled dataset DataFrame (for efficiency)
        binary: If True, use binary prompts; if False, use ternary prompts (default: False)
        
    Returns:
        Results dataframe
        
    Raises:
        FileNotFoundError: If compiled dataset is not found
        ValueError: If task is not found or PDF files are missing
    """
    # Configuration - go up to public_release_experiments directory
    # Script is at: src/evaluate_rubrics/evaluate_rubrics_markitdown_onetask.py
    base_dir = Path(__file__).parent.parent.parent
    
    # Handle different calling patterns for efficiency
    if task_row is not None:
        # Most efficient: task_row already provided
        task_name = task_row['task_name']
        # logger.info(f"Processing task: {task_name} (using provided task_row)")
    elif compiled_df is not None and task_name is not None:
        # Efficient: search in provided DataFrame
        task_rows = compiled_df[compiled_df['task_name'] == task_name]
        if len(task_rows) == 0:
            raise ValueError(f"Task '{task_name}' not found in provided DataFrame")
        task_row = task_rows.iloc[0]
        # logger.info(f"Processing task: {task_name} (using provided compiled_df)")
    elif task_name is not None:
        # Backward compatibility: load CSV file
        compiled_csv = base_dir / 'data' / 'processed_df' / 'compiled_dataset.csv'
        if not compiled_csv.exists():
            raise FileNotFoundError(f"Compiled dataset not found: {compiled_csv}. Run extract_rubrics_dataset.py first to generate compiled_dataset.csv")
        
        # Read the CSV and find the specific task
        df = pd.read_csv(compiled_csv)
        # logger.info(f"Loaded compiled dataset with {len(df)} tasks")
        
        if len(df) == 0:
            raise ValueError("No tasks found in compiled dataset")
        
        # Find the specific task
        task_rows = df[df['task_name'] == task_name]
        if len(task_rows) != 1:
            raise ValueError(f"Task '{task_name}' not found in compiled dataset. Available tasks: {list(df['task_name'].head())}")
        
        task_row = task_rows.iloc[0]
        # logger.info(f"Processing task: {task_name} (loaded from CSV)")
    else:
        raise ValueError("Must provide either task_name, or task_row, or (task_name + compiled_df)")
    
    # Parse rubrics from JSON string
    rubrics = json.loads(task_row['rubrics'])
    # logger.info(f"Loaded {len(rubrics)} rubrics")
    
    # Parse PDF paths from JSON string (not used directly, but kept for reference)
    pdf_paths_data = json.loads(task_row['pdf_paths'])
    
    # Setup PDF paths - PDFs are organized by task_name directory
    pdf_base_dir = base_dir / 'data' / 'PDFs'
    task_pdf_dir = pdf_base_dir / task_name
    
    if not task_pdf_dir.exists():
        raise ValueError(f"PDF directory not found for task {task_name}: {task_pdf_dir}")
    
    pdf_paths = {
        'gemini': task_pdf_dir / 'gemini.pdf',
        'chatgpt': task_pdf_dir / 'chatgpt.pdf',
        'perplexity': task_pdf_dir / 'perplexity.pdf'
    }
    
    # Verify ALL PDF files exist
    missing_pdfs = []
    for model, path in pdf_paths.items():
        if not path.exists():
            missing_pdfs.append(f"{model}: {path}")
        # else:
        #     logger.info(f"Found PDF for {model}: {path}")
    
    if missing_pdfs:
        raise ValueError(f"Missing required PDF files for task {task_name}:\n" + "\n".join(missing_pdfs) + 
                        f"\nAll three PDFs (gemini, chatgpt, perplexity) are required.")
    
    # Initialize evaluator
    # You'll need to set your API key here or in environment variable
    evaluator = RubricEvaluator(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url="https://example.com",
        model="gpt-5",
        binary=binary
    )
    
    # Run evaluation (async)
    results_df = await evaluator.evaluate_all_rubrics(
        rubrics=rubrics,
        pdf_paths=pdf_paths,
        save_results=save_results
    )
    
    # Add task_name to results
    results_df['task_name'] = task_name
    
    return results_df

async def main():
    """Main execution function"""
    
    # Hardcoded task name - change this to evaluate different tasks
    TASK_NAME = "683a58c9a7e7fe4e7695846f"  # First task from compiled dataset
    binary = False  # Set to True for binary prompts, False for ternary prompts
    
    try:
        # Evaluate the specific task
        results_df = await evaluate_task_rubrics(TASK_NAME, save_results=False, binary=binary)
        
        # Display summary
        print("\n" + "="*60)
        print(f"EVALUATION SUMMARY FOR TASK: {TASK_NAME}")
        print("="*60)
        
        # Overall statistics
        total_evaluations = len(results_df)
        successful = results_df['success'].sum()
        total_cost = results_df['cost'].sum()
        total_tokens = results_df['tokens_used'].sum()
        avg_confidence = results_df['confidence'].mean()
        
        print(f"\nTotal Evaluations: {total_evaluations}")
        print(f"Successful: {successful}/{total_evaluations}")
        print(f"Total Cost: ${total_cost:.4f}")
        print(f"Total Tokens: {total_tokens:,}")
        print(f"Average Confidence: {avg_confidence:.2%}")
        
        # Per-PDF summary
        print("\nPer-PDF Results:")
        for pdf_name in results_df['pdf'].unique():
            pdf_data = results_df[results_df['pdf'] == pdf_name]
            avg_score = pdf_data['score'].mean()
            
            verdict_counts = pdf_data['verdict'].value_counts()
            print(f"\n{pdf_name.upper()}:")
            print(f"  Average Score: {avg_score:.3f}")
            print(f"  Verdict Distribution:")
            for verdict, count in verdict_counts.items():
                print(f"    {verdict}: {count}")
                
        # Save detailed report
        # report_file = Path(f"evaluation_report_{TASK_NAME}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
        report_data = {
            'task_name': TASK_NAME,
            'summary': {
                'total_evaluations': total_evaluations,
                'successful': successful,
                'total_cost': total_cost,
                'total_tokens': total_tokens,
                'average_confidence': avg_confidence
            },
            'results': results_df.to_dict(orient='records')
        }
        
        # with open(report_file, 'w') as f:
        #     json.dump(report_data, f, indent=2, default=str)
            
        # logger.info(f"\nDetailed report saved to: {report_file}")
        
    except (FileNotFoundError, ValueError) as e:
        logger.error(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if not OPENAI_AVAILABLE:
        print("LiteLLM library is required. Install with: pip install litellm")
        sys.exit(1)
        
    asyncio.run(main())
