import re
import requests
from bs4 import BeautifulSoup as bs
import json
from difflib import SequenceMatcher

root_url = 'http://www.seattle.gov/'
index_url = root_url + 'neighborhoods/p-patch-community-gardening/p-patch-list'

def get_garden_urls():
   response = requests.get(index_url)
   soup = bs(response.text, 'html.parser')
   return [a.attrs.get('href') for a in soup.select('div.paginationContainer a')]

def get_garden_data(garden_url):
   garden_data = {}
   print(root_url + garden_url)
   response = requests.get(root_url + garden_url)
   soup = bs(response.text, 'html.parser')
   garden_data['name'] = soup.select('h1.pageTitle')[0].get_text().strip()
   garden_data['features'] = [a.get_text() for a in soup.select('ul.features li')]
   garden_data['address'] = re.sub('Address:  ', '', soup.select('div.Address')[0].get_text().strip())
   if len(soup.find_all("div", "Numberofplots")) > 0:
    garden_data['num_of_plots'] = re.sub('Number Of Plots:  ', '',
        soup.find_all("div", "Numberofplots")[0].get_text())
   if len(soup.find_all("div", "Established")) > 0:
    garden_data['estbl'] = re.sub('Established:  ', '',
        soup.find_all("div", "Established")[0].get_text())
   if len(soup.find_all("div", "size")) > 0:
    garden_data['size'] = re.sub('Size:  ', '', soup.find_all("div", "size")[0].get_text())
   if len(soup.find_all("div", "waitTime")) > 0:
    garden_data['wait_time'] = re.sub('Wait Time:  ', '', soup.find_all("div", "waitTime")[0].get_text())
   garden_data['description'] = soup.select('div.span')[0].get_text().strip()
   garden_data['url'] = root_url + garden_url
   return garden_data

def get_socrata_garden_data():
   soda_url = 'http://www.seattle.gov/p-patch-geo-json'
   return json.loads(requests.get(soda_url).content.decode('utf8'))

def append_geo_data(socrata_data, scraped_data):
    for i in range(0, len(scraped_data)):
        name = scraped_data[i]['name']
        for k in range(0, len(socrata_data['features'])):
            if socrata_data['features'][k]['properties']['Name'] == name:
                socrata_data['features'][k]['properties'].update(scraped_data[i])
    return socrata_data

def create_scraped_data_array():
   data = []
   garden_urls = get_garden_urls()
   for garden_url in garden_urls:
      garden_data = get_garden_data(garden_url)
      data.append(garden_data)
   return data

def show_garden_stats():
   scraped_data = create_scraped_data_array()
   socrata_data = get_socrata_garden_data()
   print("%d : %d" % (len(scraped_data), len(socrata_data)))
   gardens_w_geo = append_geo_data(socrata_data, scraped_data)
   out_file = open("gardens.json", "w") 
   json_data = json.dumps(gardens_w_geo, indent=3)
   out_file.write(json_data)
   out_file.close()

if __name__ == "__main__":
   show_garden_stats()
