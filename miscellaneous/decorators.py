from functools import wraps
from sqlalchemy.orm import Session
from fastapi import Depends

def custom_decorator(func):  # Step 1️⃣ Takes the function as an argument
	@wraps(func)  # Preserves function metadata (name, docstring, etc.)
	async def wrapper(*args, **kwargs):  # Step 2️⃣ Defines a new function (wrapper)
		print("🚀 Before function")  # Runs BEFORE the original function
		result = await func(*args, **kwargs)  # Calls the original function
		print("✅ After function")  # Runs AFTER the original function
		return result  # Returns the result of the original function

	return wrapper  # Step 3️⃣ Returns the wrapper function


@app.get("/test")
@custom_decorator
async def test():
	'''Demonstrates triple double quotes docstrings and does nothing really.'''
	print("🔄 Inside function")
	return {"message": "Hello"}

print(test.__name__)


def require_permission(role):
	def decorator(func):
		@wraps(func)
		async def wrapper(*args, **kwargs):
			user_role = kwargs.get("user_role", "guest")
			if user_role != role:
				raise PermissionError(f"Access Denied: {role} role required.")
			print(f"Access granted for {user_role} to {func.__name__}.")
			return await func(*args, **kwargs)
		return wrapper
	return decorator

@require_permission("admin")
async def delete_user(user_id, user_role):
	print(f"User {user_id} deleted.")

async def test():
	await delete_user(123, user_role="admin")  # Will succeed
	await delete_user(123, user_role="guest")  # Will raise PermissionError

test()