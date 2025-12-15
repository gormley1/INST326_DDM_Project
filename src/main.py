"""
Main application demonstrating complete DDM Grocery System
"""
from pathlib import Path
from recipe_parser import parse_recipe_file
from shopping_list import compile_shopping_list
from store_data import load_store_data, calculate_shopping_list_total
from export_utils import export_to_csv, format_shopping_list_display
from persistence import GrocerySystemState

def main():
    """Demonstrate complete grocery planning workflow"""
    print("=" * 60)
    print("DDM GROCERY PLANNING SYSTEM")
    print("=" * 60)
    
    # 1. Load recipes
    print("\n1. Loading recipes...")
    recipes = []
    recipe_files = [
        'data/sample_recipes/pasta_marinara.txt',
        'data/sample_recipes/chicken_stir_fry.pdf'
    ]
    
    for file in recipe_files:
        if Path(file).exists():
            recipe = parse_recipe_file(file)
            recipes.append(recipe)
            print(f"   ✓ Loaded: {recipe['name']}")
    
    # 2. Compile shopping list
    print("\n2. Compiling shopping list...")
    servings = {r['name']: 4 for r in recipes}
    shopping_list = compile_shopping_list(recipes, servings)
    print(f"   ✓ {len(shopping_list)} unique items")
    
    # 3. Compare stores
    print("\n3. Comparing store prices...")
    stores = ['safeway', 'giant', 'trader_joes']
    best_price = float('inf')
    best_store = None
    
    for store_name in stores:
        try:
            inventory = load_store_data(store_name)
            result = calculate_shopping_list_total(shopping_list, inventory)
            print(f"   {store_name.title()}: ${result['total']:.2f}")
            
            if result['total'] < best_price:
                best_price = result['total']
                best_store = store_name
        except FileNotFoundError:
            print(f"   {store_name}: (no data)")
    
    print(f"\n   💰 Best deal: {best_store.title()} (${best_price:.2f})")
    
    # 4. Save and export
    print("\n4. Saving results...")
    state = GrocerySystemState()
    state.save_shopping_list(shopping_list, 'weekly_plan')
    export_to_csv(shopping_list, 'weekly_shopping')
    print("   ✓ Saved to data/saved_states/weekly_plan.json")
    print("   ✓ Exported to data/exports/weekly_shopping.csv")
    
    # 5. Display formatted list
    print("\n5. Your Shopping List:")
    print(format_shopping_list_display(shopping_list))

if __name__ == "__main__":
    main()