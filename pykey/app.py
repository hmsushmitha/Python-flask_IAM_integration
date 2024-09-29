from flask import Flask, redirect, request, jsonify
from keycloak import KeycloakOpenID

app = Flask(__name__)

# Configure Keycloak
keycloak_openid = KeycloakOpenID(
    server_url="http://localhost:8081/auth",
    client_id="pykey",
    realm_name="master",
    client_secret_key="SVHPy7qX81JEU3f9BgDsUKhC36DeU4gV"
)

@app.route('/')
def home():
    return 'Hello, Minikube!'

@app.route('/protected')
def protected():
    token = request.args.get('token')
    if token:
        try:
            userinfo = keycloak_openid.userinfo(token)
            return f'Protected Content for user: {userinfo.get("preferred_username", "unknown")}'
        except Exception as e:
            return jsonify({"error": str(e)}), 401
    else:
        auth_url = keycloak_openid.auth_url(
            redirect_uri="http://localhost:5000",
            scope="openid",
            state="random_state_string"  # You should generate a unique state in production
        )
        return redirect(auth_url)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)