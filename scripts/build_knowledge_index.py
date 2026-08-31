import argparse
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def main() -> None:
    parser = argparse.ArgumentParser(
        description='Build the Beauty-AI KnowledgeFact vector index.'
    )
    parser.add_argument(
        '--knowledge-dir',
        default='data/knowledge',
        help='Directory containing KnowledgeFact JSON files (default: data/knowledge)'
    )
    args = parser.parse_args()

    from src.rag.embedding import EmbeddingService
    from src.rag.indexer import KnowledgeIndexer
    from src.rag.loader import KnowledgeFactLoader
    from src.rag.vector_store import VectorStore

    loader = KnowledgeFactLoader()
    embedding_service = EmbeddingService()
    vector_store = VectorStore()
    indexer = KnowledgeIndexer(
        embedding_service=embedding_service,
        vector_store=vector_store
    )

    facts = loader.load_directory(args.knowledge_dir)
    count = indexer.build(facts)

    print(f'Knowledge index built successfully: {count} facts')


if __name__ == '__main__':
    main()
