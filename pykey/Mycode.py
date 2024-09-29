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
    code = request.args.get('code')

    if code:
        try:
            # Exchange the authorization code for an access token
            token_response = keycloak_openid.token(
                grant_type='authorization_code',
                code=code,
                redirect_uri="http://localhost:5000"
            )
            access_token = token_response['access_token']
            
            # Fetch user information using the access token
            userinfo = keycloak_openid.userinfo(access_token)
            
            # Display access token and user information on the home page
            return jsonify({
                'message': 'Authentication successful!',
                'access_token': access_token,
                'user_info': userinfo
            })
        except Exception as e:
            return jsonify({"error": str(e)}), 401
    else:
        return 'Hello, Minikube!'

@app.route('/protected')
def protected():
    # Redirect to Keycloak for authentication
    auth_url = keycloak_openid.auth_url(
        redirect_uri="http://localhost:5000",
        scope="openid",
        state="random_state_string"  # You should generate a unique state in production
    )
    return redirect(auth_url)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
