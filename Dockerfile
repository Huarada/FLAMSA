FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PORT=8080 \
    HOME=/home/flamsa

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends poppler-utils \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 10001 flamsa \
    && useradd --uid 10001 --gid flamsa --create-home flamsa

COPY pyproject.toml README.md ./
COPY src/ ./src/
RUN python -m pip install ".[dashboard,rag,openai]"

COPY .streamlit/config.toml ./.streamlit/config.toml
COPY deploy/start_streamlit.py ./deploy/start_streamlit.py
COPY data/sources.json data/rag_corpus.json data/solutions_catalog.json ./data/
COPY data/curated/ ./data/curated/
COPY data/external/ ./data/external/
COPY data/rag_index/passages.json ./data/rag_index/passages.json
COPY knowledgeBase/ ./knowledgeBase/

# Source evidence stays read-only; only the derived passage index may be rebuilt.
RUN chmod -R a+rX src data knowledgeBase .streamlit \
    && chmod -R a-w knowledgeBase data/curated data/external \
    && chmod a-w data/sources.json data/rag_corpus.json data/solutions_catalog.json \
    && chown -R flamsa:flamsa data/rag_index

USER flamsa
EXPOSE 8080
CMD ["python", "deploy/start_streamlit.py"]
