import os
import requests
from bs4 import BeautifulSoup
import csv
from urllib.parse import urljoin


def get_book(link):
    page = requests.get(link)
    soup = BeautifulSoup(page.content,'html.parser')
    universal_product_code= soup.find('th', text='UPC').find_next_sibling('td').text
    title= soup.find('h1').text
    price_including_tax= soup.find('th', text='Price (incl. tax)').find_next_sibling('td').text
    price_excluding_tax= soup.find('th', text='Price (excl. tax)').find_next_sibling('td').text
    number_available= soup.find('th', text='Availability').find_next_sibling('td').text.strip('In stock () available')
    product_description= soup.find(class_='sub-header').find_next('p').text
    category= soup.find(class_='breadcrumb').find_all('a')[2].text
    review_rating= soup.find('p', class_='star-rating').get('class')[1]
    image_url= soup.find('div', class_='item active').find_next('img').get('src')
    return[universal_product_code, title, price_including_tax, price_excluding_tax, number_available, product_description, category, review_rating, urljoin("http://books.toscrape.com/",image_url)]

def get_categories():
    data = {}
    response = requests.get('https://books.toscrape.com/')
    soup = BeautifulSoup(response.content, 'html.parser')
    category_scrape = soup.find('div', class_='side_categories').find('li').find_all('li')
    for category in category_scrape:
        books_url = category.find('a', href = True).get('href')
        category_name = category.text.strip() 
        data[category_name] = urljoin('https://books.toscrape.com/',books_url)
    return data


def get_books_data(url):
    links = []
    r = requests.get(url)
    soup = BeautifulSoup(r.content, 'html.parser')
    for books in soup.find_all('article', class_='product_pod'):
        books_link_url = books.find('a', href = True)
        books_url = books_link_url.get('href').strip('../../../')
        links.append(urljoin('https://books.toscrape.com/catalogue/',books_url))
    next = soup.find('li', class_='next')
    if next is not None:
        next_page = url.split('/')[0 : -1]
        next_page.append(next.find('a').get('href'))
        next_page_url = '/'.join(next_page)
        links.extend(get_books_data(next_page_url))
    return links



for category_name,category_url in get_categories().items():
    os.makedirs('data_csv', exist_ok=True)
    with open('data_csv/' + category_name + '.csv', 'w', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        writer.writerow(["universal_product_code", "title", "price_including_tax", "price_excluding_tax", "number_available", "product_description", "category", "review_rating", "image_url"])
        for url in get_books_data(category_url):
            book = get_book(url)
            writer.writerow(book)