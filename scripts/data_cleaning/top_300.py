# -*- coding: utf-8 -*-
"""
Created on Tue Oct 27 15:48:34 2020

@author: Danie
"""

# Load libraries
from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
import time


# first connect to the overall leaderboard page and extra the ids of the top 50 players
url = 'https://fantasy.premierleague.com/leagues/314/standings/c'

# use the below code if we want to physically open a window
#driver = webdriver.Firefox(executable_path = r'C:\Program Files (x86)\SeliniumDrivers\geckodriver.exe')
#driver.get(url)
#time.sleep(1)


# for headless scraping
options = webdriver.FirefoxOptions()
options.add_argument('-headless')
driver = webdriver.Firefox(executable_path = r'C:\Program Files (x86)\SeliniumDrivers\geckodriver.exe',
                           options = options)
driver.get(url)
time.sleep(1)


html = driver.page_source
soup = BeautifulSoup(html)


# find the IDs of the top 50 players last week
player_ids = []
links = soup.find_all('a')
for link in links:
    if str(link['href']).startswith('/entry/'):
        player_ids.append(link['href'])
        
        
# repeat this process 5 times to capture the xxx players
x = 0 
while x < 5:
# find the IDS of the next top 50 players

# click next     
    element = driver.find_element_by_xpath("/html/body/main/div/div[2]/div[2]/div/div/div[3]/div[2]/a")
    element.click()
    
    # repeat as above
    
    html = driver.page_source
    soup = BeautifulSoup(html)
    
    
    links = soup.find_all('a')
    for link in links:
        if str(link['href']).startswith('/entry/'):
            player_ids.append(link['href'])
    
    x += 1

        
# once we have the ids we can close the window
driver.quit()
        
        
# set up empty dataframe to store information
top_300_new = pd.DataFrame()
        
# loop through each of the top 50 IDs and capture the team information       
i = 0
while i < 300:
    
    player_url = 'https://fantasy.premierleague.com' + player_ids[i]
    
    
    # connect to each players team for the latest week using headless web scraping
    options = webdriver.FirefoxOptions()
    options.add_argument('-headless')
    driver = webdriver.Firefox(executable_path = r'C:\Program Files (x86)\SeliniumDrivers\geckodriver.exe', options = options)
    driver.get(player_url)
    time.sleep(2)
    
    # change view to list to access more player information
    element = driver.find_element_by_xpath("/html/body/main/div/div[2]/div[2]/div[1]/div[4]/div/div/ul/li[2]/a")
    element.click()
    
    
    html = driver.execute_script('return document.documentElement.outerHTML')
    all_html = BeautifulSoup(html,'lxml')
    
    # player id
    idx =  player_ids[i].find('/event/6')
    player_id =  player_ids[i][7:idx]
    
    # event week
    idx = idx + 7
    game_week =  player_ids[i][idx:]
    
    # team name
    
    team_name = all_html.find_all('h2', {'class':'Title-sc-9c7mfn-0 dnXmcI'})
    
    idx = str(team_name).find("</h2>")
    team_name = str(team_name)[47:idx]
    
    
    # player names
    
    player_name = all_html.find_all('div', {'class':'ElementInTable__Name-y9xi40-1 eyyBOW'})
    
    x = 0
    for entry in player_name:
        idx = str(entry).find('</div')
            
        # subset entry from the beginning of every player's name until this index
        # get desired string
        subs = str(entry)[50:idx]
        player_name[x] = subs
        x += 1
        
    player_name = pd.DataFrame(player_name, columns = ['player_name'])
    
    # player teams
    
    player_team =  all_html.find_all('span', {'class':'ElementInTable__Team-y9xi40-2 hCvdTQ'})
    
    x = 0
    for entry in player_team:
        idx = str(entry).find('</span')
            
        # subset entry from the beginning of every player's team until this index
        # get desired string
        subs = str(entry)[51:idx]
        player_team[x] = subs
        x += 1
        
    player_team = pd.DataFrame(player_team,  columns = ['player_team'])
    
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
    team_info = pd.concat([player_name, player_team, element_type], axis = 1)
    
    # append team name info
    
    team_info['team_name'] = team_name
    
    team_info['entry_id'] = player_id
    
    team_info['event_week'] = game_week
    
    
    
    # append team information to the same df
    top_300_new = pd.concat([top_300_new, team_info])
    print(team_info)
    
    driver.quit()
 
    i += 1
    print(i)
    
    
driver.quit()


# tidy data
# change player position to match preferred format
top_300_new['element_type'] = top_300_new['element_type'].replace(['GKP', 'DEF', 'MID', 'FWD'],['Goalkeeper' ,'Defender','Midfielder','Striker'])

# change player team to match preferred format
top_300_new['player_team'] = top_300_new['player_team'].replace(
        ['ARS', 'AVL', 'BHA', 'BUR', 'CHE', 'CRY', 'EVE', 'FUL', 'LEE',
       'LEI', 'LIV', 'MCI', 'MUN', 'NEW', 'SHU', 'SOU', 'TOT', 'WBA',
       'WHU', 'WOL'],
        ['Arsenal' ,'Aston Villa','Brighton','Burnley', 'Chelsea', 
         'Crystal Palace', 'Everton', 'Fulham', 'Leeds', 'Leicester', 'Liverpool', 'Man City', 
         'Man Utd', 'Newcastle', 'Sheffield Utd', 'Southampton', 'Spurs', 'West Brom', 'West Ham', 'Wolves'])




# conbine all data from the last game week to a master copy

# loading master document
top_300_master = pd.read_excel(r'C:\Users\Danie\Documents\Personal\Coding_Jobs\FPL\data\Top_300_2020-21.xlsx')
  

# join the new with the old and save a copy
top_300_df = [top_300_master, top_300_new]

join_top_300 = pd.concat(top_300_df)

join_top_300.to_excel(r'C:\Users\Danie\Documents\Personal\Coding_Jobs\FPL\data\Top_300_2020-21.xlsx')



# combine a count of each player in the top 300 teams to another document
top_300_count = top_300_new.groupby(['player_name', 'player_team', 'element_type', 'event_week'], as_index=False).count().sort_values(by = 'team_name', ascending=False)

top_300_count['top_300_count'] = top_300_count['team_name']

top_300_count = top_300_count[['player_name', 'player_team', 'element_type', 'top_300_count','event_week']]

# load master document
top_300_count_master = pd.read_excel(r'C:\Users\Danie\Documents\Personal\Coding_Jobs\FPL\data\Top_300_count_2020-21.xlsx')

# join the old with the new and save a copy
top_300_count_df = [top_300_count_master, top_300_count]

join_top_300_count = pd.concat(top_300_count_df)

join_top_300_count.to_excel(r'C:\Users\Danie\Documents\Personal\Coding_Jobs\FPL\data\Top_300_count_2020-21.xlsx')





