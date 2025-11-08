import pandas as pd
import json
from pathlib import Path
from collections import defaultdict


def load_data(data_path):
    """Load the processed dataframe from parquet file.
    
    Args:
        data_path: Path to the parquet file
        
    Returns:
        pd.DataFrame: The loaded dataframe
    """
    df = pd.read_parquet(data_path)
    return df


def calculate_task_failure_breakdown(rubrics, presence_values, binary=False):
    """Calculate failure breakdown by category for a single task and model.
    
    Args:
        rubrics: List of rubric dictionaries (each with 'category', 'weight', etc.)
        presence_values: List of presence values ('Satisfied', 'Partially Satisfied', 'Not Satisfied')
        binary: If True, convert "Partially Satisfied" to "Not Satisfied" for binary evaluation
        
    Returns:
        dict: Dictionary mapping categories to their failure ratios for this task
              Only includes categories that have at least one failure
              Returns None if there are no failures
    """
    # Convert to binary labels if requested
    if binary:
        presence_values = ['Not Satisfied' if presence == 'Partially Satisfied' else presence 
                          for presence in presence_values]
    
    # Count failures by category
    failures_by_category = defaultdict(int)
    total_failures = 0
    
    # Iterate through each rubric and its presence value
    for rubric, presence_value in zip(rubrics, presence_values):
        if presence_value == 'Not Satisfied':
            category = rubric['category']
            failures_by_category[category] += 1
            total_failures += 1
    
    # If there are no failures, return None
    if total_failures == 0:
        return None
    
    # Calculate ratio for each category that has failures
    # Only include categories with at least one failure
    category_ratios = {}
    for category, count in failures_by_category.items():
        ratio = count / total_failures
        category_ratios[category] = ratio
    
    return category_ratios


def calculate_failure_breakdown_by_category(df, binary=False):
    """Calculate failure rate breakdown by category for each model across all tasks.
    
    For each model and each task, calculates:
    - The ratio of "Not Satisfied" rubrics per category divided by total "Not Satisfied" rubrics
    
    Then averages these ratios across all tasks.
    
    Args:
        df: DataFrame containing rubrics and presence data
        binary: If True, convert "Partially Satisfied" to "Not Satisfied" for binary evaluation
        
    Returns:
        dict: Dictionary with failure breakdown for each model
    """
    models = ['gemini', 'chatgpt', 'perplexity']
    
    # Initialize storage for each model
    model_results = {model: defaultdict(list) for model in models}
    
    # Track total tasks processed for each model (tasks with at least one failure)
    tasks_with_failures = {model: 0 for model in models}
    
    # Iterate through all rows (tasks) in the dataframe
    for idx, row in df.iterrows():
        # Parse rubrics and presence data
        rubrics = json.loads(row['rubrics'])
        presence = json.loads(row['final_presence'])
        
        # Process each model
        for model in models:
            # Get presence values for this model
            presence_key = f'{model}_present'
            presence_values = presence[presence_key]['values']
            
            # Calculate failure breakdown for this task and model
            task_breakdown = calculate_task_failure_breakdown(rubrics, presence_values, binary)
            
            # If there are failures in this task, store the results
            if task_breakdown is not None:
                tasks_with_failures[model] += 1
                
                # Store the ratio for each category
                for category, ratio in task_breakdown.items():
                    model_results[model][category].append(ratio)
    
    # Calculate averages across all tasks
    model_averages = {}
    for model in models:
        model_averages[model] = {}
        for category, ratios in model_results[model].items():
            avg_ratio = sum(ratios) / len(ratios) if ratios else 0.0
            model_averages[model][category] = {
                'average_ratio': avg_ratio,
                'num_tasks': len(ratios)
            }
        model_averages[model]['_metadata'] = {
            'tasks_with_failures': tasks_with_failures[model],
            'total_tasks': len(df)
        }
    
    return model_averages


def calculate_aggregate_failure_breakdown(df, binary=False):
    """Calculate aggregate failure breakdown by category for each model across all tasks.
    
    Unlike calculate_failure_breakdown_by_category which averages per-task ratios,
    this function aggregates all failures across all tasks and then calculates ratios.
    
    Args:
        df: DataFrame containing rubrics and presence data
        binary: If True, convert "Partially Satisfied" to "Not Satisfied" for binary evaluation
        
    Returns:
        dict: Dictionary with aggregate failure breakdown for each model
    """
    models = ['gemini', 'chatgpt', 'perplexity']
    
    # Initialize storage for each model
    model_results = {model: defaultdict(int) for model in models}
    total_failures = {model: 0 for model in models}
    
    # Iterate through all rows (tasks) in the dataframe
    for idx, row in df.iterrows():
        # Parse rubrics and presence data
        rubrics = json.loads(row['rubrics'])
        presence = json.loads(row['final_presence'])
        
        # Process each model
        for model in models:
            # Get presence values for this model
            presence_key = f'{model}_present'
            presence_values = presence[presence_key]['values']
            
            # Convert to binary labels if requested
            if binary:
                presence_values = ['Not Satisfied' if presence == 'Partially Satisfied' else presence 
                                  for presence in presence_values]
            
            # Count failures by category
            for rubric, presence_value in zip(rubrics, presence_values):
                if presence_value == 'Not Satisfied':
                    category = rubric['category']
                    model_results[model][category] += 1
                    total_failures[model] += 1
    
    # Calculate ratios
    model_ratios = {}
    for model in models:
        model_ratios[model] = {}
        total = total_failures[model]
        
        if total > 0:
            for category, count in model_results[model].items():
                ratio = count / total
                model_ratios[model][category] = {
                    'count': count,
                    'ratio': ratio
                }
        
        model_ratios[model]['_metadata'] = {
            'total_failures': total,
            'total_tasks': len(df)
        }
    
    return model_ratios


