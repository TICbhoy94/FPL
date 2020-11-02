# -*- coding: utf-8 -*-
"""
Created on Mon Nov  2 13:50:28 2020

@author: Danie
"""

# Load libraries
from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
import time

# connect to URL and read text
url = "https://fantasy.premierleague.com/entry/4808477/event/6"


# for headless scraping
options = webdriver.FirefoxOptions()
options.add_argument('-headless')
driver = webdriver.Firefox(executable_path = r'C:\Program Files (x86)\SeliniumDrivers\geckodriver.exe',
                           options = options)
driver.get(url)
time.sleep(1)


html = driver.page_source
soup = BeautifulSoup(html)


 # change view to list to access more player information
element = driver.find_element_by_xpath("/html/body/main/div/div[2]/div[2]/div[1]/div[4]/div/div/ul/li[2]/a")
element.click()
    
    
html = driver.execute_script('return document.documentElement.outerHTML')
all_html = BeautifulSoup(html,'lxml')

    
# event week
game_week =  6
    
# team name
team_name = all_html.find_all('h2', {'class':'Title-sc-9c7mfn-0 dnXmcI'})
    
idx = str(team_name).find("</h2>")
team_name = str(team_name)[47:idx]
    
    
# player names
second_name = all_html.find_all('div', {'class':'ElementInTable__Name-y9xi40-1 eyyBOW'})
    
x = 0
for entry in second_name:
    idx = str(entry).find('</div')
        
    # subset entry from the beginning of every player's name until this index
    # get desired string
    subs = str(entry)[50:idx]
    second_name[x] = subs
    x += 1
        
second_name = pd.DataFrame(second_name, columns = ['second_name'])
    
# player teams
    
team =  all_html.find_all('span', {'class':'ElementInTable__Team-y9xi40-2 hCvdTQ'})
    
x = 0
for entry in team:
        idx = str(entry).find('</span')
            
        # subset entry from the beginning of every player's team until this index
        # get desired string
        subs = str(entry)[51:idx]
        team[x] = subs
        x += 1
        
team = pd.DataFrame(team,  columns = ['team'])
    
# player positions
player_position =  all_html.find_all('span')
element_type = []
    
x = 0
for entry in player_position:
    idx = str(entry).find('</span')
            
    # subset entry from the beginning of every player's position until this index
    # get desired string
    subs = str(entry)[6:idx]
        
    # filter by returns that are equal to 3 as these will be our positions
    if len(subs) == 3:
        element_type.append(subs)
    x += 1

element_type = pd.DataFrame(element_type,  columns = ['element_type'])
    
# create a data-frame with this information 
team_info = pd.concat([second_name, team, element_type], axis = 1)
    
# append team name info
team_info['event_week'] = game_week


# tidy data
# change player position to match preferred format
team_info['element_type'] = team_info['element_type'].replace(['GKP', 'DEF', 'MID', 'FWD'],['Goalkeeper' ,'Defender','Midfielder','Striker'])

# change player team to match preferred format
team_info['team'] = team_info['team'].replace(
        ['ARS', 'AVL', 'BHA', 'BUR', 'CHE', 'CRY', 'EVE', 'FUL', 'LEE',
       'LEI', 'LIV', 'MCI', 'MUN', 'NEW', 'SHU', 'SOU', 'TOT', 'WBA',
       'WHU', 'WOL'],
        ['Arsenal' ,'Aston Villa','Brighton','Burnley', 'Chelsea', 
         'Crystal Palace', 'Everton', 'Fulham', 'Leeds', 'Leicester', 'Liverpool', 'Man City', 
         'Man Utd', 'Newcastle', 'Sheffield Utd', 'Southampton', 'Spurs', 'West Brom', 'West Ham', 'Wolves'])

# load master document
team_info_master = pd.read_excel(r'C:\Users\Danie\Documents\Personal\Coding_Jobs\FPL\data\my_team_2020-21.xlsx')

# join the old with the new and save a copy
team_info_df = [team_info_master, team_info]

join_team_info = pd.concat(team_info_df)

team_info.to_excel(r'C:\Users\Danie\Documents\Personal\Coding_Jobs\FPL\data\my_team_2020-21.xlsx')

driver.quit()
