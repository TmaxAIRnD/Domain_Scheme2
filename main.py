from scraper import Scraper
from file_writer import save_to_csv
from data_models import Book, Author, Media, Corp

def main():
    scraper = Scraper()
    books, authors, media = scraper.scrape()
    for book in books:
      if not isinstance(book, Book):
          print(f"잘못된 아이템: {book}")
    # CSV 파일 저장 로직
    save_to_csv("books.csv", books, Book)
    save_to_csv("authors.csv", authors, Author)
    save_to_csv("media.csv", media, Media)

    corps = scraper.scrape_corps_from_books()
    corps = list(set(corps))
    save_to_csv("corps.csv", corps, Corp)

    scraper.close()

if __name__ == "__main__":
    main()
