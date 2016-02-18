# coding: utf-8
from bs4 import BeautifulSoup
import requests
import sys, re
import pandas as pd
import matplotlib.pyplot as plt
import pylab
from pylab import rcParams

url = "http://www.samhsa.gov/data/sites/default/files/NSDUH119/NSDUH119/SR119SuicideByMSA2012.htm"
soup = BeautifulSoup(requests.get(url).text, 'html5lib')

title = soup.title
print title.text

first_para_text = soup.p.text
print first_para_text

first_table_line = soup.div.td.ul.li.text
print first_table_line

all_thead = soup.find_all('thead')

table_data = soup.find_all('tbody')[3].find_all('td') # Get the table data of interest

labels = all_thead[1].text.strip().split(":") # Get the column labels for table

# Define function to replace multiple strings in a label in one pass
def multiple_replace(dict, text):
    new_string = re.compile("%s" % "|".join(map(re.escape, dict.keys())))
    return new_string.sub(lambda m: dict[m.string[m.start():m.end()]], text)

# Define the strings dictionary to replace the strings as keys and the replacements as values
strings = {'MSA\n' : "", 
           'Percent': "", 
           '\n': "",
           'y': 'y ',
           ' (SE)': "",
           'Thoughtsof': 'Thoughts of'
          }

columns = [multiple_replace(strings, x) for x in labels] # Fix the column labels


#Extract data for each column, since there are 4 entries for each row, need to seperate them.
#First value is the row title, followed by data for serious thoughts, plans and attempted.
titles = []
serious = []
plans = []
attempted = []
for i in xrange(0,len(table_data),4):
    titles.append(table_data[i].text.strip())
    serious.append(table_data[i+1].text.strip())
    plans.append(table_data[i+2].text.strip())
    attempted.append(table_data[i+3].text.strip())


# Extract only the percentage value in order to create the chart - convert to floating point from string
fix_attempted = map(lambda k: float(re.search(r'\d.\d', k).group()), attempted)
fix_plans = map(lambda j: float(re.search(r'\d.\d', j).group()), plans)
fix_serious = map(lambda n: float(re.search(r'\d.\d', n).group()), serious)


# Create a dataframe with 3 columns and each metro area category as a index/row.
table_df = pd.DataFrame({ 
        columns[0]: fix_serious,
        columns[1]: fix_plans,
        columns[2]: fix_attempted
        }, index=[titles])


sorted_table = table_df.sort_values(by=['Attempted Suicide'], ascending=False) # Sort table by descending order or attempts


# Shorten names to fit on graph and center it easily
top_short = {'Dallas-Fort Worth-Arlington, TX': "DFW-TX",
              'Seattle-Tacoma-Bellevue, WA': 'SeaTac-WA',
              'Salt Lake City, UT': 'SaltLk-UT',
              'Tampa-St. Petersburg-Clearwater, FL': "Tampa-FL",
              'Los Angeles-Long Beach-Santa Ana, CA': 'LA-CA'
             }

bot_short = {'San Diego-Carlsbad-San Marcos, CA': 'San Diego-CA',
                 'St. Louis, MO-IL': 'St. Louis-MO',
                 'Washington-Arlington-Alexandria, DC-VA-MD-WV': 'Washington-DC-VA-MD',
                 'Atlanta-Sandy Springs-Marietta, GA': 'Atlanta-GA',
                'Raleigh-Cary, NC': 'Raliegh-NC'
             }


plot_labels = [multiple_replace(top_short, x) for x in sorted_table[:5].index]

get_ipython().magic(u'matplotlib inline')


bottom_labels = [multiple_replace(bot_short, x) for x in sorted_table[-5:].index]


plt.figure(figsize=(18, 10), dpi=80)
areas = plot_labels
attempts = sorted_table['Attempted Suicide'][:5]
xs = [i + 0.4 for i, _ in enumerate(areas)] # plot bars with left x-coordinates [xs], heights [attempts]
plt.ylabel("% of Attempted Suicides")
plt.title("Suicide Attempts for Top 5 Metro Areas - Source SAMHSA.gov") # label x-axis at bar centers
plt.xticks([i + 0.8 for i, _ in enumerate(areas)], areas)
plt.bar(xs, attempts)
plt.savefig('top5_suicide_attempts.png', bbox_inches='tight')
plt.show()

plt.figure(figsize=(18, 10), dpi=80)
areas = bottom_labels
attempts = sorted_table['Attempted Suicide'][-5:]
xs = [i + 0.4 for i, _ in enumerate(areas)] # plot bars with left x-coordinates [xs], heights [attempts]
plt.ylabel("% of Attempted Suicides")
plt.title("Suicide Attempts for Bottom 5 Metro Areas - Source SAMHSA.gov") # label x-axis at bar centers
plt.xticks([i + 0.8 for i, _ in enumerate(areas)], areas)
plt.bar(xs, attempts)
plt.savefig('bot5_suicide_attempts.png', bbox_inches='tight')
plt.show()

table_df.to_csv('metro-attempts.csv')

annual_df = pd.read_csv('suicide-stats.csv')

annual_df.head()

pivot_annual = annual_df.pivot('Year', 'State', 'Age-Adjusted Rate')


pivot_annual


top5_annual = pivot_annual.mean().sort_values(ascending=False)[:5]
top5_annual

bot5_annual = pivot_annual.mean().sort_values(ascending=False)[-5:]
bot5_annual


plt.figure(figsize=(18, 10), dpi=80)
states = top5_annual.index.values
t5_suicides = top5_annual.values
xs = [i + 0.4 for i, _ in enumerate(t5_suicides)] # plot bars with left x-coordinates [xs], heights 
plt.ylabel("Rate of Suicides per 100,000 Individuals")
plt.title("Suicides for Top 5 States 2005-2014 Average  - Source AFSP.org") # label x-axis at bar centers
plt.xticks([i + 0.8 for i, _ in enumerate(states)], states)
plt.bar(xs, t5_suicides)
plt.savefig('top5_states.png', bbox_inches='tight')
plt.show()


plt.figure(figsize=(18, 10), dpi=80)
b5_states = bot5_annual.index.values
b5_suicides = bot5_annual.values
xs = [i + 0.4 for i, _ in enumerate(b5_suicides)] # plot bars with left x-coordinates [xs], heights 
plt.ylabel("Rate of Suicides per 100,000 Individuals")
plt.title("Suicides for Bottom 5 States 2005-2014 Average - Source AFSP.org") # label x-axis at bar centers
plt.xticks([i + 0.8 for i, _ in enumerate(b5_states)], b5_states)
plt.bar(xs, b5_suicides)
plt.savefig('bottom5_states.png', bbox_inches='tight')
plt.show()

