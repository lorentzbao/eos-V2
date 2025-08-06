from janome.tokenizer import Tokenizer
from typing import List, Set
from collections import Counter
import re

class JapaneseTextProcessor:
    def __init__(self):
        self.tokenizer = Tokenizer()
        self.stop_words = {
            'の', 'に', 'は', 'を', 'た', 'が', 'で', 'て', 'と', 'し', 'れ', 'さ', 'ある', 'いる', 
            'する', 'です', 'ます', 'だ', 'である', 'から', 'まで', 'より', 'など', 'こと', 
            'もの', 'ため', 'よう', 'そう', 'どう', 'なる', 'なり', 'なっ', 'され', 'られ',
            'これ', 'それ', 'あれ', 'この', 'その', 'あの', 'ここ', 'そこ', 'あそこ',
            'だけ', 'でも', 'しか', 'まだ', 'もう', 'すぐ', 'ずっと', 'とても', 'まさか'
        }
    
    def tokenize(self, text: str) -> List[str]:
        tokens = []
        for token in self.tokenizer.tokenize(text):
            word = token.surface
            pos = token.part_of_speech.split(',')[0]
            
            if pos in ['名詞', '動詞', '形容詞', '副詞']:
                if len(word) > 1 and word not in self.stop_words:
                    tokens.append(word)
        
        return tokens
    
    def normalize_text(self, text: str) -> str:
        text = re.sub(r'[０-９]', lambda x: str(ord(x.group()) - ord('０')), text)
        text = re.sub(r'[Ａ-Ｚａ-ｚ]', lambda x: chr(ord(x.group()) - ord('Ａ') + ord('A')) if 'Ａ' <= x.group() <= 'Ｚ' else chr(ord(x.group()) - ord('ａ') + ord('a')), text)
        return text
    
    def process_text(self, text: str) -> List[str]:
        text = self.normalize_text(text)
        tokens = self.tokenize(text)
        return tokens
    
    def get_term_frequency(self, tokens: List[str]) -> dict:
        return dict(Counter(tokens))