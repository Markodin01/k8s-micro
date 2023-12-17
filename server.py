import crypt
import os
import jwt, datetime
from flask import Flask, request
from flask_mysqldb import MySQL

server = Flask(__name__)
mysql = MySQL(server)

server.config["MYSQL_HOST"] = os.environ.get("MYSQL_HOST")

server.config["MYSQL_USER"] = os.environ.get("MYSQL_HOST")

server.config["MYSQL_PASSWORD"] = os.environ.get("MYSQL_HOST")

server.config["MYSQL_DB"] = os.environ.get("MYSQL_HOST")

server.config["MYSQL_PORT"] = os.environ.get("MYSQL_HOST")

@server.route("/login", methods=["POST"])
def login():
	auth = request.autorization
	
	if  not auth:
		return "missing credentials", 401
	
	cur = mysql.connection.cursor()
	res = cur.execute(
		"SELECT email, password FROM user WHERE email=%s", (auth.username)
	)

	if res > 0:
		user = cur.fetchone()
		if crypt.checkpw(auth.password, user["password"]):
			token = jwt.encode(
				{
					"email": user["email"],
					"exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=30),
				},
				os.environ.get("JWT_SECRET"),
			)
			return {"token": token.decode("UTF-8")}
		else:
			return "invalid credentials", 401
		
@server.route("/validate", methods=["POST"])
def validate():
	encoded_jwt = request.headers.get("Authorization")

	if not encoded_jwt:
		return "missing token", 401
	
	encoded_jwt = encoded_jwt.split(" ")[1]
	try:
		decoded = jwt.decode(encoded_jwt, os.environ.get("JWT_SECRET"))
	except jwt.InvalidTokenError:
		return "invalid token", 401
	
	return decoded, 200
		
def createJWT(username, secret, authz, issuer):
	payload = {
		"sub": username,
		"iss": issuer,
		"exp": datetime.datetime.utcnow() + datetime.timedelta(days=30),
		"iat": datetime.datetime.utcnow(),
		"admin": authz
	}
	return jwt.encode(payload, secret, algorithm="HS256").decode("UTF-8")

	
if __name__ == "__main__":
	server.run(host="0.0.0.0", port=5000)