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
class KnowledgeFact:
    id: str
    ingredient: str
    category: str
    content: str
    source: list[str]

@dataclass
class EmbeddedKnowledgeFact:
    fact: KnowledgeFact
    vector: list[float]

@dataclass
class SearchResult:
    fact: KnowledgeFact
    score: float
