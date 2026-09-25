"""
TextChunker: splits long text into overlapping chunks suitable for embedding.

Overlap helps preserve context that would otherwise be cut at a chunk
boundary (e.g. a sentence split across two chunks).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class Chunk:
    index: int
    text: str


class TextChunker:
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 120):
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if chunk_overlap < 0 or chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be >= 0 and smaller than chunk_size")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split(self, text: str) -> List[Chunk]:
        text = text.strip()
        if not text:
            return []

        step = self.chunk_size - self.chunk_overlap
        chunks: List[Chunk] = []
        start = 0
        index = 0

        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            piece = text[start:end].strip()
            if piece:
                chunks.append(Chunk(index=index, text=piece))
                index += 1
            if end == len(text):
                break
            start += step

        return chunks
