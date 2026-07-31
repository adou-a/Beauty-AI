from fastapi.testclient import TestClient
from src.api.main import app
from src.api.dependencies import get_ingredient_service
from src.exceptions.ingredient_exception import IngredientDataError

client = TestClient(app)

def test_home():
    response = client.get('/')
    assert response.status_code == 200


def test_get_ingredient():
    response = client.get('/ingredients/烟酰胺')
    assert response.status_code == 200
    data = response.json()
    assert data['chinese_name'] == '烟酰胺'

def test_not_found():
    response = client.get('/ingredients/不存在')
    assert response.status_code == 404

class FakeService:
    def find_ingredient(self,name):
        raise IngredientDataError()


def override_service():
    return FakeService()
def test_server_error():
    app.dependency_overrides[get_ingredient_service] = override_service


    response = client.get('/ingredients/烟酰胺')
    assert response.status_code == 500
    app.dependency_overrides.clear()