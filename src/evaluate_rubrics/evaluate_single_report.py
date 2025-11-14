#!/usr/bin/env python3
"""
Rubric evaluation script for markdown documents with binary grading.

Features:
- Evaluates markdown files against rubric criteria
- Binary grading system (Satisfied/Not Satisfied)
- Automatic chunking for large documents
- Structured prompts for consistent evaluation
- Retry logic and error handling
- Token usage tracking and cost calculation
- Comprehensive logging
- Powered by Gemini 2.5 Pro
"""

import os
import sys
import json
import time
import logging
import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import pandas as pd
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
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False
    logger.error("LiteLLM library not available. Install with: pip install litellm")

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
    """Improved prompt templates for rubric evaluation (binary grading only)"""
    
    def __init__(self):
        prompts_dir = Path(__file__).parent.parent / 'prompts'
        self.SYSTEM_PROMPT = (prompts_dir / 'system_prompt.txt').read_text(encoding='utf-8')
        self.USER_PROMPT_TEMPLATE = (prompts_dir / 'user_prompt.txt').read_text(encoding='utf-8')
        self.CHUNK_PROMPT_TEMPLATE = (prompts_dir / 'chunk_prompt_template.txt').read_text(encoding='utf-8')
        self.SYNTHESIS_PROMPT_TEMPLATE = (prompts_dir / 'synthesis_prompt_template.txt').read_text(encoding='utf-8')

