#!/usr/bin/env python3
"""Calculate compliance scores from evaluation JSONL results."""

import json
import sys
from pathlib import Path
from collections import defaultdict


def main(results_file=None):
    base_dir = Path(__file__).parent.parent.parent
    
    # Get results file path
    if results_file is None:
        results_dir = base_dir / 'results'
        jsonl_files = sorted(results_dir.glob('*.jsonl'))
        if not jsonl_files:
            sys.exit(f"Error: No JSONL files found in {results_dir}")
        results_path = jsonl_files[-1]
        print(f"Using: {results_path.name}")
    else:
        results_path = Path(results_file) if Path(results_file).is_absolute() else base_dir / results_file
    
    # Load results and group by sample_id
    sample_results = defaultdict(list)
    with open(results_path, 'r') as f:
        for line in f:
            result = json.loads(line)
            sample_results[result['sample_id']].append(result)
    
    # Calculate compliance scores per sample
    compliance_scores = {}
    for sample_id, results in sample_results.items():
        scores = [r['score'] for r in results]
        weights = [r['weight'] for r in results]
        numerator = sum(score * weight for score, weight in zip(scores, weights))
        denominator = sum(w for w in weights if w > 0)
        compliance_scores[sample_id] = numerator / denominator if denominator > 0 else 0.0
    
    # Print results
    avg_score = sum(compliance_scores.values()) / len(compliance_scores) if compliance_scores else 0.0
    print("\n" + "="*60)
    print("COMPLIANCE SCORE SUMMARY")
    print("="*60)
    print(f"\nTotal Samples: {len(compliance_scores)}")
    print(f"Average Compliance Score: {avg_score:.4f}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else None)

