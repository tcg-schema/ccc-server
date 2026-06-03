FROM python:3.10-slim AS service

# WeasyPrint runtime libraries (Pango / Cairo / GDK-Pixbuf) for PDF rendering.
RUN apt-get update && apt-get install -y --no-install-recommends \
        libpango-1.0-0 libpangocairo-1.0-0 libcairo2 libgdk-pixbuf-2.0-0 \
        libffi-dev shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

RUN python3 -m venv /venv
ENV PATH="/venv/bin:$PATH"
RUN pip install --upgrade pip

COPY . .
RUN pip install --no-cache-dir .

ENV PYTHONPATH=/usr/src/app/src
EXPOSE 8080
CMD ["uvicorn", "openapi_server.main:app", "--host", "0.0.0.0", "--port", "8080"]
