import re

from src.rag.embedding import EmbeddingService
from src.rag.vector_store import VectorStore
from src.rag.models import KnowledgeFact
from src.utils.logger import get_logger
from src.exceptions.rag_exception import RetrieverError
logger = get_logger(__name__)


class Retriever:

    def __init__(self,embedding_service: EmbeddingService,vector_store: VectorStore,top_k: int = 4):

        if top_k <= 0:
            raise ValueError('top_k must be greater than 0')

        self.embedding_service = embedding_service
        self.vector_store = vector_store
        self.top_k = top_k



    def retriever(self,query: str ) -> list[KnowledgeFact]:
        if not query.strip():
            raise ValueError('Query cannot be empty')
        logger.info('Retriever knowledge for query: %s',query)
        try:
            query_vector = self.embedding_service.embed_text(query)
            matched_ingredients = self._detect_ingredients(query)

            if not matched_ingredients:
                search_results = self.vector_store.search(
                    query_vector=query_vector,
                    top_k=self.top_k,
                )
            else:
                search_results = []
                for ingredient in matched_ingredients:
                    search_results.extend(
                        self.vector_store.search(
                            query_vector=query_vector,
                            top_k=self.top_k,
                            ingredients={ingredient},
                        )
                    )

            for result in search_results:
                logger.info(
                    "Retrieval score: id=%s ingredient=%s category=%s "
                    "similarity=%.4f",
                    result.fact.id,
                    result.fact.ingredient,
                    result.fact.category,
                    result.score
                )
            facts = [result.fact for result in search_results]
            logger.info('Retrieved %s knowledge facts',len(facts))

            return facts

        except Exception as exc:
            raise RetrieverError('Knowledge retrieve failed') from exc

    def _detect_ingredients(self, query: str) -> list[str]:
        #把问题单词全部小写
        normalized_query = query.casefold()
        #创建一个matches列表，格式是一个list
        matches: list[tuple[int, str]] = []

        for ingredient, names in self._ingredient_groups():
            positions = [
                #找到成分的位置
                normalized_query.find(name)
                for name in names
                if name and name in normalized_query
            ]
            if positions:
                #取这个成分最早出现的位置
                matches.append((min(positions), ingredient))
        #对 matches 里的每一个 tuple，都取它第 0 个元素作为排序依据。
        matches.sort(key=lambda match: match[0])
        return [ingredient for _, ingredient in matches]

    def _ingredient_groups(self) -> list[tuple[str, set[str]]]:
        #创建一个groups的list
        groups: list[tuple[str, set[str]]] = []
        seen_ingredients: set[str] = set()
        #对于存在在vector_store.load以后的数据
        for embedded_fact in self.vector_store.items:
            #取其中fact中的ingredient
            ingredient = embedded_fact.fact.ingredient
            if ingredient in seen_ingredients:
                continue

            seen_ingredients.add(ingredient)
            #把成分做切开和小写处理
            names = self._extract_ingredient_names(ingredient)
            groups.append((ingredient, names))

        return groups
    #工具函数只需要ingredient
    @staticmethod
    def _extract_ingredient_names(ingredient: str) -> set[str]:
        #集合推导式 result= set()
        #返回result
        return {
            #除去name前后空格和全部转化成小写然后加入result
            name.strip().casefold()
            #当name中有这些符号就切开
            for name in re.split(r'[()/（）／]+', ingredient)
            #如果name不为空
            if name.strip()
        }
