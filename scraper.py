import requests
from bs4 import BeautifulSoup as bs
import re
import json
from difflib import SequenceMatcher
from db_session import session

root_url = 'http://www.seattle.gov/'
index_url = root_url + 'neighborhoods/p-patch-community-gardening/p-patch-list'
api_key = 'AIzaSyAB-LkkjB-aCEUB5HXcOau4v9M_8JF2krQ'

def get_garden_urls():
   response = requests.get(index_url)
   soup = bs(response.text, 'html.parser')
   return [a.attrs.get('href') for a in soup.select('div.paginationContainer a')]

def get_garden_data(garden_url):
   garden_data = {}
   print root_url + garden_url
   response = requests.get(root_url + garden_url)
   soup = bs(response.text, 'html.parser')
   garden_data['name'] = soup.select('h1.pageTitle')[0].get_text().strip()
   garden_data['features'] = [a.get_text() for a in soup.select('ul.features li')]
   garden_data['address'] = re.sub('Address:  ', '', soup.select('div.Address')[0].get_text().strip())
   if soup.has_attr('div.Numberofplots'):
      garden_data['num_of_plots'] = re.sub('Number Of Plots: ', '', soup.select('div.Numberofplots')[0].get_text())
   if soup.has_attr('div.Established'):
      garden_data['estbl'] = re.sub('Established: ', '', soup.select('div.Established')[0].get_text())
   if soup.has_attr('div.size'):
      garden_data['size'] = re.sub('Size: ', '', soup.select('div.size')[0].get_text())
   if soup.has_attr('div.waitTime'):
      garden_data['wait_time'] = re.sub('Wait Time: ', '', soup.select('div.waitTime')[0].get_text())
   garden_data['description'] = soup.select('div.span')[0].get_text().strip()
   garden_data['url'] = root_url + garden_url
   return garden_data

def add_geocode(garden):
   address = re.sub(' ', '+', garden['address'] + '+Seattle,+WA')
   url_root = 'https://maps.googleapis.com/maps/api/geocode/json?address=' + address + '&key=' + api_key
   geo_data = json.loads(requests.get(url_root).content)
   garden['lat'] = geo_data['results'][0]['geometry']['location']['lat']
   garden['formatted_address'] = geo_data['results'][0]['formatted_address']
   print garden['name']
   garden['lng'] = geo_data['results'][0]['geometry']['location']['lng']

def get_socrata_garden_data():
   soda_url = 'https://data.seattle.gov/resource/wejr-a88w.json'
   return json.loads(requests.get(soda_url).content)

def append_geo_data(socrata_data, scraped_data):
   data = []
   for soda_garden in socrata_data:
      soda_name = soda_garden['common_name']
      for scraped_garden in scraped_data:
         scraped_name = scraped_garden['name']
         match_ratio = SequenceMatcher(None, scraped_name, soda_name).ratio()
         if match_ratio >= 0.90:
            scraped_garden['lat'] = soda_garden['latitude']
            scraped_garden['lng'] = soda_garden['longitude']
            data.append(scraped_garden)
            continue
   return data

def create_scraped_data_array():
   data = []
   garden_urls = get_garden_urls()
   for garden_url in garden_urls:
      garden_data = get_garden_data(garden_url)
      data.append(garden_data)
   return data

def show_garden_stats():
   scraped_data = create_scraped_data_array()
   garden_urls = get_garden_urls()
   socrata_data = get_socrata_garden_data()
   print "%d : %d" % (len(scraped_data), len(socrata_data))
   gardens_w_geo = append_geo_data(socrata_data, scraped_data)
   out_file = open("gardens.json", "w") 
   json_data = json.dumps(gardens_w_geo, indent=3)
   out_file.write(json_data)
   out_file.close()

show_garden_stats()
