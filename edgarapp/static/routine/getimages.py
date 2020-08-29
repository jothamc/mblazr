# Download company logos
import csv
from bs4 import BeautifulSoup
from requests import get
import urllib.request
import os, os.path, requests


with open('images.csv', newline='') as infile:
    records = csv.reader(infile)
    i = 1

    for r in records:
        
        if (i==1): # skip first row
            i = 2
            continue

        log_row = r.copy()
        print('Start fetching Image to', r[1], r[2], 'filed on', r[4], '...')
        
        try:
            response = get(r[5])
            html_soup = BeautifulSoup(response.text, 'html.parser')

            table = html_soup.find_all('table', class_ = 'tableFile')[0]

            if table.find(lambda tag:tag.name=="a" and "jpg" in tag.text) is not None:
                form_image = 'https://www.sec.gov'+table.find(lambda tag:tag.name=="a" and "jpg" in tag.text)['href']

                # download file
                url = form_image
                directory = '/mnt/filings/files/'+log_row[3] # log_row[3] = cik
                
                # create dir if it doesn't exist
                if not os.path.exists(directory):
                    os.makedirs(directory)

                # write file in dir if doesn't exist
                localpath = directory+'/'+url.rsplit('/', 1)[1]
                if not os.path.isfile(localpath):
                    urllib.request.urlretrieve(form_image, localpath)

                print('Success!\n')
            
            else:
                print('No image found.\n')

        except:
            print('ERROR!')
            with open('log.csv', mode='a') as error_log:
                error_writer = csv.writer(error_log, delimiter=',')
                error_writer.writerow('Image error: ',log_row)
