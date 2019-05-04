#!/usr/bin/env python
# coding: utf-8

from bs4 import BeautifulSoup
import pymongo
import time
import pandas as pd
from splinter import Browser
from splinter.exceptions import ElementDoesNotExist
import requests
import os
import datetime as dt

def init_browser():
    # @NOTE: Replace the path with your actual path to the chromedriver
    executable_path = {'executable_path': 'chromedriver.exe'}
    return Browser("chrome", **executable_path, headless=False)

def scrape_info():
    
    browser = init_browser()

    # URLs of page to be scraped
    news_url = 'https://mars.nasa.gov/news'
    photo_url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    weather_url = 'https://twitter.com/marswxreport?lang=en'
    facts_url = 'https://space-facts.com/mars/'
    usgs_url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    short_photo_url = 'https://www.jpl.nasa.gov'
    
    #get current date and time
    pulldate = dt.datetime.now()
    pulldate = pulldate.strftime("%d %B %Y %I:%M:%S %p")
    
    # create mars dictionary
    mars_dict = {}
    
    mars_dict['pulldate'] = pulldate

    # Retrieve page with the requests module
    response = requests.get(news_url)
    # Create BeautifulSoup object; parse with 'html'
    soup = BeautifulSoup(response.text, 'html.parser')

    ########retrieve articlce title and desc
    news_title = soup.find('div',class_="content_title").text
    news_desc = soup.find('div',class_="rollover_description_inner").text

    mars_dict['news_title'] = news_title
    mars_dict['news_desc'] = news_desc

    ######## use splinter to get featured photo
    browser.visit(photo_url)
    # sleep
    time.sleep(3)
    # get html
    html = browser.html
    # parse HTML with Beautiful Soup
    soup = BeautifulSoup(html, 'html.parser')
    # click on the featured photo
    browser.find_by_id('full_image').click()
    # sleep
    time.sleep(3)
    # get soup object with link embeded 
    featured_image_url = soup.find('a',class_="button fancybox").attrs
    # concat dynamic link
    featured_image_url = short_photo_url + featured_image_url["data-fancybox-href"]

    mars_dict['featured_image_url'] = featured_image_url

    ######## Retrieve page with the requests module
    response_weather = requests.get(weather_url)
    # Create BeautifulSoup object; parse with 'lxml'
    soup_weather = BeautifulSoup(response_weather.text, 'html.parser')
    # retrieve tweet weather
    mars_weather = soup_weather.find('p', class_="TweetTextSize TweetTextSize--normal js-tweet-text tweet-text").text
    # remove trailing characters
    mars_weather = mars_weather[:-26]

    mars_dict['mars_weather'] = mars_weather

    ####### get mars facts
    mars_facts_table = pd.read_html(facts_url)
    # take the first table
    facts_df = mars_facts_table[0]
    # add columns
    facts_df.columns = ['category', 'value']
    # set index to category
    facts_df.set_index('category', inplace=True)
    # turn table back into html
    facts_html_table = facts_df.to_html()

    mars_dict['facts_html_table'] = facts_html_table

    link_list = []
    photo_url = []
    title = []

    # get URLs of hemispheres
    response_mars = requests.get(usgs_url)
    soup_mars = BeautifulSoup(response_mars.text, 'html.parser')
    data = soup_mars.findAll('div', class_="item")
    for div in data:
        links = div.findAll('a')
        for a in links:
            link_list.append("https://astrogeology.usgs.gov/" + a['href'])

    for i in link_list:
        response_X = requests.get(i)
        soup_x = BeautifulSoup(response_X.text, 'html.parser')

        for div in soup_x.findAll('div',class_='downloads'):
                a = div.findAll('a')[0]
                photo_url.append(a.attrs['href'])

        for div in soup_x.findAll('div',class_='content'):
                b = div.findAll('h2')[0]
                title.append(b.text)

    hemisphere_image_urls = []

    # create list of dictionaries
    for i, j in zip(title, photo_url):
        hemisphere_image_urls.append({"title": i, "photo_url": j})

    mars_dict['hemisphere_image_urls'] = hemisphere_image_urls

    browser.quit()

    return mars_dict