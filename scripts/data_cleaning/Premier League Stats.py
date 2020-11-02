from bs4 import BeautifulSoup
from selenium import webdriver
import pandas as pd
import time
import re
import numpy as np

#url = "https://www.bbc.co.uk/sport/football/premier-league/table"
url = 'https://www.telegraph.co.uk/football/2020/08/20/premier-league-fixtures-2020-21-full-find-matchday-schedule/'

driver = webdriver.Firefox(executable_path = r'C:\Program Files (x86)\SeliniumDrivers\geckodriver.exe')
driver.get(url)
time.sleep(1)

html = driver.execute_script('return document.documentElement.outerHTML')

all_html = BeautifulSoup(html,'lxml')
all_tables = all_html.find_all('table', {'class':"fixtures"})
print('Found '+ str(len(all_tables)) + ' tables')


table1 = all_tables[0]
df = pd.read_html(str(table1))
table1_df = pd.DataFrame.from_dict(df[0])

conversion= table1_df["Form"].str.split('.', expand=True)
conversion.columns = ['Game 5','Game 4','Game 3','Game 2','Game 1', ""]
table1_df = pd.concat([table1_df, conversion], axis = 1) 
table1_df = table1_df.drop(columns = "Form")

table1_df.to_excel(r'C:\Users\Danie\Documents\Personal\AI Learning Materials\Test.xlsx')



print(f'HTML: {all_html.h2}, name: {all_html.h2.name}, text: {all_html.h2.text}')

alls = []
for d in all_html.findAll('span', attrs={'class':test}):
     print(d)
     #x = d.find('dl', attrs={'class':'matches'})
     #print(x)


for d in all_html.findAll('span', attrs={'class':}):
     print(d)
     
     
test = 'home-side team team-54'

re.search('^home.*', test).group()

spans = str(all_html.findAll('span'))

re.search('home side team team-*', spans).group()

re.findall('.home side team team-.')
   
# Get a list of team IDs and store them in a list called 'team_list'
team_list = []   
for line in all_html:
    if re.findall('span', line.decode()):
        temp = re.findall('team-[0-9][0-9]*', line.decode())
        print(line.decode())
        for tmp in temp:
            print(tmp)
            team_list.append(tmp)
            
team_list = np.unique(team_list)