import sqlite3 as sql
import pandas as pd
# import numpy as np
import os

# get all file names under hkul-publications/processed/research
files = sorted(os.listdir('./data/research-cleaned'))

# clean all data in sql database
sql.connect('research-com.db').execute('DELETE FROM research WHERE subject = "";')

temp = pd.DataFrame()
# save all files to sql database
for file in files:
    # read file
    df = pd.read_csv('hkul-publications/data/research-cleaned/' + file, sep='\t')
    # add a column 'subject'
    df['subject'] = file.replace('-', ' ')\
                        .replace('.tsv', '')
    # make 'subject' column the first column
    df = df[['subject'] + df.columns[:-1].tolist()]
    # merge the dataframe
    temp = pd.concat([temp, df], ignore_index=True)
    
    # create table
    # df.to_sql(file.replace('.tsv', ''), con=sql.connect('research-com.db'), if_exists='append', index=False)
    # print('Saved ' + file + ' to sql database')

# save to sql database
temp.to_sql('research', con=sql.connect('research-com.db'), if_exists='replace')
# save to csv file
temp.to_csv('research-com.csv', index=False)
