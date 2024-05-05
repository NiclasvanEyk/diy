from fastapi.testclient import TestClient

from weather.http import app


def test_cities_with_numbers_get_rejected() -> None:
    client = TestClient(app)
    response = client.get("/current/imaginary-city-123")
    assert response.json() == {
        "error": "The city contains digits. This must not happen!"
    }


def test_cities_with_numbers_are_valid() -> None:
    client = TestClient(app)
    response = client.get("/current/imaginary-city")

    temperature = response.json()["temperature"]
    assert isinstance(temperature, float)
