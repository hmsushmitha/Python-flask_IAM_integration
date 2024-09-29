from flask import Flask, request, redirect, jsonify
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

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if code:
        try:
            token = keycloak_openid.token(
                grant_type='authorization_code',
                code=code,
                redirect_uri="http://localhost:5000/oauth2/callback"
            )
            userinfo = keycloak_openid.userinfo(token['access_token'])
            return jsonify({
                "success": True,
                "message": "Login successful!",
                "user": userinfo
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 401
    else:
        return "No authorization code provided.", 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
