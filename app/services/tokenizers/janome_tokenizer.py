"""
Janome tokenizer adapter.
"""

from typing import List
from janome.tokenizer import Tokenizer as JanomeTokenizerImpl
from .base_tokenizer import BaseTokenizer, Token


class JanomeTokenizer(BaseTokenizer):
    """Janome-based Japanese tokenizer implementation"""

    def __init__(self):
        super().__init__()
        self._tokenizer = JanomeTokenizerImpl()

    def tokenize(self, text: str) -> List[Token]:
        """
        Tokenize Japanese text using Janome.

        Args:
            text: Japanese text to tokenize

        Returns:
            List of Token objects
        """
        tokens = []

        try:
            for janome_token in self._tokenizer.tokenize(text):
                surface = janome_token.surface
                # Janome POS format: "名詞,一般,*,*,*,*,*"
                pos_parts = janome_token.part_of_speech.split(',')
                pos = pos_parts[0] if pos_parts else '未知語'
                base_form = pos_parts[6] if len(pos_parts) > 6 and pos_parts[6] != '*' else surface

                tokens.append(Token(
                    surface=surface,
                    pos=pos,
                    base_form=base_form
                ))
        except Exception as e:
            print(f"Janome tokenization error: {e}")

        return tokens
