#validate_file_format-simple

import os
from typing import List

def validate_file_format(filepath: str) -> bool:
    """Return True if the file path has a supported recipe extension.

    Supported extensions: .txt, .docx, .pdf

    Args:
        filepath (str): Full or relative path to a file.

    Returns:
        bool: True if supported; False otherwise.

    Raises:
        TypeError: If filepath is not a string.

    Examples:
        >>> validate_file_format("recipe.txt")
        True
        >>> validate_file_format("image.jpg")
        False
    """
    if not isinstance(filepath, str):
        raise TypeError("filepath must be a string")

    supported: List[str] = [".txt", ".docx", ".pdf"]
    _, ext = os.path.splitext(filepath)
    return ext.lower() in supported
