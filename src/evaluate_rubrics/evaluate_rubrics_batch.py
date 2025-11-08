#!/usr/bin/env python3
"""
Simple batch evaluation script for processing all tasks in compiled_dataset.csv

This script:
1. Loads all tasks from compiled_dataset.csv
2. Calls evaluate_task_rubrics() for each task  
3. Updates final_presence values with new evaluation results
4. Saves output to results/<mm_dd>/{timestamp}/processed_df/ in CSV and Parquet formats

Usage:
    python evaluate_rubrics_batch.py
"""

import os
import sys
import json
import logging
import time
import asyncio
from pathlib import Path
import pandas as pd
from datetime import datetime
from tqdm import tqdm

# Import the single-task evaluator
try:
    from evaluate_rubrics_markitdown_onetask import evaluate_task_rubrics
except ImportError:
    # Try adding the current directory to path
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    from evaluate_rubrics_markitdown_onetask import evaluate_task_rubrics

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def generate_final_presence_format(results_df: pd.DataFrame) -> dict:
    """Convert evaluation results to final_presence format
    
    Args:
        results_df: Results DataFrame from evaluate_task_rubrics
        
    Returns:
        Dictionary in final_presence format
    """
    final_presence = {}
    
    # Get task name for error reporting
    task_name = results_df['task_name'].iloc[0] if not results_df.empty else "Unknown"
    
    # Get unique models/PDFs
    models = sorted(results_df['pdf'].unique()) if not results_df.empty else []
    
    for model in models:
        model_results = results_df[results_df['pdf'] == model]
        
        # Extract verdict values (should be in order of rubrics)
        verdict_values = model_results['verdict'].tolist()
        
        # Count null/error values
        null_count = len([v for v in verdict_values if v in ['Error', 'Unknown', None]])
        total_count = len(verdict_values)
        
        # Check that null_count must be 0
        if null_count > 0:
            raise ValueError(f"Task '{task_name}' has {null_count} null/error evaluations for {model}. All evaluations must be successful.")
        
        # Store in the format expected
        final_presence[f'{model}_present'] = {
            'values': verdict_values,
            'null_count': null_count,
            'total_count': total_count
        }
    
    return final_presence

async def evaluate_all_tasks(binary=False):
    """Evaluate all tasks in compiled_dataset.csv and update final_presence values (async with parallelization)
    
    Args:
        binary: If True, use binary prompts; if False, use ternary prompts (default: False)
    
    Results are automatically saved to results/<mm_dd>/{timestamp}/processed_df/
        
    Returns:
        DataFrame in same format as compiled_dataset.csv but with updated final_presence values
    """
    
    # Get base directory
    base_dir = Path(__file__).parent.parent.parent
    compiled_csv = base_dir / 'data' / 'processed_df' / 'compiled_dataset.csv'
    
    if not compiled_csv.exists():
        raise FileNotFoundError(f"Compiled dataset not found: {compiled_csv}")
    
    # Load all tasks once
    df = pd.read_csv(compiled_csv)
    logger.info(f"Found {len(df)} tasks to evaluate")
    
    # Evaluate each task and collect results
    successful_task_rows = []
    evaluation_details = []
    
    try:
        for idx, task_row in tqdm(df.iterrows(), total=len(df), desc="Evaluating tasks"):
            
            task_name = task_row['task_name']
            logger.info(f"Processing task: {task_name}")
            
            task_start_time = time.time()
            # Evaluate this task (pass task_row for efficiency - no need to reload CSV)
            results_df = await evaluate_task_rubrics(save_results=False, task_row=task_row, binary=binary)
            task_time = time.time() - task_start_time
            
            if results_df.empty:
                logger.error(f"No results for task {task_name}")
                raise ValueError(f"Task {task_name} returned empty results")
                
            # Generate final_presence format and create updated row
            final_presence = generate_final_presence_format(results_df)
            updated_row = task_row.copy()
            updated_row['final_presence'] = json.dumps(final_presence)
            
            successful_task_rows.append(updated_row)
            evaluation_details.append(results_df)
            logger.info(f"Task {task_name} completed: {len(results_df)} evaluations in {task_time:.2f}s")
    finally:
        # Save results if we have any successful tasks
        if successful_task_rows:
            is_partial = len(successful_task_rows) < len(df)
            if is_partial:
                logger.warning(f"Saving partial results for {len(successful_task_rows)}/{len(df)} completed tasks")
            else:
                logger.info(f"Saving results for {len(successful_task_rows)} completed tasks")
            output_df = pd.DataFrame(successful_task_rows)
            
            # Create directory structure: results/<date>/{timestamp}/processed_df/
            now = datetime.now()
            date_dir = now.strftime("%m_%d")
            timestamp = now.strftime("%Y%m%d_%H%M%S")
            
            results_dir = base_dir / 'results' / date_dir / timestamp / 'processed_df'
            results_dir.mkdir(parents=True, exist_ok=True)
            
            # Save both CSV and Parquet versions
            csv_file = results_dir / 'compiled_dataset.csv'
            parquet_file = results_dir / 'compiled_dataset.parquet'
            
            output_df.to_csv(csv_file, index=False)
            
            try:
                output_df.to_parquet(parquet_file, index=False)
            except ImportError:
                logger.warning("Parquet support not available. Install pyarrow: pip install pyarrow")
                parquet_file = None
                    
            # logger.info(f"Results saved to: {results_dir}")
            # logger.info(f"  CSV: {csv_file}")
            # if parquet_file:
            #     logger.info(f"  Parquet: {parquet_file}")
    
    # Create main output dataframe
    output_df = pd.DataFrame(successful_task_rows)
    # logger.info(f"Successfully evaluated {len(output_df)} tasks")
    
    # Print summary (create compiled_results only for statistics)
    print("\n" + "="*60)
    print("BATCH EVALUATION SUMMARY") 
    print("="*60)
    
    print(f"\nSuccessfully Processed: {len(output_df)} tasks")
    
    if evaluation_details:
        # Only create compiled_results when we need detailed statistics
        compiled_results = pd.concat(evaluation_details, ignore_index=True)
        total_evaluations = len(compiled_results)
        total_cost = compiled_results['cost'].sum()
        total_tokens = compiled_results['tokens_used'].sum()
        
        print(f"Total Evaluations: {total_evaluations:,}")
        print(f"Total Cost: ${total_cost:.4f}")
        print(f"Total Tokens: {total_tokens:,}")
        
        # Per-model summary
        print(f"\nPer-Model Results:")
        for model in compiled_results['pdf'].unique():
            model_data = compiled_results[compiled_results['pdf'] == model]
            verdict_counts = model_data['verdict'].value_counts()
            print(f"\n{model.upper()}: {len(model_data):,} evaluations, Avg Score: {model_data['score'].mean():.3f}")
            for verdict, count in verdict_counts.items():
                print(f"  {verdict}: {count}")
    
    return output_df

async def main():
    """Main execution function"""
    
    binary = False  # Set to True for binary prompts, False for ternary prompts
    
    try:
        start_time = time.time()
        output_df = await evaluate_all_tasks(binary=binary)
        total_time = time.time() - start_time
        
        print(f"\nTotal Time: {total_time:.2f}s ({total_time/60:.2f} minutes)")
        # logger.info("Batch evaluation completed successfully!")
    except Exception as e:
        logger.error(f"Batch evaluation failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())