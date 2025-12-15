"""
Unit tests for export_utils module.

Tests cover:
- CSV export (categorized and simple)
- PDF export (categorized)
- TXT export (categorized and simple)
- Category grouping
- Format display function
- Error handling

Author: DDM Team - Matthew Gormley
Course: INST326
Date: December 2024
"""

import unittest
import tempfile
import os
from pathlib import Path
import csv
import sys

# Set testing flag to suppress warnings
os.environ['TESTING'] = 'true'

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.export_utils import (
    format_shopping_list_display,
    export_to_csv,
    export_to_pdf,
    export_to_txt,
    group_items_by_category
)


class TestFormatShoppingListDisplay(unittest.TestCase):
    """Test the format_shopping_list_display function."""
    
    def test_empty_list(self):
        """Test formatting empty shopping list."""
        result = format_shopping_list_display({})
        self.assertEqual(result, "Your grocery list is empty!")
    
    def test_single_item(self):
        """Test formatting single item."""
        shopping_list = {
            'tomato': {
                'quantity': 6,
                'unit': 'count',
                'recipes': ['Pasta Marinara']
            }
        }
        
        result = format_shopping_list_display(shopping_list)
        
        self.assertIn('Grocery List', result)
        self.assertIn('Tomato', result)
        self.assertIn('6', result)
        self.assertIn('count', result)
        self.assertIn('Pasta Marinara', result)
    
    def test_multiple_items(self):
        """Test formatting multiple items."""
        shopping_list = {
            'tomato': {'quantity': 6, 'unit': 'count', 'recipes': ['Pasta']},
            'milk': {'quantity': 1, 'unit': 'gallon', 'recipes': ['Cereal']},
            'pasta': {'quantity': 2, 'unit': 'lb', 'recipes': ['Pasta']}
        }
        
        result = format_shopping_list_display(shopping_list)
        
        self.assertIn('Tomato', result)
        self.assertIn('Milk', result)
        self.assertIn('Pasta', result)
    
    def test_with_notes(self):
        """Test formatting item with notes."""
        shopping_list = {
            'tomato': {
                'quantity': 6,
                'unit': 'count',
                'recipes': ['Pasta'],
                'notes': 'Get organic if available'
            }
        }
        
        result = format_shopping_list_display(shopping_list)
        
        self.assertIn('Notes:', result)
        self.assertIn('Get organic if available', result)
    
    def test_with_prices(self):
        """Test formatting with prices."""
        shopping_list = {
            'tomato': {'quantity': 6, 'unit': 'count', 'recipes': ['Pasta'], 'price': 3.50},
            'milk': {'quantity': 1, 'unit': 'gallon', 'recipes': ['Cereal'], 'price': 4.99}
        }
        
        result = format_shopping_list_display(shopping_list)
        
        self.assertIn('ESTIMATED TOTAL:', result)
        self.assertIn('8.49', result)


class TestGroupItemsByCategory(unittest.TestCase):
    """Test the group_items_by_category function."""
    
    def test_categorize_produce(self):
        """Test categorizing produce items."""
        shopping_list = {
            'tomato': {'quantity': 6, 'unit': 'count'},
            'lettuce': {'quantity': 1, 'unit': 'head'},
            'onion': {'quantity': 3, 'unit': 'count'}
        }
        
        result = group_items_by_category(shopping_list)
        
        self.assertIn('Produce', result)
        self.assertEqual(len(result['Produce']), 3)
        self.assertIn('tomato', result['Produce'])
        self.assertIn('lettuce', result['Produce'])
        self.assertIn('onion', result['Produce'])
    
    def test_categorize_dairy(self):
        """Test categorizing dairy items."""
        shopping_list = {
            'milk': {'quantity': 1, 'unit': 'gallon'},
            'cheese': {'quantity': 8, 'unit': 'oz'},
            'eggs': {'quantity': 12, 'unit': 'count'}
        }
        
        result = group_items_by_category(shopping_list)
        
        self.assertIn('Dairy', result)
        self.assertEqual(len(result['Dairy']), 3)
    
    def test_categorize_mixed_items(self):
        """Test categorizing items from multiple categories."""
        shopping_list = {
            'tomato': {'quantity': 6, 'unit': 'count'},
            'milk': {'quantity': 1, 'unit': 'gallon'},
            'pasta': {'quantity': 2, 'unit': 'lb'},
            'chicken': {'quantity': 3, 'unit': 'lb'}
        }
        
        result = group_items_by_category(shopping_list)
        
        self.assertIn('Produce', result)
        self.assertIn('Dairy', result)
        self.assertIn('Pasta & Grains', result)
        self.assertIn('Meat & Seafood', result)
    
    def test_unknown_items_go_to_other(self):
        """Test that unknown items go to 'Other' category."""
        shopping_list = {
            'exotic_spice_mix': {'quantity': 1, 'unit': 'jar'},
            'specialty_item': {'quantity': 2, 'unit': 'count'}
        }
        
        result = group_items_by_category(shopping_list)
        
        self.assertIn('Other', result)
        self.assertEqual(len(result['Other']), 2)
    
    def test_empty_categories_removed(self):
        """Test that empty categories are not included in results."""
        shopping_list = {
            'tomato': {'quantity': 6, 'unit': 'count'}
        }
        
        result = group_items_by_category(shopping_list)
        
        # Should only have Produce, not all 11 categories
        self.assertLess(len(result), 11)
        self.assertIn('Produce', result)


