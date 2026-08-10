from src.rag.vector_store import VectorStore

store = VectorStore()

items = store.load()


print('Loaded vector: ',store.count())


if items:
    first = items[0]
    print('source: ', first.source)

    print('index: ',first.index)
    print('content: ',first.content)
    print('vector length: ',len(first.vector))