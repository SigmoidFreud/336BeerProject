# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
import json
import re
import requests
import time
import urllib
import random
from sqlalchemy import create_engine




profile_re = re.compile(r'\/beer\/profile')
style_re = re.compile(r'\/beer\/style\/')

####
# For crawling the style pages and gathering beer profile URLs:
#
# URL = "http://beeradvocate.com/beer/style"
# seed = gather_urls(URL)
# dump_urls(seed, 'new_urls.txt')
####

def get_type(soup):
	return soup.find_all('b')[5].string

def get_title(soup):
        return soup.title.string

def get_score(soup):
        return soup.find('span', {'class':'BAscore_big'}).string

def get_reviews(soup):
        collection = []
	#print soup.body.find(attrs = {'id':'rating_fullview_content_2'})
        reviews = soup.find_all('div', id = "rating_fullview_content_2")
        i = 0
        for item in reviews:
		i += 1
                review = {
                'score': item.find('span', {'class':'BAscore_norm'}).string,
                'text': ' '.join([line.strip() for line in item.strings])
                }
                collection.append(review)
		if i == 2: 
			break

        return collection

def get_info(URL):
        soup = BeautifulSoup(urllib.urlopen(URL))
        # In case requests isn't getting it:
        # r = urllib2.urlopen(URL)
        # soup = BeautifulSoup(r.read())
        profile = {
        'name': get_title(soup),
	'type': get_type(soup),
        'url': URL,
        'score': get_score(soup),
        'reviews': get_reviews(soup)
        }
        return profile

def load_urls():
        urllist = []
        engine = create_engine('mysql://root@127.0.0.1:3306/BeerDB')
        con = engine.connect()
        result = con.execute("SELECT BeerURL from BeerReview")
        for row in result:
                urllist.append(row['BeerURL'])
        result.close()
        con.close()
        return urllist

def crawl_urls(url_list,nums):
        # randlist = []
        # for num in range(nums):
                # rand = random.randint(0,5044)
                # if rand not in randlist:
                        # beer = get_info(url_list[rand])
                        # randlist.append(rand)
                # else:
                        # num -= 1
                        # continue
                # beertostring = (beer['name'], beer['type'], beer['score'], '\n'.join([rev['text'] for rev in beer['reviews']], beer['url']))
                # print beertostring
        file = open("reviews.csv", "w")
        file.write('\t'.join(['BeerTitle','type','score','reviews','url']))
        file.write('\n')
        for url in url_list:
                # This is ugly because I don't know of a simple
                # SQLite query with a no-results response.
                # print "Fetching ", url
                beer = get_info(url)
                t = [beer['name'].encode("utf-8"), beer['type'].encode("utf-8"), beer['score'].encode("utf-8"), ' ^^^ '.join([rev['text'] for rev in beer['reviews']]).encode("utf-8"), beer['url'].encode("utf-8")]
                file.write('\t'.join(t))
                file.write('\n')
                # Trying to be polite! Even 1 second is kind of short.
                
        file.close()


def main():
        # scraped urls by iteratively visiting neighboring beers of each initial beer in list
        # then i scraped the data by search fr specific tags
        urls = load_urls()
        # print urls
        crawl_urls(urls,100)

if __name__ == '__main__':
        main()
