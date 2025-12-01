"""Debug abstract class behavior"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models.Store import AbstractStore, CSVStore
import inspect

print("Testing AbstractStore...")

# Check if class is abstract
print(f"Is AbstractStore abstract? {inspect.isabstract(AbstractStore)}")
print(f"Abstract methods: {AbstractStore.__abstractmethods__}")

# Try to instantiate
try:
    store = AbstractStore("test")
    print("❌ PROBLEM: AbstractStore was instantiated!")
except TypeError as e:
    print(f"✓ CORRECT: {e}")