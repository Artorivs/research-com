import pandas as pd
# import numpy as np
import re
import os

#### CAUTION  ####
#### BEFORE RUNNING THIS SCRIPT, PLEASE USE THE FOLLOWING REGEX TO CHECK AND/OR CLEAN THE FILE ####
'''
> \s{2,}                                : There should not be more than 2 \s in between values
> \t(?=\d+\t\d+\t(https:))              : Every line should only has one scholar data
> (?<=\n)\t(?=\d+\t\d+\t(https:))       : No tab after a new line
'''
#### ALSO, CHECK IF PIPELINE SEPERATED THE SCHOLAR COLUMN DATA PROPERLY ####

# get all filenames under hkul_publications/dataset/research
def get_filenames(path):
    filenames = []
    for filename in os.listdir(path):
        if filename.endswith(".tsv"):
            filenames.append(filename)
    
    # sort the filenames in alphabetical order
    filenames.sort()
    return filenames

rootpath = "./dataset/research/"
filenames = get_filenames(rootpath)

for filename in filenames:
    filepath = rootpath + filename
    df = pd.read_csv(filepath, sep='\t', header=0, dtype={'World':str, 'National':str})

    df = df.dropna(axis=0, how='any') # drop row with NaN
    df = df.reset_index(drop=True) # reset index

    ### strip the whitespace
    df.loc[:,'World']       = df.loc[:,'World'].apply(lambda x: str(x).strip())
    df.loc[:,'National']    = df.loc[:,'National'].apply(lambda x: str(x).strip())
    df.loc[:,'H-index']     = df.loc[:,'H-index'].apply(lambda x: str(x).strip())
    df.loc[:,'Citations']   = df.loc[:,'Citations'].apply(lambda x: str(x).strip())
    df.loc[:,'Citations']   = df.loc[:,'Citations'].apply(lambda x: str(x).strip())
    df.loc[:,'Publications']= df.loc[:,'Publications'].apply(lambda x: str(x).strip())
    
    ### seperate scholar data with pipeline '|' for further cleaning
    for i in range(len(df)):
        ## replace specific commas with |
        df.loc[i,"Scholar"] = re.sub(r'(?<=\s)\,(?=\w)', '|', df.loc[i,"Scholar"])
        df.loc[i,"Scholar"] = re.sub(r'(?<=\w)\,(?=\w)', '|', df.loc[i,"Scholar"])
        df.loc[i,"Scholar"] = re.sub(r'(?<=\))\,(?=\w)', '|', df.loc[i,"Scholar"])
        
    df["Scholar"] = df["Scholar"].str.split("|") # split the Scholar column by "|"

    df.loc[:, 'scholar'] = df.loc[:, 'Scholar'].apply(lambda x: x[1].strip().title())
    df.loc[:, 'Institution'] = df.loc[:, 'Scholar'].apply(lambda x: x[2].strip())
    for i in range(len(df)):
        if len(df.loc[i, 'Scholar']) == 4:
            df.loc[i, 'Country'] = df["Scholar"][i][3].strip()
        else:
            df.loc[i, 'Country'] = df["Scholar"][i][2].split(',').pop().strip()
    df.loc[:, 'URL'] = df["Scholar"].apply(lambda x: x[0].strip())

    df.drop(columns=["Scholar"], inplace=True)
    ## rearrange columns: world, national, scholar, institution, country, url, h-index, citations, publications
    colnames = list(map(lambda x: x.lower(), df.columns))
    df.columns = colnames
    colnames = colnames[:2] + colnames[5:] + colnames[2:5]
    df = df[colnames]
    
    df.to_csv(rootpath+'processed/'+filename, sep='\t', index=False)
