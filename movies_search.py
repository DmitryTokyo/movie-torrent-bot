import logging
import re
import urllib.parse
from bs4 import BeautifulSoup
import httpx
import os

logger = logging.getLogger('kinoTorrent')


def connect_to_torrent_tracker(client, headers):
    url = 'https://kinozal.tv/takelogin.php'

    payload = {
        'username': os.getenv('USERNAME'),
        'password': os.getenv('PASSWORD'),
        'returnto': ''
    }
    res = client.post(url, data=payload, headers=headers)
    res.raise_for_status()


def get_movies_search_result(query, client):
    encoded_query = urllib.parse.quote(query.encode('windows-1251'))
    url = f'https://kinozal.tv/browse.php?s={encoded_query}'
    res = client.get(url)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, 'lxml')
    search_table = soup.find(class_='t_peer').find_all('tr', class_='bg')
    movies_data = []
    for data in search_table:
        a_tag = data.find('a', class_=re.compile(r'r[01]'))
        if not a_tag:
            continue
        is_gold = 'r1' in a_tag.get('class', [])
        try:
            movie_size = data.find('td', class_='s', string=re.compile(r'(ГБ|МБ)')).text
        except AttributeError:
            logger.error(data)
            raise AttributeError
        movie_sid = data.find('td', class_='sl_s').text
        movie_peer = data.find('td', class_='sl_p').text
        movie_name = a_tag.text
        torrent_file_link = a_tag['href']
        movie_id = torrent_file_link.split('id=')[1]
        movies_data.append({
            'movie_id': movie_id,
            'movie_name': movie_name,
            'size': movie_size,
            'peer': movie_peer,
            'sid': movie_sid,
            'torrent_link': torrent_file_link,
            'is_gold': is_gold,
        })
    return movies_data


def search_movie(query):
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:133.0) Gecko/20100101 Firefox/133.0',
    }
    with httpx.Client(follow_redirects=True) as client:
        res = client.get('https://kinozal.tv/', headers=headers)
        res.raise_for_status()
        connect_to_torrent_tracker(client, headers)
        results = get_movies_search_result(query, client)
    return results

def get_searching_result(query):
    results = search_movie(query)
    if results:
        return sorted(results, key=lambda x: (not x['is_gold'], -int(x['sid'])))
    return results


def get_movie_page(movie_link):
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:133.0) Gecko/20100101 Firefox/133.0',
    }
    movie_page_url = f'https://kinozal.tv{movie_link}'
    with httpx.Client(follow_redirects=True) as client:
        res = client.get('https://kinozal.tv/', headers=headers)
        res.raise_for_status()
        connect_to_torrent_tracker(client, headers)
        res = client.get(movie_page_url)
        res.raise_for_status()
        return res.text


def download_movie(movie_link):
    movie_page = get_movie_page(movie_link)
    soup = BeautifulSoup(movie_page, 'lxml')
    download_file_link = soup.find(class_='mn1_content').find('a')['href']
    url = f'https:{download_file_link}'
    file_id = movie_link.split('=')[1]
    with httpx.Client(follow_redirects=True) as client:
        response = client.get(url)
        with open(f'[kinozal.tv]id{file_id}.torrent', 'wb') as file:
            file.write(response.content)


if __name__ in '__main__':
    get_searching_result('терминатор')
