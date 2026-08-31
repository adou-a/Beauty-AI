import json
from pathlib import Path

import pytest

from src.rag.loader import KnowledgeFactLoader
from src.rag.models import KnowledgeFact, Source


def make_fact(fact_id: str = 'retinol_definition_001') -> dict[str, object]:
    return {
        'id': fact_id,
        'ingredient': 'retinol',
        'category': 'definition',
        'content': 'Retinol is a vitamin A derivative.',
        'source': [
            {
                'name': 'AAD article',
                'type': 'AAD',
                'url': 'https://example.com/aad'
            }
        ]
    }


def write_fact(path: Path, fact: dict[str, object]) -> None:
    path.write_text(
        json.dumps(fact, ensure_ascii=False),
        encoding='utf-8'
    )


def test_load_directory_returns_knowledge_facts_in_stable_order(tmp_path: Path):
    write_fact(tmp_path / 'b.json', make_fact('retinol_risk_001'))
    write_fact(tmp_path / 'a.json', make_fact('retinol_definition_001'))

    facts = KnowledgeFactLoader().load_directory(str(tmp_path))

    assert all(isinstance(fact, KnowledgeFact) for fact in facts)
    assert [fact.id for fact in facts] == [
        'retinol_definition_001',
        'retinol_risk_001'
    ]
    assert isinstance(facts[0].source[0], Source)
    assert facts[0].source[0] == Source(
        name='AAD article',
        type='AAD',
        url='https://example.com/aad'
    )


def test_load_directory_preserves_multiple_source_order(tmp_path: Path):
    fact = make_fact()
    fact['source'] = [
        {'name': 'First source', 'type': 'research', 'url': 'https://first.test'},
        {'name': 'Second source', 'type': 'guidance', 'url': 'https://second.test'}
    ]
    write_fact(tmp_path / 'fact.json', fact)

    loaded = KnowledgeFactLoader().load_directory(str(tmp_path))[0]

    assert [source.name for source in loaded.source] == [
        'First source',
        'Second source'
    ]


def test_load_directory_accepts_missing_and_null_optional_source_fields(
    tmp_path: Path
):
    fact = make_fact()
    fact['source'] = [
        {'name': 'Missing optional fields'},
        {'name': 'Null optional fields', 'type': None, 'url': None}
    ]
    write_fact(tmp_path / 'fact.json', fact)

    loaded = KnowledgeFactLoader().load_directory(str(tmp_path))[0]

    assert loaded.source == [
        Source(name='Missing optional fields'),
        Source(name='Null optional fields', type=None, url=None)
    ]


def test_load_directory_rejects_empty_directory(tmp_path: Path):
    with pytest.raises(ValueError, match='contains no JSON files'):
        KnowledgeFactLoader().load_directory(str(tmp_path))


def test_load_directory_rejects_broken_json(tmp_path: Path):
    (tmp_path / 'broken.json').write_text('{"id":', encoding='utf-8')

    with pytest.raises(json.JSONDecodeError):
        KnowledgeFactLoader().load_directory(str(tmp_path))


def test_load_directory_rejects_missing_required_field(tmp_path: Path):
    fact = make_fact()
    del fact['category']
    write_fact(tmp_path / 'missing.json', fact)

    with pytest.raises(ValueError, match=r'missing\.json.*category'):
        KnowledgeFactLoader().load_directory(str(tmp_path))


def test_load_directory_rejects_invalid_source_type(tmp_path: Path):
    fact = make_fact()
    fact['source'] = 'AAD'
    write_fact(tmp_path / 'invalid_source.json', fact)

    with pytest.raises(ValueError, match='non-empty list'):
        KnowledgeFactLoader().load_directory(str(tmp_path))


def test_load_directory_rejects_empty_source_list(tmp_path: Path):
    fact = make_fact()
    fact['source'] = []
    write_fact(tmp_path / 'empty_source.json', fact)

    with pytest.raises(ValueError, match='non-empty list'):
        KnowledgeFactLoader().load_directory(str(tmp_path))


@pytest.mark.parametrize('source_item', ['AAD', 123])
def test_load_directory_rejects_non_object_source_items(
    tmp_path: Path,
    source_item: object
):
    fact = make_fact()
    fact['source'] = [source_item]
    write_fact(tmp_path / 'invalid_item.json', fact)

    with pytest.raises(ValueError, match='must be an object'):
        KnowledgeFactLoader().load_directory(str(tmp_path))


def test_load_directory_rejects_source_without_name(tmp_path: Path):
    fact = make_fact()
    fact['source'] = [{'type': 'AAD'}]
    write_fact(tmp_path / 'missing_name.json', fact)

    with pytest.raises(ValueError, match="missing required field 'name'"):
        KnowledgeFactLoader().load_directory(str(tmp_path))


@pytest.mark.parametrize('name', ['', '   ', 123])
def test_load_directory_rejects_invalid_source_name(tmp_path: Path, name: object):
    fact = make_fact()
    fact['source'] = [{'name': name}]
    write_fact(tmp_path / 'invalid_name.json', fact)

    with pytest.raises(ValueError, match="source field 'name'"):
        KnowledgeFactLoader().load_directory(str(tmp_path))


@pytest.mark.parametrize(
    ('field_name', 'value'),
    [
        ('type', 123),
        ('url', 123),
        ('type', '   '),
        ('url', '   ')
    ]
)
def test_load_directory_rejects_invalid_optional_source_fields(
    tmp_path: Path,
    field_name: str,
    value: object
):
    fact = make_fact()
    fact['source'] = [{'name': 'Source', field_name: value}]
    write_fact(tmp_path / 'invalid_optional.json', fact)

    with pytest.raises(ValueError, match=field_name):
        KnowledgeFactLoader().load_directory(str(tmp_path))


def test_load_directory_rejects_duplicate_ids(tmp_path: Path):
    write_fact(tmp_path / 'first.json', make_fact())
    write_fact(tmp_path / 'second.json', make_fact())

    with pytest.raises(ValueError, match='Duplicate KnowledgeFact id'):
        KnowledgeFactLoader().load_directory(str(tmp_path))


@pytest.mark.parametrize('field_name', ['id', 'ingredient', 'category', 'content'])
def test_load_directory_rejects_blank_string_fields(
    tmp_path: Path,
    field_name: str
):
    fact = make_fact()
    fact[field_name] = '   '
    write_fact(tmp_path / 'blank.json', fact)

    with pytest.raises(ValueError, match=field_name):
        KnowledgeFactLoader().load_directory(str(tmp_path))
