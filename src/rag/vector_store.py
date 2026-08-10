import json
from pathlib import Path
from src.rag.models import EmbeddedChunk


class VectorStore:
    #初始化，定义保存的位置
    def __init__(self,storage_path: str = 'data/vector_store.json'):

        self.storage_path = Path(storage_path)
        self.items: list[EmbeddedChunk] = []

    #添加一个chunk
    def add(self,chunk: EmbeddedChunk) -> None:
        self.items.append(chunk)
    #一次加入多个chunk
    def add_many(self,chunks: list[EmbeddedChunk]):
        self.items.extend(chunks)


    #返回保留chunk的数量
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

        for chunk in self.items:
            data.append(
                {
                    'content': chunk.content,
                    'source': chunk.source,
                    'index': chunk.index,
                    'vector': chunk.vector
                }
            )
            #写入文件
        self.storage_path.write_text(json.dumps(data,ensure_ascii = False,indent = 2),encoding = 'utf-8')

    #把硬盘的向量加载到数据中
    def load(self) -> list[EmbeddedChunk]:
        #查看有没有json
        if not self.storage_path.exists():
            self.items = []
            return self.items
        #读取以后是dict形式
        raw_data = json.loads(self.storage_path.read_text(encoding='utf-8'))
        
        self.items = [EmbeddedChunk(
            content=item['content'],
            source=item['source'],
            index = item['index'],
            vector=item['vector']
        )
        for item in raw_data
        ]
        return self.items