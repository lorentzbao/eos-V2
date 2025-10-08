"""
Tokenizer factory for creating tokenizer instances based on configuration.
"""

from typing import Optional
from .base_tokenizer import BaseTokenizer
from .janome_tokenizer import JanomeTokenizer
from .mecab_tokenizer import MeCabTokenizer


def get_tokenizer(tokenizer_type: Optional[str] = None) -> BaseTokenizer:
    """
    Factory function to create a tokenizer instance.

    Args:
        tokenizer_type: Type of tokenizer to create. Options:
            - 'janome': Janome tokenizer (default, pure Python)
            - 'mecab': MeCab tokenizer (faster, requires C++ library)
            - None: Auto-detect (tries MeCab first, falls back to Janome)

    Returns:
        An instance of BaseTokenizer

    Raises:
        ValueError: If the specified tokenizer_type is not supported
        ImportError: If the required tokenizer library is not installed

    Examples:
        >>> tokenizer = get_tokenizer('janome')
        >>> tokenizer = get_tokenizer('mecab')
        >>> tokenizer = get_tokenizer()  # Auto-detect
    """
    if tokenizer_type is None:
        # Auto-detect: try MeCab first (faster), fallback to Janome
        try:
            return MeCabTokenizer()
        except ImportError:
            print("MeCab not available, falling back to Janome")
            return JanomeTokenizer()

    tokenizer_type = tokenizer_type.lower()

    if tokenizer_type == 'janome':
        return JanomeTokenizer()
    elif tokenizer_type == 'mecab':
        return MeCabTokenizer()
    else:
        raise ValueError(
            f"Unknown tokenizer type: {tokenizer_type}. "
            f"Supported types: 'janome', 'mecab'"
        )
