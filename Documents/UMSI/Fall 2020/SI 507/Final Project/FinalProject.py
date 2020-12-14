# Step 1: Create and Save Cache
# Step 2: Create Print and URL dictionary
# Step 3: Create Print instance with necessary information for all my tables
# Step 4: Create all the tables in my database
# Step 5: Populate each table with relevant information
#   a. Create list of each record using for loop - e.g., ('About', 'LastName', 'FirstName') for each producer
#   b. Use INSERT INTO <Table Name> VALUES<list of my values> (see slides week 11, L1)
#   c. NOTE: can't insert fewer values into table than you have fields. To make this work, specify fields that I want to insert into - 
#       how do with for loop? Maybe make life easy on myself and/or write into program to put "null" into empty fields so I don't have
#       to deal with this? Or use try/except when I know things might not be there....
#   d. NOTE: INSERT modifies DB, REMEMBER TO CALL connection.commit() after inserts (can do after batch of inserts)
#   e. NOTE: can use question marks as placeholders, then use lists to populate values later:
#       import sqlite3
#       conn = sqlite3.connect("Teams2.sqlite")
#       cur = conn.cursor()
#       insert_teams = '''
#           INSERT INTO teams
#           VALUES (NULL, ?, ?, ?, ?)
#       '''
#       portland_trailblazers = ["Moda Center", "Portland", "2", "Trailblazers"]
#       cur.execute(insert_teams, portland_trailblazers) #cursor
#       conn.commit() #connection
# Step 6: Make plots
#   a. Bar charts for: different producers, different techniques, different titles?
#   b. Scatter chart for dates
# Step 7: Interactive commands to sort data

#################################
##### Name: Erin Annis
##### Uniqname: eaannis
#################################

from bs4 import BeautifulSoup
import requests
import json
import time
import sqlite3
import re
import csv
import os
import numpy as np

os.chdir('/Users/erinannis/Documents/UMSI/Fall 2020/SI 507/Final Project')

BASE_URL = 'http://www.james-gillray.org/catalog_insert.html'
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
    cache_dict: dict
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

def make_request(baseurl):
    '''Make a request to the Web API using the baseurl and params
    Parameters
    ----------
    baseurl: string
        The URL for the API endpoint
    params: dictionary
        A dictionary of param: param_value pairs
    Returns
    -------
    string
        the results of the query as a Python object loaded from JSON
    '''
    response = requests.get(baseurl)
    return response.json()

# Load the cache, save in global variable
CACHE_DICT = load_cache()

# Step 2: Build print and url dictionary
def build_print_url_dict():
    ''' Make a dictionary that maps print name to print page url from GET RIGHT WEBSITE

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a print name and value is the url
        e.g. {'six pence a day':'http://www.james-gillray.org/pop/sixpence.html'}
        NOTE: title needs to be lower case
    '''
    print_url_dict = {}
    ## Make the soup for the main page
    url_text = make_url_request_using_cache(BASE_URL, CACHE_DICT)
    soup = BeautifulSoup(url_text, 'html.parser') # convert our saved cache data to a BeautifulSoup object

    prints_list_parent = soup.find_all('a')
    
    prints_list = []
    for x in prints_list_parent:
        prints_list.append(str(x))
    
    for print_list in prints_list:
        ## extract the print details URL
        print_details_url = 'http://www.james-gillray.org/' + print_list.split("'")[1]
        
        ## Make the soup for print details
        url_text = make_url_request_using_cache(print_details_url, CACHE_DICT)
        soup = BeautifulSoup(url_text, 'html.parser')
        ## extract print name
        print_name = soup.find('h1')
        print_name = print_name.text.strip()

        ## add print url and name to dictionary
        print_url_dict[print_name.lower()]=print_details_url
    print(len(print_url_dict))
    return print_url_dict

