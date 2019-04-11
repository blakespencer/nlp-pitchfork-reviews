from bs4 import BeautifulSoup
import requests
import numpy
import time
import csv

import sys

lower_range = int(sys.argv[1])
upper_range = int(sys.argv[2])


url = 'https://pitchfork.com/reviews/albums/?page={}'


def get_review_hrefs(index):
    output = []
    url_page = url.format(index)
    response = requests.get(url_page)
    while(response.status_code != 200):
        time.sleep(numpy.random.exponential(5, 1))
        response = requests.get(url_page)
    html = response.text
    soup = BeautifulSoup(html, 'lxml')
    reviews = soup.find('div', {'class': 'fragment-list'}
                        ).find_all('div', {'class': 'review'})
    for review in reviews:
        href = review.find('a')
        output.append('https://pitchfork.com' + href.get('href'))
    return output


def get_album_info(href):
    response = requests.get(href)
    while(response.status_code != 200):
        time.sleep(numpy.random.exponential(5, 1))
        response = requests.get(href)
    html = response.text
    soup = BeautifulSoup(html, 'lxml')
    review_details = soup.find('div', {'class': 'review-detail'})
    ablum_score = review_details.find('span', {'class': 'score'}).text
    album_year = review_details.find(
        'span', {'class': 'single-album-tombstone__meta-year'}).text[-4:]
    artist = (review_details
              .find('ul', {'class': 'artist-links artist-list single-album-tombstone__artist-links'}).text)
    album_name = review_details.find(
        'h1', {'class': 'single-album-tombstone__review-title'}).text
    try:
        text = "".join([i.text for i in (review_details
                                         .find('div', {'class': 'row review-body'})
                                         .find('div', {'class', 'review-detail__article-content'})
                                         .find('div', {'class': 'contents dropcap'})
                                         .find_all('p'))
                        ])
    except:
        text = ''
    try:
        genres = ([i.text for i in review_details
                   .find('div', {'class': 'article-meta article-meta--reviews'})
                   .find('ul', {'class': 'genre-list genre-list--before'})
                   .find_all('li')
                   ])
    except:
        genres = []
    review_date = (review_details
                   .find('div', {'class': 'article-meta article-meta--reviews'})
                   .find('time').text
                   )
    return {'ablum_score': ablum_score,
            'album_year': album_year,
            'artist': artist,
            'album_name': album_name,
            'text': text,
            'genres': ', '.join(genres),
            'review_date': review_date
            }


def write_csv_reviews(lower_range, upper_range):
    keys = ([
        'ablum_score',
        'album_year',
        'artist',
        'album_name',
        'text',
        'genres',
        'review_date'
    ])
    rows = []
    count = 0
    for i in range(lower_range, upper_range + 1):
        sleep_seconds = numpy.random.exponential(5, 1)
        time.sleep(sleep_seconds)
        hrefs = get_review_hrefs(i)
        for link in hrefs:
            count += 1
            print(count, link)
            rows.append(get_album_info(link))
    with open('{}_{}.csv'.format(lower_range, upper_range), 'w') as output_file:
        dict_writer = csv.DictWriter(output_file,  fieldnames=keys)
        dict_writer.writeheader()
        dict_writer.writerows(rows)


write_csv_reviews(lower_range, upper_range)
