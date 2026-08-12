class RAGError(Exception):
    pass


class RetrieverError(RAGError):
    pass


class VctorStoreError(RAGError):
    pass