# Step 3: Get date, BM Number
def build_print_bm_dict():
    ''' Make a dictionary that maps print name to print page url from GET RIGHT WEBSITE

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a print name and value is the url
        e.g. {'six pence a day':'http://www.james-gillray.org/pop/sixpence.html'}
        NOTE: title needs to be lower case
    '''
    pass #Think about building this....
    '''
    #print_bm_dict = {}
    ## Make the soup for the main page
    url_text = make_url_request_using_cache(BASE_URL, CACHE_DICT)
    soup = BeautifulSoup(url_text, 'html.parser') # convert our saved cache data to a BeautifulSoup object

    bm_list_parent = soup.find_all('td')
    #td_text = bm_list_parent.text.strip()
    return bm_list_parent

    bms_list = []
    for x in bm_list_parent:
        x = bm_list_parent.find('')
        print(x)
        print(type(x))
        return x
        #bms_list.append(str(x))
    #return bms_list

    for bm_list in bms_list:
        ## extract the print's BM number
        print_bm_number = bm_list.split("'")
        print(print_bm_number)
        return print_bm_number

        ## Make the soup for print details
        url_text = make_url_request_using_cache(print_details_url, CACHE_DICT)
        soup = BeautifulSoup(url_text, 'html.parser')
        ## extract print name
        print_name = soup.find('h1')
        print_name = print_name.text.strip()

        ## add print url and name to dictionary
        print_url_dict[print_name.lower()]=print_details_url
    print(len(print_url_dict))
    return print_url_dict
    '''

# Step 3: Get print instance information - some from james-gillray.org, and some from British Museum file
def get_print_instance(print_url):
    '''Make an instances from a national site URL.
    
    Parameters
    ----------
    print_url: string
        The URL for a print page in nps.gov CHANGE
    
    Returns
    -------
    instance
        a print instance
        Attributes: museum_number, print_description, print_technique, print_producer_type, print_producer_first_name, print_producer_last_name, print_inscription, print_curator_comments
    '''

    ## Make the soup for the site page
    url_text = make_url_request_using_cache(print_url, CACHE_DICT)
    soup = BeautifulSoup(url_text, 'html.parser') # convert our saved cache data to a BeautifulSoup object

    print_description = str()
    for p in soup.find_all('p'):
        if p.find(class_ = 'centered'):
            continue
        elif p.find('figcaption'):
            continue
        elif p.find('strong'):
            continue
        else:
            p = p.text.strip().replace('\n', ' ').replace("\\", "")
            print_description = print_description + p + " "
    
    contents = []
    with open('SI507_Final_Project_Data.txt', 'r') as file_object:
        contents = [row for row in csv.reader(file_object, delimiter='\t')]
    

    contents_dict = {}
    for content in contents[1:]:
        #title_list.append(content[3])
        contents_dict[content[2]] = [content[i] for i in (0, 1, 3, 7, 14, 20, 22, 23)]
    
    return contents_dict
    
    '''
    try: #NOTE: there is more than one technique
        print_techniques = soup.find(class_='object-detail_data-term').find('Technique')
        for print_technique in print_techniques:
            print_technique = print_techniques.find('href').find('vterm')
            print_technique = print_technique.text.strip()
    except:
        print_technique = "N/A"
    try: #NOTE: there is more than one producer type
        print_made_by = soup.find(class_='object-detail_data-description').find('Print made by')
        print_made_by = print_made_by.text.strip()
    except:
        print_made_by = "N/A"
    try: #NOTE: there is more than one producer name
        print_producer_name = soup.find(class_='object-detail_data-description').find('href').find('vterm')
        print_producer_name = print_producer_name.text.strip()
    except:
        print_producer_name = "N/A"
    try:
        print_inscription = soup.find(class_='object-detail_data-description-list').find('Inscription content:').find('span')
        if (print_inscription is not None):
            print_inscription = print_inscription.text.strip()
    except:
        print_inscription = "N/A"
    try:
        print_curator_comments = soup.find(class_='object-detail_data-term').find("Curator's comments").find('span')
        if (print_curator_comments is not None):
            print_curator_comments = print_curator_comments.text.strip()
    except:
        print_curator_comments = "N/A"

    return museum_number, print_description, print_technique, print_made_by, print_producer_name, print_inscription, print_curator_comments
    '''
