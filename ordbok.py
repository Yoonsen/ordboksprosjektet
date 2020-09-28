import streamlit as st
import dhlab.nbtext as nb
import pandas as pd

@st.cache(suppress_st_warning=True)
def ngram(word, period):
    if " " in word:
        bigram = word.split()[:2]
        res = nb.bigram(first = bigram [0], second = bigram [1], period = period)
    else:
        res = nb.unigram(word, period = period)
    return res

@st.cache(suppress_st_warning=True)
def sumword(words, period):
    wordlist =   [x.strip() for x in words.split(',')]
    ref = pd.concat([nb.unigram(w, period = period) for w in wordlist], axis = 1).sum(axis = 1)
    ref.columns = ["tot"]
    return ref


@st.cache(suppress_st_warning = True)
def wildcard(word = 'frum*', faktor = 2, frekvens = 50, antall = 50):
    res = nb.sorted_wildcardsearch(
        {
            'word': word,   # her legges selve søkeordet inn
            'factor': faktor,           # factor bestemmer hvor mye lenger treffene skal være enn ordet med jokertegn.
            'freq_lim':frekvens,        # sett begrensninger på frekvensen, minimumsverdi
            'limit':antall            # begrensning på antall treff

        })
    return res




st.title('Ord og bigram')

words = st.sidebar.text_input('Fyll inn ord med * her og der', "")
if word == "":
    word = "frum"

frekvens = st.sidebar.number_input('frekvensgrense', 50)
faktor = st.sidebar.number_input('forskjell i ordlengde', 3)
limit = st.sidebar.number_input('antall treff', 50)


sammenlign = st.sidebar.text_input("Relativiser til summen av følgende token", ".")
 
allword = [w.strip() for w in words.split(',')]

period_slider = st.sidebar.slider(
    'Angi periode',
    1900, 2020, (1950, 2000)
)


smooth_slider = st.sidebar.slider('Glatting', 0, 8, 3)

resultat = wildcard(word = word, faktor = faktor, frekvens = frekvens, antall = limit)
df = pd.concat([nb.frame(nb.unigram(x), x) for x in resultat.index], axis = 1)

df = df.rolling(window= smooth_slider).mean()

# Råfrekvenser unigram
if sammenlign != "":
    tot = sumword(sammenlign, ddk, subject, period=(period_slider[0], period_slider[1]))
    for x in df:
        df[x] = df[x]/tot
        
df.index = pd.to_datetime(df.index, format='%Y')
st.line_chart(df)

#st.line_chart(tot)