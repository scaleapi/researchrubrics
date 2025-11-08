import pandas as pd
import json
from pathlib import Path
import numpy as np
from collections import defaultdict
from sklearn.metrics import f1_score


def load_data(data_path):
    """Load the processed dataframe from parquet file.
    
    Args:
        data_path: Path to the parquet file
        
    Returns:
        pd.DataFrame: The loaded dataframe
    """
    df = pd.read_parquet(data_path)
    return df


def calculate_macro_f1_per_task(true_labels, pred_labels, binary=False):
    """Calculate macro F1 score for a single task using sklearn.
    
    Args:
        true_labels: List of true labels (ground truth)
        pred_labels: List of predicted labels (model predictions)
        binary: If True, convert "Partially Satisfied" to "Not Satisfied" for binary evaluation
        
    Returns:
        float: Macro F1 score for this task
    """
    # Convert to binary labels if requested
    if binary:
        true_labels = ['Not Satisfied' if label == 'Partially Satisfied' else label 
                       for label in true_labels]
        pred_labels = ['Not Satisfied' if label == 'Partially Satisfied' else label 
                       for label in pred_labels]
        # Define labels for binary case
        labels = ['Satisfied', 'Not Satisfied']
    else:
        # Define the possible labels for ternary case
        labels = ['Satisfied', 'Partially Satisfied', 'Not Satisfied']
    
    # Use sklearn's f1_score with macro averaging
    macro_f1 = f1_score(true_labels, pred_labels, labels=labels, average='macro', zero_division=0)
    return macro_f1


def calculate_model_f1_scores(ground_truth_df, predicted_df, limit_rows=None, binary=False):
    """Calculate macro F1 scores for all models by comparing ground truth vs predicted data.
    
    Args:
        ground_truth_df: DataFrame containing ground truth presence data
        predicted_df: DataFrame containing predicted presence data
        limit_rows: Optional limit on number of rows to process (for debugging)
        binary: If True, convert "Partially Satisfied" to "Not Satisfied" for binary evaluation
        
    Returns:
        dict: Dictionary with lists of F1 scores for each model per task
    """
    # Limit rows if specified (for debugging)
    if limit_rows is not None:
        ground_truth_df = ground_truth_df.head(limit_rows)
        predicted_df = predicted_df.head(limit_rows)
        
    # Initialize lists to store F1 scores for each model per task
    model_f1_scores = {
        'gemini': [],
        'chatgpt': [],
        'perplexity': []
    }
    
    # Ensure both dataframes have the same number of rows
    min_rows = min(len(ground_truth_df), len(predicted_df))
    
    # Iterate through all rows (tasks) in both dataframes
    for idx in range(min_rows):
        gt_row = ground_truth_df.iloc[idx]
        pred_row = predicted_df.iloc[idx]
        
        # Parse presence data from both dataframes
        gt_presence = json.loads(gt_row['final_presence'])
        pred_presence = json.loads(pred_row['final_presence'])
        
        # For each model, compare ground truth vs predicted
        for model in ['gemini', 'chatgpt', 'perplexity']:
            model_key = f'{model}_present'
            
            # Extract ground truth and predicted presence lists for this model
            gt_values = gt_presence[model_key]['values']
            pred_values = pred_presence[model_key]['values']
            
            # Ensure both lists have the same length
            min_length = min(len(gt_values), len(pred_values))
            gt_values = gt_values[:min_length]
            pred_values = pred_values[:min_length]
            
            # Calculate F1 score for this model on this task
            f1 = calculate_macro_f1_per_task(gt_values, pred_values, binary)
            model_f1_scores[model].append(f1)
            
        if limit_rows is not None:
            print(f"Task {idx+1}: Gemini F1={model_f1_scores['gemini'][-1]:.4f}, "
                  f"ChatGPT F1={model_f1_scores['chatgpt'][-1]:.4f}, "
                  f"Perplexity F1={model_f1_scores['perplexity'][-1]:.4f}")
    
    return model_f1_scores


def calculate_average_f1_scores(model_f1_scores):
    """Calculate average F1 scores across all tasks for each model.
    
    Args:
        model_f1_scores: Dictionary with lists of F1 scores for each model
        
    Returns:
        dict: Dictionary with average F1 scores for each model
    """
    avg_f1_scores = {}
    for model, f1_scores in model_f1_scores.items():
        avg_f1_scores[model] = np.mean(f1_scores) if f1_scores else 0.0
    
    return avg_f1_scores




if __name__ == "__main__":
    # Define paths to the two dataframes
    base_path = Path(__file__).parent.parent.parent
    ground_truth_path = base_path / "data" / "processed_df" / "compiled_dataset.parquet"
    predicted_path = base_path / "results" / "11_04" / "20251104_034416" / "processed_df" / "compiled_dataset.parquet"
    
    # Set binary flag - change this to True for binary evaluation (Partially Satisfied -> Not Satisfied)
    binary = True
    
    # For debugging, limit to first 2 entries
    limit_rows = None # 2
    
    print(f"Loading data from:")
    print(f"  Ground Truth: {ground_truth_path}")
    print(f"  Predicted:    {predicted_path}")
    print(f"Limiting to first {limit_rows} rows for debugging")
    print(f"Evaluation mode: {'Binary' if binary else 'Ternary'}")
    if binary:
        print("(Converting 'Partially Satisfied' -> 'Not Satisfied')")
    print()
    
    # Load both dataframes
    ground_truth_df = load_data(ground_truth_path)
    predicted_df = load_data(predicted_path)
    
    print(f"Ground Truth DF loaded: {len(ground_truth_df)} tasks")
    print(f"Predicted DF loaded:    {len(predicted_df)} tasks")
    print()
    
    # Calculate F1 scores by comparing ground truth vs predicted
    print("=== Calculating F1 Scores (Ground Truth vs Predicted) ===")
    f1_scores = calculate_model_f1_scores(ground_truth_df, predicted_df, limit_rows, binary)
    avg_f1_scores = calculate_average_f1_scores(f1_scores)
    
    # Print results
    print("\n" + "="*60)
    print("MACRO F1 SCORE RESULTS")
    print("="*60)
    
    print(f"\nAverage F1 Scores across {min(len(ground_truth_df), len(predicted_df), limit_rows or float('inf'))} tasks:")
    for model in ['gemini', 'chatgpt', 'perplexity']:
        print(f"  {model.capitalize():<12}: {avg_f1_scores[model]:.4f}")
    
    print(f"\nNote: F1 scores calculated by comparing ground truth vs predicted presence lists for each model.")
    if binary:
        print(f"      Each task's macro F1 is calculated across the 2 classes: Satisfied, Not Satisfied")
        print(f"      'Partially Satisfied' labels were converted to 'Not Satisfied' for binary evaluation")
    else:
        print(f"      Each task's macro F1 is calculated across the 3 classes: Satisfied, Partially Satisfied, Not Satisfied")
    print(f"      Ground truth data from: {ground_truth_path.name}")
    print(f"      Predicted data from:    {predicted_path.name}")
