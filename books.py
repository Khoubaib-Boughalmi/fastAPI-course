from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import JSONResponse
app = FastAPI()

books = [
  {"id": 1, "title": "Book one", "author": "Author one", "category": "Science"},
  {"id": 2, "title": "Book two", "author": "Author two", "category": "Science"},
  {"id": 3, "title": "Book three", "author": "Author three", "category": "Math"},
  {"id": 4, "title": "Book four", "author": "Author one", "category": "History"},
]

@app.get("/books")
async def read_all_books():
  return books

# fastAPI follows a chronological url matching patters
@app.get("/books/bookone")
async def read_book():
  return JSONResponse(books[0], status_code=200)

# URL params
@app.get("/books/{book_id}")
async def read_book(book_id: int):
  book = next((book for book in books if book.get("id") == book_id), None)
  if book == None:
    raise HTTPException(status_code=404, detail=f"Book with id {book_id} not found")
  return JSONResponse(book, status_code=200)
    
# Query params
# example: /books/authors/author_name?book_category=category_name
@app.get("/books/authors/{book_author}")
async def get_book_by_author(book_author: str, book_category: str):
  author_books = []
  for book in books:
    if book["author"].casefold() == book_author.casefold() and \
        book["category"].casefold() == book_category.casefold():
      author_books.append(book)
  return author_books

@app.post("/books/create")
async def create_book(new_book=Body()):
  print(new_book)
  books.append(new_book)
  return JSONResponse(new_book, status_code=201)

@app.put("/books/{book_id}")
async def update_book(book_id: int, new_book=Body()):
  for i in range(len(books)):
    if books[i].get("id") == book_id:
      books[i] = new_book
      break
  return JSONResponse(new_book, status_code=200)

@app.delete("/books/{book_id}")
async def delete_book(book_id: int):
  for i in range(len(books)):
    if books[i].get("id") == book_id:
      books.pop(i)
      break


