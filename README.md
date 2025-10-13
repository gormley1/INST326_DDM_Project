DDM Grocery List Information Retrieval & Analysis Tool

An early-stage grocery tool that reads recipes, extracts ingredients, compares store prices, and builds one organized shopping list. The main goal is to help people (especially families and students on a budget) save both time and money while planning meals.

Version: 0.1.0
Status: Phase 1 — Function Library (foundations)


Team Members & Roles

Team DDM — INST326 Section 0303

Darrell Cox — Documentation Lead
Focus: ingredient parsing, grouping, conversions

Denis Njoroge — Lead Developer
Focus: shopping list logic, price lookup, file validation, TXT parsing

Matthew Gormley — Data Architect & Project Coordinator
Focus: store data, PDF parsing, display formatting, totals


Domain Focus & Problem Statement

Domain: Information Retrieval / Data Management

Problem (why this matters):
Grocery prices bounce around due to inflation, supply chain issues, and dynamic pricing. It’s hard to know which store is actually cheapest and what your total will be until you check out. That makes budgeting stressful—especially when every dollar matters.

Our solution:

Read recipes from files (.txt, .pdf, .docx coming soon)

Pull out the ingredients in a clean, standard way

Compare prices across local stores (using mock CSVs for now)

Build one smart shopping list you can use or share



Installation & Setup

Requirements

Python 3.8+

Git

pip

Steps

# 1) Clone
git clone https://github.com/team-ddm/grocery-list-project.git
cd grocery-list-project

# 2) Create + activate venv
python -m venv venv
venv\Scripts\activate   # Windows
# or
source venv/bin/activate  # Mac/Linux

# 3) Install deps
pip install -r requirements.txt

Quick check:
python -c "print('Setup successful!')"


Quick Start

from src.recipe_parser import parse_recipe_file
from src.shopping_list import compile_shopping_list
from src.store_data import load_store_data, calculate_shopping_list_total, compare_store_totals  # compare_store_totals coming soon
from src.export_utils import export_to_csv  # when ready

# 1) Import two recipes (txt + pdf)
r1 = parse_recipe_file('data/sample_recipes/pasta_marinara.txt')
r2 = parse_recipe_file('data/sample_recipes/chicken_stir_fry.pdf')

# 2) Build the combined shopping list (scale servings)
recipes = [r1, r2]
servings = {r1['name']: 4, r2['name']: 2}
shopping = compile_shopping_list(recipes, servings)

# 3) Load a store inventory and total it up
inv = load_store_data('safeway')
summary = calculate_shopping_list_total(shopping, inv)
print('Estimated total:', summary['total'])


Project Structure
ddm-grocery-project/
├─ README.md
├─ requirements.txt
├─ src/
│  ├─ recipe_parser.py           # validate_file_format, parse_recipe_file, parse_txt_recipe, parse_pdf_recipe, extract_ingredients_from_text
│  ├─ ingredient_processor.py    # convert_fraction, parse_ingredient_line, normalize_ingredient_name, clean_ingredient_text, convert_units
│  ├─ shopping_list.py           # compile_shopping_list, calculate_total_quantity, group_items_by_category, (validate_serving_size TBD)
│  ├─ store_data.py              # load_store_data, find_item_price, calculate_shopping_list_total, (compare_store_totals TBD)
│  └─ export_utils.py            # export_to_csv, export_to_pdf, format_shopping_list_display (currently in main code block)
├─ data/
│  ├─ mock_stores/
│  │  ├─ safeway_inventory.csv
│  │  ├─ giant_inventory.csv
│  │  └─ trader_joes_inventory.csv
│  └─ sample_recipes/
│     ├─ pasta_marinara.txt
│     └─ chicken_stir_fry.pdf
└─ docs/ (optional)



Function Library Overview (with owners)
Recipe Import & Parsing

validate_file_format(filepath) — Simple (Denis)
Checks .txt/.docx/.pdf extension support.

parse_recipe_file(filepath) — Medium (Matt)
Dispatches to the right parser based on extension.

parse_txt_recipe(filepath) — Medium (Denis)
Reads plain text recipes; grabs name, ingredients, directions.

parse_pdf_recipe(filepath) — Complex (Matt)
Uses pdfplumber to extract text, then same idea as TXT.

