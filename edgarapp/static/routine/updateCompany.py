# /home/capitalrap/edgarapp/static/routine/updatecompany.py

# update the list of tickers in mysql table Company
# ignore existing companies based on cik (unique)

import urllib.request, requests, json, mysql.connector
from mysql.connector import Error, errorcode
from urllib.request import urlopen

 
try:
    connection = mysql.connector.connect(host='172.104.7.112',
                                         database='edgarData',
                                         user='reguser',
                                         password='Edgar@2020')
    cursor = connection.cursor()

    print('Connection to mysql was successful.\nCommiting updates\n...')

    # load SEC json file
    json_url = urlopen('https://www.sec.gov/files/company_tickers.json')
    data = json.loads(json_url.read())

    # parse and upload
    for p in data:
        company = [data[p]['cik_str'], data[p]['ticker'], data[p]['title']]
        cursor.execute("CREATE TABLE IF NOT EXISTS edgarapp_company (cik int, ticker text, name text)")
        cursor.execute("INSERT IGNORE INTO edgarapp_company (cik, ticker, name) VALUES (%s, %s, %s)", company)

    # close connection to database
    connection.commit()
    connection.close()
    print('Company database has been updated!')

except mysql.connector.Error as error:
    print("Failed to insert record into table {}".format(error))

finally:
    if (connection.is_connected()):
        connection.close()
        print("Mysql connection is closed")
