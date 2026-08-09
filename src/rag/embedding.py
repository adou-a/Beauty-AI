from sentence_transformers import SentenceTransformer
from src.rag.models import Chunk,EmbeddedChunk



class EmbeddingService:
    def __init__(self,model_name: str = ('sentence-transformers/''paraphrase-multilingual-MiniLM-L12-v2')):

        self.model = SentenceTransformer(model_name)

    #负责把文字转化成向量
    def embed_text(self,text: str) -> list[float]:

        vector = self.model.encode(text,normalize_embeddings= True)

        return vector.tolist()

    def embed_chunk(self,chunk:Chunk) -> EmbeddedChunk:

        vector = self.embed_text(chunk.content)

        return EmbeddedChunk(content = chunk.content,source = chunk.source,index = chunk.index,vector = vector)