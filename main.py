from bs4 import BeautifulSoup
import json
from selenium import webdriver
import csv
import regex as re
import os

LOGIN = 'suchy002'
LOGIN_URL = 'https://www.filmweb.pl/login'
FILE_PATH = f'csv_files/{LOGIN}_movies.csv'
FILMWEB_URL = f'https://www.filmweb.pl/user/{LOGIN}/films?page='


def log_in_filmweb(browser):
    browser.get(LOGIN_URL)
    browser.find_element_by_id("didomi-notice-agree-button").click()
    input("Log in your account, then\n press Enter to continue...")


def try_scrape(action):
    try:
        action
        return action
    except: pass


def scrape_movies_data(url):
    driver.get(url)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    #print(soup.prettify())
    movies = soup.find_all('div', attrs={'class': re.compile('^FilmPreview filmPreview filmPreview--FILM Film.*')})
    user_info = soup.find_all('script', type="application/json", id=True)
    for movie in movies:
        id = movie.get('data-id')
        title = movie.find('h2', class_='filmPreview__title').text
        duration, year, acc_rate, user_rate, user_date = 0, 0, 0, 0, 0
        genre, country = [], []
        duration = try_scrape(movie.find('div', class_='filmPreview__filmTime').get('data-duration'))
        year = try_scrape(movie.find('div', class_='filmPreview__year').text)
        genre = try_scrape(movie.find('div', class_='filmPreview__info filmPreview__info--genres').find_all('a'))
        country = try_scrape(movie.find('div', class_='filmPreview__info filmPreview__info--countries').find_all('a'))
        acc_rate = try_scrape(movie.find('span', class_='rateBox__rate').text)
        genre = [g.text for g in genre]
        country = [c.text for c in country]
        for n in user_info:
            if n.get('id') == id:
                data = json.loads(n.string)
                user_rate = data['r']
                user_date = str(data['d']['d']) + '.' + str(data['d']['m']) + '.' + str(data['d']['y'])
        movie = {'title': title, 'year': year, 'acc_rate': acc_rate, 'duration': duration,
                 'genre': genre, 'country': country, 'user_rate': user_rate, 'user_date': user_date}
        check_new_movie(movie)


def check_new_movie(new_movie):
    print(new_movie['title'])
    if not any((d['title'] == new_movie['title'] and d['year'] == new_movie['year']) for d in watched_movies):
        print('Nie bylo.')
        my_movies.append(new_movie)
    else:
        print('BYLO!!!!')
    watched_movies.insert(0, {'title': new_movie.get('title'), 'year': new_movie.get('year')})


def create_csv_file():
    with open(FILE_PATH, mode='w') as file:
        file_writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        file_writer.writerow(['Title', 'Year', 'ACC_rate', 'Duration', 'Genre', 'Country', 'User_Rate', 'User_Date'])


def read_csv_file():
    csv_list = []
    with open(FILE_PATH, mode='r') as file:
        file_reader = csv.DictReader(file, delimiter=',', quotechar='"')
        for row in file_reader:
            csv_list.append({'title': row['Title'], 'year': row['Year']})
    csv_list.reverse()
    return csv_list


def save_csv_file(csv_list):
    with open(FILE_PATH, mode='a') as file:
        file_writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for element in csv_list:
            file_writer.writerow([element.get('title'), element.get('year'), element.get('acc_rate'),
                                  element.get('duration'), element.get('genre'), element.get('country'),
                                  element.get('user_rate'), element.get('user_date')])


driver = webdriver.Chrome(executable_path='/home/suchy/Others/chromedriver/chromedriver')
my_movies = []

if not os.path.isfile(FILE_PATH):
    create_csv_file()
    watched_movies = read_csv_file()
    log_in_filmweb(driver)
    for page in range(1, 30):
        scrape_movies_data(FILMWEB_URL + str(page))
else:
    watched_movies = read_csv_file()
    scrape_movies_data(FILMWEB_URL)


if my_movies:
    my_movies.reverse()
    save_csv_file(my_movies)


driver.close()


