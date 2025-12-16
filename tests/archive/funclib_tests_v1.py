# test_functions.py
"""
Comprehensive test suite for DDM Grocery List Function Library
Run with: python test_functions.py
"""


import os
import sys

# Adds the parent directory (project root) to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# Test results tracking
tests_passed = 0
tests_failed = 0
test_details = []


def test_function(func_name, test_name, test_func):
    """Helper to run a test and track results"""
    global tests_passed, tests_failed, test_details
    
    try:
        test_func()
        tests_passed += 1
        test_details.append(f"✓ {func_name}: {test_name}")
        print(f"✓ {func_name}: {test_name}")
    except AssertionError as e:
        tests_failed += 1
        test_details.append(f"✗ {func_name}: {test_name} - {str(e)}")
        print(f"✗ {func_name}: {test_name} - {str(e)}")
    except Exception as e:
        tests_failed += 1
        test_details.append(f"✗ {func_name}: {test_name} - ERROR: {str(e)}")
        print(f"✗ {func_name}: {test_name} - ERROR: {str(e)}")


print("=" * 60)
print("DDM GROCERY LIST FUNCTION LIBRARY - TEST SUITE")
print("=" * 60)
print()

# ====================
# RECIPE PARSER TESTS
# ====================
print("Testing recipe_parser.py...")
print("-" * 60)

from src.recipe_parser import (
    validate_file_format,
    extract_ingredients_from_text,
    parse_txt_recipe
)

def test_validate_format_txt():
    assert validate_file_format("recipe.txt") == True

def test_validate_format_pdf():
    assert validate_file_format("recipe.pdf") == True

def test_validate_format_docx():
    assert validate_file_format("recipe.docx") == True

def test_validate_format_invalid():
    assert validate_file_format("recipe.jpg") == False

def test_validate_format_type_error():
    try:
        validate_file_format(123)
        assert False, "Should raise TypeError"
    except TypeError:
        pass

test_function("validate_file_format", "accepts .txt", test_validate_format_txt)
test_function("validate_file_format", "accepts .pdf", test_validate_format_pdf)
test_function("validate_file_format", "accepts .docx", test_validate_format_docx)
test_function("validate_file_format", "rejects .jpg", test_validate_format_invalid)
test_function("validate_file_format", "raises TypeError for non-string", test_validate_format_type_error)


def test_extract_ingredients_basic():
    text = """Ingredients:
- 2 cups flour
- 1 tsp salt
- 3 eggs"""
    result = extract_ingredients_from_text(text)
    assert len(result) >= 2, f"Expected at least 2 ingredients, got {len(result)}"

def test_extract_ingredients_empty():
    result = extract_ingredients_from_text("")
    assert result == []

def test_extract_ingredients_no_section():
    text = "Just some random text"
    result = extract_ingredients_from_text(text)
    assert isinstance(result, list)

test_function("extract_ingredients_from_text", "extracts basic list", test_extract_ingredients_basic)
test_function("extract_ingredients_from_text", "handles empty input", test_extract_ingredients_empty)
test_function("extract_ingredients_from_text", "handles text without ingredients", test_extract_ingredients_no_section)

print()


# ==========================
# INGREDIENT PROCESSOR TESTS
# ==========================
print("Testing ingredient_processor.py...")
print("-" * 60)

from src.ingredient_processor import (
    parse_ingredient_line,
    normalize_ingredient_name,
    clean_ingredient_text,
    convert_units
)

def test_parse_basic():
    result = parse_ingredient_line("2 cups flour")
    assert result['quantity'] == 2.0
    assert result['unit'] == 'cups'
    assert 'flour' in result['item']

def test_parse_fraction():
    result = parse_ingredient_line("1 1/2 tsp vanilla")
    assert result['quantity'] == 1.5

def test_parse_simple_fraction():
    result = parse_ingredient_line("1/2 cup sugar")
    assert result['quantity'] == 0.5

def test_parse_no_unit():
    result = parse_ingredient_line("3 eggs")
    assert result['quantity'] == 3.0
    assert 'egg' in result['item']

def test_parse_with_prep():
    result = parse_ingredient_line("2 cups diced tomatoes")
    assert result['preparation'] == 'diced'
    assert 'tomato' in result['item']

test_function("parse_ingredient_line", "parses basic ingredient", test_parse_basic)
test_function("parse_ingredient_line", "handles mixed fractions", test_parse_fraction)
test_function("parse_ingredient_line", "handles simple fractions", test_parse_simple_fraction)
test_function("parse_ingredient_line", "handles no unit", test_parse_no_unit)
test_function("parse_ingredient_line", "extracts preparation", test_parse_with_prep)


def test_normalize_basic():
    result = normalize_ingredient_name("Fresh Tomatoes")
    assert result == "tomato"

def test_normalize_synonym():
    result = normalize_ingredient_name("Green onion")
    assert result == "scallion"

