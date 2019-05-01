# -*- coding: utf-8 -*-
"""
Created on Sat Apr 27 09:08:12 2019

@author: rossp
"""

import pandas as pd
from bs4 import BeautifulSoup
import urllib.request

def scrape_world_pop():
    url = 'https://www.worldometers.info/world-population/world-population-by-year/'
    response = urllib.request.urlopen(url) 
    html = response.read()
    soup = BeautifulSoup(html, 'html.parser')
    clean_soup = soup.prettify()
    start = clean_soup.find('<th>')
    end = clean_soup.find('source')
    html_string = clean_soup[start:end]
    indexers = []
    for i in range (1951, 2020):
       ind = html_string.find(str(i))
       indexers.append(ind)
    indexers = indexers[::-1]
    pre_data = []
    for i in indexers:
        html_short = html_string[i:i+120]
        findyear = html_short[:4]
        findpop = html_short[90:][:html_short[90:].find('\n')]
        findpop = findpop.replace(",","")
        findpop = findpop.replace(" ","")
        row = [findyear, findpop]
        pre_data.append(row)
    pop_df = pd.DataFrame(pre_data,columns=['year','population'])
    pop_df['year'] = pop_df['year'].astype(int)
    return pop_df      

def get_movie_data():
    df = pd.read_csv('tmdb_5000_movies.csv')
    df['year'] = df['release_date'].str[:4]
    df= df[df.year.notnull()] # exclude non nulls for future join
    df.year = df.year.astype(int)# strip release year from date
    df.revenue = df.revenue.astype(float)
    df = df[df.year <= 2018]
    df = df[df.revenue > 500000]
    return df

def get_cpi_data():
    df = pd.read_excel('avgcpi.xlsx')
    df.year = df.year.astype(int)
    df.avg_monthly_cpi = df.avg_monthly_cpi.astype(float)
    return df

def main():
    # gather datasets
    world_pop = scrape_world_pop()
    movie_data = get_movie_data()
    cpi_data = get_cpi_data()
    # merge together datasets
    base_data = movie_data.merge(world_pop, how='left', on='year')
    base_data = base_data.merge(cpi_data, how='left',  on='year')
    # build analytical data points
    base_data['revenue_adjusted'] = 251.107*base_data.revenue.div(base_data.avg_monthly_cpi) #/ base_data.avg_monthly_cpi # CPI adjusted to 2018 prices (251.107 is the avg monthly CPI for 2018)
    base_data['adj_rev_per_population'] = base_data.revenue_adjusted / base_data.population.astype(float)
    base_data = base_data.sort_values(by=['adj_rev_per_population'])
    base_data['ranking'] = base_data.adj_rev_per_population.rank(pct=True)
    base_data.to_excel('results.xlsx')
        
if __name__ == '__main__':
    main()
