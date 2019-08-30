import csv
import application

with open('books.csv') as csvfile:
    csvread = csv.DictReader(csvfile)
    cnt = 0
    for row in csvread:
        application.db.execute('INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)', {'isbn':row['isbn'], 'title':row['title'], 'author':row['author'], 'year':(row['year'])})
    application.db.commit()
