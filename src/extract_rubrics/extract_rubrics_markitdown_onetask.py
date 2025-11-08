#!/usr/bin/env python3
"""
Script to process evaluation CSV files and extract rubrics.
Changes:
- PDF to Markdown conversion using markitdown
- Caching of converted documents - to save redoing
- More detailed logging
"""

import pandas as pd
import os
import requests
import json
import logging
import hashlib
import pdb
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from urllib.parse import urlparse
from dataclasses import dataclass, asdict

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

try:
    from markitdown import MarkItDown
    MARKITDOWN_AVAILABLE = True
except ImportError:
    MARKITDOWN_AVAILABLE = False
    logger.warning("MarkItDown not available. Install with: pip install markitdown")

@dataclass
class RubricItem:
    """Data class for rubric items"""
    title: str
    weight: float
    category: str
    row_index: int
    
@dataclass
class PDFLinks:
    """Data class for PDF links"""
    gemini_pdf: Optional[str]
    chatgpt_pdf: Optional[str]
    perplexity_pdf: Optional[str]
    
@dataclass
class FinalPresence:
    """Data class for final presence"""
    gemini_present: Optional[Dict[str, Any]]
    chatgpt_present: Optional[Dict[str, Any]]
    perplexity_present: Optional[Dict[str, Any]]

