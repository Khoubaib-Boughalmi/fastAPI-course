from functools import wraps
from fastapi import Depends, FastAPI, Request
from database import engine, sessionLocal
from sqlalchemy.orm import Session
import models

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

"""
	- Database session middleware ensures that a single session is maintained throughout the request: middleware-based session, all endpoints within the same request lifecycle share the same session (querying data, logging in, sending an email...).
 	- Properly commits on success and rolls back on failure
	It reduces the overhead of creating and destroying multiple database connections.
	It ensures consistency across different parts of the request (e.g., if a transaction spans multiple operations, they all happen within the same session).
	It allows you to commit or rollback changes at the end of the request, preventing half-completed database operations in case of an error. ==> Atomicity
"""


@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
	db = sessionLocal()
	request.state.db = db
	try:
		response = await call_next(request)
		if request.method not in ["GET"]:
			db.commit()
	except:
		db.rollback()
		raise
	finally:
		db.close()
	return response


def get_db(request: Request) -> Session:
	return request.state.db


@app.get("/todos")
async def get_all_todos(db: Session = Depends(get_db)):
	return db.query(models.Todos).all()


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
	return require_permission

@require_permission("admin")
async def delete_user(user_id, user_role):
	print(f"User {user_id} deleted.")

async def test():
	await delete_user(123, user_role="admin")  # Will succeed
	await delete_user(123, user_role="guest")  # Will raise PermissionError

test()