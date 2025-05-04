# 🧠 Item Name NLP Extractor (FastAPI + spaCy)

This is a lightweight NLP microservice that extracts a concise **item name** (product type) from long Spanish product titles using `spaCy` and `FastAPI`.

It’s designed to support **search engine ingestion** pipelines (e.g., Apache Solr with TF-IDF), where long product titles need to be normalized into short searchable item types like:

- `"Aceite vegetal botella, 900 ml"` → `Aceite Vegetal`
- `"Chocolate de leche barra, 150 g"` → `Chocolate de Leche`

---

## 🚀 Features

- Built with **FastAPI** for speed and interactive Swagger docs.
- Uses **spaCy** with the `es_core_news_md` model.
- Smart token selection that skips stopwords and units (e.g. "ml", "kg").
- Supports configurable extraction length via `max_tokens` parameter.
- Dockerized for easy deployment.

---

## 🔧 Requirements

- Python 3.10+
- Docker (optional)

---

## 🛠 Usage

### ▶️ Run locally (without Docker)

```bash
pip install -r requirements.txt
uvicorn nlp_service:app --reload
```


### 🐳 Run with Docker
```bash
docker build -t item-name-nlp .
docker run -p 8000:8000 item-name-nlp
```

### 📥  API Example
POST /extract_item_name
```bash
{
  "text": "Leche en polvo semidescremada instantánea, 760 g",
  "max_tokens": 2
}
```
Response
```bash
{
  "item_name": "Leche en Polvo"
}
```
**max_tokens** is optional, determines how many meaningful tokens (excluding stopwords and units like "ml", "kg") will be extracted from the input to form the item_name, by default is 2.

### 🔍 Why This Exists
In TF-IDF-based search engines like Solr, long product titles can dilute search relevance. This service extracts a clean, normalized item_name field to improve indexing and ranking precision.


### 📄 License
MIT – feel free to fork, use, and contribute.