extract_ingredients_from_text(text_block) — Medium (Darrell)
Pulls bullet-style ingredient lines from a block of text.

parse_docx_recipe(filepath) — (Unclaimed / TODO)

Ingredient Processing

convert_fraction(frac_str) — Helper (Matt)
Converts things like 1 1/2 or 2/5 to floats.

parse_ingredient_line(ingredient_string) — Medium (Darrell)
Returns {quantity, unit, item, preparation} from one line.

normalize_ingredient_name(raw_ingredient) — Medium (Denis)
Lowercases, removes descriptors, basic synonyms, naive plurals.

clean_ingredient_text(text) — Simple (Darrell)
Removes bullets/extra spaces.

convert_units(quantity, from_unit, to_unit) — Medium (Darrell)
Basic volume/weight conversions (tbsp/tsp/cup, oz/lb).

Shopping List Logic

compile_shopping_list(recipe_list, num_servings_dict) — Complex (Denis)
Combines ingredients across recipes; scales servings; notes unit mismatches.

calculate_total_quantity(ingredient_entries) — Medium (Matt)
Sums quantities for the same ingredient (keeps first unit).

group_items_by_category(shopping_list) — Medium (Darrell)
Buckets items: produce/dairy/meat/etc. (simple mapping).

format_shopping_list_display(shopping) — Simple (Matt)
Clean console string for the final list.

Note: validate_serving_size and compare_store_totals are planned next.

Store Data & Pricing

load_store_data(store_name, data_source='csv') — Medium (Matt)
Reads mock CSV store inventories into a dict.

find_item_price(item_name, store_inventory) — Simple→Medium (Denis)
Exact + basic plural/singular matching; returns price info dict.

calculate_shopping_list_total(shopping_list, store_inventory) — Medium (Matt)
Itemized totals + not-found list for a specific store.


Usage Examples (short + realistic)
A) Parse TXT + PDF, then Display
from src.recipe_parser import parse_recipe_file
from src.shopping_list import compile_shopping_list
from export_utils import format_shopping_list_display  # or from the location you placed it

r_txt = parse_recipe_file('data/sample_recipes/pasta_marinara.txt')
r_pdf = parse_recipe_file('data/sample_recipes/chicken_stir_fry.pdf')

shopping = compile_shopping_list([r_txt, r_pdf], {r_txt['name']: 4, r_pdf['name']: 2})
print(format_shopping_list_display(shopping))


B) Price Out at One Store

from src.store_data import load_store_data, calculate_shopping_list_total

inv = load_store_data('safeway')
summary = calculate_shopping_list_total(shopping, inv)
print(summary['total'])
print(summary['itemized'])
print('Missing:', summary['not_found'])

C) Clean + Normalize One Ingredient


from src.ingredient_processor import clean_ingredient_text, normalize_ingredient_name

raw = "  • Fresh Tomatoes  "
cleaned = clean_ingredient_text(raw)          # "Fresh Tomatoes"
normalized = normalize_ingredient_name(cleaned) # "tomato"
print(normalized)



Contribution Guidelines (how we work)

Branch names
[name]-[feature]
# examples:
denis-shopping-list
darrell-parsing
matthew-pdf-display


Workflow

git pull origin main

git checkout -b yourname-feature

Write or update a function (keep it small + clear)

Test with a tiny script or doctest

Commit with a clear message

Push and open a PR

Tag a reviewer (ex: @darrell)

Code rules

Every function has a proper docstring (what it does, args, returns, examples)

Follow PEP 8 (spacing, names, etc.)

Validate inputs and handle errors

Keep logic beginner-friendly and readable

Add at least one quick example or doctest


Development Timeline

Phase 1 (Now) — Function library foundations ✅ in progress

Implement & document core functions

Mock store CSVs

Phase 2 — Classes (Recipe, Ingredient, Store, ShoppingList)

Phase 3 — Integration & polishing (exports, compare_store_totals, docx parser)



Course Info

Course: INST326 — Object-Oriented Programming for Information Science
Section: 0303 | Semester: Fall 2025
Instructor: [Instructor Name]



Contact

Questions or bugs?

Open an issue on GitHub

Or message our group chat

Lead contact: matthew.j.j.gormley@gmail.com


Last Updated: October 2025
Version: 0.1.0 (Phase 1)