from src.rag.models import Document,Chunk


class TextChunker:

    def __init__(self,chunk_size: int = 500, overlap: int = 100):
        self.chunk_size = chunk_size
        self.overlap = overlap
    #输入Document 输出Chunk列表
    def split(self,document: Document) -> list[Chunk]:
        #创建空列表
        chunks = []
        #表示从文本第0个字符开始
        start = 0
        #chunk编号
        index = 0



        text = document.content
        if not (0 < self.overlap < self.chunk_size):
            raise ValueError('overlap must be smaller than chunk_size')
       
        #只要有文字就切
        while start < len(text):
            #计算结束的位置
            end = start + self.chunk_size
            #切字符串
            content = text[start: end]

            chunk  = Chunk(content= content,source= document.source,index= index)
            chunks.append(chunk)
            #移动开始的位置
            start += (self.chunk_size - self.overlap)

            index += 1

        return chunks