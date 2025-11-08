import pandas as pd
import pdb
from pathlib import Path
import json


def calculate_weighted_score(weights, presence_list, verbose=False, binary=False):
    """Calculate weighted score based on presence values.
    
    Args:
        weights: List of weight values for each rubric
        presence_list: List of presence values (Satisfied/Partially Satisfied/Not Satisfied)
        verbose: Whether to print the score details
        binary: If True, convert "Partially Satisfied" to "Not Satisfied" for binary evaluation
        
    Returns:
        float: The calculated score (numerator/denominator)
    """
    # Convert to binary labels if requested
    if binary:
        presence_list = ['Not Satisfied' if presence == 'Partially Satisfied' else presence 
                        for presence in presence_list]
    
    # Map presence values to scores
    score_map = {
        'Satisfied': 1.0,
        'Partially Satisfied': 0.5,
        'Not Satisfied': 0.0
    }
    
    # Calculate weighted numerator
    numerator = sum(weight * score_map.get(presence, 0) 
                    for weight, presence in zip(weights, presence_list))
    
    # Calculate denominator (sum of positive weights)
    denominator = sum(weight for weight in weights if weight > 0)
    
    # Calculate and return score
    score = numerator / denominator if denominator > 0 else 0
    
    if verbose:
        print(f"Weighted Score: {score:.4f} (numerator: {numerator:.4f}, denominator: {denominator:.4f})")
    
    return score


def load_data(data_path):
    """Load the processed dataframe from parquet file.
    
    Args:
        data_path: Path to the parquet file
        
    Returns:
        pd.DataFrame: The loaded dataframe
    """
    df = pd.read_parquet(data_path)
    return df


def calculate_model_scores(df, binary=False):
    """Calculate weighted scores for all models across all rows in the dataframe.
    
    Args:
        df: DataFrame containing rubrics and presence data
        binary: If True, convert "Partially Satisfied" to "Not Satisfied" for binary evaluation
        
    Returns:
        dict: Dictionary with lists of scores for each model (gemini, chatgpt, perplexity)
    """
    # Initialize lists to store scores for each model
    gemini_scores = []
    chatgpt_scores = []
    perplexity_scores = []
    
    # Iterate through all rows in the dataframe
    for idx, row in df.iterrows():
        # Parse rubrics and presence data
        rubrics = json.loads(row['rubrics'])
        presence = json.loads(row['final_presence'])
        
        # Extract rubric weights
        rubric_weights = [rubric.get('weight') for rubric in rubrics]
        
        # Extract presence lists for each model
        gemini_present = presence['gemini_present']['values']
        chatgpt_present = presence['chatgpt_present']['values']
        perplexity_present = presence['perplexity_present']['values']
        
        # Calculate scores for each model
        gemini_score = calculate_weighted_score(rubric_weights, gemini_present, binary=binary)
        chatgpt_score = calculate_weighted_score(rubric_weights, chatgpt_present, binary=binary)
        perplexity_score = calculate_weighted_score(rubric_weights, perplexity_present, binary=binary)
        
        # Append to lists
        gemini_scores.append(gemini_score)
        chatgpt_scores.append(chatgpt_score)
        perplexity_scores.append(perplexity_score)
    
    return {
        'gemini': gemini_scores,
        'chatgpt': chatgpt_scores,
        'perplexity': perplexity_scores
    }

if __name__ == "__main__":
    data_path = Path(__file__).parent.parent.parent / "results" / "11_04" / "20251104_034416" / "processed_df" / "compiled_dataset.parquet"
    
    # Set binary flag - change this to True for binary evaluation (Partially Satisfied -> Not Satisfied)
    binary = False
    
    print(f"Loading data from: {data_path}")
    df = load_data(data_path)
    print(f"Loaded {len(df)} tasks")
    print(f"Evaluation mode: {'Binary' if binary else 'Ternary'}")
    if binary:
        print("(Converting 'Partially Satisfied' -> 'Not Satisfied')")
    
    # Calculate scores for all models
    scores = calculate_model_scores(df, binary)
    
    # Calculate and print averages
    print(f"\nAverage Scores across {len(df)} rows:")
    print(f"Gemini:     {sum(scores['gemini']) / len(scores['gemini']):.4f}")
    print(f"ChatGPT:    {sum(scores['chatgpt']) / len(scores['chatgpt']):.4f}")
    print(f"Perplexity: {sum(scores['perplexity']) / len(scores['perplexity']):.4f}")
    
    # pdb.set_trace()

