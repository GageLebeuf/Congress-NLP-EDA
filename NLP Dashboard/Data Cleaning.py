# -*- coding: utf-8 -*-
"""
Created on Mon Nov 29 13:20:49 2021

@author: Gage
"""

import pandas as pd
import re, spacy, gensim, os, glob
from textblob import TextBlob
import matplotlib.pyplot as plt



### Tokenizer
def sent_to_words(sentences):
    for sentence in sentences:
        yield(gensim.utils.simple_preprocess(str(sentence), deacc=True))  # deacc=True removes punctuations


### Lemmatization function
def lemmatization(texts, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV']): #'NOUN', 'ADJ', 'VERB', 'ADV'
    texts_out = []
    for sent in texts:
        doc = nlp(" ".join(sent)) 
        texts_out.append(" ".join([token.lemma_ if token.lemma_ not in ['-PRON-'] else '' for token in doc if token.pos_ in allowed_postags]))
    return texts_out

# Remove first and  end spaces
def remove_first_end_spaces(string):
    return "".join(string.rstrip().lstrip())

# Pull all necessary files

os.chdir(r"C:\Users\Gage\Desktop\Academic\Datasets\CongressTweets")

path = os.getcwd()

csv_files = glob.glob(os.path.join(path,"*.csv"))


df=pd.DataFrame()

for f in csv_files:
    df1 = pd.read_csv(f,encoding=("UTF-8"), header=0)
    df = pd.concat([df,df1],axis=0)

# Pull supplementary data (Party affiliation / Twitter Handles / State )

os.chdir(r"C:\Users\Gage\Desktop\Academic\Datasets")

handles = pd.read_csv('CongressTwitterAcc.csv')
handles = handles[['TwitterHandle', 'Party', 'State']]
handles = handles.rename(columns = {'TwitterHandle' : 'Influencer'})

partyaffil = handles[['Influencer','Party']]

stateaffil = handles[['Influencer','State']]


df = df[['Influencer', 'Twitter Screen Name', 'Hit Sentence']]

# keep increasing the range to weed on n/a
# clean states so geopandas can actually recognize them



party = pd.Series(partyaffil.Party.values, index = partyaffil.Influencer).to_dict()

state = pd.Series(stateaffil.State.values, index = stateaffil.Influencer).to_dict()





# Map missing information to master DF (state and party)

df['party'] = df['Influencer'].map(party).apply(lambda x: x[0] if type(x)==list else x)

df['State'] = df['Influencer'].map(state).apply(lambda x: x[0] if type(x)==list else x)

os.chdir(r"C:\Users\Gage\Desktop\Academic\Datasets\Datasets")


statecode = pd.read_csv('statecodes.txt')

statecode = statecode[['code','state']]

statecodedict = pd.Series(statecode.code.values, index = statecode.state).to_dict()



# Map missing information to master DF (State Code for geopandas)

df['Code'] = df['State'].map(statecodedict).apply(lambda x: x[0] if type(x)==list else x)


df = df.dropna()       


df = df.rename( columns = {"Hit Sentence": 'text1'})


nlp = spacy.load('en_core_web_sm', disable=['parser', 'ner'])


### Cleaning step
#################

# Convert to list
data = df.text1.tolist()
# Remove Emails
data = [re.sub(r'\S*@\S*\s?', '', sent) for sent in data]
# Remove new line characters
data = [re.sub(r'\s+', ' ', sent) for sent in data]
# Remove distracting single quotes
data = [re.sub(r"\'", "", sent) for sent in data]

data_words = list(sent_to_words(data))




### Lemmatization step


data_lemmatized = lemmatization(data_words, allowed_postags=['NOUN', 'ADJ', 'VERB', 'ADV']) #select noun and verb

df['text'] = data_lemmatized



# Extracting sentiment for each tweet
    
sentiment_objects = [TextBlob(tweet) for tweet in df['text']]


sentiment_objects[0].polarity, sentiment_objects[0]

sentiment_values = pd.DataFrame([[tweet.sentiment.polarity, str(tweet)] for tweet in sentiment_objects])

#df = df.loc[~df.index.duplicated(keep='first')]

df.loc[:,'sentiment'] = sentiment_values[0]


# Remove empty spaces at end of State's names (Before this step it would double count states)
df['State'] = [remove_first_end_spaces(i) for i in df['State']]


df.to_csv(r'C:\Users\Gage\Desktop\Academic\NLP Dashboard\data\MasterDF.csv')

