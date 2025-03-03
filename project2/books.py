from typing import Optional
from fastapi import FastAPI, Body
from pydantic import BaseModel, Field

app = FastAPI()


class Book(BaseModel):
    id: Optional[int] = None
    title: str
    author: str
    category: str
    rating: float = Field(gt=0, lt=11)


class BookRequest(BaseModel):
    id: Optional[int] = Field(description="ID is not required on create", default=None)
    title: str = Field(min_length=5, max_length=50)
    author: str = Field(min_length=3, max_length=20)
    category: str = Field(min_length=1, max_length=20)
    rating: float = Field(gt=0, lt=11)

    model_config = {
      "json_schema_extra": {
        "example": {
          "title": "Book X",
          "author": "Author X",
          "category": "Computer Science",
          "rating": 6.9
        }
      }
    }

books = [
    Book(id=1, title="Book one", author="Author one", category="Science", rating=7.6),
    Book(id=2, title="Book two", author="Author two", category="Math", rating=6.3),
    Book(
        id=3, title="Book three", author="Author three", category="Science", rating=8.6
    ),
    Book(id=4, title="Book four", author="Author one", category="History", rating=9.2),
]


@app.get("/books")
async def read_all_books():
    return books


@app.get("/books/{book_id}")
async def read_book(book_id: int):
  for book in books:
    if book.id == book_id:
      return book

@app.get("/books/")
async def read_books_by_category(book_category: str):
  _books: list[Book] = []
  for book in books:
    if book.category.casefold() == book_category.casefold():
      _books.append(book)
  return _books

@app.post("/books")
async def create_book(book_request: BookRequest):
    new_book = Book(**book_request.model_dump(exclude={"id"}), id=generate_book_id())
    books.append(new_book)
    return new_book

def generate_book_id():
    return 1 if len(books) == 0 else books[-1].id + 1

