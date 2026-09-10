from sentence_transformers import SentenceTransformer
from src.rag.models import KnowledgeFact,EmbeddedKnowledgeFact


DEFAULT_EMBEDDING_MODEL = (
    'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
)
DEFAULT_EMBEDDING_REVISION = 'e8f8c211226b894fcb81acc59f3b34ba3efd5f42'


class EmbeddingService:
    def __init__(
        self,
        model_name: str = DEFAULT_EMBEDDING_MODEL,
        revision: str = DEFAULT_EMBEDDING_REVISION,
    ):
        self.model_name = model_name
        self.revision = revision

        self.model = SentenceTransformer(model_name, revision=revision)

    #负责把文字转化成向量
    def embed_text(self,text: str) -> list[float]:

        vector = self.model.encode(text,normalize_embeddings= True)

        return vector.tolist()

    def embed_fact(self,fact: KnowledgeFact) -> EmbeddedKnowledgeFact:

        vector = self.embed_text(fact.content)

        return EmbeddedKnowledgeFact(fact = fact,vector = vector)
    

       
