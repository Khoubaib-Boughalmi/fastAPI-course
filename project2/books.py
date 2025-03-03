from typing import Optional
from fastapi import FastAPI, Body
from pydantic import BaseModel, Field
from datetime import datetime
from random import random
app = FastAPI()


# Used for response body (That is why we assume that the fields are valid)
class Book(BaseModel):
    id: Optional[int] = None
    title: str
    author: str
    category: str
    rating: float = Field(gt=0, lt=11)
    published_date: int


# Used for request body (That is why we do not assume that the fields are valid)
class BookRequest(BaseModel):
    id: Optional[int] = Field(description="ID is not required on create", default=None)
    title: str = Field(min_length=5, max_length=50)
    author: str = Field(min_length=3, max_length=20)
    category: str = Field(min_length=1, max_length=20)
    rating: float = Field(gt=0, lt=11)
    published_date: int = Field(description="Default: Current year", default=datetime.now().year)

    model_config = {
      "json_schema_extra": {
        "example": {
          "title": "Book X",
          "author": "Author X",
          "category": "Computer Science",
          "rating": int(random() * 100) / 10,
          "published_date": datetime.now().year
        }
      }
    }

books = [
    Book(id=1, title="Book one", author="Author one", category="Science", rating=7.6, published_date=2001),
    Book(id=2, title="Book two", author="Author two", category="Math", rating=6.3, published_date=2017),
    Book(
        id=3, title="Book three", author="Author three", category="Science", rating=8.6
    , published_date=2021),
    Book(id=4, title="Book four", author="Author one", category="History", rating=9.2, published_date=2025),
]

@app.get("/books")
async def read_all_books():
    return books


@app.get("/books/{book_id}")
async def read_book(book_id: int):
  for book in books:
    if book.id == book_id:
      return book

@app.get("/books/category/{book_category}")
async def read_books_by_category(book_category: str):
  _books: list[Book] = []
  for book in books:
    if book.category.casefold() == book_category.casefold():
      _books.append(book)
  return _books

@app.get("/books/publish/{book_published_date}")
async def read_books_by_publish_year(book_published_date: int):
  _books: list[Book] = []
  for book in books:
    if book.published_date == book_published_date:
      _books.append(book)
  return _books

@app.post("/books")
async def create_book(book_request: BookRequest):
    new_book = Book(**book_request.model_dump(exclude={"id"}), id=generate_book_id())
    books.append(new_book)
    return new_book

def generate_book_id():
    return 1 if len(books) == 0 else books[-1].id + 1


@app.put("/books/{book_id}")
async def update_book(book_id: int, book: BookRequest):
  for i in range(len(books)):
    if books[i].id == book_id:
      updated_book_data = {"id": books[i].id, **book.model_dump(exclude={"id"})}
      books[i] = Book(**updated_book_data)
      break
  return updated_book_data

@app.delete("/books/{book_id}")
async def delete_book(book_id: int):
  for i in range(len(books)):
    if books[i].id == book_id:
      deleted = books.pop(i)
      break
  return deleted