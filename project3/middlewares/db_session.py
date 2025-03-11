from fastapi import Request
from sqlalchemy.orm import Session
from database import sessionLocal

async def db_session_middleware(request: Request, call_next):
	"""
		- Database session middleware ensures that a single session is maintained throughout the request: middleware-based session, all endpoints within the same request lifecycle share the same session (querying data, logging in, sending an email...).
		- Properly commits on success and rolls back on failure
		It reduces the overhead of creating and destroying multiple database connections.
		It ensures consistency across different parts of the request (e.g., if a transaction spans multiple operations, they all happen within the same session).
		It allows you to commit or rollback changes at the end of the request, preventing half-completed database operations in case of an error. ==> Atomicity
	"""
	db = sessionLocal()
	request.state.db = db
	try:
		response = await call_next(request)
		if request.method not in ["GET"]:
			db.commit()
	except:
		print("Something went wrong: Rollback")
		db.rollback()
		raise
	finally:
		db.close()
	return response

def get_db(request: Request) -> Session:
	return request.state.db
