# Testing Strategy - Cornucopia Grocery List System

## Overview

The Cornucopia system uses a comprehensive three-tier testing strategy following the **Test Pyramid** approach: heavy unit testing at the base, moderate integration testing in the middle, and focused system testing at the top.

**Total Test Count: 85 tests**

- Unit Tests: 72 tests
- Integration Tests: 8 tests
- System Tests: 5 tests

## Test Levels

### 1. Unit Tests (72 tests)

Unit tests verify individual components work correctly in isolation. Almost all of these are leftover from Project 03, with some updates. More testing files used in other projects can be found in `tests/archive`.

**`test_recipe_book.py` (42 tests)**

- Basic CRUD operations (add, get, update, remove recipes)
- Tag management (add tags, remove tags, search by tags)
- Data persistence (save/load from JSON)
- Import/export functionality
- Search and filtering
- Error handling

**`test_export_utils.py` (30 tests)**

- CSV export (categorized and simple formats)
- PDF export (with title, categorization, recipes list)
- TXT export (categorized and simple formats)
- Category grouping logic
- Format display functions
- Error handling for file operations

### 2. Integration Tests (8 tests)

Integration tests verify that components work together correctly.

**`test_integration.py` (8 tests)**

- **TestRecipeToRecipeBook**: Parse recipes from files → save to RecipeBook → verify persistence
- **TestRecipeBookToShoppingList**: Retrieve recipes → compile shopping list → verify aggregation
- **TestShoppingListToStoreComparison**: Create list → compare stores → verify price calculations
- **TestShoppingListToExport**: Create list → export to all formats → verify file creation
- **TestCompleteUserJourney**: Full workflow from import to export
- **TestErrorRecovery**: Invalid input handling, missing data handling

### 3. System Tests (5 tests)

System tests verify complete user workflows function as intended.

**`test_system.py` (5 tests)**

- **TestCompleteRecipeWorkflow**: Import 3 recipes (TXT/PDF/DOCX) → tag → create list → compare prices → export PDF
- **TestMultiDayMealPlanning**: Plan 3 days of meals → aggregate shopping list → verify scaling
- **TestPersistenceAcrossSessions**: Add recipes → close program → reopen → verify data intact
- **TestTagBasedOrganization**: Filter recipes by tags → create targeted shopping lists
- **TestStoreComparisonDecision**: Compare stores → identify cheapest → export with recommendation

## Running Tests

### Run All Tests

```bash
# From project root
python -m unittest discover tests -p "test_*.py" -v
```

### Run Specific Test Levels

```bash
# Unit tests only
python -m unittest tests.test_recipe_book tests.test_export_utils -v

# Integration tests only
python -m unittest tests.test_integration -v

# System tests only
python -m unittest tests.test_system -v
```

### Run Single Test File

```bash
python -m unittest tests.test_recipe_book -v
```

    Just insert the test file you want to run in place of `test_recipe_book`

### Run Specific Test Class

```bash
python -m unittest tests.test_system.TestCompleteRecipeWorkflow -v
```

## Test Coverage

### What We Test

**Functional Requirements:**

- Recipe import from TXT/PDF/DOCX formats
- Recipe storage with JSON persistence
- Tag-based organization
- Shopping list compilation with quantity aggregation
- Multi-store price comparison
- Export to CSV/PDF/TXT formats

**Data Integrity:**

- Persistence across program sessions
- Correct quantity scaling for servings
- Proper ingredient aggregation
- Tag management accuracy

**Error Handling:**

- Invalid file formats
- Missing files
- Corrupt JSON data
- Invalid recipe data
- Missing store inventory

**User Workflows:**

- Complete recipe-to-shopping-list pipeline
- Multi-day meal planning
- Tag-based recipe filtering
- Store comparison and selection

### What We Don't Test

- External API calls (not yet implemented, but we have plans for future development!)
- Web scraping functionality (placeholder only, potential gray area legality depending on use case)
- GUI/CLI user input validation (tested manually using files in `data` repository, see exports folder for outputs)
- Receipt OCR processing (future feature to allow users to scan in results of shopping list; this is the goal mechanism for price aggregation & comparison, inspired by Waze/Fetch/Ibotta/Expensify)

## Test Best Practices

### Writing Good Tests

1. **Follow Arrange-Act-Assert Pattern**

```python
def test_example(self):
    # Arrange: Set up test data
    recipe = {'name': 'Test', 'ingredients': [], 'directions': ''}

    # Act: Perform the action
    self.recipe_book.add_recipe(recipe)

    # Assert: Verify the result
    self.assertEqual(self.recipe_book.count_recipes(), 1)
```

2. **Use Descriptive Test Names**

- DO: `test_parse_and_save_txt_recipe`
- DON'T: `test_1`

3. **Test One Thing Per Test**
   Each test should verify a single behavior or requirement.

4. **Use setUp and tearDown**
   Clean up resources (temp files, directories) after each test.

5. **Make Tests Independent**
   Tests should not depend on other tests running first.

### Temporary File Handling

All tests that create files use `tempfile.mkdtemp()`:

```python
def setUp(self):
    self.temp_dir = tempfile.mkdtemp()

def tearDown(self):
    shutil.rmtree(self.temp_dir)
```

This ensures no test artifacts clog up the project & require manual deletion.

## Test Dependencies

Tests require these packages (in `requirements.txt`):

- `PyPDF2` - PDF parsing
- `python-docx` - DOCX parsing
- `pdfplumber` - PDF text extraction
- `fpdf2` - PDF generation

Install with:

```bash
pip install -r requirements.txt
```

## Continuous Improvement

### Adding New Tests

When adding new features:

1. Write unit tests first (test the component in isolation)
2. Add integration tests (test how it works with other components)
3. Add system tests if it affects user workflows

### Test Maintenance

- Run tests before committing code
- Update tests when changing functionality
- Remove or update obsolete tests; move to `tests/archive` for storage
- Keep test data files in `data/sample_recipes/`

## Test Results Interpretation

### Success

```
Ran 85 tests in 12.345s
OK
```

### Failure Example

```
FAIL: test_export_to_pdf (test_export_utils.TestExportToPDF)
AssertionError: PDF file not created
```

**Action**: Check if `fpdf2` is installed, verify file permissions

### Error Example

```
ERROR: test_parse_txt_recipe (test_integration.TestRecipeToRecipeBook)
FileNotFoundError: [Errno 2] No such file or directory: 'data/sample_recipes/scrambled_eggs.txt'
```

**Action**: Ensure sample recipe files exist in `data/sample_recipes/`

## Contact

Questions about tests? Contact:

- **Denis Njoroge** - Lead Developer
- **Matthew Gormley** - Data Architect & Coordinator, Co-Lead Developer
- **Darrell Cox** - Documentation Lead

---

**Last Updated**: December 15, 2024  
**Project**: INST326 Cornucopia Grocery List System  
**Team**: DDM
