from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
import spacy
from spacy.lang.es.stop_words import STOP_WORDS
from nltk.stem.snowball import SnowballStemmer

nlp = spacy.load("es_core_news_md")
spanish_stemmer = SnowballStemmer('spanish')

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
    use_lemmatization: Optional[bool] = False
    use_stemming: Optional[bool] = False

class ItemNameResponse(BaseModel):
    item_name: str

@app.post("/extract_item_name", response_model=ItemNameResponse)
def extract_item_name(req: ItemRequest):
    doc = nlp(req.text)
    product_tokens = []
    meaningful_count = 0

    # Main loop: Process tokens, apply transformations, and check for meaningfulness and stop words
    for token in doc:
        # is_meaningful checks token attributes (punct, num, units based on token.text)
        if not is_meaningful(token):
            continue

        token_representation: str
        if req.use_stemming:
            token_representation = spanish_stemmer.stem(token.text)
        elif req.use_lemmatization:
            token_representation = token.lemma_
        else:
            token_representation = token.text
        
        # Only consider non-stopwords for product_tokens and meaningful_count
        if token_representation.lower() not in STOP_WORDS:
            product_tokens.append(token_representation)
            meaningful_count += 1
        
        if meaningful_count == req.max_tokens:
            break
    
    # Fallback: If no "meaningful non-stopwords" were found, 
    # get the first N non-stopwords, applying transformations.
    # This part activates if the main loop didn't find enough tokens 
    # that are both "meaningful" (by is_meaningful) AND non-stopwords.
    # The original fallback was: if not product_tokens (after the first loop, which stored full tokens)
    # then iterate again and just collect tokens if not stop words.
    # The current product_tokens can be empty if all meaningful tokens were stopwords.
    # Or it can be empty if no tokens were meaningful at all.
    
    # If after the first pass, product_tokens (which now contains only meaningful non-stopwords) 
    # is still short of req.max_tokens, OR if it's empty, we might need a broader fallback.
    # The original code had a simple "if not product_tokens:" check which implies the first loop yielded nothing.
    # Let's stick to the spirit of the original fallback: if the first loop resulted in an empty product_tokens list.
    if not product_tokens:
        # This fallback loop does not check is_meaningful. It just finds the first N non-stopwords.
        fallback_product_tokens = []
        for token in doc: # Iterate through the original document again
            token_representation: str
            if req.use_stemming:
                token_representation = spanish_stemmer.stem(token.text)
            elif req.use_lemmatization:
                token_representation = token.lemma_
            else:
                token_representation = token.text

            if token_representation.lower() not in STOP_WORDS:
                fallback_product_tokens.append(token_representation)
            if len(fallback_product_tokens) == req.max_tokens:
                break
        product_tokens = fallback_product_tokens # Assign to product_tokens

    if not product_tokens:
        return {"item_name": "Desconocido"}

    return {
        "item_name": " ".join([text.capitalize() for text in product_tokens])
    }