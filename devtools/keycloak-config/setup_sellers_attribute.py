import httpx
import time
import json
import os

# --- Configurações ---
KEYCLOAK_URL = os.getenv("KEYCLOAK_URL", "http://localhost:8080")
REALM_NAME = os.getenv("REALM_NAME", "marketplace")
ADMIN_USER = os.getenv("KEYCLOAK_ADMIN_USER", "admin_marketplace")
ADMIN_PASSWORD = os.getenv("KEYCLOAK_ADMIN_PASSWORD", "senha123")
CLIENT_ID = os.getenv("KEYCLOAK_CLIENT_ID", "admin-cli")
MAX_RETRIES = 30
RETRY_DELAY = 5  # seconds


def wait_for_keycloak():
    """Aguarda o Keycloak estar online e saudável."""
    print("Aguardando o Keycloak iniciar...")
    for i in range(MAX_RETRIES):
        try:
            response = httpx.get(f"{KEYCLOAK_URL}/health", timeout=5)
            if response.status_code == 200 and response.json().get('status') == 'UP':
                print("\nKeycloak iniciado e saudável.")
                return True
        except httpx.RequestError:
            pass  # Ignora erros de conexão enquanto espera
        except json.JSONDecodeError:
            pass  # Ignora erros de JSON se a resposta não for JSON válida ainda
        print(".", end="", flush=True)
        time.sleep(RETRY_DELAY)
    print("\nErro: Keycloak não iniciou dentro do tempo esperado.")
    return False


def get_admin_token():
    """Obtém o token de acesso do admin."""
    print("Obtendo token de acesso do admin...")
    token_url = f"{KEYCLOAK_URL}/realms/{REALM_NAME}/protocol/openid-connect/token"
    data = {
        "grant_type": "password",
        "client_id": CLIENT_ID,
        "username": ADMIN_USER,
        "password": ADMIN_PASSWORD,
    }
    try:
        response = httpx.post(token_url, data=data, timeout=10)
        response.raise_for_status()  # Lança exceção para status 4xx/5xx
        token_data = response.json()
        access_token = token_data.get("access_token")
        if access_token:
            print("Token de acesso obtido com sucesso.")
            return access_token
        else:
            print(f"Erro: 'access_token' não encontrado na resposta. Resposta: {token_data}")
            return None
    except httpx.HTTPStatusError as e:
        print(f"Erro HTTP ao obter token: {e.response.status_code} - {e.response.text}")
        return None
    except httpx.RequestError as e:
        print(f"Erro de requisição ao obter token: {e}")
        return None


def create_realm(token):
    """Cria o realm 'varejo' se ele não existir."""
    print(f"Verificando e criando o realm '{REALM_NAME}'...")
    realm_url = f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}"
    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = httpx.get(realm_url, headers=headers, timeout=10)
        if response.status_code == 200:
            print(f"Realm '{REALM_NAME}' já existe.")
            return True
        elif response.status_code == 404:
            # Realm não encontrado, vamos criá-lo
            create_url = f"{KEYCLOAK_URL}/admin/realms"
            realm_config = {"realm": REALM_NAME, "enabled": True}
            create_response = httpx.post(create_url, headers=headers, json=realm_config, timeout=10)
            create_response.raise_for_status()
            print(f"Realm '{REALM_NAME}' criado com sucesso.")
            return True
        else:
            print(f"Erro inesperado ao verificar/criar realm: {response.status_code} - {response.text}")
            return False
    except httpx.HTTPStatusError as e:
        print(f"Erro HTTP ao criar realm: {e.response.status_code} - {e.response.text}")
        return False
    except httpx.RequestError as e:
        print(f"Erro de requisição ao criar realm: {e}")
        return False


