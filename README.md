# Cornucopia Grocery List Assistant

**Smart meal planning & grocery shopping made easy**

Version 1.0.0 | INST326 Fall 2025 | Team DDM

## Table of Contents

- [Overview](#overview)
- [Problem Statement](#problem-statement)
- [Features](#features)
- [Team](#team)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Testing](#testing)
- [Technical Architecture](#technical-architecture)
- [Documentation](#documentation)
- [Future Enhancements](#future-enhancements)
- [License](#license)

## Overview

Cornucopia is a command-line grocery shopping assistant that helps users import & manage recipes, organize meals, compare store prices, and generate optimized formatted shopping lists. Built with Python using object-oriented programming principles, Cornucopia addresses the real-world challenge of managing time requirements for meal planning & grocery expenses in an era of limited personal tie & fluctuating food prices.

### Key Capabilities

- Import recipes from multiple formats (TXT, PDF, DOCX)
- Organize recipes with custom tags (dinner, quick, vegetarian, etc.)
- Plan meals for multiple days with automatic ingredient aggregation
- Compare prices across multiple grocery stores
- Export shopping lists to PDF, CSV, or TXT formats

## Problem Statement

Grocery prices fluctuate weekly due to inflation, supply chain disruptions, and dynamic pricing strategies. Many people, the developers included, barely have enough time to cook meals everyday, let alone plan out grocery shopping every single week. This instability disproportionately affects low-income households and people with limited time (such as students & young professionals). The difference of a few dollars can determine whether bills get paid on time, and an extra hour of shopping can mean the difference between self care, making dinner, or going hungry.

**Our Solution**: Cornucopia provides price transparency and time-saving automation to help users make expedited & informed grocery shopping decisions.

## Features

### Recipe Management

- **Multi-format import**: TXT, PDF, DOCX supported in current version
- **Persistent storage**: JSON-based recipe book
- **Tag organization**: Categorize recipes (breakfast, dinner, quick, Italian, etc.)
- **Fuzzy search**: Find recipes by name or ingredient

### Smart Shopping Lists

- **Multi-recipe aggregation**: Combine ingredients from multiple recipes
- **Quantity scaling**: Automatically adjust for servings
- **Unit handling**: Handle mixed units (cups, tablespoons, pounds)
- **Multi-day planning**: Plan meals for entire week (up to 14 days)

### Price Comparison

- **Multi-store support**: Compare Safeway, Giant, Trader Joe's
- **Price calculations**: Itemized totals with missing items tracking
- **Best value finder**: Identify cheapest store automatically

### Export Options

- **PDF**: Professional formatted lists with checkboxes
- **CSV**: Spreadsheet-compatible format
- **TXT**: Simple text format for mobile devices & VS Code interface
- **Categorized organization**: Items grouped by store section (Produce, Dairy, etc.)

### User Settings

- Customizable default servings
- Preferred store selection
- Default export format
- Export directory configuration

## Team

**Team DDM - INST326 Section 0303**

| Member              | Role                                            | Contributions                                                                                                        |
| ------------------- | ----------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| **Matthew Gormley** | Data Architect & Lead Coordinator, Co-Developer | RecipeBook class, export utilities (CSV/PDF/TXT), store data integration, main CLI application, project coordination |
| **Darrell Cox**     | Documentation Lead                              | Recipe parsing (TXT/PDF/DOCX), ingredient processing, documentation, usage guides                                    |
| **Denis Njoroge**   | Lead Developer                                  | Shopping list compilation, ingredient normalization, store comparison, testing framework                             |

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Git (for cloning repository)

### Setup Instructions

1. **Clone the repository**

```bash
git clone https://github.com/your-team/ddm-grocery-project.git
cd ddm-grocery-project
```

2. **Create virtual environment**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Mac/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Verify installation**

```bash
python main.py
```

You should see the Cornucopia welcome screen (the Main Menu with 7 options).

## Usage

### Quick Start

1. **Run the application**

```bash
python main.py
```

2. **Import your first recipe** (Option 1)

   - Enter path to recipe file (can be external from project directory): `data/sample_recipes/scrambled_eggs.txt`
   - Add tags when prompted: `breakfast, quick`

3. **Create a shopping list** (Option 3)

   - Select number of days: `1`
   - Choose recipes to include
   - Enter servings for each recipe

4. **Compare store prices** (Option 4)

   - View price comparison across stores
   - See which store is cheapest

5. **Export your list** (Option 5)
   - Choose format: PDF, CSV, or TXT
   - List saved to `exports/` directory

### Example Workflows

#### Workflow 1: Weekend Meal Prep

```
1. Import Recipe → avocado_toast.txt (tag: breakfast)
2. Import Recipe → veggie_quesadilla.pdf (tag: lunch)
3. Import Recipe → chicken_caesar_wrap.pdf (tag: lunch)
4. Create Shopping List → Select all 3 recipes → 4 servings each
5. Compare Prices → See cheapest store
6. Export → PDF format → Print for shopping
```

#### Workflow 2: Weekly Meal Planning

```
1. View Recipe Book → Filter by "dinner" tag
2. Create Shopping List → Plan 7 days → Select recipes for each day
3. Compare Prices → Identify best store
4. Export → CSV → Upload to Google Drive for family
```

#### Workflow 3: Quick Breakfast Planning

```
1. View Recipe Book → Search "egg"
2. Create Shopping List → Select 2 breakfast recipes → 2 servings
3. Export → TXT → Send to phone for quick shopping
```

## Project Structure

```
ddm-grocery-project/
│
├── main.py                      # Main CLI application
├── requirements.txt             # Python dependencies
├── README.md                    # This file
├── TESTING.md                   # Testing documentation
│
├── data/                        # Data files
│   ├── mock_stores/            # Store inventory CSV files
│   │   ├── safeway_inventory.csv
│   │   ├── giant_inventory.csv
|   |   └── traderjoes_inventory.csv
│   ├── sample_recipes/         # Example recipe files (there are more than what's listed)
│   │   ├── scrambled_eggs.txt
│   │   ├── veggie_quesadilla.pdf
│   │   └── greek_yogurt_parfait.docx
│   └── users/                  # User data directories
│       └── test_user/
│           ├── recipe_book.json
│           └── settings.json
│
├── src/                        # Source code
│   ├── models/                 # Class definitions
│   │   ├── RecipeBook.py      # Recipe storage & management
│   │   ├── Ingredient.py      # Ingredient class
│   │   ├── ShoppingList.py    # ShoppingList class
│   │   └── Store.py           # Store hierarchy (Abstract, CSV, API, Scraper)
│   ├── recipe_parser.py        # RecipeParser class (TXT/PDF/DOCX)
│   ├── shopping_list.py        # Shopping list compilation
│   ├── ingredient_processor.py # Ingredient normalization
│   ├── store_data.py           # Store data loading & comparison
│   └── export_utils.py         # Export functions (CSV/PDF/TXT)
│
├── tests/                      # Test suite
│   ├── test_recipe_book.py     # RecipeBook unit tests (42 tests)
│   ├── test_export_utils.py    # Export unit tests (30 tests)
│   ├── test_integration.py     # Integration tests (8 tests)
│   ├── test_system.py          # System tests (5 tests)
|   └── archive/                # Old/obsolete tests from past project components (multiple files)
│
└── exports/                    # Generated shopping lists
    ├── shopping_list_20241216.pdf
    └── shopping_list_20241216.csv
```

## Testing

### Test Strategy

Cornucopia uses a comprehensive three-tier testing approach:

**85+ Total Tests**

- **Unit Tests (72)**: Test individual components in isolation
- **Integration Tests (8)**: Test component interactions
- **System Tests (5)**: Test complete user workflows

### Running Tests

```bash
# Run all tests
python -m unittest discover tests -p "test_*.py" -v

# Run specific test file
python -m unittest tests.test_recipe_book -v

# Run specific test class
python -m unittest tests.test_system.TestCompleteRecipeWorkflow -v
```

### Test Coverage

- Recipe import from all formats (TXT, PDF, DOCX)
- Recipe storage and persistence
- Shopping list compilation and aggregation
- Store price comparison
- Export to all formats (CSV, PDF, TXT)
- Tag management
- Error handling
- Complete user workflows

For detailed testing documentation, see [TESTING.md](TESTING.md).

## Technical Architecture

### Object-Oriented Design

**Core Classes:**

- `RecipeBook`: Manages recipe collection with JSON persistence
- `RecipeParser`: Inheritance hierarchy for parsing recipes from different file formats
- `Ingredient`: Represents single ingredient with quantity/unit
- `ShoppingList`: Aggregates ingredients from multiple recipes
- `AbstractStore`: Abstract base for store types
- `CSVStore`, `MockAPIStore`, `WebScraperStore`: Store implementations

**Design Patterns:**

- **Inheritance**: Store hierarchy (AbstractStore --> CSVStore, APIStore, ScraperStore)
- **Composition**: ShoppingList HAS ingredients, HAS recipes, HAS store comparisons
- **Polymorphism**: Same interface, different implementations (load_inventory, price_for)
- **Abstraction**: Abstract methods force implementation in subclasses

### Data Flow

```
Recipe Files (TXT/PDF/DOCX)
    ↓
RecipeParser (parse & validate)
    ↓
RecipeBook (store with tags)
    ↓
compile_shopping_list (aggregate ingredients)
    ↓
ShoppingList (with quantities & units)
    ↓
compare_store_totals (calculate prices)
    ↓
export_to_pdf/csv/txt (generate output)
    ↓
User receives shopping list
```

### Technology Stack

- **Language**: Python 3.8+
- **Data Storage**: JSON (recipe_book.json)
- **PDF Handling**: PyPDF2 (reading), fpdf2 (generation), pdfplumber (text extraction)
- **DOCX Handling**: python-docx
- **Testing**: unittest (standard library)

## Documentation

### Available Documentation

- **README.md** (this file): Project overview, installation, usage
- **TESTING.md**: Comprehensive testing strategy and instructions
- **Inline Documentation**: All functions have detailed docstrings & comments in code
- **Project Charter**: Original project proposal (submitted earlier in the semester)

### Code Documentation Standards

All functions include:

- Purpose description
- Parameter types and descriptions
- Return value description
- Usage examples
- Error conditions

Example:

```python
def compile_shopping_list(recipe_list: List[Dict], num_servings_dict: Dict) -> Dict:
    """
    Aggregate ingredients from multiple recipes into one shopping list.

    Args:
        recipe_list: List of recipe dictionaries
        num_servings_dict: Map of recipe name → servings multiplier

    Returns:
        dict: Aggregated shopping list with quantities and units

    Example:
        >>> recipes = [{'name': 'Pasta', 'ingredients': ['2 cups flour']}]
        >>> servings = {'Pasta': 2}
        >>> compile_shopping_list(recipes, servings)
        {'flour': {'quantity': 4.0, 'unit': 'cups', ...}}
    """
```

## Project Evolution

### Project 1: Function Library (Oct 2024)

- Built 15+ utility functions
- Recipe parsing (TXT, PDF)
- Ingredient processing
- Store data loading
- Basic shopping list compilation

### Project 2: OOP Classes (Nov 2024)

- Created `RecipeBook` class with persistence
- Implemented `Ingredient` class
- Built `ShoppingList` class with composition
- Added encapsulation and properties

### Project 3: Advanced OOP (Nov 2024)

- Designed `AbstractStore` hierarchy (inheritance)
- Implemented `CSVStore`, `MockAPIStore`, `WebScraperStore` (polymorphism)
- Added abstract base classes (ABC)
- Demonstrated composition vs inheritance

### Project 4: Integration & Testing (Dec 2024)

- Built complete CLI application (`main.py`)
- Created 85+ comprehensive tests
- Added export functionality (PDF, CSV, TXT)
- Implemented tag-based organization
- Added multi-day meal planning
- Professional documentation

## Future Enhancements

### Planned Features (Post-Semester, built by Matt solo as a personal project)

**Phase 1: Enhanced Data Collection**

- Receipt OCR processing (scan receipts to build price database)
- Crowdsourced price data (users contribute pricing)
- Real-time store API integration (if inexpensive/with permission)
- Price history tracking (for individual users, geographic locations, and store chains)

**Phase 2: Advanced Features**

- Nutrition analysis per recipe (need a nutritional database first)
- Dietary restriction filtering (gluten-free, vegan, nut allergy, etc.)
- Meal plan templates (keto, Mediterranean, etc.)
- Pantry inventory management
- Shopping List building based on available ingredient matches to existing recipes
- Expiration date tracking

**Phase 3: User Experience**

- Web interface (Flask/Django)
- Mobile app (React Native)
- User accounts with cloud sync
- Recipe sharing community
- Meal planning calendar
- Savings tracking
- Deal/price drop notifications

**Phase 4: Intelligence**

- Machine learning price predictions
- Personalized recipe recommendations
- Automatic unit conversions with ML
- Smart ingredient substitutions

### Known Limitations

- **Store Data**: Currently uses mock CSV data (real API integration or user price database pending)
- **Unit Conversions**: Basic conversions only (cups ↔ tablespoons, oz ↔ lbs)
- **Recipe Parsing**: May struggle with non-standard formats (especially PDF tables)
- **Price Accuracy**: Dependent on data freshness
- **Store Coverage**: Limited to stores with data files

## Contributing

This project was completed as part of INST326 coursework. For questions or suggestions:

**Team Contact:**

- Matthew Gormley: gormley1@terpmail.umd.edu
- Darrell Cox: [GitHub/Email]
- Denis Njoroge: [GitHub/Email]

## License

This project was created for educational purposes as part of INST326: Object-Oriented Programming for Information Science at the University of Maryland.
More robust license pending (given potential future development, this is NOT an open source project).

**Course**: INST326 - Fall 2025  
**Section**: 0303  
**Instructor**: Dr. Christopher Dempwolf (happy retirement!!)
**Institution**: University of Maryland, College of Information

## Acknowledgments

- **Course Instructors & TAs**: For guidance throughout the semester
- **Team DDM**: For excellent collaboration and dedication despite setbacks and a myriad of challenges
- **Python Community**: For excellent libraries (fpdf2, PyPDF2, python-docx, etc.)
- **Users**: Who will benefit from grocery price transparency
- **Claude**: AI tool used over the course of the project for debugging source code, documentation formatting, mock data generation, and test suite development assistance

**Last Updated**: December 16, 2025  
**Version**: 1.0.0  
**Status**: Project Complete - Ready for Demo

_Making grocery shopping easier, one recipe at a time._
