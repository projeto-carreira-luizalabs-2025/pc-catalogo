URL_MONGO_MIGRATION_TEST = "mongodb://admin:admin@localhost:27018/test_db?authSource=admin"
APP_DIR=app

# Criar o diretório venv
build-venv:
	python3.12 -m venv venv

# Instalar os pacotes
requirements-test:
	pip install --upgrade pip
	pip install -r requirements/test.txt
	

# Verificar o código
check-lint:
	isort -c ${APP_DIR} ${ROOT_TESTS_DIR}
	bandit -c pyproject.toml -r -f custom ${APP_DIR} ${ROOT_TESTS_DIR}
	black --check ${APP_DIR} ${ROOT_TESTS_DIR}
	flake8 --max-line-length=120 ${APP_DIR} ${ROOT_TESTS_DIR}
	mypy ${APP_DIR} ${ROOT_TESTS_DIR}

#Carregar as variáveis de ambiente
load-env:
	@./devtools/scripts/push-env "devtools/dotenv.$(env)"

# Carregar a variável de testes
load-test-env:
	@env=test make $(MAKE_ARGS) load-env

# Subir o docker (Mongo + API Catalogo) para os testes
docker-tests-up:
	docker-compose -f devtools/docker-compose-tests.yml up --build

# Descer e remover o docker dos testes
docker-tests-down:
	docker-compose -f devtools/docker-compose-tests.yml down

# Subir o docker (Keycloak) para os testes 
docker-tests-keycloak-up:
	docker-compose -f devtools/docker-compose-keycloak.yml up --build

# Descer e remover o docker do Keycloak
docker-tests-keycloak-down:
	docker-compose -f devtools/docker-compose-keycloak.yml down
	
# Realizar a migração do banco de dados
migration:
	mongodb-migrate --url "$(URL_MONGO_MIGRATION_TEST)"

# Testar fazendo a cobertura do código
coverage:
	pytest --cov=${APP_DIR} --cov-report=term-missing --cov-report=xml ${ROOT_TESTS_DIR} --cov-fail-under=90 --durations=5


