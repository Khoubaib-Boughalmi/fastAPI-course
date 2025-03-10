import jwt
from typing import Optional
from functools import wraps
from fastapi import Depends, FastAPI, HTTPException, Header

app = FastAPI()


def require_permission(role):
	def decorator(func):
		@wraps(func)
		async def wrapper(*args, **kwargs):
			user_role = kwargs.get("user_role", "guest")
			print(user_role)
			if user_role != role:
				raise HTTPException(status_code=403, detail=f"Access Denied: {role} role required.")
			print(f"Access granted for {user_role} to {func.__name__}.")
			return await func(*args, **kwargs)
		return wrapper
	return decorator

SECRET_KEY = "mySecretKey"

def jwt_decode_token(token: str) -> dict:
	print("toooken", token)
	try:
		decoded = jwt.decode(token, key=SECRET_KEY, algorithms=["HS256"])
		role = decoded.get("role", "guest")
		return role
	except jwt.ExpiredSignatureError:
		raise HTTPException(status_code=403, detail="Token has expired.")
	except jwt.InvalidTokenError:
		raise HTTPException(status_code=403, detail="Invalid token.")     
	except Exception as e:
		raise HTTPException(status_code=403, detail=e)
		
def extract_user_permission(authorization: Optional[str]= Header()) -> str:
	"""
		This function can be used to extract user role from jwt
 	"""
	if authorization is None:
		raise HTTPException(status_code=401, detail="Authorization header missing")
	token = authorization.replace("Bearer ", "")
	try:
		decoded_token = jwt_decode_token(token)
		return decoded_token
	except:
		return "guest"

@app.get("/admin")
@require_permission("admin")
async def get_admin_information(user_role: str = Depends(extract_user_permission)):     
	return {"Information": "This is a secret information only accessible to admins", "role": user_role}

