import asyncio
import sys
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health():
    print("Testing GET / ...")
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    print("✓ Health check passed!")

def test_get_pokemon_by_name():
    print("Testing GET /api/pokemon/pikachu ...")
    response = client.get("/api/pokemon/pikachu")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "pikachu"
    assert data["id"] == 25
    assert "electric" in data["types"]
    assert data["image"] is not None
    print(f"✓ Pikachu fetched successfully: ID {data['id']}, Types {data['types']}, Image {data['image']}")

def test_get_pokemon_by_id():
    print("Testing GET /api/pokemon/1 ...")
    response = client.get("/api/pokemon/1")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "bulbasaur"
    assert data["id"] == 1
    assert "grass" in data["types"]
    print(f"✓ Pokemon #1 fetched successfully: Name {data['name']}, Types {data['types']}")

def test_pokemon_not_found():
    print("Testing GET /api/pokemon/invalid_pokemon_xyz ...")
    response = client.get("/api/pokemon/invalid_pokemon_xyz")
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    print(f"✓ 404 error handled correctly: {data['detail']}")

if __name__ == "__main__":
    test_health()
    test_get_pokemon_by_name()
    test_get_pokemon_by_id()
    test_pokemon_not_found()
    print("\n🎉 ALL TESTS PASSED SUCCESSFULLY!")
