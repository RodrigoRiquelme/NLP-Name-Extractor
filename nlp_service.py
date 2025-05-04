from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import spacy
from spacy.lang.es.stop_words import STOP_WORDS

nlp = spacy.load("es_core_news_md")

app = FastAPI(
    title="Item Name Extractor",
    description="Extracts a concise product type from Spanish product descriptions.",
    version="4.0.0"
)

UNITS = {"ml", "g", "kg", "l", "litros", "gramos", "cc", "cm", "un", "und"}

def is_meaningful(token):
    txt = token.text.lower()
    return (
        not token.is_punct and
        not token.like_num and
        txt not in UNITS
    )

class ItemRequest(BaseModel):
    text: str
    max_tokens: Optional[int] = 2

class ItemNameResponse(BaseModel):
    item_name: str

@app.post("/extract_item_name", response_model=ItemNameResponse)
def extract_item_name(req: ItemRequest):
    doc = nlp(req.text)
    product_tokens = []
    meaningful_count = 0

    for token in doc:
        if not is_meaningful(token):
            continue

        product_tokens.append(token)
        if token.text.lower() not in STOP_WORDS:
            meaningful_count += 1

        if meaningful_count == req.max_tokens:
            break

    # Fallback: get first N non-stopwords
    if not product_tokens:
        for token in doc:
            if token.text.lower() not in STOP_WORDS:
                product_tokens.append(token)
            if len(product_tokens) == req.max_tokens:
                break

    if not product_tokens:
        return {"item_name": "Desconocido"}

    return {
        "item_name": " ".join([t.text.capitalize() for t in product_tokens])
    }