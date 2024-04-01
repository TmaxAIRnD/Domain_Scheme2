from dataclasses import dataclass
from typing import List

@dataclass
class Book:
    id: int
    title: str
    author: str
    publisher: str
    published_date: str
    category: str
    rating_value: str
    isbn: str
    page_num: str
    size: str
    language: str
    keywords: List[str]
    summary: str

@dataclass
class Author:
    author: str
    country: str
    job: str

@dataclass
class Media:
    title: str
    paper_book: str
    ebook: str

@dataclass(frozen=True)
class Corp:
    publisher: str
    sector: str
    company_size: str
