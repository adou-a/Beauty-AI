from pathlib import Path
from src.rag.models import Document

#找所有符合的文件
class DocumentLoader:

    def load_directory(self,directory:str) -> list[Document]:
        #创造一个空列表来放读取出来的文档
        documents = []
        #转换路径，
        path = Path(directory)
        #历经所有的markdown文件
        for file_path in path.glob('*.md'):
            #读取文件内容
            content = file_path.read_text(encoding= 'utf-8')
            #判断空文件
            if not content.strip():
                continue
            #创建Document

            document = Document(content = content,source=file_path.name)
            documents.append(document)
        return documents
            