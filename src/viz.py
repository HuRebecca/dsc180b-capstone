#!/usr/bin/env python

'''
FILE: 

DESCRIPTION: 
'''
import pandas as pd
import os
from collections import Counter
import matplotlib.pylab as plt
import gzip
import numpy as np
import warnings
warnings.filterwarnings("ignore") 


'''
FUNCTION: 

INPUTS: path: path to folder containing each year's movies

OUTPUTS: 

DESCRIPTION: 
'''
def num_movies_per_genre(path):
    year_genres = []
    most_pop_genres = ['Comedy', 'Drama', 'Western']
    for file in os.listdir(path):
        if "ipynb" in file:
            continue
        yearly = []
        year = os.path.splitext(file)[0]
        year = int(year)
        filename = os.path.join( path, file)
        data = pd.read_csv(filename, header = None)
        num_movies = len(data)
        for genre in data[2]:
            cleaned = (genre.replace("'", '').replace("[", '').replace("]", '').replace("\\n", ''))
            cleaned = cleaned.split(', ')
            for elem in cleaned:
                if elem != '':
                    if elem.strip() in most_pop_genres:
                        yearly.append(elem.strip())
        yearly = Counter(yearly)
        for key in most_pop_genres:
            if key not in yearly:
                yearly[key] = 0
        yearly = sorted(yearly.items())
        yearly.append(('placeholder', year))
        yearly.append(('num_movies', num_movies))
        counts = []
        for tup in yearly:
            counts.append(tup[1])
        year_genres.append(counts)
    df = pd.DataFrame(year_genres)
    df.columns = ['Comedy', 'Drama', 'Western', 'year', 'num_movies']

    return df


'''
FUNCTION: 

INPUTS: 

OUTPUTS: 

DESCRIPTION: 
'''
def plot_time_periods(df, fig_file_name, plot_title, most_pop_genres):
    bins = np.arange(1930, 2015, step = 5)
    df['time'] = pd.cut(df['year'], bins, include_lowest= True)
    grouped_years = df.groupby('time').sum()
    grouped_years = grouped_years.reset_index()
    intervals = list(grouped_years['time'])
    start = [int(round(x.left)) for x in intervals]

    grouped_years['start'] = start
    
    for genre in most_pop_genres:
        grouped_years[genre] = grouped_years[genre]/grouped_years['num_movies']
    most_pop_genres.append('start')
    grouped_years = grouped_years[most_pop_genres]
    grouped_years = grouped_years.set_index('start')
    ax = grouped_years.plot.bar(figsize = (10, 10), title = plot_title)
    ax.set_xlabel('Start of Time Period')
    ax.set_ylabel('Percentage of All Movies')
    fig = ax.get_figure()
    fig.show()
    fig.savefig(fig_file_name)


'''
FUNCTION: 

INPUTS: oscars_file: csv for oscars nominations/winners
        path: path to folder containing each year's movies

OUTPUTS: 

DESCRIPTION: 
'''
def oscars_genres(oscars_file, path):
    genre_list = []
    most_pop = ['Drama', 'Comedy', 'Biography']
    oscars_file = pd.read_csv(oscars_file)
    
    for i, row in oscars_file.iterrows():
        yearly = []
        num_movies = 0
        year = row['Year']
        file = str(year)+'.csv'
        if year not in [1999, 2000] and year < 2008:
            filename = os.path.join(path, file)
            data = pd.read_csv(filename, header = None)
            movie = row['Movie']
            genre = data[data[0] == movie][2].values
            num_movies += 1
            if len(genre) == 0:
                cleaned == None
            else:
                genre = genre[0]
                cleaned = (genre.replace("'", '').replace("[", '').replace("]", '').replace("\\n", ''))
                cleaned = str(cleaned).split(', ')
                cleaned = cleaned[0]
        else:
            cleaned = None
        if cleaned in most_pop:
            yearly.append(cleaned)
        yearly = Counter(yearly)
        for key in most_pop:
            if key not in yearly:
                yearly[key] = 0
                
        yearly = sorted(yearly.items())
        yearly.append(('placeholder', year))
        yearly.append(('num_movies', num_movies))
        counts = []
        for tup in yearly:
            counts.append(tup[1])
        genre_list.append(counts)
    df = pd.DataFrame(genre_list)
    df.columns = ['Biography', 'Comedy', 'Drama', 'year', 'num_movies']
        
    return df


def create_race(ethnicities):
    '''
    ethnicities: list of strings
    '''
    race_dict = {'Black': ['AfricanAmerican', 'Ugandan'],
             'Asian': ['Indian', 'Chinese'],
             'Hispanic/Latino': ['Mexican']
            }
    
    ethnicity_string = ''.join(str(elem) for elem in ethnicities)
    for k in race_dict.keys():
        for e in race_dict[k]:
            if e in ethnicity_string:
                return k
    return 'White'

