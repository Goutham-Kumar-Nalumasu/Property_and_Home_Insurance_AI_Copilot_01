FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Expose ports: FastAPI (8000), Streamlit (8501), MCP server (5000)
EXPOSE 8000 8501 5000

# Start MCP server in background and then FastAPI + Streamlit
# For simplicity, we run all three in one container (development)
CMD qdrant --port=6333 & \
    python -m app.mcp_server & \
    uvicorn app.main:app --host 0.0.0.0 --port 8000 & \
    streamlit run app/frontend/streamlit_app.py --server.address 0.0.0.0 --server.port 8501