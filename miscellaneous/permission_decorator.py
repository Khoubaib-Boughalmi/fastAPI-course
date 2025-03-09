from fastapi import Depends, FastAPI, HTTPException
from functools import wraps
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

def extract_user_permission():
	"""
		This function can be used to extract user role from jwt or session
 	"""
	return "supervisor"

@app.get("/admin")
@require_permission("admin")
async def get_admin_information(user_role: str = Depends(extract_user_permission)):     
	return {"Information": "This is a secret information only accessible to admins", "role": user_role}
