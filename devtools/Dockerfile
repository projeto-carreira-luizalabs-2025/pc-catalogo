# Primeira etapa: instalar os pacotes do Python
# Montar a estrutura de arquivos da aplicação
FROM python:3.12-slim AS construtor

SHELL ["/bin/bash", "-c"]

WORKDIR /catalogo

COPY requirements ./requirements

RUN pip install --upgrade pip && pip install -r requirements/base.txt

# Instalar meus pacotes
RUN python -m venv venv && \
  .  venv/bin/activate && \
  pip install --upgrade pip && \
  pip install --no-cache-dir -r requirements/base.txt

# Imagem final a ser entregue / conterá a minha aplicação
FROM python:3.12-slim


ENV PYTHONPATH=/app
ENV PATH=/catalogo/venv/bin:$PATH

WORKDIR /app
COPY --from=construtor /catalogo/venv /catalogo/venv
COPY app /projeto/app
COPY requirements.txt /app

RUN python -m compileall app

COPY . .

EXPOSE 8000


CMD ["uvicorn", "app.api_main:app", "--host", "0.0.0.0", "--port", "8000"]

# Montagem Docker
# docker docker build -f ./devtools/Dockerfile -t catalogo:0.0.1 .
# Execução
# docker run --rm -e ENV=dev -p 8000:8000 catalogo:0.0.1

#Docker compose
#docker-compose -f docker-compose-catalogo.yml up --build

#sqa_4145de8c472e9aa81985dc4622eebdbf1f7498b3