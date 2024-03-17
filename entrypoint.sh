#!/bin/bash
dockerize -wait tcp://qdrant:6333 -timeout 60s
python /app/llm_loading.py
exec "$@"
