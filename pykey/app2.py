from flask import Flask, redirect, request
from keycloak import KeycloakOpenID

app = Flask(__name__)

# Configure Keycloak
keycloak_openid = KeycloakOpenID(
    server_url="http://localhost:8081/auth/",
    client_id="pykey",
    realm_name="master",
    client_secret_key="SVHPy7qX81JEU3f9BgDsUKhC36DeU4gV"
)

@app.route('/')
def home():
    return 'Hello, Minikube!'

@app.route('/login')
def login():
    auth_url = keycloak_openid.auth_url(
        redirect_uri="http://localhost:5000/oauth2/callback",
        scope="openid",
        state="random_state_string"  # Generate a unique state for CSRF protection
    )
    return redirect(auth_url)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
