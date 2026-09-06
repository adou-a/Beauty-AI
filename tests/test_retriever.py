import pytest

from src.rag.models import EmbeddedKnowledgeFact, KnowledgeFact, Source
from src.rag.retriever import Retriever
from src.rag.vector_store import VectorStore


class QueryEmbeddingService:
    def __init__(self) -> None:
        self.queries: list[str] = []

    def embed_text(self, text: str) -> list[float]:
        self.queries.append(text)
        if "刺激" in text or "色素沉着" in text:
            return [0.0, 1.0]
        return [1.0, 0.0]


def make_fact(
    fact_id: str,
    ingredient: str,
    category: str,
    vector: list[float],
) -> EmbeddedKnowledgeFact:
    fact = KnowledgeFact(
        id=fact_id,
        ingredient=ingredient,
        category=category,
        content=f"Knowledge for {fact_id}",
        source=[Source(name="test-source")],
    )
    return EmbeddedKnowledgeFact(fact=fact, vector=vector)


def build_retriever(top_k: int = 3) -> tuple[Retriever, QueryEmbeddingService]:
    embedding = QueryEmbeddingService()
    store = VectorStore()
    store.add_many(
        [
            make_fact(
                "retinol_definition_001",
                "视黄醇(Retinol)",
                "definition",
                [0.6, 0.4],
            ),
            make_fact(
                "retinol_function_001",
                "视黄醇(Retinol)",
                "function",
                [0.9, 0.1],
            ),
            make_fact(
                "retinol_risk_001",
                "视黄醇(Retinol)",
                "risk",
                [0.0, 0.95],
            ),
            make_fact(
                "salicylic_acid_function_001",
                "水杨酸（Salicylic Acid）",
                "function",
                [1.0, 0.0],
            ),
            make_fact(
                "salicylic_acid_risk_001",
                "水杨酸（Salicylic Acid）",
                "risk",
                [0.0, 1.0],
            ),
            make_fact(
                "niacinamide_function_001",
                "烟酰胺（NIACINAMIDE）",
                "function",
                [0.95, 0.05],
            ),
            make_fact(
                "niacinamide_risk_001",
                "烟酰胺（NIACINAMIDE）",
                "risk",
                [0.1, 0.9],
            ),
            make_fact(
                "l_ascorbic_acid_definition_001",
                "L-抗坏血酸（L-Ascorbic Acid）",
                "definition",
                [0.7, 0.3],
            ),
            make_fact(
                "l_ascorbic_acid_function_001",
                "L-抗坏血酸（L-Ascorbic Acid）",
                "function",
                [0.8, 0.2],
            ),
            make_fact(
                "l_ascorbic_acid_risk_001",
                "L-抗坏血酸（L-Ascorbic Acid）",
                "risk",
                [0.05, 0.95],
            ),
            make_fact(
                "sodium_hyaluronate_function_001",
                "透明质酸钠（Sodium Hyaluronate）",
                "function",
                [1.0, 0.0],
            ),
        ]
    )
    return Retriever(embedding, store, top_k=top_k), embedding


@pytest.mark.parametrize(
    "query",
    ["视黄醇", "retinol", "RETINOL", "视黄醇有什么作用"],
)
def test_retinol_queries_only_return_retinol_facts(query: str):
    retriever, _ = build_retriever()

    facts = retriever.retriever(query)

    assert facts
    assert len(facts) == retriever.top_k
    assert {fact.ingredient for fact in facts} == {"视黄醇(Retinol)"}
    if "作用" in query:
        assert facts[0].id == "retinol_function_001"


@pytest.mark.parametrize(
    "query",
    ["视黄醇有什么作用", "retinol有什么作用", "RETINOL有什么作用"],
)
def test_detects_retinol_aliases_as_one_fixed_ingredient(query: str):
    retriever, _ = build_retriever()

    assert retriever._detect_ingredients(query) == ["视黄醇(Retinol)"]


def test_detects_multiple_ingredients_in_query_order():
    retriever, _ = build_retriever()

    assert retriever._detect_ingredients("烟酰胺和视黄醇哪个好") == [
        "烟酰胺（NIACINAMIDE）",
        "视黄醇(Retinol)",
    ]


def test_ingredient_groups_deduplicate_repeated_knowledge_facts():
    retriever, _ = build_retriever()

    groups = retriever._ingredient_groups()
    aliases_by_ingredient = dict(groups)

    assert len(groups) == 5
    assert [ingredient for ingredient, _ in groups].count(
        "视黄醇(Retinol)"
    ) == 1
    assert aliases_by_ingredient["视黄醇(Retinol)"] == {
        "视黄醇",
        "retinol",
    }


def test_salicylic_acid_query_only_returns_salicylic_acid_facts():
    retriever, _ = build_retriever()

    facts = retriever.retriever("水杨酸会刺激吗")

    assert facts
    assert {fact.ingredient for fact in facts} == {
        "水杨酸（Salicylic Acid）"
    }
    assert facts[0].id == "salicylic_acid_risk_001"


def test_niacinamide_query_only_returns_niacinamide_facts():
    retriever, _ = build_retriever()

    facts = retriever.retriever("烟酰胺有什么作用")

    assert facts
    assert {fact.ingredient for fact in facts} == {
        "烟酰胺（NIACINAMIDE）"
    }


def test_multi_ingredient_query_returns_evidence_for_each_ingredient():
    retriever, embedding = build_retriever()

    query = "烟酰胺和L-抗坏血酸有什么区别"

    facts = retriever.retriever(query)

    returned_ingredients = {fact.ingredient for fact in facts}
    assert "烟酰胺（NIACINAMIDE）" in returned_ingredients
    assert "L-抗坏血酸（L-Ascorbic Acid）" in returned_ingredients
    assert len(facts) > retriever.top_k
    assert embedding.queries == [query]


def test_query_without_ingredient_keeps_global_semantic_search():
    retriever, _ = build_retriever()

    facts = retriever.retriever("什么成分可以改善色素沉着")

    assert len(facts) == retriever.top_k
    assert len({fact.ingredient for fact in facts}) > 1


def test_english_ingredient_name_matching_is_case_insensitive():
    retriever, _ = build_retriever()

    facts = retriever.retriever("what does niacinamide do")

    assert facts
    assert {fact.ingredient for fact in facts} == {
        "烟酰胺（NIACINAMIDE）"
    }


def test_unlisted_alias_does_not_trigger_ingredient_filtering():
    retriever, _ = build_retriever()

    assert retriever._detect_ingredients("A醇有什么作用") == []
