from bs4 import BeautifulSoup
import requests
import json
import time
import sqlite3
import os
import plotly.graph_objects as go
from flask import Flask, render_template, request

os.chdir('/Users/erinannis/Documents/UMSI/Fall 2020/SI 507/Final Project')

BASE_URL = 'https://findit.library.yale.edu/?f%5Bcreator_sim%5D%5B%5D=Gillray%2C+James%2C+1756-1815%2C+printmaker.&f%5Bdigital_collection_sim%5D%5B%5D=Lewis+Walpole+Library'
CACHE_FILENAME = "gillray_cache.json"
CACHE_DICT = {}

DB_NAME = 'gillray_prints.sqlite'

headers = {
    'User-Agent': 'UMSI 507 Course Project - Python Scraping',
    'From': '<eaannis>@umich.edu',
    'Course-Info': 'https://si.umich.edu/programs/courses/507'
}

# Step 1: Create and Save Cache
def load_cache():
    ''' opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary
    Parameters
    ----------
    None
    Returns
    -------
    The opened cache
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_file_contents = cache_file.read()
        cache = json.loads(cache_file_contents)
        cache_file.close()
    except:
        cache = {}
    return cache

def save_cache(cache):
    ''' saves the current state of the cache to disk
    Parameters
    ----------
    cache: dict
        The dictionary to save
    Returns
    -------
    None
    '''
    cache_file = open(CACHE_FILENAME, 'w')
    contents_to_write = json.dumps(cache)
    cache_file.write(contents_to_write)
    cache_file.close()

def make_url_request_using_cache(url, cache):
    '''Makes a request using the cache 
    Parameters
    ----------
    url: string
        The URL for the webpage endpoint
    cache: dict
    Returns
    -------
    cache[url]: dict value
    '''
    if (url in cache.keys()): # the url is our unique key
        print("Using cache")
        return cache[url]
    else:
        print("Fetching")
        time.sleep(1)
        response = requests.get(url, headers=headers)
        cache[url] = response.text # notice that we save response.text to our cache dictionary. We turn it into a BeautifulSoup object later, since BeautifulSoup objects are nor json parsable. 
        save_cache(cache)
        return cache[url] # in both cases, we return cache[url]

def make_request(url):
    '''Make a request using the baseurl 
    Parameters
    ----------
    baseurl: string
        The URL for the webpage endpoint
    Returns
    -------
    string
        the results of the query as a Python object loaded from JSON
    '''
    response = requests.get(url)
    return response.json()

## function to go to the next page:
def get_next_page_url(soup):
    '''Proceeds to the next page
    Parameters
    ----------
    soup: a beautiful soup object
    Returns
    -------
    none
    '''
    next_page = soup.find('div', class_='pagination').find(class_=None).find_all('a')[1]['href']

    if (next_page is not None):
        next_page_url = 'https://findit.library.yale.edu/' + next_page
        return next_page_url
    else:
        return None

    '''
    def crawl_web(seed, max_pages):
    tocrawl = [seed]
    crawled = []
    while tocrawl:
        page = tocrawl.pop()
        if page not in crawled and len(crawled) < max_pages:
            union(tocrawl, get_all_links(get_page(page)))
            crawled.append(page)
    return crawled
    '''

# Load the cache, save in global variable
CACHE_DICT = load_cache()

# Step 2: Create DB with Tables
def create_db():
    '''Creats and SQLite Database 
    Parameters
    ----------
    none
    Returns
    -------
    none
    '''
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    drop_techniques_sql = 'DROP TABLE IF EXISTS "Techniques"'
    drop_producers_sql = 'DROP TABLE IF EXISTS "Printsellers"'
    drop_prints_sql = 'DROP TABLE IF EXISTS "Prints"'

    create_techniques_sql = '''
        CREATE TABLE IF NOT EXISTS "Techniques" (
            "Id"    INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            "Technique" TEXT NOT NULL UNIQUE,
            "Website"   TEXT
        );
    '''

    create_printsellers_sql = '''
        CREATE TABLE IF NOT EXISTS "Printsellers" (
            "Id"    INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            "Name"  TEXT NOT NULL UNIQUE,
            "Website" TEXT
        );
    '''
    create_prints_sql = '''
        CREATE TABLE IF NOT EXISTS "Prints" (
            "Id"    INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            "Title" TEXT NOT NULL,
            "Date" TEXT,
            "TechniqueId"   INTEGER,
            "PrintsellerId" INTEGER,
            "Description"   TEXT,
            "Website"   TEXT NOT NULL
        )
    '''

    cur.execute(drop_techniques_sql)
    cur.execute(drop_producers_sql)
    cur.execute(drop_prints_sql)
    cur.execute(create_techniques_sql)
    cur.execute(create_printsellers_sql)
    cur.execute(create_prints_sql)
    conn.commit()
    conn.close()

# Step 3: Get all info, load into tables
def load_tables():
    '''Crawls/scrapes webpages to get information for the DB tables
    Formats information to go into the tables
    Loads information into the tables
    Parameters
    ----------
    none
    Returns
    -------
    none
    '''

    print_names = []
    print_descriptions = []
    print_dates = []
    print_urls = []
    printsellers = []
    techniques = []

    insert_printsellers = '''
        INSERT OR IGNORE INTO Printsellers
        VALUES (NULL, ?, 'http://www.james-gillray.org/printsellers.html')
    '''

    insert_techniques = '''
        INSERT OR IGNORE INTO Techniques
        VALUES (NULL, ?, 'http://www.james-gillray.org/tech_printing.html')
    '''

    insert_prints = '''
        INSERT INTO Prints
        VALUES (NULL, ?, ?, ?, ?, ?, ?)
    '''
    ## Make the soup for the main page
    url_text = make_url_request_using_cache(BASE_URL, CACHE_DICT)
    soup = BeautifulSoup(url_text, 'html.parser') # convert our saved cache data to a BeautifulSoup object

    next_page_url = get_next_page_url(soup=soup)

    ## For each print listed
    while len(print_names) <= 188:
        prints_list_parent = soup.find('div', id='documents')
        prints_listing_divs = prints_list_parent.find_all('div', recursive=False)
        for prints_listing_div in prints_listing_divs:

            ## extract the print details URL
            print_link_tag = prints_listing_div.find('a')
            print_details_path = print_link_tag['href']
            print_details_url = 'https://findit.library.yale.edu' + print_details_path
            print_urls.append(print_details_url)

            ## Make the soup for print details
            url_text = make_url_request_using_cache(print_details_url, CACHE_DICT)
            soup = BeautifulSoup(url_text, 'html.parser')

            # Extract print name
            print_name = soup.find('h1')
            print_name = print_name.text.strip().replace(' [graphic].', '')
            print_names.append(print_name)
            
            # Extract print description
            print_description = soup.find('dd', class_='blacklight-abstract_tsim')
            if (print_description is not None):
                print_description = print_description.text.strip()
                print_descriptions.append(print_description)
            
            # Extract print date
            try:
                print_date = soup.find('dd', class_='blacklight-copyright_tsim')
                if (print_date is not None):
                    print_date = print_date.text.strip().replace('[', '').replace(']','')
                    print_dates.append(print_date)
            except:
                print('No Date')

            # Extract print publisher
            print_publisher = soup.find('dd', class_='blacklight-subject_name_tsim')
            if (print_publisher is not None):
                print_publisher = str(print_publisher).split('>')
                for element in print_publisher:
                    element = element.split('<dd')
                    element = element[0].split('<br/')
                    for item in element:
                        if 'publisher' in item:
                            item = item.replace('</dd', '')
                            item = item.replace(', publisher.', '')
                            printsellers.append(item)

            # Extract print technique
            print_technique = soup.find('dd', class_='blacklight-genre_ssim')
            if (print_technique is not None):
                print_technique = str(print_technique).split('>')
                print_technique = print_technique[1].split('--')
                print_technique = print_technique[0]
                techniques.append(print_technique)

        if len(print_names) == 188:
            break
        else:
            url_text = make_url_request_using_cache(next_page_url, CACHE_DICT)
            soup = BeautifulSoup(url_text, 'html.parser') # convert our saved cache data to a BeautifulSoup object
            try:
                next_page_url = get_next_page_url(soup=soup)
            except:
                break

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    printseller_ids = []
    for name in printsellers:
        cur.execute(insert_printsellers, [name])
        printseller_id = cur.lastrowid
        printseller_ids.append(printseller_id)
    
    technique_ids = []
    for technique in techniques:
        cur.execute(insert_techniques, [technique])
        technique_id = cur.lastrowid
        technique_ids.append(technique_id)

    for name, date, technique_id, printseller_id, description, url in zip(print_names, print_dates, technique_ids, printseller_ids, print_descriptions, print_urls):
        cur.execute(insert_prints, [
            name,
            date,
            technique_id,
            printseller_id,
            description,
            url
        ])

    conn.commit()
    conn.close()

# Step 4: Make Bar Chart
def create_bar_chart(xvals, yvals):
    '''Creates a bar chart
    Parameters
    --------
    xvals, yvals = lists
    '''
    bar_data = go.Bar(x=xvals, y=yvals)
    basic_layout = go.Layout(title="A Bar Graph") 
    #Can also include gridline, fonts, etc. - colors too???
    fig = go.Figure(data=bar_data, layout=basic_layout) 
    fig.show() #Creates HTML page, renders the graph object

# Step 5: Make Scatter Plot
def create_scatter_plot(xvals, yvals, mode):
    ''' Creates a scatter plot
    Parameters
    --------
    xvals, yvals = lists
    '''
    scatter_data = go.Scatter(x=xvals, y=yvals, mode='markers')
    # with Scatter: x values = quantitative (can't have qualitative x value), use fig.write_html("scatter.html", auto_open=True) #replaces fig.show(), saves file as well as shows it
    basic_layout = go.Layout(title="A Scatter Plot") 
    #Can also include gridline, fonts, etc. - colors too???
    #See citiesPopArea.py to see how to label elements on scatter plot
    fig = go.Figure(data=scatter_data, layout=basic_layout) 
    fig.show() #Creates HTML page, renders the graph object

'''
cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix']
population = [ 8398748, 3990456, 2705994, 2325502, 1660272]
area = [301.5, 468.7, 227.3, 637.5, 517.6]
text = cities
marker={'symbol':'square', 'size':30, 'color': 'green'},
mode='markers+text'
create_scatter_plot(area, population, mode)
'''

# Step 6: Flask? or maybe Django?

# Step 7: Interactive commands
if __name__ == "__main__":
    create_db()
    load_tables()