def configure_user_profile(token):
    """Configura o User Profile para o atributo 'seller'."""
    attribute_sellers = "sellers"
    print(f"Configurando User Profile para o realm '{REALM_NAME}' para adicionar o atributo '${attribute_sellers}'...")
    user_profile_url = f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users/profile"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    try:
        # 1. Obter a configuração atual do User Profile
        response = httpx.get(user_profile_url, headers=headers, timeout=10)
        response.raise_for_status()
        profile_config = response.json()

        # 2. Garantir que 'attributes' exista e seja uma lista
        if 'attributes' not in profile_config or not isinstance(profile_config['attributes'], list):
            profile_config['attributes'] = []

        # 3. Verificar se o atributo 'seller' já existe
        seller_attribute_exists = any(attr.get('name') == attribute_sellers for attr in profile_config['attributes'])

        if not seller_attribute_exists:
            print(f"Adicionando atributo '{attribute_sellers}' ao User Profile...")
            new_attribute = {
                "name": attribute_sellers,
                "displayName": "${" + attribute_sellers + "}",
                "validations": {
                    "length": {
                        "min": 3,
                        "max": 255
                    }
                },
                "required": {
                    "roles": ["user"]
                },
                "permissions": {
                    "view": ["admin", "user"], 
                    "edit": ["admin"]
                },
                "multivalued": False,
                "annotations": {},
            }
            profile_config['attributes'].append(new_attribute)
        else:
            print(f"Atributo '${attribute_sellers}' já existe no User Profile.")

        # 4. Enviar a configuração atualizada
        put_response = httpx.put(user_profile_url, headers=headers, json=profile_config, timeout=10)
        put_response.raise_for_status()
        print(f"User Profile atualizado para o atributo '${attribute_sellers}'.")
        return True
    except httpx.HTTPStatusError as e:
        print(f"Erro HTTP ao configurar User Profile: {e.response.status_code} - {e.response.text}")
        return False
    except httpx.RequestError as e:
        print(f"Erro de requisição ao configurar User Profile: {e}")
        return False


def create_test_user(token):
    """Cria um usuário de teste com o atributo 'sellers'."""
    print(f"Criando usuário de teste 'testeuser' com o atributo 'seller' no realm '{REALM_NAME}'...")
    users_url = f"{KEYCLOAK_URL}/admin/realms/{REALM_NAME}/users"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    user_data = {
        "username": "testeuser",
        "enabled": True,
        "firstName": "Usuario",
        "lastName": "Teste",
        "email": "testeuser@example.com",
        "credentials": [{"type": "password", "value": "password", "temporary": False}],
        "attributes": {"sellers": ["luizalabs"]},
    }

    try:
        # Primeiro, verifica se o usuário já existe
        check_user_url = f"{users_url}?username=testeuser"
        check_response = httpx.get(check_user_url, headers=headers, timeout=10)
        check_response.raise_for_status()
        existing_users = check_response.json()

        if existing_users:
            print("Usuário 'testeuser' já existe. Pulando criação.")
            return True  # Considera sucesso se já existe
        else:
            # Usuário não existe, então cria
            response = httpx.post(users_url, headers=headers, json=user_data, timeout=10)
            response.raise_for_status()
            print(f"Usuário 'testeuser' criado no realm '{REALM_NAME}' com o atributo 'sellers: luizalabs'.")
            return True
    except httpx.HTTPStatusError as e:
        print(f"Erro HTTP ao criar usuário: {e.response.status_code} - {e.response.text}")
        return False
    except httpx.RequestError as e:
        print(f"Erro de requisição ao criar usuário: {e}")
        return False


if __name__ == "__main__":
    if not wait_for_keycloak():
        exit(1)

    admin_token = get_admin_token()
    if not admin_token:
        exit(1)

    if not create_realm(admin_token):
        exit(1)

    if not configure_user_profile(admin_token):
        exit(1)

    # XXX Descomente se desejar criar usuário teste
    #if not create_test_user(admin_token):
    #    exit(1)

    print("\n--- Configuração do Keycloak concluída! ---")
    print(f"Você pode acessar o Keycloak Admin Console em {KEYCLOAK_URL}/admin/master")
    print(f"Credenciais de admin: {ADMIN_USER}/{ADMIN_PASSWORD}")
    print(f"Após logar, selecione o realm '{REALM_NAME}' e verifique o usuário 'testeuser'.")
