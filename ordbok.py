import streamlit as st
import dhlab.nbtext as nb
import pandas as pd
from PIL import Image

@st.cache(suppress_st_warning=True, show_spinner = False)
def ngram(wordex, period):
    if " " in word:
        bigram = word.split()[:2]
        res = nb.bigram(first = bigram [0], second = bigram [1], period = period)
    else:
        res = nb.unigram(word, period = period)
    return res

@st.cache(suppress_st_warning=True, show_spinner = False)
def sumword(words, period, media = 'bok'):
    wordlist =   [x.strip() for x in words.split(',')]
    ref = pd.concat([nb.unigram(w, media = media, period = period) for w in wordlist], axis = 1).sum(axis = 1)
    ref.columns = ["tot"]
    return ref


@st.cache(suppress_st_warning = True, show_spinner = False)
def wildcard(word = 'frum*', faktor = 2, frekvens = 50, antall = 50):
    res = nb.sorted_wildcardsearch(
        {
            'word': word,   # her legges selve søkeordet inn
            'factor': faktor,           # factor bestemmer hvor mye lenger treffene skal være enn ordet med jokertegn.
            'freq_lim':frekvens,        # sett begrensninger på frekvensen, minimumsverdi
            'limit':antall            # begrensning på antall treff

        })
    return res


@st.cache(suppress_st_warning = True, show_spinner = False)
def ngbok(x, period):
    try:
        r = nb.frame(nb.unigram(x, period, media='bok'), x)
    except:
        r = pd.DataFrame()
    return r

@st.cache(suppress_st_warning = True, show_spinner = False)
def ngavis(x, period):
    try:
        r = nb.frame(nb.unigram(x, period, media='avis'), x)
    except:
        r = pd.DataFrame()
    return r

# App code

image = Image.open('NB-logo-no-eng-svart.png')
st.image(image, width = 200)
st.title('Ordsøk for revisjonsprosjektet')

word = st.sidebar.text_input('Ett ord med jokertegnet *, eller flere ord skilt med komma', "frum*")

faktor = st.sidebar.number_input('Forskjell i ordlengde', min_value = 0, value = 2)
frekvens = st.sidebar.number_input('Frekvensgrense', min_value = 1, value = 50)
limit = st.sidebar.number_input('Antall treff', min_value = 5, value = 10)

using_wildcard = True

if ',' in word and not '*' in word:
    resultat = pd.DataFrame([w.strip() for w in word.split(',')]).set_index(0)
    using_wildcard = False
else:
    resultat = wildcard(word = word, faktor = faktor, frekvens = frekvens, antall = limit)


sammenlign = st.sidebar.text_input("Relativiser til summen av følgende token", ".")

period_slider = st.sidebar.slider(
    'Angi periode',
    1900, 2020, (1950, 2000)
)


smooth_slider = st.sidebar.slider('Glatting', 0, 8, 3)



dfb = pd.concat([ngbok(x, period=(period_slider[0], period_slider[1]))  for x in resultat.index], axis = 1)
dfa = pd.concat([ngavis(x, period=(period_slider[0], period_slider[1]))  for x in resultat.index], axis = 1)

# update result
# if not using wildcard

if not using_wildcard:
    r0 = dfb.sum(axis=0).transpose()
    r1 = dfa.sum(axis = 0).transpose()
    resultat = pd.concat([r0, r1], axis = 1)
    resultat.columns = ['bok', 'avis']
    
dfb = dfb.rolling(window= smooth_slider).mean()
dfa = dfa.rolling(window= smooth_slider).mean()

# Råfrekvenser unigram
if sammenlign != "":
    totb = sumword(sammenlign, period=(period_slider[0], period_slider[1]))
    tota = sumword(sammenlign, media = 'avis', period=(period_slider[0], period_slider[1]))
    for x in dfb:
        dfb[x] = dfb[x]/totb
    for x in dfa:
        dfa[x] = dfb[x]/tota

dfb.index = pd.to_datetime(dfb.index, format='%Y')
dfa.index = pd.to_datetime(dfa.index, format='%Y')

# draw the trendlines
st.header('Trendlinjer totalt for bøker')
st.line_chart(dfb)

st.header('Trendlinjer totalt for aviser')
st.line_chart(dfa)


# draw frequencies - will use them to select afterwards
st.header('Frekvenser')
st.write(resultat)


#words_to_print = [w for w in resultat.index]

#check_boxes = [st.checkbox(word_to_print, key = word_to_print) for word_to_print in words_to_print]

#st.write([w for w, checked in zip(words_to_print, check_boxes) if checked])



# show concordances
st.header('Konkordanser')
konk_ord = st.text_input('konkordanseord', list(resultat.index)[0])
konks = nb.concordance(konk_ord, corpus='bok', yearfrom = period_slider[0], yearto = period_slider[1], size = 20, kind='json')

st.markdown('\n\n'.join([ str(j['before']) + ' _' + str(j['word']) + '_ ' + str(j['after']) \
            + ' $\\bullet$  [' + str(j['title']) + '](' + str(j['urn']) + '?searchText=' + konk_ord + '), ' + \
          j['author'] + ', ' + str(j['year']) for j in konks]
                       ))
#st.write(konks)
