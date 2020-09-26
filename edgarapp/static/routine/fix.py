# ../static/routine/updatefilings.py
# download index files and write content into Mysql
# @radiasl for ExarNorth

import csv, time, urllib.request
from bs4 import BeautifulSoup
from requests import get

# Download index files and write content into Mysql
import mysql.connector, requests, os, os.path
from mysql.connector import Error, errorcode


try:
    connection = mysql.connector.connect(host='172.104.7.112',
                                         database='edgarData',
                                         user='reguser',
                                         password='Edgar@2020')

    cursor = connection.cursor()

    print('Connection to mysql was successful.\nFetching filings\n...')

    with open('sample.csv', newline='') as infile:
        records = csv.reader(infile)
        i = 1

        for r in records:
            
            if (i==1): # skip first row
                i = 2
                continue
            
            log_row = r.copy()
            print('Start fetching URL to', r[1], r[2], 'filed on', r[4], '...')
            start_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            if r[4].split('-')[0] == '2020' or r[4].split('-')[0] == '2019':
                try:
                    response = get(r[5])
                    html_soup = BeautifulSoup(response.text, 'html.parser')
                    end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())

                    print('Success!', start_time, ' --> ', end_time, '\n')
                    table = html_soup.find_all('table', class_ = 'tableFile')[0]
                    form_link = 'https://www.sec.gov'+table.a['href']
                    print(table.a['href'])
                    print(form_link)

                    # download file
                    url = form_link
                    if 'ix?doc=/' in form_link:
                        print('-------------------- STARTING XBRL DOC ------------------------')
                        url = url.replace('ix?doc=/', '')
                        req = requests.get(url)
                        print('got request')
                        directory = '/mnt/filings/files/'+log_row[3] # log_row[3] = cik

                        # create dir if it doesn't exist
                        if not os.path.exists(directory):
                            os.makedirs(directory)

                        # write file in dir if doesn't exist
                        localpath = directory+'/'+log_row[4]+'-'+url.rsplit('/', 1)[1]  # directory/filingdate-filename
                        if os.path.isfile(localpath):
                            print('writing new file')
                            with open(localpath, 'w') as f:
                                print('writing')
                                f.write(str(req.content))
                            print('finished writing')

                        # add file path to database
                        loglocal = [log_row[3], log_row[1], log_row[2], log_row[4], log_row[3]+'/'+log_row[4]+'-'+url.rsplit('/', 1)[1]]
                        try:
                            # Add a filing date as a primary key
                            # cursor.execute("CREATE TABLE IF NOT EXISTS edgarapp_filing (cik int, name text, filingtype text, filingdate varchar(20), filingpath text, PRIMARY KEY(cik, filingdate))")
                            cursor.execute("UPDATE edgarapp_filing SET filingpath = %s  WHERE (cik = %s AND name = %s AND filingtype = %s AND filingdate = %s)", [loglocal[-1], loglocal[0], loglocal[1], loglocal[2], loglocal[3]])
                            connection.commit()
                        except mysql.connector.Error as e:
                            print('MySQL error is: {}'.format(e))
                            self.connection.rollback() 


                    # save picture
                    #if table.find(lambda tag:tag.name=="a" and "jpg" in tag.text) is not None:
                    #    form_image = 'https://www.sec.gov'+table.find(lambda tag:tag.name=="a" and "jpg" in tag.text)['href']

                    #    # download image
                    #    url_image = form_image
                    #    localpath_image = directory+'/'+url_image.rsplit('/', 1)[1]
                    #    if not os.path.isfile(localpath_image):
                    #        urllib.request.urlretrieve(form_image, localpath_image)
                    #
                    #    print('Success getting the image!\n')
                    #
                    #else:
                    #    print('No image found.\n')

                except:
                    end_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
                    print('ERROR!', start_time, ' --> ', end_time, '\n')

                    with open('log.csv', mode='a') as error_log:
                        error_writer = csv.writer(error_log, delimiter=',')
                        error_writer.writerow(log_row)


        # populate idx table
        connection.commit()
        connection.close()
        print('\nProgram finished updating.')

except mysql.connector.Error as error:
    print("Failed to insert record into table {}".format(error))

finally:
    if (connection.is_connected()):
        connection.close()
        print("Mysql connection is closed")