x = get_print_instance('http://www.james-gillray.org/pop/whore.html')
#print(x)
print(type(x))
print(len(x))
"""
# Step 4: Create tables in database
def create_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    drop_techniques_sql = 'DROP TABLE IF EXISTS "Techniques"'
    drop_producers_sql = 'DROP TABLE IF EXISTS "Producers"'
    drop_prints_sql = 'DROP TABLE IF EXISTS "Prints"'

    create_techniques_sql = '''
        CREATE TABLE IF NOT EXISTS "Techniques" (
            "Id"    INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            "Technique" TEXT NOT NULL
        );
    '''
    create_producers_sql = '''
        CREATE TABLE IF NOT EXISTS "Producers" (
            "Id"    INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            "Role" TEXT NOT NULL,
            "LastName"  TEXT NOT NULL,
            "FirstName" TEXT NOT NULL
        );
    '''
    create_prints_sql = '''
        CREATE TABLE IF NOT EXISTS "Prints" (
            "Id"    INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            "MuseumNumber"  TEXT NOT NULL,
            "Title" TEXT NOT NULL,
            "Description"   TEXT NOT NULL,
            "TechniqueId"   INTEGER NOT NULL,
            "ProducerId"    INTEGER NOT NULL,
            "Inscriptions"  TEXT,
            "CuratorComments"   TEXT,
            "Website"   TEXT NOT NULL
        )
    '''
    cur.execute(drop_techniques_sql)
    cur.execute(drop_producers_sql)
    cur.execute(drop_prints_sql)
    cur.execute(create_techniques_sql)
    cur.execute(create_producers_sql)
    cur.execute(create_prints_sql)
    conn.commit()
    conn.close()

# Step 5a: Load data into Techniques table
def load_techniques():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    insert_techniques = '''
        INSERT INTO Techniques
        VALUES (NULL, ?)
    '''

    conn.commit()
    conn.close()

# Step 5b: Load data into Producers table
def load_producers():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    
    insert_producers = '''
        INSERT INTO Producers
        VALUES (NULL, ?, ?, ?)
    '''

    conn.commit()
    conn.close()

# Step 5c: Load data into Prints table
def load_prints():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    insert_prints = '''
        INSERT INTO Prints
        VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?)
    '''

    conn.commit()
    conn.close()

# Step 6a: Create bar chart
def create_bar_chart(xvals, yvals):
    '''
    ????
    Parameters
    --------
    xvals, yvals = lists
    '''
    bar_data = go.Bar(x=xvals, y=yvals)
    #basic_layout = go.Layout(title="A Bar Graph") 
    #Can also include gridline, fonts, etc. - colors too???
    fig = go.Figure(data=bar_data, layout=basic_layout) 
    fig.show() #Creates HTML page, renders the graph object

# Step 6b: Create scatter plot
def create_scatter_plot(xvals, yvals):
    '''
    ????
    Parameters
    --------
    xvals, yvals = lists
    '''
    scatter_data = go.Scatter(x=xvals, y=yvals)
    # with Scatter: x values = quantitative (can't have qualitative x value), use fig.write_html("scatter.html", auto_open=True) #replaces fig.show(), saves file as well as shows it
    #basic_layout = go.Layout(title="A Bar Graph") 
    #Can also include gridline, fonts, etc. - colors too???
    # For scatter plot, use mode = 'markers' - see documentation, can change symbol, size, color, etc. of markers
    #See citiesPopArea.py to see how to label elements on scatter plot
    fig = go.Figure(data=scatter_data, layout=basic_layout) 
    fig.show() #Creates HTML page, renders the graph object

# Step 7: Interactive commands
if __name__ == "__main__":
    pass
    # params = &page=1 through &page=10
"""

"""
Plotly: see week 11 Further Reading for documentation
"""