# -*- coding: utf-8 -*-
"""
Created on Tue Jun 23 16:17:27 2020

@author: Daniel
"""
# Load libraries
from urllib.request import urlopen
import json
from datetime import date
import pandas as pd

# connect to URL and read text
url = 'https://fantasy.premierleague.com/api/bootstrap-static/'

text = urlopen(url).read().decode()
data = json.loads(text)

# create DataFrames from text
players = pd.DataFrame.from_dict(data['elements'])
teams   = pd.DataFrame.from_dict(data['teams'])
events = pd.DataFrame.from_dict(data['events'])


#Fixture Dates

matchdays = events[['name', 'deadline_time']]
matchdays['deadline_time'] = matchdays["deadline_time"].str.split('T', expand=True)
matchdays.columns = ['game_week', 'date']
        
# Calculate the last match-week
today =  str(date.today())

x = -1
while True:
    x += 1
    if today < matchdays['date'][x]:
        current_game_week =  matchdays['game_week'][x-1]
        break

# append game week info onto this weeks player info    
players['Game Week'] = current_game_week

# divide by 10 to get `6.2` instead of `62`
players['now_cost'] = players['now_cost'] / 10

# convert team's number to its name
players['team'] = players['team'].apply(lambda x: teams.iloc[x-1]['name'])

# Change the element type to reflect the playing position
players['element_type'] = players['element_type'].replace([1,2,3,4],['Goalkeeper' ,'Defender','Midfielder','Striker'])

# Bring in information surrounding the top_300 players
top_300_count = pd.read_excel(r'C:\Users\Danie\Documents\Personal\Coding_Jobs\FPL\data\Top_300_count_2020-21.xlsx')

# merge onto players df
players = pd.merge(players, top_300_count, left_on =  ['second_name', 'team', 'element_type', 'Game Week'],
                   right_on = ['player_name', 'player_team', 'element_type', 'event_week'], 
                   how = 'left').drop(['player_name', 'player_team', 'event_week'], axis = 1)


# fill missing values with 0
players['top_300_count'] = players['top_300_count'].fillna(0)

# Bring in team of the week info
tow = pd.read_excel(r'C:\Users\Danie\Documents\Personal\Coding_Jobs\FPL\data\ToW_Master_2020-21.xlsx')

# merge onto players df
players = pd.merge(players, tow, on =  ['second_name', 'team', 'element_type', 'Game Week'],
                   how = 'left',suffixes=('', '_drop'))

# fill all nan falues with zero before converting to boolean
players['tow?'] = players.loc[:,'first_name_drop'].fillna(0)

players['tow?'] = players['tow?'].astype('bool')

# drop duplicate columns
players = players[players.columns[~players.columns.str.endswith('_drop')]]


# load in my team
my_team = pd.read_excel(r'C:\Users\Danie\Documents\Personal\Coding_Jobs\FPL\data\my_team_2020-21.xlsx')

# merge onto players df
players = pd.merge(players, my_team, on =  ['second_name', 'team', 'element_type', 'Game Week'],
                   how = 'left',suffixes=('', '_drop'))

# fill all nan falues with zero before converting to boolean
players['my_team?'] = players.loc[:,'first_name_drop'].fillna(0)

players['my_team?'] = players['my_team?'].astype('bool')

# Merge new week with the master copy
master = pd.read_excel(r'C:\Users\Danie\Documents\Personal\Coding_Jobs\FPL\data\FPL_Master_2020-21.xlsx')

dataframes = [master, players]

join = pd.concat(dataframes)

#Export excel sheet as the new master copy
join.to_excel(r'C:\Users\Danie\Documents\Personal\Coding_Jobs\FPL\data\FPL_Master_2020-21.xlsx')

# Combine with data from the top 300 players
top_300_master = pd.read_excel(r'C:\Users\Danie\Documents\Personal\Coding_Jobs\FPL\data\Top_300_2020-21.xlsx')

top_300_count = top_300_master.groupby(['player_name', 'player_team', 'element_type'])['player_name'].count().sort_values(ascending=False)

top_300_count['element_type'] = top_300_count['element_type'].replace(['GKP', 'DEF', 'MID', 'FWD'],['Goalkeeper' ,'Defender','Midfielder','Striker'])



# Team of the Week Calculation

