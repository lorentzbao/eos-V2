"""
MeCab tokenizer adapter.
"""

from typing import List
from .base_tokenizer import BaseTokenizer, Token


class MeCabTokenizer(BaseTokenizer):
    """MeCab-based Japanese tokenizer implementation"""

    def __init__(self):
        super().__init__()
        try:
            import MeCab
            self._tagger = MeCab.Tagger()
        except ImportError:
            raise ImportError(
                "MeCab is not installed. Please install it with: "
                "pip install mecab-python3"
            )

    def tokenize(self, text: str) -> List[Token]:
        """
        Tokenize Japanese text using MeCab.

        Args:
            text: Japanese text to tokenize

        Returns:
            List of Token objects
        """
        tokens = []

        try:
            # Parse the text
            node = self._tagger.parseToNode(text)

            while node:
                # Skip BOS/EOS nodes
                if node.surface:
                    surface = node.surface
                    # MeCab feature format: "名詞,一般,*,*,*,*,機械,キカイ,キカイ"
                    features = node.feature.split(',')
                    pos = features[0] if features else '未知語'
                    base_form = features[6] if len(features) > 6 and features[6] != '*' else surface

                    tokens.append(Token(
                        surface=surface,
                        pos=pos,
                        base_form=base_form
                    ))

                node = node.next
        except Exception as e:
            print(f"MeCab tokenization error: {e}")

        return tokens
