import pandas as pd
from difflib import SequenceMatcher, get_close_matches

reviews_album=["a","e","g","a1wher","dad;fkn","awduifw","adfoqo","vj897","cc"]

df = pd.DataFrame({'album':["a","b","c","d"]})

df['closest_match'] = [get_close_matches(x, reviews_album)[0] if get_close_matches(x, reviews_album) else None for x in df['album']]
df['closest_match_ratio'] = [SequenceMatcher(None, a, b).ratio() if b is not None else None for a, b in zip(df['album'], df['closest_match'])]

print(df)