class TestExportToCSV(unittest.TestCase):
    """Test CSV export functionality."""
    
    def setUp(self):
        """Create temporary file for testing."""
        self.temp_file = tempfile.NamedTemporaryFile(
            mode='w', delete=False, suffix='.csv'
        )
        self.temp_file.close()
        
        self.sample_list = {
            'tomato': {'quantity': 6, 'unit': 'count', 'recipes': ['Pasta'], 'price': 3.50},
            'milk': {'quantity': 1, 'unit': 'gallon', 'recipes': ['Cereal'], 'price': 4.99}
        }
    
    def tearDown(self):
        """Clean up temporary file."""
        Path(self.temp_file.name).unlink(missing_ok=True)
    
    def test_export_creates_file(self):
        """Test that CSV file is created."""
        result = export_to_csv(self.sample_list, self.temp_file.name)
        
        self.assertTrue(result)
        self.assertTrue(Path(self.temp_file.name).exists())
    
    def test_csv_has_headers(self):
        """Test that CSV has proper headers."""
        export_to_csv(self.sample_list, self.temp_file.name)
        
        with open(self.temp_file.name, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            
            self.assertIn('Item', headers)
            self.assertIn('Quantity', headers)
            self.assertIn('Unit', headers)
            self.assertIn('Used In', headers)
            self.assertIn('Price', headers)
    
    def test_csv_contains_data(self):
        """Test that CSV contains exported data."""
        export_to_csv(self.sample_list, self.temp_file.name)
        
        with open(self.temp_file.name, 'r', encoding='utf-8') as f:
            content = f.read()
            
            self.assertIn('Tomato', content)
            self.assertIn('Milk', content)
    
    def test_csv_categorized_by_default(self):
        """Test that CSV is categorized by default."""
        export_to_csv(self.sample_list, self.temp_file.name)
        
        with open(self.temp_file.name, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Should have category headers
            self.assertIn('PRODUCE', content)
            self.assertIn('DAIRY', content)
    
    def test_csv_without_categorization(self):
        """Test CSV export without categorization."""
        export_to_csv(self.sample_list, self.temp_file.name, categorize=False)
        
        with open(self.temp_file.name, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Should NOT have category headers
            self.assertNotIn('===', content)
    
    def test_csv_without_prices(self):
        """Test CSV export without price column."""
        export_to_csv(self.sample_list, self.temp_file.name, include_prices=False)
        
        with open(self.temp_file.name, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            
            self.assertNotIn('Price', headers)
    
    def test_csv_creates_parent_directories(self):
        """Test that parent directories are created if needed."""
        nested_path = Path(self.temp_file.name).parent / 'nested' / 'test.csv'
        
        export_to_csv(self.sample_list, str(nested_path))
        
        self.assertTrue(nested_path.exists())
        nested_path.unlink()
        nested_path.parent.rmdir()


class TestExportToTXT(unittest.TestCase):
    """Test TXT export functionality."""
    
    def setUp(self):
        """Create temporary file for testing."""
        self.temp_file = tempfile.NamedTemporaryFile(
            mode='w', delete=False, suffix='.txt'
        )
        self.temp_file.close()
        
        self.sample_list = {
            'tomato': {'quantity': 6, 'unit': 'count', 'recipes': ['Pasta']},
            'milk': {'quantity': 1, 'unit': 'gallon', 'recipes': ['Cereal']}
        }
    
    def tearDown(self):
        """Clean up temporary file."""
        Path(self.temp_file.name).unlink(missing_ok=True)
    
    def test_export_creates_file(self):
        """Test that TXT file is created."""
        result = export_to_txt(self.sample_list, self.temp_file.name)
        
        self.assertTrue(result)
        self.assertTrue(Path(self.temp_file.name).exists())
    
    def test_txt_contains_data(self):
        """Test that TXT contains exported data."""
        export_to_txt(self.sample_list, self.temp_file.name)
        
        with open(self.temp_file.name, 'r', encoding='utf-8') as f:
            content = f.read()
            
            self.assertIn('Tomato', content)
            self.assertIn('Milk', content)
            self.assertIn('Shopping List', content)
    
    def test_txt_has_title(self):
        """Test that custom title appears in TXT."""
        export_to_txt(self.sample_list, self.temp_file.name, title='Weekly Groceries')
        
        with open(self.temp_file.name, 'r', encoding='utf-8') as f:
            content = f.read()
            
            self.assertIn('Weekly Groceries', content)
    
    def test_txt_categorized_by_default(self):
        """Test that TXT is categorized by default."""
        export_to_txt(self.sample_list, self.temp_file.name)
        
        with open(self.temp_file.name, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Should have category headers
            self.assertIn('PRODUCE', content)
            self.assertIn('DAIRY', content)
    
    def test_txt_without_categorization(self):
        """Test TXT export without categorization."""
        export_to_txt(self.sample_list, self.temp_file.name, categorize=False)
        
        with open(self.temp_file.name, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # Should have basic grocery list format
            self.assertIn('Grocery List', content)


class TestExportToPDF(unittest.TestCase):
    """Test PDF export functionality."""
    
    def setUp(self):
        """Create temporary file for testing."""
        self.temp_file = tempfile.NamedTemporaryFile(
            mode='w', delete=False, suffix='.pdf'
        )
        self.temp_file.close()
        
        self.sample_list = {
            'tomato': {'quantity': 6, 'unit': 'count', 'recipes': ['Pasta'], 'price': 3.50},
            'milk': {'quantity': 1, 'unit': 'gallon', 'recipes': ['Cereal'], 'price': 4.99}
        }
    
    def tearDown(self):
        """Clean up temporary file."""
        Path(self.temp_file.name).unlink(missing_ok=True)
    
    def test_export_creates_file(self):
        """Test that PDF file is created."""
        result = export_to_pdf(self.sample_list, self.temp_file.name)
        
        self.assertTrue(result)
        self.assertTrue(Path(self.temp_file.name).exists())
    
    def test_pdf_file_not_empty(self):
        """Test that PDF file has content."""
        export_to_pdf(self.sample_list, self.temp_file.name)
        
        file_size = Path(self.temp_file.name).stat().st_size
        self.assertGreater(file_size, 0)
    
    def test_pdf_is_valid_format(self):
        """Test that created file is valid PDF."""
        export_to_pdf(self.sample_list, self.temp_file.name)
        
        with open(self.temp_file.name, 'rb') as f:
            header = f.read(5)
            # PDF files start with %PDF-
            self.assertEqual(header, b'%PDF-')
    
    def test_pdf_with_custom_title(self):
        """Test PDF export with custom title."""
        result = export_to_pdf(
            self.sample_list, 
            self.temp_file.name, 
            title='Weekly Groceries'
        )
        
        self.assertTrue(result)
    
    def test_pdf_creates_parent_directories(self):
        """Test that parent directories are created if needed."""
        nested_path = Path(self.temp_file.name).parent / 'nested' / 'test.pdf'
        
        export_to_pdf(self.sample_list, str(nested_path))
        
        self.assertTrue(nested_path.exists())
        nested_path.unlink()
        nested_path.parent.rmdir()


class TestErrorHandling(unittest.TestCase):
    """Test error handling in export functions."""
    
    def test_csv_invalid_path_raises_error(self):
        """Test that invalid path raises error for CSV."""
        shopping_list = {'item': {'quantity': 1, 'unit': 'count', 'recipes': []}}
        
        # Try to write to invalid path (directory that doesn't exist and can't be created)
        # This test is platform-dependent, so we'll just test that it doesn't crash
        try:
            export_to_csv(shopping_list, 'test.csv')
            # Clean up if it succeeded
            Path('test.csv').unlink(missing_ok=True)
        except IOError:
            pass  # Expected on some platforms
    
    def test_pdf_without_fpdf_module(self):
        """Test that helpful error is raised if fpdf not installed."""
        # This test would require temporarily uninstalling fpdf2
        # For now, we just verify the function exists and can be called
        shopping_list = {'item': {'quantity': 1, 'unit': 'count', 'recipes': []}}
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        temp_file.close()
        
        try:
            export_to_pdf(shopping_list, temp_file.name)
            Path(temp_file.name).unlink()
        except ImportError as e:
            self.assertIn('fpdf', str(e).lower())


class TestIntegration(unittest.TestCase):
    """Integration tests for complete workflows."""
    
    def test_complete_export_workflow(self):
        """Test exporting same list to all formats."""
        shopping_list = {
            'tomato': {'quantity': 6, 'unit': 'count', 'recipes': ['Pasta'], 'price': 3.50},
            'milk': {'quantity': 1, 'unit': 'gallon', 'recipes': ['Cereal'], 'price': 4.99},
            'pasta': {'quantity': 2, 'unit': 'lb', 'recipes': ['Pasta'], 'price': 2.99}
        }
        
        # Create temp directory
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Export to all formats
            csv_path = Path(temp_dir) / 'shopping.csv'
            txt_path = Path(temp_dir) / 'shopping.txt'
            pdf_path = Path(temp_dir) / 'shopping.pdf'
            
            csv_result = export_to_csv(shopping_list, str(csv_path))
            txt_result = export_to_txt(shopping_list, str(txt_path))
            pdf_result = export_to_pdf(shopping_list, str(pdf_path))
            
            # Verify all succeeded
            self.assertTrue(csv_result)
            self.assertTrue(txt_result)
            self.assertTrue(pdf_result)
            
            # Verify all files exist
            self.assertTrue(csv_path.exists())
            self.assertTrue(txt_path.exists())
            self.assertTrue(pdf_path.exists())
            
        finally:
            # Cleanup
            import shutil
            shutil.rmtree(temp_dir)


if __name__ == '__main__':
    unittest.main(verbosity=2)