# Pokémon Search API

A small FastAPI backend for the PokéSearch frontend. It looks up a Pokémon by its English name or Pokédex number, retrieves the data from PokéAPI, and returns only the fields used by the frontend.

## Live service

- Render URL: <https://jack-li-backfrontend.onrender.com>
- Interactive API documentation: <https://jack-li-backfrontend.onrender.com/docs>
- Health check: <https://jack-li-backfrontend.onrender.com/>

The free Render instance may sleep when idle, so the first request after a period of inactivity can take longer to respond.

## API endpoint

### `GET /api/pokemon/{identifier}`

Looks up a Pokémon by English name or Pokédex number. Names are case-insensitive.

Example requests:

```text
GET https://jack-li-backfrontend.onrender.com/api/pokemon/pikachu
GET https://jack-li-backfrontend.onrender.com/api/pokemon/25
```

A successful response (`200 OK`) looks like:

```json
{
  "id": 25,
  "name": "pikachu",
  "types": ["electric"],
  "image": "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/25.png",
  "height": 4,
  "weight": 60
}
```

Height is returned in decimeters and weight in hectograms. The frontend converts these to meters and kilograms for display.

Errors use FastAPI's JSON format, for example:

```json
{
  "detail": "Pokemon 'unknown-name' not found. Please check the spelling or ID."
}
```

Common status codes are `404` when the Pokémon is not found, `504` when PokéAPI times out, and `502` when PokéAPI returns an unsuccessful response.

## How the frontend uses the backend

The frontend reads the backend base URL from `frontend/config.js` (or a URL saved in the browser's local storage). It sends a `GET` request to `/api/pokemon/{identifier}` when the user submits a name or number. On success it displays the name, number, types, image, height, and weight. It displays the response's `detail` message for API errors and gives a local validation message when the query is empty.

The deployed frontend should use this base URL:

```text
https://jack-li-backfrontend.onrender.com
```

## Run locally

Run these commands from the `backend` directory:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

On Windows PowerShell, activate the virtual environment with:

```powershell
.venv\Scripts\Activate.ps1
```

The local API runs at <http://127.0.0.1:8000>. Open <http://127.0.0.1:8000/docs> for the interactive API documentation, or try <http://127.0.0.1:8000/api/pokemon/pikachu>.

To point the frontend at the local backend, temporarily set `DEFAULT_API_URL` in `frontend/config.js` to `http://localhost:8000`. Set it back to the Render URL before deploying the frontend.

## Deploy on Render

This repository keeps the backend in the `backend/` directory. Configure the Render Web Service with:

- Root Directory: `backend`
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`

The service uses Python 3 and deploys from the `main` branch.

## Configuration and secrets

The backend reads `POKEAPI_BASE_URL` from the environment and defaults to `https://pokeapi.co/api/v2`. For local development, an optional `.env` file can define this setting. Do not commit `.env` files or credentials; `.env` is ignored by Git.

PokéAPI is a public API and does not require an API key. This project therefore does not need a secret key to make its Pokémon lookup requests.

## Dependencies

Dependencies are listed in `requirements.txt`: FastAPI, Uvicorn, HTTPX, python-dotenv, and Pydantic.
