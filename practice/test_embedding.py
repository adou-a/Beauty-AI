from src.rag.loader import DocumentLoader
from src.rag.chunker import TextChunker
from src.rag.embedding import EmbeddingService

loader = DocumentLoader()

documents = loader.load_directory('data/knowledge')

chunker = TextChunker(chunk_size= 200,overlap= 50)

embedding_service = EmbeddingService()

for document in documents:
    chunks = chunker.split(document)

    for chunk in chunks[:2]:

        embedded_chunk = (embedding_service.embed_chunk(chunk))
        print('source: ',embedded_chunk.source)
        print('index: ',embedded_chunk.index)
        print('content: ', embedded_chunk.content)

        print('vector length: ',len(embedded_chunk.vector))
        print('vector preview: ',embedded_chunk.vector[:5])

        print('-' * 50)
