#!/usr/bin/env python3
"""
Batch evaluation script for all markdown reports.
Evaluates all markdown files in agent_responses/ and saves results to JSONL.
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import from single report evaluator
from evaluate_single_report import evaluate_task_rubrics

async def evaluate_all_reports(agent_responses_dir: str = None, output_file: str = None):
    """Evaluate all markdown files and save results
    
    Args:
        agent_responses_dir: Directory containing markdown files (default: agent_responses/)
        output_file: Output JSONL file path (default: results/batch_evaluation_{timestamp}.jsonl)
        
    Returns:
        None (results saved to file)
    """
    base_dir = Path(__file__).parent.parent.parent
    
    # Set default paths
    if agent_responses_dir is None:
        agent_responses_dir = base_dir / 'agent_responses'
    else:
        agent_responses_dir = Path(agent_responses_dir)
        if not agent_responses_dir.is_absolute():
            agent_responses_dir = base_dir / agent_responses_dir
    
    if not agent_responses_dir.exists():
        raise FileNotFoundError(f"Agent responses directory not found: {agent_responses_dir}")
    
    # Find all markdown files
    markdown_files = sorted(agent_responses_dir.glob('*.md'))
    
    if not markdown_files:
        raise ValueError(f"No markdown files found in: {agent_responses_dir}")
    
    logger.info(f"Found {len(markdown_files)} markdown files to evaluate")
    
    # Prepare output directory
    results_dir = base_dir / 'results'
    results_dir.mkdir(exist_ok=True)
    
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = results_dir / f'batch_evaluation_{timestamp}.jsonl'
    else:
        output_file = Path(output_file)
        if not output_file.is_absolute():
            output_file = base_dir / output_file
    
    # Evaluate each markdown file
    all_results = []
    compliance_scores = {}
    total_cost = 0.0
    total_tokens = 0
    
    for i, markdown_file in enumerate(markdown_files, 1):
        sample_id = markdown_file.stem
        logger.info(f"[{i}/{len(markdown_files)}] Evaluating: {sample_id}")
        
        try:
            # Evaluate single report
            results_df, compliance_score = await evaluate_task_rubrics(str(markdown_file))
            
            # Store compliance score
            compliance_scores[sample_id] = compliance_score
            
            # Extract results for this sample
            for _, row in results_df.iterrows():
                result_entry = {
                    'sample_id': sample_id,
                    'rubric_title': row['rubric_title'],
                    'verdict': row['verdict'],
                    'score': row['score'],
                    'confidence': row['confidence'],
                    'reasoning': row['reasoning'],
                    'tokens_used': row['tokens_used'],
                    'cost': row['cost'],
                    'success': row['success'],
                    'weight': row['weight']
                }
                all_results.append(result_entry)
                total_cost += row['cost']
                total_tokens += row['tokens_used']
        
        except Exception as e:
            logger.error(f"Failed to evaluate {sample_id}: {e}")
            continue
    
    # Save all results to JSONL
    with open(output_file, 'w') as f:
        for result in all_results:
            f.write(json.dumps(result) + '\n')
    
    logger.info(f"\nResults saved to: {output_file}")
    
    # Calculate and print final scores
    print("\n" + "="*60)
    print("BATCH EVALUATION SUMMARY")
    print("="*60)
    
    # Calculate average compliance score
    overall_avg_compliance = sum(compliance_scores.values()) / len(compliance_scores) if compliance_scores else 0.0
    
    print(f"\nTotal Samples Evaluated: {len(compliance_scores)}")
    print(f"Total Rubric Evaluations: {len(all_results)}")
    print(f"Average Compliance Score: {overall_avg_compliance:.3f}")
    print(f"Total Cost: ${total_cost:.4f}")
    print(f"Total Tokens: {total_tokens:,}")
    
    # Verdict distribution
    verdict_counts = {}
    for result in all_results:
        verdict = result['verdict']
        verdict_counts[verdict] = verdict_counts.get(verdict, 0) + 1
    
    print(f"\nOverall Verdict Distribution:")
    for verdict, count in sorted(verdict_counts.items()):
        percentage = (count / len(all_results)) * 100
        print(f"  {verdict}: {count} ({percentage:.1f}%)")

async def main():
    """Main execution function
    
    Args:
        directory: Directory containing markdown files (default: agent_responses/)
    """
    directory = None
    try:
        await evaluate_all_reports(agent_responses_dir=directory)
    except Exception as e:
        logger.error(f"Batch evaluation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

