from src.rag.similarity import cosine_similarity
import pytest

def test_same_vector_similarity():

    vector = [1.0, 2.0, 3.0]

    score = cosine_similarity(vector,vector)

    assert abs(score - 1.0) < 0.000001


def test_opposite_vector_similarity():

    vector_a = [1.0, 0.0]
    vector_b = [-1.0,0.0]

    score = cosine_similarity(vector_a = vector_a,vector_b = vector_b)
    assert abs(score + 1.0) < 0.000001

def test_different_dimensions_raise_erroe():

    with pytest.raises(ValueError):
        cosine_similarity([1.0, 2.0],
                          [1.0,2.0,3.0])