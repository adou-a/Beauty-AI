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