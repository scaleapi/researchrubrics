#!/usr/bin/env python3
"""
Script to process all evaluation CSV files and compile them into a dataset.
Iterates through data/raw_csvs directory and extracts rubrics, prompts, PDFs, and presence data.
"""

import pandas as pd
import logging
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import asdict
import json
from tqdm import tqdm

from extract_rubrics_markitdown_onetask import RubricExtractor

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatasetCompiler:
    """Class to compile multiple CSV extractions into a dataset"""
    
    def __init__(self, base_dir: str = None):
        """Initialize the DatasetCompiler
        
        Args:
            base_dir: Base directory for operations (should be public_release_experiments)
        """
        if base_dir is None:
            # Go up 3 levels: extract_rubrics_dataset.py -> extract_rubrics -> src -> public_release_experiments
            self.base_dir = Path(__file__).parent.parent.parent
        else:
            self.base_dir = Path(base_dir)
            
        self.extractor = RubricExtractor(base_dir=str(self.base_dir))
        self.raw_csvs_dir = self.base_dir / 'data' / 'raw_csvs'
        # self.output_dir = self.base_dir / 'data' / 'compiled'
        # self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def find_all_csvs(self) -> List[Path]:
        """Find all CSV files in the raw_csvs directory
        
        Returns:
            List of paths to CSV files
        """
        if not self.raw_csvs_dir.exists():
            logger.error(f"Raw CSVs directory not found: {self.raw_csvs_dir}")
            return []
            
        csv_files = list(self.raw_csvs_dir.rglob('*.csv'))
        logger.info(f"Found {len(csv_files)} CSV files")
        return csv_files
        
    def process_single_csv(self, csv_path: Path) -> Dict[str, Any]:
        """Process a single CSV file and return structured data
        
        Args:
            csv_path: Path to CSV file
            
        Returns:
            Dictionary with processed data or error information
        """
        # Get relative path from base_dir for processing
        try:
            relative_path = csv_path.relative_to(self.base_dir)
        except ValueError:
            # If csv_path is not relative to base_dir, use absolute path
            relative_path = csv_path
            
        result = {
            'csv_file': str(relative_path),
            'csv_filename': csv_path.name,
            'success': False,
            'error': None,
            'task_name': None,
            'prompt': None,
            'rubrics': None,
            'rubrics_count': 0,
            'pdf_paths': None,
            'final_presence': None,
        }
        
        try:
            logger.info(f"Processing: {csv_path.name}")
            
            # Process the task
            task_result = self.extractor.process_task(str(relative_path))
            
            # Check if there was an error in processing
            if 'error' in task_result:
                result['error'] = task_result['error']
                result['success'] = False
                return result
            
            # Extract and structure the data
            result['task_name'] = task_result['task_name']
            result['prompt'] = task_result['prompt']
            result['rubrics'] = [asdict(r) for r in task_result['rubrics']]  # Convert to dict for serialization
            result['rubrics_count'] = len(task_result['rubrics'])
            result['pdf_paths'] = task_result['pdf_path']  # Includes path and error (error=None means success)
            result['final_presence'] = task_result['final_presence']
            result['success'] = True
            
            logger.info(f"✓ Successfully processed {csv_path.name} ({result['rubrics_count']} rubrics)")
            
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"✗ Failed to process {csv_path.name}: {e}")
            
        return result
        
    def compile_dataset(self) -> pd.DataFrame:
        """Compile all CSVs into a single dataset
        
        Returns:
            DataFrame with compiled data (only successful tasks)
        """
        csv_files = self.find_all_csvs()
        
        if not csv_files:
            logger.warning("No CSV files found to process")
            return pd.DataFrame()
            
        logger.info(f"Starting to process {len(csv_files)} CSV files...")
        
        successful_results = []
        failed_results = []
        
        for csv_path in tqdm(csv_files, desc="Processing CSVs"):
            result = self.process_single_csv(csv_path)
            
            if result['success']:
                # Only keep the columns we want for successful tasks
                successful_results.append({
                    'csv_filename': result['csv_filename'],
                    'task_name': result['task_name'],
                    'prompt': result['prompt'],
                    'rubrics': result['rubrics'],
                    'rubrics_count': result['rubrics_count'],
                    'pdf_paths': result['pdf_paths'],
                    'final_presence': result['final_presence']
                })
            else:
                # Track failed tasks separately
                failed_results.append({
                    'csv_filename': result['csv_filename'],
                    'error': result['error']
                })
            
        # Create DataFrame with only successful results
        df = pd.DataFrame(successful_results)
        
        # Log summary statistics
        success_count = len(successful_results)
        error_count = len(failed_results)
        
        logger.info("\n" + "="*60)
        logger.info("COMPILATION COMPLETE")
        logger.info("="*60)
        logger.info(f"Total files: {len(csv_files)}")
        logger.info(f"Successful: {success_count}")
        logger.info(f"Failed: {error_count}")
        
        # Print errors separately if any
        if error_count > 0:
            print("\n" + "="*60)
            print("TASKS WITH ERRORS")
            print("="*60)
            for failed in failed_results:
                print(f"\n{failed['csv_filename']}:")
                print(f"  Error: {failed['error']}")
            print("\n" + "="*60)
        
        # Save the compiled dataframe
        processed_dir = self.base_dir / 'data' / 'processed_df'
        processed_dir.mkdir(parents=True, exist_ok=True)
        
        # Save as both CSV and parquet
        csv_path = processed_dir / 'compiled_dataset.csv'
        parquet_path = processed_dir / 'compiled_dataset.parquet'
        
        # For CSV, serialize complex columns
        df_for_csv = df.copy()
        for col in ['rubrics', 'pdf_paths', 'final_presence']:
            if col in df_for_csv.columns:
                df_for_csv[col] = df_for_csv[col].apply(lambda x: json.dumps(x) if x is not None else None)
        df_for_csv.to_csv(csv_path, index=False)
        logger.info(f"\nSaved CSV to: {csv_path}")
        
        # For Parquet, serialize complex columns
        df_for_parquet = df.copy()
        for col in ['rubrics', 'pdf_paths', 'final_presence']:
            if col in df_for_parquet.columns:
                df_for_parquet[col] = df_for_parquet[col].apply(lambda x: json.dumps(x) if x is not None else None)
        df_for_parquet.to_parquet(parquet_path, index=False)
        logger.info(f"Saved Parquet to: {parquet_path}")
            
        return df


def main():
    """Main function"""
    compiler = DatasetCompiler()
    df = compiler.compile_dataset()
    
    # Display summary
    print("\n" + "="*60)
    print("DATASET SUMMARY")
    print("="*60)
    print(f"Total records: {len(df)}")
    
    if len(df) > 0:
        print(f"\nAverage rubrics per task: {df['rubrics_count'].mean():.1f}")
        print(f"Total rubrics extracted: {df['rubrics_count'].sum()}")
        
        # Show a sample
        print("\nSample records:")
        print(df[['csv_filename', 'task_name', 'rubrics_count']].head(10).to_string())
    
    return df


if __name__ == "__main__":
    main()

