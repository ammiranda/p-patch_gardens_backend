import requests
import bs4

root_url = 'http://www.seattle.gov'
index_url = root_url + '/neighborhoods/p-patch-community-gardening/p-patch-list'

def get_garden_urls():
   response = requests.get(index_url)
   soup = bs4.BeautifulSoup(response.text, 'html.parser')
   return [a.attrs.get('href') for a in soup.select('div.paginationContainer a')]

def get_garden_data(garden_url):
   garden_data = {}
   response = requests.get(root_url + garden_url)
   soup = bs4.BeautifulSoup(response.text, 'html.parser')
   garden_data['name'] = soup.select('h1.pageTitle span').get_text()
   garden_data['features'] = [a.get_text() for a in soup.select('ul.features li')]
   return garden_data


