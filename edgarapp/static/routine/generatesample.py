# ..static/routine/generatesample.py
# Generate the list of index files archived in EDGAR since start_year (earliest: 1993)
# adapted from http://kaichen.work/?p=946
# @radiasl for ExarNorth

import datetime
 
current_year = datetime.date.today().year
current_quarter = (datetime.date.today().month - 1) // 3 + 1
start_year = 2020 #TODO: edit as needed
years = list(range(start_year, current_year))
quarters = ['QTR1', 'QTR2', 'QTR3', 'QTR4']
history = [(y, q) for y in years for q in quarters]

for i in range(1, current_quarter + 1):
    history.append((current_year, 'QTR%d' % i))
urls = ['https://www.sec.gov/Archives/edgar/full-index/%d/%s/crawler.idx' % (x[0], x[1]) for x in history]
urls.sort()
 
# Download index files and write content into SQLite
import sqlite3, os
import requests

con = sqlite3.connect('edgar_htm_idx.db')
cur = con.cursor()
cur.execute('DROP TABLE IF EXISTS idx')
cur.execute('CREATE TABLE idx (conm TEXT, type TEXT, cik TEXT, date TEXT, path TEXT)')

print('Connection to database was successful.\nFetching filings\n...')
 
for url in urls:
    file = requests.get(url)
    # problem with these two:
    if (url=='https://www.sec.gov/Archives/edgar/full-index/2017/QTR3/crawler.idx') or (url=='https://www.sec.gov/Archives/edgar/full-index/2011/QTR4/crawler.idx'):
        file.encoding = 'latin1'
    lines = file.text.splitlines()
    nameloc = lines[7].find('Company Name')
    typeloc = lines[7].find('Form Type')
    cikloc = lines[7].find('CIK')
    dateloc = lines[7].find('Date Filed')
    urlloc = lines[7].find('URL')

    records = [tuple([line[:typeloc].strip(), line[typeloc:cikloc].strip(), line[cikloc:dateloc].strip(),
                      line[dateloc:urlloc].strip(), line[urlloc:].strip()]) for line in lines[9:] if (("10-K" in line[typeloc:cikloc].strip()) or ("10-Q" in line[typeloc:cikloc].strip()) or (("13F-HR" in line[typeloc:cikloc].strip()) and not ("13F-HR/A" in line[typeloc:cikloc].strip())) or ("DEF 14A" in line[typeloc:cikloc].strip()))]

    cur.executemany('INSERT INTO idx VALUES (?, ?, ?, ?, ?)', records)
    print(url, 'downloaded and wrote to SQLite')
 
con.commit()
con.close()
print('\nProgram finished updating.')


# Write SQLite database to Stata and csv
import pandas
from sqlalchemy import create_engine
 
engine = create_engine('sqlite:///edgar_htm_idx.db')
with engine.connect() as conn, conn.begin():
    data = pandas.read_sql_table('idx', conn)
    if os.path.exists("sample.csv"):
        os.remove("sample.csv")
    data.to_csv('sample.csv')
    os.remove("edgar_htm_idx.db")
