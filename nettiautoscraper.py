import urllib
import urllib.request
from bs4 import BeautifulSoup

import numpy as np
#import cv2

import os
import time
import json

path = "nautoClassifier/"

def make_soup(url):
    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
    headers={'User-Agent':user_agent,} 

    request=urllib.request.Request(url,None,headers)

    try:
        thepage = urllib.request.urlopen(request)
        soupdata = BeautifulSoup(thepage, "html.parser")
        return soupdata
    except:
        print(url+" NOT FOUND")

cars = {"brand": "", "models": []}
totalImages = 0


def getCars():
    starttime = time.time()
    url = "https://www.nettiauto.com"
    soup = make_soup(url)
    select = soup.find('select', {'id': 'srch_id_make'})
    options = select.findChildren()
    brands = []
    options_nodupes = list(set(options))
    print("Init took "+str(time.time()-starttime)+" seconds")
    for option in options:
        for brand in option:
            try:
                if not brand.startswith("<") and len(brand) != 1:
                    brands.append(brand.replace(" ", "-"))
            except:
                pass
    print("Brands took "+str(time.time()-starttime)+" seconds")
    brands_nodupes = list(set(brands))
    for brand in brands_nodupes:
        soup = make_soup(url+"/"+brand)
        if soup:
            select = soup.find('select', {'id': 'srch_id_model'})
            options = select.findChildren()
            models = []
            for o in options:
                if not o.text.startswith("Malli") and not o.text.startswith("<") and not o.text.startswith("-"):
                    models.append(o.text.replace(" ", "-"))
            cars[brand] = models
    print("Models took "+str(time.time()-starttime)+" seconds")
    with open('cars.json', 'w') as fp:
        json.dump(cars, fp)

    print("Obtaining all available vehicles took "+str(time.time()-starttime)+" seconds")
        
def dlCars(brand, model):
    print("Downloading images for "+str(brand)+" "+str(model))
    if not os.path.isfile("cars.json"):
        print("Cars.json not found, generating...")
    pageOfPage = 1
    totPage = 1
    while pageOfPage <= totPage:
        url = "https://www.nettiauto.com/%s/%s?page=%s"%(brand, model, pageOfPage)
        soup = make_soup(url)
        pageOfPage = int(soup.findAll("span", { "class" : "pageOfPage" })[0].text)
        totPage = int(soup.findAll("span", { "class" : "totPage" })[0].text)
        print("page "+str(pageOfPage)+" of "+str(totPage))
        directory = path+brand+"_"+model+"/"
        if not os.path.exists(directory):
            os.makedirs(directory)

        for img in soup.findAll('img'):
            #if int(img.get('width')) > 100 and int(img.get('height')) > 100:
            image = img.get('src')
            filename = image.rsplit('/', 1)[1]#str(pageOfPage)+"_"+str(i)
            # gif's are ads
            if "logo" not in filename and ".gif" not in filename:
                try:
                    imagefile = open(directory+filename, 'wb')
                    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
                    headers={'User-Agent':user_agent,} 
                    request=urllib.request.Request(image,None,headers)
                    imagefile.write(urllib.request.urlopen(request).read())
                    totalImages += 1
                    imagefile.close()
                except:
                    pass

        pageOfPage += 1

with open('cars.json') as data_file:    
    data = json.load(data_file)

total = 0
for k, v in data.items():
    for m in v:
        total += 1

i = 1
for k, v in data.items():
    starttime = time.time()
    for m in v:
        dlCars(k, m)
        print(str(i)+"/"+str(total))
        i += 1
    print("Downloading "+str(total)+" vehicles and "+str(totalImages)+" took "+str(time.time()-starttime)+" seconds")