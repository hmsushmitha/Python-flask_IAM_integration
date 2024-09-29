from flask import Flask, redirect, request, render_template_string
from keycloak import KeycloakOpenID
import requests

app = Flask(__name__)

# URL to the OpenID Connect configuration endpoint
well_known_url = "http://keycloak.default.svc.cluster.local:8080/realms/master/.well-known/openid-configuration"

# Fetch OpenID configuration
def fetch_openid_config(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        raise RuntimeError(f"Failed to fetch OpenID configuration: {e}")

# Extract the OpenID configuration
openid_config = fetch_openid_config(well_known_url)
authorization_endpoint = openid_config.get('authorization_endpoint')
token_endpoint = openid_config.get('token_endpoint')
userinfo_endpoint = openid_config.get('userinfo_endpoint')

# Configure Keycloak
keycloak_openid = KeycloakOpenID(
    server_url=None,  # Not used directly since we're setting endpoints manually
    client_id="pykey",
    realm_name="master",
    client_secret_key="SVHPy7qX81JEU3f9BgDsUKhC36DeU4gV",
    authorization_endpoint=authorization_endpoint,
    token_endpoint=token_endpoint,
    userinfo_endpoint=userinfo_endpoint
)

# HTML Template with Enhanced UI
template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Keycloak Authentication</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
            color: #333;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            flex-direction: column;
        }
        .container {
            background-color: #fff;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            padding: 20px;
            width: 80%;
            max-width: 600px;
        }
        h1 {
            color: #4CAF50;
        }
        pre {
            background-color: #f4f4f4;
            padding: 10px;
            border-radius: 5px;
            overflow-x: auto;
        }
        .btn {
            display: inline-block;
            padding: 10px 20px;
            margin-top: 20px;
            font-size: 16px;
            color: #fff;
            background-color: #4CAF50;
            border: none;
            border-radius: 5px;
            text-decoration: none;
            text-align: center;
        }
        .btn:hover {
            background-color: #45a049;
        }
    </style>
</head>
<body>
    <div class="container">
        {% if access_token and userinfo %}
            <h1>Authentication Successful!</h1>
            <h2>User Information</h2>
            <pre>{{ userinfo | tojson(indent=2) }}</pre>
            <h2>Access Token</h2>
            <pre>{{ access_token }}</pre>
        {% else %}
            <h1>Welcome to Minikube!</h1>
            <p>Click the button below to authenticate:</p>
            <a href="/protected" class="btn">Login with Keycloak</a>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/')
def home():
    code = request.args.get('code')

    if code:
        try:
            # Exchange the authorization code for an access token
            token_response = keycloak_openid.token(
                grant_type='authorization_code',
                code=code,
                redirect_uri="http://localhost:5000/"
            )
            access_token = token_response['access_token']
            
            # Fetch user information using the access token
            userinfo = keycloak_openid.userinfo(access_token)
            
            # Render the template with tokens and user info
            return render_template_string(template, access_token=access_token, userinfo=userinfo)
        except Exception as e:
            return render_template_string(template, access_token=None, userinfo=None)
    else:
        return render_template_string(template, access_token=None, userinfo=None)

@app.route('/protected')
def protected():
    # Redirect to Keycloak for authentication
    auth_url = keycloak_openid.auth_url(
        redirect_uri="http://localhost:5000/",
        scope="openid",
        state="random_state_string"  # Generate a unique state in production
    )
    return redirect(auth_url)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
