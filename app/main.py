from fastapi import FastAPI, Query
from . import crud
from .models import SearchResponse

app = FastAPI(title="Pharmacy Search API")

@app.get("/search/prefix", response_model=SearchResponse)
def search_prefix(q: str = Query(..., min_length=1), limit: int = 20):
    return {"results": crud.q_prefix(q, limit)}

@app.get("/search/substring", response_model=SearchResponse)
def search_substring(q: str = Query(..., min_length=1), limit: int = 20):
    return {"results": crud.q_substring(q, limit)}

@app.get("/search/fulltext", response_model=SearchResponse)
def search_fulltext(q: str = Query(..., min_length=1), limit: int = 20):
    return {"results": crud.q_fulltext(q, limit)}

@app.get("/search/fuzzy", response_model=SearchResponse)
def search_fuzzy(q: str = Query(..., min_length=1), limit: int = 20):
    return {"results": crud.q_fuzzy(q, limit)}
