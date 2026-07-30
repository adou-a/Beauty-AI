from src.config.settings import APP_ENV


def test_app_environment():

    assert APP_ENV == "development"