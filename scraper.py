import requests
import bs4
import re
from time import sleep

root_url = 'http://www.seattle.gov/'
index_url = root_url + 'neighborhoods/p-patch-community-gardening/p-patch-list'

def get_garden_urls():
   response = requests.get(index_url)
   soup = bs4.BeautifulSoup(response.text, 'html.parser')
   return [a.attrs.get('href') for a in soup.select('div.paginationContainer a')]

def get_garden_data(garden_url):
   garden_data = {}
   print root_url + garden_url
   response = requests.get(root_url + garden_url)
   soup = bs4.BeautifulSoup(response.text, 'html.parser')
   garden_data['name'] = soup.select('h1.pageTitle span')[0].get_text()
   garden_data['features'] = [a.get_text() for a in soup.select('ul.features li')]
   garden_data['address'] = re.sub('Address: ', '', soup.select('div.Address')[0].get_text())
   if soup.has_attr('div.Numberofplots'):
      garden_data['num_of_plots'] = re.sub('Number Of Plots: ', '', soup.select('div.Numberofplots')[0].get_text())
   garden_data['estbl'] = re.sub('Established: ', '', soup.select('div.Established')[0].get_text())
   if soup.has_attr('div.size'):
      garden_data['size'] = re.sub('Size: ', '', soup.select('div.size')[0].get_text())
   if soup.has_attr('div.waitTime'):
      garden_data['wait_time'] = re.sub('Wait Time: ', '', soup.select('div.waitTime')[0].get_text())
   garden_data['description'] = soup.select('div.span')[0].get_text()
   return garden_data

def show_garden_stats():
   garden_urls = get_garden_urls()
   i = 0
   progress_str = '.'
   for garden_url in garden_urls:
      sleep(1)
      i += 1
      if i % 5 == 0:
         progress_str += '.'
         print progress_str
   print 'scrape complete with no errors'

show_garden_stats()
