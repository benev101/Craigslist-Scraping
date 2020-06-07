import re
import sys
from datetime import date
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup

sys.path.append('..')

Today = str(date.today())
df = pd.DataFrame()

for i in map(str, range(0,2900,100)):
    s = requests.Session()
    s.proxies = {"http": "http://61.233.25.166:80"}
    source = s.get('https://dallas.craigslist.org/search/cto?s='+ i)

    soup = BeautifulSoup(source.content, 'lxml')

    Results = soup.find_all('li', class_ = 'result-row')

    Titles = []

    for info in Results:
        title = info.find(class_  = 'result-title hdrlnk').get_text()
        Titles.append(title)

    Prices = []

    for price in Results:
        cost = price.find(class_ = 'result-price').get_text()
        Prices.append(cost)
        
    Links = []

    for link in Results:
        click = link.find(class_ = 'result-title hdrlnk')['href']
        Links.append(click)

    Boroughs = []

    for hood in Results:
        hoods = hood.find(class_ = 'result-hood')
        if hoods is not None:
            boro = hoods.get_text()
            correct = re.search(r'\((.*?)\)', boro).group(1)
            Boroughs.append(correct)
        else:
            boro = None
            Boroughs.append(boro)

    PostDates = []

    for date in Results: 
        dates = date.find(class_ = 'result-date')['datetime']
        PostDates.append(dates)

    Description = []
    specs = []

    for link in Links:
        listing = requests.get(str(link))
        
        Listing_soup = BeautifulSoup(listing.content, features="lxml")
        
        Desc = Listing_soup.find('section', {'id': 'postingbody'})
        if Desc is not None:
            stuff = Desc.get_text()
            Description.append(stuff)
        else:
            txt = None
            Description.append(txt)
        
        data = Listing_soup.find_all(class_ = 'attrgroup')

        for i in data:
            f = i.get_text()
            if ':' in f:
                split1 = f.split(':', 1)
                specs.append(split1[1])
                                                            
    Cars = ({
        'Post Titles': Titles,
        'Prices': Prices,
        'Locations': Boroughs,
        'PostDates': PostDates,
        'Description': Description,
        'Specs': specs,
        'Links': Links,
        })
    df = df.append(pd.DataFrame(Cars))

    df['Odometer'] = df['Specs'].str.extract(r'\s*odometer\:(.*)\s')
    df['Transmission'] = df['Specs'].str.extract(r'\s*transmission\:(.*)')
    df['Title Status'] = df['Specs'].str.extract((r'\s*title status\:(.*)'))

    #df['trans']= df['Specs'].str.extract(r'(\s*transmission:\s\d*)')
    #df['manauto'] = df['trans'].str.extract(r'(\d+)')
    #df['tran']= df['Specs'].str.extract(r'(\s*transmission\:(.*)\s*)')

df[['Titles', 'Prices', 'Links', 'PostDates', 'Description', 'Specs', 'Odometer', 'Transmission', 'Title']].to_csv(r'C:\Users\bdukoff\Desktop\Bots\Cars.csv', index = False)