def test_normalize_empty():
    result = normalize_ingredient_name("")
    assert result == ""

def test_normalize_removes_descriptors():
    result = normalize_ingredient_name("organic whole milk")
    assert "organic" not in result
    assert "whole" not in result

test_function("normalize_ingredient_name", "normalizes and removes plural", test_normalize_basic)
test_function("normalize_ingredient_name", "handles synonyms", test_normalize_synonym)
test_function("normalize_ingredient_name", "handles empty string", test_normalize_empty)
test_function("normalize_ingredient_name", "removes descriptors", test_normalize_removes_descriptors)


def test_clean_bullets():
    result = clean_ingredient_text("- 2 cups flour")
    assert result == "2 cups flour"

def test_clean_spaces():
    result = clean_ingredient_text("  2   cups  flour  ")
    assert result == "2 cups flour"

def test_clean_empty():
    result = clean_ingredient_text("")
    assert result == ""

test_function("clean_ingredient_text", "removes bullets", test_clean_bullets)
test_function("clean_ingredient_text", "removes extra spaces", test_clean_spaces)
test_function("clean_ingredient_text", "handles empty", test_clean_empty)


def test_convert_cups_to_tbsp():
    result = convert_units(2, 'cups', 'tbsp')
    assert result == 32.0

def test_convert_oz_to_lb():
    result = convert_units(16, 'oz', 'lb')
    assert result == 1.0

def test_convert_tbsp_to_tsp():
    result = convert_units(1, 'tbsp', 'tsp')
    assert result == 3.0

def test_convert_same_unit():
    result = convert_units(5, 'cups', 'cups')
    assert result == 5

def test_convert_incompatible():
    result = convert_units(2, 'cups', 'lb')
    assert result == 2  # Should return original

test_function("convert_units", "cups to tablespoons", test_convert_cups_to_tbsp)
test_function("convert_units", "ounces to pounds", test_convert_oz_to_lb)
test_function("convert_units", "tablespoons to teaspoons", test_convert_tbsp_to_tsp)
test_function("convert_units", "same unit", test_convert_same_unit)
test_function("convert_units", "incompatible units", test_convert_incompatible)

print()


# =======================
# SHOPPING LIST TESTS
# =======================
print("Testing shopping_list.py...")
print("-" * 60)

from src.shopping_list import (
    compile_shopping_list,
    calculate_total_quantity,
    group_items_by_category,
    # validate_serving_size
)

def test_compile_basic():
    recipes = [
        {'name': 'Pasta', 'ingredients': ['2 cups tomato', '1 lb pasta']}
    ]
    servings = {'Pasta': 1}
    result = compile_shopping_list(recipes, servings)
    assert 'tomato' in result or 'pasta' in result

def test_compile_multiple_recipes():
    recipes = [
        {'name': 'Pasta', 'ingredients': ['2 cups tomato']},
        {'name': 'Salad', 'ingredients': ['3 each tomato']}
    ]
    servings = {'Pasta': 1, 'Salad': 1}
    result = compile_shopping_list(recipes, servings)
    assert 'tomato' in result
    assert result['tomato']['quantity'] > 2  # Should be combined

def test_compile_scaling():
    recipes = [
        {'name': 'Pasta', 'ingredients': ['2 cups flour']}
    ]
    servings = {'Pasta': 2}
    result = compile_shopping_list(recipes, servings)
    assert 'flour' in result
    assert result['flour']['quantity'] == 4.0

test_function("compile_shopping_list", "basic compilation", test_compile_basic)
test_function("compile_shopping_list", "combines multiple recipes", test_compile_multiple_recipes)
test_function("compile_shopping_list", "scales by servings", test_compile_scaling)


def test_total_quantity_same_unit():
    entries = [
        {'quantity': 2, 'unit': 'cups'},
        {'quantity': 1, 'unit': 'cups'}
    ]
    result = calculate_total_quantity(entries)
    assert result['quantity'] == 3.0

def test_total_quantity_empty():
    result = calculate_total_quantity([])
    assert result['quantity'] == 0

test_function("calculate_total_quantity", "sums same units", test_total_quantity_same_unit)
test_function("calculate_total_quantity", "handles empty list", test_total_quantity_empty)


def test_group_by_category():
    shopping = {
        'tomato': {'quantity': 6, 'unit': 'count', 'recipes': ['Pasta']},
        'milk': {'quantity': 1, 'unit': 'gallon', 'recipes': ['Cereal']}
    }
    result = group_items_by_category(shopping)
    assert 'produce' in result
    assert 'dairy' in result

test_function("group_items_by_category", "organizes by category", test_group_by_category)


# def test_validate_positive():
    # assert validate_serving_size(4) == True

# def test_validate_float():
    # assert validate_serving_size(2.5) == True

