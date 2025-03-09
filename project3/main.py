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
