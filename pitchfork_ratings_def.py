import pandas as pd
import requests
import retry
import time
import urllib
from bs4 import BeautifulSoup
from urllib.request import urlopen

def gather_info(album_link):
    '''
    This function parses the HTML of the page and attempts to gather attributes like artist name, album, genre,
    date, and the review text itself, instead inputting a null value if the requested element is not found on
    the page. All of the data are put into a Pandas dataframe and returned for use in the gather function.
    VARIABLES
    album_link - A string that refers to the album section of a link to a Pitchfork review.
    e.g. '/reviews/albums/neil-young-promise-of-the-real-visitor/'
    '''
    page = requests.get(album_link) #request URL
    soup = BeautifulSoup(page.content, 'html.parser') #parse with beautifulsoup

    status = True
    while status:
        if page.status_code != 200:
            print("Error: ",page.status_code)
            time.sleep(2)
            page = requests.get(album_link) #request URL
            soup = BeautifulSoup(page.content, 'html.parser') #parse with beautifulsoup
        else:
            status = False

    title = str(soup.find('title').string) #album and artist 
    sents = [element.text for element in soup.find_all('p')] #cleaned text output
    all_text = " ".join(sents)
    selected_text = all_text.split('Reviewed: ',1)[1]
    selected_text = selected_text.split(" ",3)
    review_text = selected_text[3]
    review_text = review_text.split(" By signing up you agree to our User Agreement (including the class action waiver and arbitration",1)[0]
    
    try:
        score = float((soup.find(class_="score").string)) #score
    except AttributeError:
        try:
            score = float((soup.find(class_="BaseWrap-sc-gjQpdd BaseText-ewhhUZ Rating-bkjebD iUEiRd bwCcXY imqiqZ").string))
        except:
            # score = float((soup.find(class_="BaseWrap-sc-gjQpdd BaseText-ewhhUZ Rating-iATjmx iUEiRd bwCcXY dBMsvl").string))
            score = float((soup.find(class_="BaseWrap-sc-gjQpdd BaseText-ewhhUZ Rating-bkjebD iUEiRd bwCcXY fuVxVq").string))
    try:
        genre = soup.find(class_="genre-list__link").string #genre
    except AttributeError:
        try:
            genre = all_text.split("Genre: ",1)[1]
            genre = genre.split("Label: ",1)[0].strip()
        except IndexError:
            genre = None
    try:
        reviewed_date = str(soup.find(class_="pub-date").string) #date
    except AttributeError:
        reviewed_date = selected_text[0]+" "+selected_text[1]+" "+selected_text[2]
    try:
        artist = soup.find(class_="BaseWrap-sc-gjQpdd BaseText-ewhhUZ SplitScreenContentHeaderArtist-ftloCc iUEiRd Byyns kRtQWW").string
    except:
        artist = get_artist(title)
    try:
        album = soup.find(class_="BaseWrap-sc-gjQpdd BaseText-ewhhUZ SplitScreenContentHeaderHed-lcUSuI iUEiRd ckzqqn fTtZlw").string
    except:
        album = get_album(title)
        
    df = pd.DataFrame({'artist': [artist]
                       ,'album': [album]
                       ,'score': [score]
                       ,'genre': [genre]
                       ,'review': [review_text]
                       ,'best': [1 if "best new" in all_text.lower() else 0]
                       ,'reviewed_date': [reviewed_date]
                       ,'link':[album_link]})
    return df

def get_artist(title):
    '''
    This function retreives the artist name from the scraped title string.
    VARIABLES
    title - A string of a cleaned Pitchfork album review title.
    '''
    artist = ''
    for character in title:
        #add to string up until ':' 
        if character != ":":
            artist += character
        else:
            break
    return artist
        
def get_album(title):
    '''
    This function retreives the album name from the scraped title string.
    VARIABLES
    title - A string of a cleaned Pitchfork album review title.
    ''' 
    my_str = ''
    #find ':' and index and start there
    index = title.find(":")
    title = title[index+2:]
    #for each character afterwards, add it until '|'
    for character in title:
        if character == "|":
            break
        else:
            my_str +=character
    album = my_str[:-14] #return just the title
    return album

@retry.retry(urllib.error.URLError, tries=4, delay=3, backoff=2)
def urlopen_with_retry(url):
    return urllib.request.urlopen(url)