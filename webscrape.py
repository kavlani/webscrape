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

table_data = soup.find_all('tbody')[3].find_all('td')

labels = all_thead[1].text.strip().split(":")


def multiple_replace(dict, text):
    new_string = re.compile("(%s)" % "|".join(map(re.escape, dict.keys())))
    return new_string.sub(lambda m: dict[m.string[m.start():m.end()]], text)

strings = {'MSA\n' : "", 
           'Percent': "", 
           '\n': "",
           'y': 'y ',
           'Thoughtsof': 'Thoughts of'
          }

new_columns = [multiple_replace(strings, x) for x in labels]


columns = [re.sub(r'.\(SE\)', "", x) for x in new_columns]


titles = []
serious = []
plans = []
attempted = []
for i in xrange(0,len(table_data),4):
    titles.append(table_data[i].text.strip())
    serious.append(table_data[i+1].text.strip())
    plans.append(table_data[i+2].text.strip())
    attempted.append(table_data[i+3].text.strip())

fix_attempted = []
fix_plans = []
fix_serious = []
for i in xrange(len(attempted)):
    fix_attempted.append(float(re.search(r'\d.\d', attempted[i]).group()))
    fix_plans.append(float(re.search(r'\d.\d', plans[i]).group()))
    fix_serious.append(float(re.search(r'\d.\d', serious[i]).group()))

table_df = pd.DataFrame({ 
        columns[0]: fix_serious,
        columns[1]: fix_plans,
        columns[2]: fix_attempted
        }, index=[titles])

sorted_table = table_df.sort_values(by=['Attempted Suicide'], ascending=False)


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

