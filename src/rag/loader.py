import json
from pathlib import Path
from src.rag.models import Document, KnowledgeFact, Source

#找所有符合的文件,确定来源
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


class KnowledgeFactLoader:
    REQUIRED_FIELDS = {
        'id',
        'ingredient',
        'category',
        'content',
        'source'
    }
    STRING_FIELDS = ('id', 'ingredient', 'category', 'content')

    def load_directory(self, directory: str) -> list[KnowledgeFact]:
        path = Path(directory)

        if not path.exists():
            raise FileNotFoundError(f'Knowledge fact directory does not exist: {path}')
        if not path.is_dir():
            raise NotADirectoryError(f'Knowledge fact path is not a directory: {path}')

        file_paths = sorted(path.glob('*.json'))
        if not file_paths:
            raise ValueError(f'Knowledge fact directory contains no JSON files: {path}')

        facts = []
        id_sources: dict[str, Path] = {}

        for file_path in file_paths:
            data = json.loads(file_path.read_text(encoding='utf-8'))
            fact = self._build_fact(data, file_path)

            if fact.id in id_sources:
                raise ValueError(
                    f'Duplicate KnowledgeFact id {fact.id!r} in {file_path}; '
                    f'first defined in {id_sources[fact.id]}'
                )

            id_sources[fact.id] = file_path
            facts.append(fact)

        return facts

    def _build_fact(self, data: object, file_path: Path) -> KnowledgeFact:
        if not isinstance(data, dict):
            raise ValueError(f'Knowledge fact JSON must be an object: {file_path}')

        missing_fields = self.REQUIRED_FIELDS - data.keys()
        if missing_fields:
            missing = ', '.join(sorted(missing_fields))
            raise ValueError(
                f'Knowledge fact file {file_path} is missing required fields: {missing}'
            )

        for field_name in self.STRING_FIELDS:
            value = data[field_name]
            if not isinstance(value, str):
                raise ValueError(
                    f'Knowledge fact field {field_name!r} must be a string in {file_path}'
                )
            if not value.strip():
                raise ValueError(
                    f'Knowledge fact field {field_name!r} cannot be empty in {file_path}'
                )

        sources = self._build_sources(data['source'], file_path)

        return KnowledgeFact(
            id=data['id'],
            ingredient=data['ingredient'],
            category=data['category'],
            content=data['content'],
            source=sources
        )

    def _build_sources(self, data: object, file_path: Path) -> list[Source]:
        if not isinstance(data, list) or not data:
            raise ValueError(
                f"Knowledge fact field 'source' must be a non-empty list in {file_path}"
            )

        sources = []
        for index, item in enumerate(data):
            if not isinstance(item, dict):
                raise ValueError(
                    f'Knowledge fact source item {index} must be an object in {file_path}'
                )

            if 'name' not in item:
                raise ValueError(
                    f"Knowledge fact source item {index} is missing required field 'name' "
                    f'in {file_path}'
                )

            name = item['name']
            if not isinstance(name, str):
                raise ValueError(
                    f"Knowledge fact source field 'name' must be a string in {file_path}"
                )
            if not name.strip():
                raise ValueError(
                    f"Knowledge fact source field 'name' cannot be empty in {file_path}"
                )

            optional_values = {}
            for field_name in ('type', 'url'):
                value = item.get(field_name)
                if value is not None and not isinstance(value, str):
                    raise ValueError(
                        f'Knowledge fact source field {field_name!r} must be a string '
                        f'or null in {file_path}'
                    )
                if isinstance(value, str) and not value.strip():
                    raise ValueError(
                        f'Knowledge fact source field {field_name!r} cannot be empty '
                        f'in {file_path}'
                    )
                optional_values[field_name] = value

            sources.append(
                Source(
                    name=name,
                    type=optional_values['type'],
                    url=optional_values['url']
                )
            )

        return sources