# def test_validate_negative():
    # try:
        # validate_serving_size(-2)
        # assert False, "Should raise ValueError"
    # except ValueError:
        # pass

# def test_validate_wrong_type():
     # try:
        # validate_serving_size("four")
        # assert False, "Should raise TypeError"
    # except TypeError:
        # pass

#test_function("validate_serving_size", "accepts positive int", test_validate_positive)
#test_function("validate_serving_size", "accepts positive float", test_validate_float)
#test_function("validate_serving_size", "rejects negative", test_validate_negative)
#test_function("validate_serving_size", "rejects non-number", test_validate_wrong_type)

print()


# ===================
# STORE DATA TESTS
# ===================
print("Testing store_data.py...")
print("-" * 60)

from src.store_data import (
    find_item_price,
    calculate_shopping_list_total
)

def test_find_item_exact():
    inventory = {'tomato paste': {'price': 0.89, 'size': '6', 'unit': 'oz'}}
    result = find_item_price('tomato paste', inventory)
    assert result is not None
    assert result['price'] == 0.89

def test_find_item_not_found():
    inventory = {'tomato': {'price': 0.50}}
    result = find_item_price('banana', inventory)
    assert result is None

def test_find_item_plural():
    inventory = {'tomato': {'price': 0.50}}
    result = find_item_price('tomatoes', inventory)
    assert result is not None

test_function("find_item_price", "finds exact match", test_find_item_exact)
test_function("find_item_price", "returns None for missing", test_find_item_not_found)
test_function("find_item_price", "handles plurals", test_find_item_plural)


def test_calculate_total_basic():
    shopping = {'tomato': {'quantity': 2, 'unit': 'count', 'recipes': ['Pasta']}}
    inventory = {'tomato': {'price': 0.50}}
    result = calculate_shopping_list_total(shopping, inventory)
    assert result['total'] == 1.0

def test_calculate_total_missing_items():
    shopping = {
        'tomato': {'quantity': 2, 'unit': 'count', 'recipes': ['Pasta']},
        'rare_item': {'quantity': 1, 'unit': 'each', 'recipes': ['Test']}
    }
    inventory = {'tomato': {'price': 0.50}}
    result = calculate_shopping_list_total(shopping, inventory)
    assert len(result['not_found']) == 1

test_function("calculate_shopping_list_total", "calculates basic total", test_calculate_total_basic)
test_function("calculate_shopping_list_total", "tracks missing items", test_calculate_total_missing_items)

print()


# ====================
# EXPORT UTILS TESTS
# ====================
print("Testing export_utils.py...")
print("-" * 60)

from src.export_utils import format_shopping_list_display

def test_format_display_basic():
    shopping = {'tomato': {'quantity': 6, 'unit': 'count', 'recipes': ['Pasta']}}
    result = format_shopping_list_display(shopping)
    assert 'tomato' in result.lower()
    assert '6' in result

def test_format_display_empty():
    result = format_shopping_list_display({})
    assert 'empty' in result.lower()

test_function("format_shopping_list_display", "formats basic list", test_format_display_basic)
test_function("format_shopping_list_display", "handles empty list", test_format_display_empty)

print()


# ====================
# INTEGRATION TESTS
# ====================
print("Testing Integration (Full Pipeline)...")
print("-" * 60)

def test_full_pipeline():
    """Test the complete workflow"""
    # This would require actual test files, so we'll make it simple
    recipes = [
        {
            'name': 'Test Pasta',
            'ingredients': ['2 cups flour', '1 tsp salt', '2 eggs'],
            'directions': 'Mix and cook'
        }
    ]
    servings = {'Test Pasta': 2}
    
    # Compile shopping list
    shopping_list = compile_shopping_list(recipes, servings)
    assert len(shopping_list) >= 2
    
    # Format for display
    display = format_shopping_list_display(shopping_list)
    assert len(display) > 0
    
    # Group by category
    grouped = group_items_by_category(shopping_list)
    assert len(grouped) > 0

test_function("Integration", "full pipeline works", test_full_pipeline)

print()


# ====================
# SUMMARY
# ====================
print("=" * 60)
print("TEST SUMMARY")
print("=" * 60)
print(f"Tests Passed: {tests_passed}")
print(f"Tests Failed: {tests_failed}")
print(f"Total Tests: {tests_passed + tests_failed}")
print(f"Success Rate: {(tests_passed/(tests_passed+tests_failed)*100):.1f}%")
print()

if tests_failed > 0:
    print("Failed Tests:")
    for detail in test_details:
        if detail.startswith("✗"):
            print(f"  {detail}")
    print()

print("=" * 60)


# Our group had Claude help us with generating an initial testing suite that puts everything in one nice, 
# easy readout to help with troubleshooting. As of 10/12/25, our functions passed 36/39 of the tests here, 
# giving our functions a success rate of 92.3% 
# This function library is still in active development and final tweaks are being made, so it should be 100% success soon.