def get_race(df):
    df['race'] = df['ethnicity'].apply(create_race)
    onehot = pd.get_dummies(df['race'])
    df = df.join(onehot)
    df_eth = df[['year','Asian', 'Black', 'Hispanic/Latino', 'White']]
    df_eth['Non_White'] = df_eth['Asian'] + df_eth['Black'] + df_eth['Hispanic/Latino']
    df_eth['Total'] = df_eth['Non_White'] + df_eth['White']
    return df_eth

def create_time_periods(df):
    bins = np.arange(1930, 2015, step = 5)
    df['time'] = pd.cut(df['year'], bins, include_lowest= True)
    grouped_years = df.groupby('time').sum()
    grouped_years = grouped_years.reset_index()
    intervals = list(grouped_years['time'])
    start = [int(round(x.left)) for x in intervals]

    grouped_years['start'] = start
    grouped_years = grouped_years[['start','Asian', 'Black', 'Hispanic/Latino', 'White', 'Non_White', 'Total']]
    for race in ['Asian', 'Black', 'Hispanic/Latino', 'White', 'Non_White']:
        grouped_years[race] = grouped_years[race]/grouped_years['Total']
    return grouped_years

def plot_compare(df, cols, outdir):
    styles=['b', 'b--', 'y', 'y--']
    labels = ['Oscars Non White Nom', 'GG Non White Nom', 'Oscars Black Nom', 'GG Black Nom']
    ax = df.plot(x = "start", y = cols, style = styles, figsize = (10, 10),\
                 title = 'Oscars and Golden Globes Race Distribution over Time')
    ax.legend(labels = labels)
    ax.set_xlabel('Start of Time Period')
    ax.set_ylabel('Number of Actors')
    fig = ax.get_figure()
    fig.show()
    fig.savefig(outdir + 'race_dist_over_time.png')
    
    
'''
FUNCTION: 

INPUTS: 

OUTPUTS: 

DESCRIPTION: 
'''
def create_plot_oscar_genre_dist_over_time(indir, outdir):
    year_genres = num_movies_per_genre(indir)

    fig_file_name = "genre_dist_over_time.png"
    plot_title = 'Genre Distribution of All Movies over Time'
    most_pop_genres = ['Comedy', 'Drama', 'Western']
    plot_time_periods(year_genres, outdir + fig_file_name, plot_title, most_pop_genres)

    
'''
FUNCTION: 

INPUTS: 

OUTPUTS:

DESCRIPTION: 
'''
def create_plot_oscar_nominated_genre_dist_over_time(indir_oscars, indir_movie_data, outdir):
    genre_list = oscars_genres(indir_oscars, indir_movie_data)
    
    fig_file_name = "genre_dist_nominated_over_time.png"
    plot_title = 'Genre Distribution of Oscar Nominated Movies over Time'
    most_pop_genres = ['Comedy', 'Drama', 'Biography']
    plot_time_periods(genre_list, outdir + fig_file_name, plot_title, most_pop_genres)
    

'''
FUNCTION: 

INPUTS: 

OUTPUTS:

DESCRIPTION: 
'''
def create_comparison_oscars_gg(indir, outdir):
    golden = pd.read_csv(indir[2])
    golden.head()
    
    golden_eth = get_race(golden)
    golden_eth['year'] = golden_eth['year'].str.replace("\[1\]", '')
    golden_eth['year'] = pd.to_numeric(golden_eth['year'])
   
    oscars = pd.read_csv(indir[1])
    oscars.columns = map(str.lower, oscars.columns)
    oscars_eth = get_race(oscars)

    oscars_grouped = create_time_periods(oscars_eth)
    golden_grouped = create_time_periods(golden_eth)
    combined = pd.merge(oscars_grouped, golden_grouped, on = 'start', suffixes = ('_osc', '_gold'))
    
    plot_compare(combined, ['Non_White_osc', 'Non_White_gold', 'Black_osc', 'Black_gold'], outdir)


'''
FUNCTION: 

INPUTS: 

OUTPUTS: 

DESCRIPTION: 
'''
def create_plots(indir, outdir):
    if outdir and not os.path.exists(outdir[0]):
        os.makedirs(outdir[0])
        
    create_plot_oscar_genre_dist_over_time(indir[0], outdir[0])
    create_plot_oscar_nominated_genre_dist_over_time(indir[1], indir[0], outdir[0])
    create_comparison_oscars_gg(indir, outdir[0])
    
    
    
    