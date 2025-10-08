"""
Base tokenizer interface and Token data class.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List


@dataclass
class Token:
    """Unified token representation across different tokenizers"""
    surface: str      # The word/token text
    pos: str          # Part of speech (名詞, 動詞, etc.)
    base_form: str    # Base/dictionary form of the word

    def __str__(self):
        return f"{self.surface}({self.pos})"


class BaseTokenizer(ABC):
    """Abstract base class for Japanese tokenizers"""

    def __init__(self):
        """Initialize the tokenizer"""
        self.stop_words = {
            'する', 'ある', 'なる', 'いる', 'できる', 'という', 'として',
            'の', 'に', 'は', 'を', 'が', 'で', 'て', 'と', 'から', 'まで',
            'これ', 'それ', 'あれ', 'この', 'その', 'あの', 'ここ', 'そこ', 'あそこ',
            'こちら', 'そちら', 'あちら', 'どこ', 'だれ', 'なに', 'なん', 'いつ', 'どう',
        }
        self.pos_filter = ['名詞', '動詞', '形容詞', '副詞']

    @abstractmethod
    def tokenize(self, text: str) -> List[Token]:
        """
        Tokenize Japanese text into a list of tokens.

        Args:
            text: Japanese text to tokenize

        Returns:
            List of Token objects
        """
        pass

    def tokenize_and_filter(self, text: str, min_length: int = 2) -> List[str]:
        """
        Tokenize text and apply POS filtering and length filtering.

        Args:
            text: Text to tokenize
            min_length: Minimum token length to include

        Returns:
            List of filtered token surfaces (strings)
        """
        tokens = self.tokenize(text)
        filtered = []

        for token in tokens:
            # Filter by POS tag
            if token.pos not in self.pos_filter:
                continue

            # Filter by length
            if len(token.surface) < min_length:
                continue

            # Filter stop words
            if token.surface.lower() in self.stop_words:
                continue

            filtered.append(token.surface)

        return filtered