class RubricEvaluator:
    """Enhanced rubric evaluation system with binary grading using Gemini 2.5 Pro"""
    
    def __init__(self, api_key: str = None, base_url: str = None, model: str = "litellm_proxy/gemini/gemini-2.5-pro-preview-06-05", max_concurrent: int = 20):
        """Initialize the evaluator
        
        Args:
            api_key: LiteLLM API key (optional, will use LITELLM_API_KEY env var if not provided)
            base_url: API base URL
            model: Model to use (default: "litellm_proxy/gemini/gemini-2.5-pro-preview-06-05")
            max_concurrent: Maximum number of concurrent API calls (default: 20)
        """
        if not LITELLM_AVAILABLE:
            raise ImportError("LiteLLM library required")
            
        self.model = model
        self.max_concurrent = max_concurrent
        self.semaphore = None  # Will be initialized when needed in async context
        self.prompts = ImprovedPromptTemplates()
        
        # Load .env file if api_key not provided and LITELLM_API_KEY not in environment
        if not api_key and not os.getenv("LITELLM_API_KEY"):
            # Try to find .env file in public_release_experiments directory
            # Script is at: src/evaluate_rubrics/evaluate_markdown_with_rubrics.py
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
        self.api_key = api_key or os.getenv("LITELLM_API_KEY")
        self.base_url = base_url
        
        # Token limits for Gemini 2.5 Pro
        self.token_limits = {
            "litellm_proxy/gemini/gemini-2.5-pro-preview-06-05": 200000,
        }
        
        # Pricing per 1M tokens for Gemini 2.5 Pro
        self.pricing = {
            "litellm_proxy/gemini/gemini-2.5-pro-preview-06-05": {"input": 1.25, "output": 10.0},
        }
        
        # Cache for processed documents
        self.document_cache = {}
        
    def load_document(self, file_path: Path, use_cache: bool = True) -> str:
        """Load document content (markdown only)
        
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
            
        # Load markdown file
        markdown_path = file_path.with_suffix('.md')
        if markdown_path.exists():
            # logger.info(f"Loading markdown: {markdown_path}")
            content = markdown_path.read_text(encoding='utf-8')
        else:
            logger.error(f"Markdown file not found: {markdown_path}")
            content = ""
            
        # Cache the content
        if use_cache:
            self.document_cache[cache_key] = content
            
        return content
        
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
                context_limit = self.token_limits.get(self.model) - 50000  # Reserve tokens for response
                
                if use_chunking and estimated_tokens > context_limit:
                    result = await self._evaluate_with_chunks(rubric, document_content)
                else:
                    result = await self._evaluate_single(rubric, document_content)
                    
                result.duration = time.time() - start_time
                return result
                
            except Exception as e:
                logger.error(f"Evaluation failed: {e}")
                return EvaluationResult(
                    rubric_title=rubric.get('criterion'),
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
            rubric_title=rubric.get('criterion'),
            rubric_category=rubric.get('axis'),
            rubric_weight=rubric.get('weight')
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
                    max_tokens=50000,
                    response_format={"type": "json_object"},  # Ensure JSON response
                    api_key=self.api_key,
                    base_url=self.base_url
                )
                
                # Parse response
                response_text = response.choices[0].message.content
                result_data = json.loads(response_text)
                
                # Calculate cost
                tokens_used = response.usage.total_tokens
                cost = self._calculate_cost(response.usage)
                
                return EvaluationResult(
                    rubric_title=rubric.get('criterion'),
                    pdf_name='',
                    verdict=result_data.get('verdict'),
                    score=float(result_data.get('score')),
                    confidence=float(result_data.get('confidence')),
                    reasoning=result_data.get('reasoning'),
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
                rubric_title=rubric.get('criterion'),
                rubric_category=rubric.get('axis')
            )
            
            response = await litellm.acompletion(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are evaluating document chunks for rubric criteria."},
                    {"role": "user", "content": chunk_prompt}
                ],
                max_tokens=50000,
                response_format={"type": "json_object"},
                api_key=self.api_key,
                base_url=self.base_url
            )
            
            chunk_data = json.loads(response.choices[0].message.content)
            
            # if chunk_data.get('relevant_evidence'):
            all_evidence.extend(chunk_data['relevant_evidence'])
                
            total_tokens += response.usage.total_tokens
            total_cost += self._calculate_cost(response.usage)
            
        # Synthesize final evaluation
        synthesis_prompt = self.prompts.SYNTHESIS_PROMPT_TEMPLATE.format(
            all_evidence=json.dumps(all_evidence, indent=2),
            rubric_title=rubric.get('criterion'),
            rubric_category=rubric.get('axis')
        )

        final_response = await litellm.acompletion(
            model=self.model,
            messages=[
                {"role": "system", "content": self.prompts.SYSTEM_PROMPT},
                {"role": "user", "content": synthesis_prompt}
            ],
            max_tokens=50000,
            response_format={"type": "json_object"},
            api_key=self.api_key,
            base_url=self.base_url
        )
        
        final_data = json.loads(final_response.choices[0].message.content)
        total_tokens += final_response.usage.total_tokens
        total_cost += self._calculate_cost(final_response.usage)
        
        return EvaluationResult(
            rubric_title=rubric.get('criterion'),
            pdf_name='',
            verdict=final_data.get('verdict', 'Unknown'),
            score=float(final_data.get('score')),
            confidence=float(final_data.get('confidence')),
            reasoning=final_data.get('reasoning'),
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
        
        input_tokens = getattr(usage, 'prompt_tokens')
        output_tokens = getattr(usage, 'completion_tokens')
        
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
            for i, result in enumerate(evaluation_results):
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
                    'error': result.error,
                    'weight': rubrics[i]['weight']
                })
                
        # Create dataframe
        results_df = pd.DataFrame(results)
        
        # Save results to JSONL
        if save_results:
            # Get sample_id from pdf_name (which is the sample_id in our case)
            sample_id = list(pdf_paths.keys())[0] if pdf_paths else None
            
            if sample_id:
                # Get base directory (3 levels up from this file)
                base_dir = Path(__file__).parent.parent.parent
                results_dir = base_dir / 'results'
                results_dir.mkdir(exist_ok=True)
                output_file = results_dir / f'{sample_id}.jsonl'
                
                with open(output_file, 'w') as f:
                    for result in results:
                        result_entry = {
                            'sample_id': sample_id,
                            'rubric_title': result['rubric_title'],
                            'verdict': result['verdict'],
                            'score': result['score'],
                            'confidence': result['confidence'],
                            'reasoning': result['reasoning'],
                            'tokens_used': result['tokens_used'],
                            'cost': result['cost'],
                            'success': result['success'],
                            'weight': result['weight']
                        }
                        f.write(json.dumps(result_entry) + '\n')
                
                logger.info(f"Results saved to: {output_file}")
            
        return results_df

async def evaluate_task_rubrics(markdown_file_path: str, rubrics_jsonl_path: str = None, save_results: bool = False) -> tuple:
    """Evaluate a single markdown report against rubrics
    
    Uses binary grading (Satisfied/Not Satisfied) with Gemini 2.5 Pro as the judge model.
    
    Args:
        markdown_file_path: Path to markdown file (e.g., "models_responses/683a58c9a7e7fe4e7695848e.md")
        rubrics_jsonl_path: Path to rubrics JSONL file (default: data/researchrubrics/processed_data.jsonl)
        save_results: Whether to save results to JSONL file (default: False)
        
    Returns:
        Tuple of (results_df, compliance_score)
        
    Raises:
        FileNotFoundError: If markdown or rubrics file not found
        ValueError: If sample_id not found in rubrics file
    """
    base_dir = Path(__file__).parent.parent.parent
    
    # Parse markdown file path
    markdown_path = Path(markdown_file_path)
    if not markdown_path.is_absolute():
        markdown_path = base_dir / markdown_path
    
    if not markdown_path.exists():
        raise FileNotFoundError(f"Markdown file not found: {markdown_path}")
    
    # Extract sample_id from filename (e.g., "683a58c9a7e7fe4e7695848e.md" -> "683a58c9a7e7fe4e7695848e")
    sample_id = markdown_path.stem
    
    # Load rubrics from JSONL
    if rubrics_jsonl_path is None:
        rubrics_jsonl_path = base_dir / 'data' / 'researchrubrics' / 'processed_data.jsonl'
    else:
        rubrics_jsonl_path = Path(rubrics_jsonl_path)
        if not rubrics_jsonl_path.is_absolute():
            rubrics_jsonl_path = base_dir / rubrics_jsonl_path
    
    if not rubrics_jsonl_path.exists():
        raise FileNotFoundError(f"Rubrics file not found: {rubrics_jsonl_path}")
    
    # Find rubrics for this sample_id
    rubrics = None
    with open(rubrics_jsonl_path, 'r') as f:
        for line in f:
            data = json.loads(line)
            if data.get('sample_id') == sample_id:
                rubrics = data['rubrics']
                break
    
    if rubrics is None:
        raise ValueError(f"No rubrics found for sample_id: {sample_id}")
    
    # Initialize evaluator
    evaluator = RubricEvaluator(
        api_key=os.getenv("LITELLM_API_KEY"),
        base_url=os.getenv("API_BASE_URL"),
        model="litellm_proxy/gemini/gemini-2.5-pro-preview-06-05"
    )
    
    # Create single-file path dict
    markdown_paths = {sample_id: markdown_path}
    
    # Run evaluation (async) - save_results is handled in evaluate_all_rubrics
    results_df = await evaluator.evaluate_all_rubrics(
        rubrics=rubrics,
        pdf_paths=markdown_paths,
        save_results=save_results
    )
    
    # Add sample_id to results
    results_df['sample_id'] = sample_id
    
    # Calculate compliance score
    numerator = sum(results_df.iloc[i]['score'] * rubrics[i]['weight'] 
                   for i in range(len(results_df)))
    denominator = sum(rubric['weight'] for rubric in rubrics if rubric['weight'] > 0)
    compliance_score = numerator / denominator if denominator > 0 else 0.0
    
    return results_df, compliance_score

async def main():
    """Main execution function"""
    
    # Example markdown file
    MARKDOWN_FILE = "models_responses/683a58c9a7e7fe4e7695846f.md"
    
    try:
        # Evaluate single markdown report
        results_df, compliance_score = await evaluate_task_rubrics(MARKDOWN_FILE, save_results=False)
        
        # Display summary
        sample_id = results_df['sample_id'].iloc[0]
        print("\n" + "="*60)
        print(f"EVALUATION SUMMARY FOR: {sample_id}")
        print("="*60)
        
        # Overall statistics
        total_evaluations = len(results_df)
        successful = results_df['success'].sum()
        total_cost = results_df['cost'].sum()
        total_tokens = results_df['tokens_used'].sum()
        avg_confidence = results_df['confidence'].mean()
        
        print(f"\nTotal Evaluations: {total_evaluations}")
        print(f"Successful: {successful}/{total_evaluations}")
        print(f"Compliance Score: {compliance_score:.3f}")
        print(f"Total Cost: ${total_cost:.4f}")
        print(f"Total Tokens: {total_tokens:,}")
        print(f"Average Confidence: {avg_confidence:.2%}")
        
        # Verdict distribution
        verdict_counts = results_df['verdict'].value_counts()
        print("\nVerdict Distribution:")
        for verdict, count in verdict_counts.items():
            print(f"  {verdict}: {count}")
        
        # Print verdicts as a list
        verdicts_list = results_df['verdict'].tolist()
        print(f"\nVerdicts List: {verdicts_list}")
        
    except (FileNotFoundError, ValueError) as e:
        logger.error(f"Error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if not LITELLM_AVAILABLE:
        print("LiteLLM library is required. Install with: pip install litellm")
        sys.exit(1)
        
    asyncio.run(main())

