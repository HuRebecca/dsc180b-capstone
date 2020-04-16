#!/usr/bin/env python

'''
FILE: dataIngestion.py

DESCRIPTION: This file collects the data needed for this project
'''

import requests
from bs4 import BeautifulSoup
import re
import json
import csv
import os
from pathlib import Path
import pandas as pd
import re
from tqdm import tqdm
import os


'''
FUNCTION: get_table(website)

INPUTS: website: url for wiki page with list of nominees and winners

OUTPUTS: returns the Wikipedia html table that needs to be scraped 

DESCRIPTION: This function takes the wikipedia link and finds the table that 
  contains all the winners and nominees for the Best Actor Oscar award on that webpage
  and returns the table.
'''
def get_table(website):
    #webpage url
    url = website
    page = requests.get(url)
    
    #creates beautiful soup object
    soup = BeautifulSoup(page.content, 'html.parser')
    table = soup.find_all('table')[2]
    
#return the correct table
return table


'''
FUNCTION: create_csv_of_actors(website, outdir)

INPUTS: website: url for wiki page with list of nominees and winners
        outdir: directory to write csv files to

OUTPUTS: None (writes csv to file)

DESCRIPTION: This function parses through the table of the Best Actor Oscar award 
  winners and nomineed writes the table to a csv file.
'''
def create_csv_of_actors(website ,outdir): #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    #gets the correct table to parse
    table = get_table(website)
    
    #loops through all the rows in the table
    for row in table.find_all('tr'):
        td_tags = row.find_all('td')
        th_tags = row.find_all('th')

         #initialize fields to be scraped
        count = 1
        actor = ''
        role = ''
        movie = ''
        link = None
        winner = False

        #if the row in the table is not a full row then skip
        if len(td_tags) == 1:
            continue

        #loop through each column in the row and get the winners
        for th in th_tags:
            year = th.text.strip("\n")
            year = year[0: year.find("(")]
            winner = True
            
        #loop through each column in the row
        for col in td_tags:  
          
            #collect the actor name
            if count == 1:
                actor = col.text.strip("\n")
                actor = actor[0: actor.find("[")]

            #collect the character name
            elif count == 2:
                role = col.text.strip("\n")
            
            #collect the movie name
            elif count == 3:
                movie = col.text.strip("\n")
            count = count + 1

        #get the link for the wikipedia page about the movie
        for a in row.findAll('a'):
            if movie in a.text:
                link = "https://en.wikipedia.org/" + a.get('href')
                break

        #create a row to write to the csv file
        if winner == True:
            lst = [year, actor, role, movie, link, True]
            winner = False
        else:
            lst = [year, actor, role, movie, link, False]
            
        #write row to csv file
        with open(outdir + "actorsTemp.csv",'a+', newline='') as outF:
                writer = csv.writer(outF, dialect='excel')
                writer.writerow(lst)
                

'''
FUNCTION: add_ethnicity_to_nominees_and_winners()

INPUTS: outdir: directory to write csv files to

OUTPUTS: None (writes changes to csv file)

DESCRIPTION: This function takes the created actors csv file and add the actor's ethnicity to it.
'''
def add_ethnicity_to_nominees_and_winners(outdir):
     #loads the actors csv file
    table = pd.read_csv("actors.csv")
    table.head()

    #get a list of the actors and reformat it to be used in url
    actors = table["Actor"]
    actors = actors.values
    actors_cleaned = [x.replace(" ", "-") for x in actors]

    #initialize list to store ethnicities of actors
    ethnicity = []
    
    #loop through all actors in the file
    for actor in tqdm(actors_cleaned):
      
        #find the webpage with ethnicity info on the actor
        url = 'https://ethnicelebs.com/{}'.format(actor)
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
       
        #initialize variables to help collect data
        found = False
        lst = []
        
        #loop through all the text in the html of the webpage
        for p in soup.findAll('p'):
            
            #find the one about the ethnicity
            if "Ethnicity:" in p.text:
                
                #clean the string with info about ethnicity
                lst = p.text.split(" ")[1:]

                lst = [re.sub(r'\W+', '', x) for x in lst]

                lst = [x.replace("mother", "") for x in lst]
                lst = [x.replace("father", "") for x in lst]

                lst = [x for x in lst if x != ""]
                lst = [x for x in lst if ord(x[0]) > 64]
                lst = [x for x in lst if ord(x[0]) < 91]
                
                #append to master list of lists
                ethnicity.append(lst)
                found = True
                
                #do not coninute looking
                break   
                
        #if webpage or info not found then append empty list
        if found == False:
            ethnicity.append(lst)
            
    #add ethnicity to table and write to csv file
    table["Ethnicity"] = ethnicity
    
    table.to_csv(outdir + 'actorsWithEthnicity.csv', index = False)
    
    
'''
FUNCTION: create_csv_per_year(tableNum, year, outdir)

INPUTS: tableNum: which table on the html page to scrape
        year: which year of movies to scrape
        outfir: diectory to write csv files to

OUTPUTS: None (writes to csv file)

DESCRIPTION: This function takes a Wikipedia page of all the movies created in the USA for a particular
    year and scrapes the information on the movie and the list of main characters' actors and writes
    the table to a csv file. 
'''
def create_csv_per_year(tabNum, year, outdir):
    os.mkdir(outdir + 'ListOfMovPerYear')
    
    #find the correct url for that year and create a beautiful soup object
    url = 'https://en.wikipedia.org/wiki/List_of_American_films_of_{}'.format(year)
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    #scrape every table from the first one of movies starting with ("A" - "B")
    #till the last table of movies starting with ("Z")
    for tab in soup.find_all('table')[tabNum:]:
        td_tags = tab.find_all('td')
        
        #intialize variables to help parse the file
        count = 0
        title = ""
        actors = []
        
        #loop through the tables on the webpage
        for i in td_tags:
            
            #if the table is not a table containing movie info
            if len(td_tags) < 50 :
                continue

            #scrape the title
            if count == 0:
                title = i.text

            #scrape the actors info
            elif count == 2:
                actors = i.text.split(",")

            count = count + 1
            
            #reset counter and fields every row and write row to csv file
            if count == 5:
                lst = [title, actors]
                with open(outdir + 'ListOfMovPerYear' + "/{}.csv".format(year),'a+', newline='') as outF:
                    writer = csv.writer(outF, dialect='excel')
                    writer.writerow(lst)
                
                count = 0
                title = ""
                actors = []
                

'''
FUNCTION: all_movies_per_year(outdir)

INPUTS: outdir: directory to write csv files to

OUTPUTS: None (writes to csv file)

DESCRIPTION: This function calls on other functions to create the csv
    files for the all the movies made each year between 1934 and 2019
'''
def all_movies_per_year(outdir):
    for year in range(1934, 1993):
        create_csv_per_year(1,year, outdir)

    for year in range(1993, 2020):
        create_csv_per_year(2,year, outdir)

        
def collect_data(websites, outdir):
  if outdir and not os.path.exists(outdir):
        os.makedirs(outdir)
  
  create_csv_of_actors(websites[0],outdir)
  
  #-----TODO - clean up actors.csv -------
  
  add_ethnicity_to_nominees_and_winners(outdir)
  
  all_movies_per_year(outdir)
  
  
