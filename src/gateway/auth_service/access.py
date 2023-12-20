import os, requests

def login(request):
    auth = request.authorization
    if not auth:
        return None, ("missing credentials", 401)
    res = requests.post(
        f'http://{os.environ.get("AUTH_SVC_ADDRESS")}/login',
        auth={"username": auth.username, "password": auth.password}
    )
    if res.status_code == 200:
        return res.json(), 200
    else:
        return None, (res.text, res.status_code)