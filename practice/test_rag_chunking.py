from src.rag.loader import DocumentLoader
from src.rag.chunker import TextChunker


loader = DocumentLoader()
documents = loader.load_directory('data/knowledge')

chunker = TextChunker(chunk_size = 200, overlap = 200)

for document in documents:
    chunks = chunker.split(document)

    print(document.source,len(chunks))

    #查看前两个chunk
    for chunk in chunks[:2]:
        print(chunk.index,chunk.content)


        print('-' * 50)