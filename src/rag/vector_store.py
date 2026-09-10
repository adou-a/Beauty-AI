import json
from math import isfinite
from pathlib import Path
from src.rag.models import EmbeddedKnowledgeFact, KnowledgeFact, SearchResult, Source
from src.rag.similarity import cosine_similarity



class VectorStore:
    #初始化，定义保存的位置
    def __init__(self,storage_path: str = 'data/vector_store.json'):

        self.storage_path = Path(storage_path)
        self.items: list[EmbeddedKnowledgeFact] = []

    #添加一个嵌入后的知识事实
    def add(self, item: EmbeddedKnowledgeFact) -> None:
        self.items.append(item)

    #一次加入多个嵌入后的知识事实
    def add_many(self, items: list[EmbeddedKnowledgeFact]) -> None:
        self.items.extend(items)


    #返回保存的知识事实数量
    def count(self):
        return len(self.items)

    #清除内存
    def clear(self):

        self.items = []


    #把内存的数据加载到硬盘里
    def save(self):
        #创建目录
        self.storage_path.parent.mkdir(parents = True,exist_ok = True)
        data = []

        for embedded_fact in self.items:
            fact = embedded_fact.fact
            data.append(
                {
                    'fact': {
                        'id': fact.id,
                        'ingredient': fact.ingredient,
                        'category': fact.category,
                        'content': fact.content,
                        'source': [
                            {
                                'name': source.name,
                                'type': source.type,
                                'url': source.url
                            }
                            for source in fact.source
                        ]
                    },
                    'vector': embedded_fact.vector
                }
            )
            #写入文件
        self.storage_path.write_text(json.dumps(data,ensure_ascii = False,indent = 2),encoding = 'utf-8')

    #把硬盘的向量加载到数据中
    def load(self) -> list[EmbeddedKnowledgeFact]:
        #查看有没有json
        if not self.storage_path.exists():
            self.items = []
            return self.items
        #读取以后是dict形式
        raw_data = json.loads(self.storage_path.read_text(encoding='utf-8'))
        
        self.items = []
        for item in raw_data:
            fact_data = item['fact']
            sources = [
                Source(
                    name=source_data['name'],
                    type=source_data.get('type'),
                    url=source_data.get('url')
                )
                for source_data in fact_data['source']
            ]
            fact = KnowledgeFact(
                id=fact_data['id'],
                ingredient=fact_data['ingredient'],
                category=fact_data['category'],
                content=fact_data['content'],
                source=sources
            )
            self.items.append(
                EmbeddedKnowledgeFact(
                    fact=fact,
                    vector=item['vector']
                )
            )
        return self.items

    def load_required(self) -> list[EmbeddedKnowledgeFact]:
        if not self.storage_path.is_file():
            raise RuntimeError(
                f'Required vector store is not a regular file: {self.storage_path}'
            )

        try:
            items = self.load()
        except Exception as exc:
            raise RuntimeError(
                f'Required vector store could not be loaded: {self.storage_path}'
            ) from exc

        if not items:
            raise RuntimeError('Required vector store index is empty')

        return items


    def search(
        self,
        query_vector: list[float],
        top_k: int = 4,
        ingredients: set[str] | None = None,
    ) -> list[SearchResult]:
        #结果取的数量应该大于0
        if top_k <= 0:
            raise ValueError('top_k must be greater than 0')

        results = []

        #取items里面的嵌入知识事实
        for embedded_fact in self.items:
            if (
                ingredients is not None
                and embedded_fact.fact.ingredient not in ingredients
            ):
                continue

            score = cosine_similarity(query_vector, embedded_fact.vector)

            result = SearchResult(fact=embedded_fact.fact, score=score)
            results.append(result)
        #进行排序，按照关联分数排序
        results.sort(key=lambda result: result.score,reverse=True)

        return results[:top_k]