def tow_calculation():
# filter players
    goalkeepers = players[ players['element_type'] == 'Goalkeeper']
    defenders   = players[ players['element_type'] == 'Defender' ]
    midfielders = players[ players['element_type'] == 'Midfielder' ]
    forwards = players[ players['element_type'] == 'Striker' ]
    
    
#Sort Goalkeepers by event points
    sorted_data_gk = goalkeepers.sort_values(['event_points'], ascending = False)

#Cut out all other goal keepers leaving the top 2
    sorted_data_gk = sorted_data_gk[:2]
    print(sorted_data_gk)
#Choose what information we want to keep
    sorted_data_gk = sorted_data_gk[['first_name','second_name', 'team','event_points', 'now_cost','transfers_in_event','transfers_out_event','element_type','Game Week']]


#Sort Defenders by event point
    sorted_data_df = defenders.sort_values(['event_points'], ascending = False)

#Cut out all other Defenders leaving the top 5
    sorted_data_df = sorted_data_df[:5]
    print(sorted_data_df)
#Choose what information we want to keep
    sorted_data_df = sorted_data_df[['first_name','second_name', 'team','event_points', 'now_cost','transfers_in_event','transfers_out_event','element_type','Game Week']]

#Sort Midfielders by event point
    sorted_data_mf = midfielders.sort_values(['event_points'], ascending = False)

#Cut out all other Midfielders leaving the top 5
    sorted_data_mf = sorted_data_mf[:5]
    print(sorted_data_mf)
#Choose what information we want to keep
    sorted_data_mf = sorted_data_mf[['first_name','second_name', 'team','event_points', 'now_cost','transfers_in_event','transfers_out_event','element_type','Game Week']]

#Sort Strikers by event point
    sorted_data_fw = forwards.sort_values(['event_points'], ascending = False)

#Cut out all other Strikers leaving the top 3
    sorted_data_fw = sorted_data_fw[:3]
    print(sorted_data_fw)

#Choose what information we want to keep
    sorted_data_fw = sorted_data_fw[['first_name','second_name', 'team','event_points', 'now_cost','transfers_in_event','transfers_out_event','element_type','Game Week']]

#Save the New Team of the Week to File
    tow = [sorted_data_gk,sorted_data_df,sorted_data_mf,sorted_data_fw]
    global team_of_the_Week_new 
    team_of_the_Week_new = pd.concat(tow)
    
    return (team_of_the_Week_new)
    
tow_calculation()

print(team_of_the_Week_new)



# Check that no more than 3 clubs exist in the ToW
tow_teams = team_of_the_Week_new['team'].value_counts()
tow_teams_list = team_of_the_Week_new['team'].value_counts().index.tolist()


while tow_teams.iloc[0] > 3:
    tow_teams = team_of_the_Week_new['team'].value_counts()
    tow_teams_list = team_of_the_Week_new['team'].value_counts().index.tolist()
    
# Go through the count of each team and see how many times it comes up
    i = 0
    for entries in tow_teams:
        if entries > 3:
            
            # If it comes up over 3 times, we need to remove one of the players
            output = tow_teams_list[i]
            illegal_players = team_of_the_Week_new.loc[team_of_the_Week_new['team'] == output]
            
            # Find the player with the lowest number of points
            illegal_players = illegal_players.sort_values(['event_points'], ascending = False)
            illegal_entry = illegal_players[3:]
            illegal_name = illegal_entry['second_name'].values[0]
        
            # Delete the player from the copy data set  
            dfb = next(iter(players[players['second_name']== str(illegal_name)].index), 'no match')
            players = players.drop(index = [dfb]) # We have already saved all player information so it is okay if we remove this
            tow_calculation()
        else:
            i = i + 1
        
    break
            
print(team_of_the_Week_new)


#Open up Master ToW and change the element type to reflect the playing position
tow_master =  pd.read_excel(r'C:\Users\Danie\Documents\Personal\Coding_Jobs\FPL\data\ToW_Master_2020-21.xlsx')

tow_dataframes = [tow_master, team_of_the_Week_new]

join_ToW = pd.concat(tow_dataframes)

join_ToW.to_excel(r'C:\Users\Danie\Documents\Personal\Coding_Jobs\FPL\data\ToW_Master_2020-21.xlsx')






