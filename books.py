from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
app = FastAPI()

books = [
  {"id": 1, "title": "Book one", "author": "Author one", "category": "Science"},
  {"id": 2, "title": "Book two", "author": "Author two", "category": "Science"},
  {"id": 3, "title": "Book three", "author": "Author three", "category": "Math"},
  {"id": 4, "title": "Book four", "author": "Author four", "category": "History"},
]

@app.get("/books")
async def read_all_books():
  return books


@app.get("/books/{book_id}")
async def read_book(book_id: int):
  book = next((book for book in books if book.get("id") == book_id), None)
  if book == None:
    raise HTTPException(status_code=404, detail=f"Book with id {book_id} not found")
  return JSONResponse(book, status_code=200)
    