def print_results(model_averages, model_aggregate, binary=False):
    """Print the results in a readable format.
    
    Args:
        model_averages: Dictionary with per-task averaged failure breakdown for each model
        model_aggregate: Dictionary with aggregate failure breakdown for each model
        binary: If True, indicates binary evaluation mode for display purposes
    """
    models = ['gemini', 'chatgpt', 'perplexity']
    
    print("\n" + "="*100)
    print("FAILURE RATE BREAKDOWN BY CATEGORY")
    print("="*100)
    print("\nFor each model and category, this shows:")
    print("  - Avg Ratio: average per-task ratio (# 'Not Satisfied' in category / total 'Not Satisfied' per task)")
    print("  - Agg Ratio: aggregate ratio across all tasks (total 'Not Satisfied' in category / total 'Not Satisfied')")
    print("  - Tasks: number of tasks with at least one failure in that category\n")
    
    for model in models:
        print("\n" + "-"*100)
        print(f"MODEL: {model.upper()}")
        print("-"*100)
        
        metadata_avg = model_averages[model]['_metadata']
        metadata_agg = model_aggregate[model]['_metadata']
        print(f"\nTasks with failures: {metadata_avg['tasks_with_failures']} / {metadata_avg['total_tasks']}")
        print(f"Total failures across all tasks: {metadata_agg['total_failures']}")
        print(f"\nFailure breakdown by category:\n")
        
        # Get all unique categories from both sources
        all_categories = set()
        for cat in model_averages[model].keys():
            if cat != '_metadata':
                all_categories.add(cat)
        for cat in model_aggregate[model].keys():
            if cat != '_metadata':
                all_categories.add(cat)
        
        # Prepare data for sorting by aggregate ratio
        category_data = []
        for category in all_categories:
            avg_data = model_averages[model].get(category, {'average_ratio': 0.0, 'num_tasks': 0})
            agg_data = model_aggregate[model].get(category, {'ratio': 0.0, 'count': 0})
            category_data.append((category, avg_data, agg_data))
        
        # Sort by aggregate ratio (descending)
        category_data.sort(key=lambda x: x[2]['ratio'], reverse=True)
        
        # Print table header
        print(f"{'Category':<40} {'Avg Ratio':<12} {'Agg Ratio':<12} {'Tasks'}")
        print(f"{'-'*40} {'-'*12} {'-'*12} {'-'*8}")
        
        total_avg_ratio = 0.0
        total_agg_ratio = 0.0
        for category, avg_data, agg_data in category_data:
            avg_ratio = avg_data['average_ratio']
            num_tasks = avg_data['num_tasks']
            agg_ratio = agg_data['ratio']
            total_avg_ratio += avg_ratio
            total_agg_ratio += agg_ratio
            print(f"{category:<40} {avg_ratio:>10.4f}   {agg_ratio:>10.4f}   {num_tasks:>6}")
        
        print(f"{'-'*40} {'-'*12} {'-'*12} {'-'*8}")
        print(f"{'TOTAL':<40} {total_avg_ratio:>10.4f}   {total_agg_ratio:>10.4f}")
        print(f"\nNote: Avg Ratio total may not sum to 1.0 because ratios are averaged across tasks.")
        print(f"      Agg Ratio total should sum to 1.0 (aggregate calculation).")


if __name__ == "__main__":
    # data_path = Path(__file__).parent.parent.parent / "data" / "processed_df" / "compiled_dataset.parquet"
    data_path = Path(__file__).parent.parent.parent / "results" / "11_04" / "20251104_034416" / "processed_df" / "compiled_dataset.parquet"
    
    # Set binary flag - change this to True for binary evaluation (Partially Satisfied -> Not Satisfied)
    binary = False
    
    print(f"Loading data from: {data_path}")
    df = load_data(data_path)
    print(f"Loaded {len(df)} tasks")
    print(f"Evaluation mode: {'Binary' if binary else 'Ternary'}")
    if binary:
        print("(Converting 'Partially Satisfied' -> 'Not Satisfied')")
    print()
    
    # Calculate failure breakdown by category (per-task average)
    model_averages = calculate_failure_breakdown_by_category(df, binary)
    
    # Calculate aggregate failure breakdown (across all tasks)
    model_aggregate = calculate_aggregate_failure_breakdown(df, binary)
    
    # Print combined results
    print_results(model_averages, model_aggregate, binary)

