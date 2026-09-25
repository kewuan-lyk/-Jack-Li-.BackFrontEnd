import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

POKEAPI_BASE_URL = os.getenv("POKEAPI_BASE_URL", "https://pokeapi.co/api/v2")
API_SECRET_KEY = os.getenv("API_SECRET_KEY")

app = FastAPI(
    title="Pokemon Search API",
    description="Backend API for searching Pokemon info from PokéAPI",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PokemonResponse(BaseModel):
    id: int
    name: str
    types: List[str]
    image: Optional[str] = None
    height: int
    weight: int


class ErrorResponse(BaseModel):
    detail: str


@app.get("/")
def read_root():
    return {
        "status": "healthy",
        "message": "Pokemon Search Engine Backend API is running",
        "endpoints": {
            "search_pokemon": "/api/pokemon/{name_or_id}"
        }
    }


@app.get(
    "/api/pokemon/{identifier}",
    response_model=PokemonResponse,
    responses={
        404: {"model": ErrorResponse, "description": "Pokemon not found"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
        502: {"model": ErrorResponse, "description": "Bad gateway / External API failure"}
    }
)
async def get_pokemon(identifier: str):
    """
    Fetch Pokemon details by name or pokedex ID.
    - **identifier**: Pokemon English name (case insensitive) or Pokedex ID (e.g. 'pikachu' or '25')
    """
    query = identifier.strip().lower()
    if not query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pokemon name or ID cannot be empty"
        )

    target_url = f"{POKEAPI_BASE_URL.rstrip('/')}/pokemon/{query}"

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(target_url)

            if response.status_code == 404:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Pokemon '{identifier}' not found. Please check the spelling or ID."
                )
            
            response.raise_for_status()
            data = response.json()

            # Extract types
            types = [t["type"]["name"] for t in data.get("types", [])]

            # Extract image (prefer official-artwork, fallback to default sprite)
            sprites = data.get("sprites", {})
            official_artwork = sprites.get("other", {}).get("official-artwork", {}).get("front_default")
            default_sprite = sprites.get("front_default")
            image_url = official_artwork or default_sprite

            return PokemonResponse(
                id=data["id"],
                name=data["name"],
                types=types,
                image=image_url,
                height=data.get("height", 0),
                weight=data.get("weight", 0)
            )

    except HTTPException:
        # Re-raise explicit HTTPExceptions (like 404 or 400)
        raise
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Request to external PokéAPI timed out. Please try again later."
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"External PokéAPI error: {e.response.status_code}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )
