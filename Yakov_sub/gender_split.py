import pandas as pd
import re

def preprocess_names(df, Column_Name):
    #Remove space if the first letter of the word is a space
    
    df['temp_Column_Name'] = df[Column_Name]
    df['temp_Column_Name'] = df['temp_Column_Name'].str.lstrip()
    
    #Remove single letter in the Names
    #df[Column_Name] = df[Column_Name].str.replace(r'\b[A-Za-z]\b', '')
    df['temp_Column_Name'] = df['temp_Column_Name'].apply(lambda x: ' '.join([w for w in x.split() if len(w) > 1]))
    #Remove names in brackets
    #df[Column_Name] = df[Column_Name].str.replace(r'\s?\([^()]*\)', '')
    df['temp_Column_Name'] = df['temp_Column_Name'].apply(lambda x: re.sub("[\(\[].*?[\)\]]", "", x))
    
    rwords = ['Doctor','Professor','Captain','Jr','Sr','III','II', 'IV']
    for word in rwords:
        df.loc[:, 'temp_Column_Name'] = df['temp_Column_Name'].str.replace(word,"")
        
    df['temp_Column_Name'] = df['temp_Column_Name'].str.lstrip()
    
    df['First Name'] = df['temp_Column_Name'].str.split(" ", expand=True)[0]
    df['Last Name'] = df['temp_Column_Name'].str.split().str[-1]
    df.drop(columns=['temp_Column_Name'], inplace=True)
    return df