class RubricExtractor:
    """Class to handle rubric extraction and PDF processing"""
    
    def __init__(self, base_dir: Optional[str] = None):
        """Initialize the RubricExtractor
        
        Args:
            base_dir: Base directory for operations
        """
        if base_dir is None:
            # Go up 3 levels: extract_rubrics_markitdown.py -> extract_rubrics -> src -> public_release_experiments
            self.base_dir = Path(__file__).parent.parent.parent
        else:
            self.base_dir = Path(base_dir)
            
        self.cache_dir = self.base_dir / 'cache'
        self.data_dir = self.base_dir / 'data'
        self.cache_dir.mkdir(exist_ok=True)
        self.data_dir.mkdir(exist_ok=True)
        
        if MARKITDOWN_AVAILABLE:
            self.md_converter = MarkItDown()
        else:
            self.md_converter = None
            
    def load_dataframe(self, csv_filename: str) -> Dict[str, Any]:
        """Load CSV file as dataframe with error handling
        
        Args:
            csv_filename: Name of the CSV file
            
        Returns:
            Dictionary with 'data' (dataframe) and 'error' keys
        """
        csv_path = self.base_dir / csv_filename
        
        if not csv_path.exists():
            return {'data': None, 'error': f"CSV file not found: {csv_path}"}
            
        try:
            df = pd.read_csv(csv_path)
            logger.info(f"Loaded dataframe with shape: {df.shape}")
            
            if df is None or len(df) == 0:
                return {'data': None, 'error': "Dataframe is empty"}
            
            return {'data': df, 'error': None}
        except Exception as e:
            logger.error(f"Failed to load CSV: {e}")
            return {'data': None, 'error': f"Failed to load CSV: {str(e)}"}
            
    def extract_pdf_links_and_presence(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Extract PDF links and presence from dataframe with validation
        
        Args:
            df: Input dataframe
            
        Returns:
            Dictionary with 'data' (pdf_links and final_presence) and 'error' keys
        """
        errors = []
        
        # Extract PDF URLs from specific rows
        pdf_links = PDFLinks(
            gemini_pdf=self._clean_url(df.iloc[3]['prompt'] if len(df) > 3 else None),
            chatgpt_pdf=self._clean_url(df.iloc[6]['prompt'] if len(df) > 6 else None),
            perplexity_pdf=self._clean_url(df.iloc[9]['prompt'] if len(df) > 9 else None)
        )
        
        # Extract final presence
        final_presence = FinalPresence(
            gemini_present=self._extract_presence(df, 'gemini_present'),
            chatgpt_present=self._extract_presence(df, 'chatgpt_present'),
            perplexity_present=self._extract_presence(df, 'perplexity_present')
        )
        
        # Validate presence data
        final_presence_dict = asdict(final_presence)
        for col_name, col_data in final_presence_dict.items():
            if not col_data:
                errors.append(f"{col_name} column is missing")
            elif col_data['null_count'] > 0:
                errors.append(f"{col_name} column has {col_data['null_count']} empty values")
        
        data = {
            'pdf_links': asdict(pdf_links),
            'final_presence': final_presence_dict
        }
        
        if errors:
            return {'data': data, 'error': "; ".join(errors)}
        
        return {'data': data, 'error': None}
        
    def _clean_url(self, url: Any) -> Optional[str]:
        """Clean and validate URL
        
        Args:
            url: URL to clean
            
        Returns:
            Cleaned URL or None
        """
        if not url or pd.isna(url):
            return None
            
        url = str(url).strip()
        
        if not url.startswith(('http://', 'https://')):
            return None
            
        return url
        
    def _extract_score(self, df: pd.DataFrame, column: str) -> Optional[str]:
        """Extract score containing % symbol
        
        Args:
            df: Dataframe
            column: Column name
            
        Returns:
            Score string or None
        """
        if column not in df.columns:
            return None
            
        mask = df[column].astype(str).str.contains('%', na=False)
        if mask.any():
            return df.loc[mask, column].iloc[0]
            
        return None
        
    def _extract_presence(self, df: pd.DataFrame, column: str) -> Optional[Dict[str, Any]]:
        """Extract presence data from column
        
        Args:
            df: Dataframe
            column: Column name
            
        Returns:
            Dict with values and null_count, or None if column missing
        """
        if column not in df.columns:
            return None
            
        # Get all values (including nulls for counting)
        all_values = df[column]
        non_null_values = all_values.dropna()
        null_count = all_values.isnull().sum()
        
        return {
            'values': [str(val) for val in non_null_values.tolist()] if len(non_null_values) > 0 else [],
            'null_count': int(null_count),
            'total_count': len(all_values)
        }
        
    def _truncate_to_last_valid_row(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Truncate dataframe to last row with valid rubric title
        
        Args:
            df: Original dataframe
            
        Returns:
            Dictionary with 'data' (truncated dataframe) and 'error' keys
        """
        last_valid_row = -1
        
        # Find the latest row with a valid title (rubric)
        if 'title' in df.columns:
            # Find last non-null, non-empty title
            for idx in df.index[::-1]:  # Iterate backwards
                title = df.loc[idx, 'title']
                if pd.notna(title) and str(title).strip() != '':
                    last_valid_row = idx
                    break
        
        if last_valid_row >= 0:
            # Truncate to include rows 0 through last_valid_row
            truncated_df = df.iloc[:last_valid_row + 1].copy()
            logger.info(f"Truncated dataframe from {len(df)} to {len(truncated_df)} rows (last valid rubric title at row {last_valid_row})")
            return {'data': truncated_df, 'error': None}
        else:
            logger.warning("No valid rubric titles found")
            return {'data': None, 'error': "No valid rubric titles found"}
        
    def download_pdf(self, url: str, save_path: Path, convert_to_markdown: bool = True, task_name: Optional[str] = None) -> Dict[str, Any]:
        """Download PDF and optionally convert to markdown
        
        Args:
            url: PDF URL
            save_path: Where to save PDF
            convert_to_markdown: Whether to convert to markdown
            task_name: Task name for fallback to predownloaded PDFs
            
        Returns:
            Dictionary with download results
        """
        result = {
            'url': url,
            'pdf_path': str(save_path),
            'markdown_path': None,
            'success': False,
            'error': None
        }
        
        if not url:
            # Try to copy from predownloaded PDFs
            if task_name:
                predownloaded_dir = self.data_dir / 'predownloaded_pdfs' / task_name
                predownloaded_pdf = predownloaded_dir / save_path.name
                
                if not predownloaded_pdf.exists():
                    result['error'] = f'Empty URL and predownloaded PDF not found: {predownloaded_pdf}'
                    return result
                
                try:
                    # Copy the predownloaded PDF
                    save_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(predownloaded_pdf, save_path)
                    logger.info(f"Copied predownloaded PDF: {predownloaded_pdf} -> {save_path}")
                    result['success'] = True
                except Exception as e:
                    result['error'] = f'Failed to copy predownloaded PDF: {str(e)}'
                    raise Exception(f'Failed to copy predownloaded PDF: {str(e)}')
                    return result
            else:
                result['error'] = 'Empty URL'
                raise Exception('Empty URL')
                return result
        else:
            try:
                # Download PDF
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                response = requests.get(url, headers=headers, timeout=30, allow_redirects=True)
                response.raise_for_status()
                
                if len(response.content) == 0:
                    result['error'] = 'Empty response'
                    return result
                    
                # Save PDF
                save_path.parent.mkdir(parents=True, exist_ok=True)
                save_path.write_bytes(response.content)
                
                logger.info(f"Downloaded PDF: {save_path} ({len(response.content)} bytes)")
                result['success'] = True
                
            except Exception as e:
                result['error'] = str(e)
                logger.error(f"Failed to download {url}: {e}")
                raise Exception(f'Failed to download {url}: {str(e)}')
                return result
        
        # Convert to Markdown if requested (common for both download and copy)
        if convert_to_markdown and self.md_converter:
            markdown_path = save_path.with_suffix('.md')
            try:
                markdown_content = self._convert_pdf_to_markdown(save_path)
                markdown_path.write_text(markdown_content, encoding='utf-8')
                result['markdown_path'] = str(markdown_path)
                logger.info(f"Converted to Markdown: {markdown_path}")
            except Exception as e:
                logger.warning(f"Failed to convert PDF to Markdown: {e}")
        
        return result
        
    def _convert_pdf_to_markdown(self, pdf_path: Path) -> str:
        """Convert PDF to Markdown using markitdown
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Markdown content
        """
        if not self.md_converter:
            raise RuntimeError("MarkItDown not available")
            
        # Check cache first
        cache_key = self._get_file_hash(pdf_path)
        cache_file = self.cache_dir / f"{cache_key}.md"
        
        if cache_file.exists():
            logger.info(f"Using cached markdown: {cache_file}")
            return cache_file.read_text(encoding='utf-8')
            
        # Convert PDF
        result = self.md_converter.convert(str(pdf_path))
        markdown_content = result.text_content
        
        # Cache the result
        cache_file.write_text(markdown_content, encoding='utf-8')
        
        return markdown_content
        
    def _get_file_hash(self, file_path: Path) -> str:
        """Get SHA256 hash of file
        
        Args:
            file_path: Path to file
            
        Returns:
            Hash string
        """
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
        
    def get_all_rubrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Extract all rubrics from dataframe with validation
        
        Args:
            df: Cleaned dataframe
            
        Returns:
            Dictionary with 'data' (list of RubricItem objects) and 'error' keys
        """
        rubrics = []
        errors = []
        
        for index, row in df.iterrows():
            rubric = RubricItem(
                title=row['title'],
                weight=row['weight'],
                category=row.get('category'),
                row_index=index
            )
            
            # Validate weight
            try:
                float(rubric.weight)
            except (ValueError, TypeError):
                errors.append(f"Rubric {index+1} has invalid weight: {rubric.weight}")
            
            # Validate category
            if rubric.category is None or str(rubric.category).strip() == '':
                errors.append(f"Rubric {index+1} has missing category")
            
            rubrics.append(rubric)
        
        if not rubrics:
            return {'data': None, 'error': "No rubrics found"}
        
        if errors:
            return {'data': rubrics, 'error': "; ".join(errors)}
            
        logger.info(f"Extracted {len(rubrics)} rubrics")
        return {'data': rubrics, 'error': None}
        
    def process_task(self, csv_filename: str) -> Dict[str, Any]:
        """Process entire task: load CSV, extract data, download PDFs
        
        Args:
            csv_filename: CSV filename
            
        Returns:
            Dictionary with all results or error
        """
        errors = []
        
        # Load dataframe
        df_result = self.load_dataframe(csv_filename)
        if df_result['error']:
            errors.append(df_result['error'])
            return {"error": "; ".join(errors)}  # Fatal error, can't continue
        df = df_result['data']
        
        # Truncate to last valid rubric row
        truncate_result = self._truncate_to_last_valid_row(df)
        if truncate_result['error']:
            errors.append(truncate_result['error'])
            return {"error": "; ".join(errors)}  # Fatal error, can't continue
        df = truncate_result['data']
        
        # Get task name (remove .csv extension first, then take first part before underscore)
        filename_only = Path(csv_filename).stem  # Gets filename without extension
        task_name = filename_only.split('_')[0]
        
        # Extract prompt
        prompt = df.iloc[0, 0] if len(df) > 0 and len(df.columns) > 0 else None
        if not prompt or str(prompt).strip() == '':
            errors.append("Prompt extraction failed")
        
        # Extract data (PDFs and presence)
        extracted_result = self.extract_pdf_links_and_presence(df)
        if extracted_result['error']:
            errors.append(extracted_result['error'])
        extracted_data = extracted_result['data']
        
        # Get rubrics from truncated dataframe
        rubrics_result = self.get_all_rubrics(df)
        if rubrics_result['error']:
            errors.append(rubrics_result['error'])
        rubrics = rubrics_result['data']
        
        # Download PDFs and structure results
        task_data_dir = self.data_dir / 'PDFs' / task_name
        pdf_names = {
            'gemini_pdf': 'gemini.pdf',
            'chatgpt_pdf': 'chatgpt.pdf',
            'perplexity_pdf': 'perplexity.pdf'
        }
        
        pdf_path = {}
        for pdf_key, pdf_filename in pdf_names.items():
            url = extracted_data['pdf_links'].get(pdf_key)
            save_path = task_data_dir / pdf_filename
            
            download_result = self.download_pdf(url, save_path, task_name=task_name)
            pdf_path[pdf_key] = {
                'path': download_result['pdf_path'],
                'error': download_result.get('error')
            }
        
        # Check for PDF download errors
        for pdf_name, pdf_info in pdf_path.items():
            if pdf_info['error'] is not None:
                errors.append(f"{pdf_name}: {pdf_info['error']}")
        
        # Return error if any issues found
        if errors:
            return {"error": "; ".join(errors)}
        
        return {
            'task_name': task_name,
            'dataframe': df,
            'rubrics': rubrics,
            'prompt': prompt,
            'pdf_links': extracted_data['pdf_links'],
            'final_presence': extracted_data['final_presence'],
            'pdf_path': pdf_path
        }

def main():
    """Main function"""
    csv_filename = "data/raw_csvs/Fixed_Extracts_2025-10-30T01-29-46-357Z/683a58c9a7e7fe4e7695846f_683a58c9a7e7fe4e7695846f_fixed_A-G_row7.csv"
    
    extractor = RubricExtractor()
    
    try:
        results = extractor.process_task(csv_filename)
        
        # Check if there was an error
        if 'error' in results:
            return results
        
        # Add debugging breakpoint
        pdb.set_trace()
        
        return {
            'prompt': results['prompt'],
            'rubrics': results['rubrics'], 
            'pdf_paths': results['pdf_path'],
            'final_presence': results['final_presence']
        }
        
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        raise

if __name__ == "__main__":
    main()
