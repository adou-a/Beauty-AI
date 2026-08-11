from  dataclasses import dataclass



@dataclass
class Document:
    content: str
    source: str


@dataclass
class Chunk:
    content: str
    source: str
    index: int


@dataclass
class EmbeddedChunk:
    content: str
    source: str
    index: int
    vector: list[float]

@dataclass
class SearchResult:
    chunk: EmbeddedChunk
    score: float