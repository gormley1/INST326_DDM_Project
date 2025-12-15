import unittest
from src.ingredient_processor import parse_ingredient_line, normalize_ingredient_name
from src.shopping_list import compile_shopping_list
from src.store_data import load_store_data, calculate_shopping_list_total

class IntegrationTests(unittest.TestCase):
    """Tests for component interactions"""
    
    def test_recipe_to_shopping_list_workflow(self):
        """Test complete flow: parse recipes → compile list"""
        recipes = [
            {'name': 'Pasta', 'ingredients': ['2 cups flour', '3 eggs']},
            {'name': 'Cookies', 'ingredients': ['1 cup flour', '2 eggs']}
        ]
        servings = {'Pasta': 2, 'Cookies': 1}
        
        shopping = compile_shopping_list(recipes, servings)
        
        # Verify ingredients combined correctly
        self.assertIn('flour', shopping)
        self.assertEqual(shopping['flour']['quantity'], 5.0)  # 4 + 1
        
    def test_shopping_list_to_store_pricing(self):
        """Test shopping list → store pricing integration"""
        shopping = {
            'tomato': {'quantity': 6, 'unit': 'count', 'recipes': ['Pasta']},
            'flour': {'quantity': 2, 'unit': 'cups', 'recipes': ['Bread']}
        }
        
        inventory = load_store_data('safeway')
        result = calculate_shopping_list_total(shopping, inventory)
        
        self.assertIsInstance(result['total'], float)
        self.assertGreater(result['total'], 0)
        self.assertIn('itemized', result)
        
    def test_ingredient_parsing_to_normalization(self):
        """Test ingredient parsing → normalization pipeline"""
        raw = "2 cups Fresh Tomatoes, diced"
        parsed = parse_ingredient_line(raw)
        normalized = normalize_ingredient_name(parsed['item'])
        
        self.assertEqual(normalized, 'tomato')
        self.assertEqual(parsed['preparation'], 'diced')
        
    def test_multi_store_comparison_integration(self):
        """Test comparing same list across multiple stores"""
        shopping = {'tomato': {'quantity': 5, 'unit': 'count', 'recipes': ['Salad']}}
        
        safeway = load_store_data('safeway')
        giant = load_store_data('giant')
        
        safeway_total = calculate_shopping_list_total(shopping, safeway)
        giant_total = calculate_shopping_list_total(shopping, giant)
        
        self.assertIsNotNone(safeway_total['total'])
        self.assertIsNotNone(giant_total['total'])
        
    def test_save_load_shopping_list_integration(self):
        """Test saving and loading maintains data integrity"""
        from src.persistence import GrocerySystemState
        
        original = {
            'flour': {'quantity': 3.5, 'unit': 'cups', 'recipes': ['Bread', 'Cookies']}
        }
        
        state = GrocerySystemState()
        state.save_shopping_list(original, 'test_list')
        loaded = state.load_shopping_list('test_list')
        
        self.assertEqual(original, loaded)