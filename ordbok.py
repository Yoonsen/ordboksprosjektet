import streamlit as st
import dhlab.nbtext as nb
import pandas as pd
import matplotlib.pyplot as plt
from io import StringIO, BytesIO
from PIL import Image

@st.cache(suppress_st_warning=True, show_spinner = False)
def ngram(wordex, period, ddk = None):
    if " " in word:
        bigram = word.split()[:2]
        res = nb.bigram(first = bigram [0], second = bigram [1], ddk=ddk, period = period)
    else:
        res = nb.unigram(word, period = period, ddk=ddk)
    return res

@st.cache(suppress_st_warning=True, show_spinner = False)
def sumword(words, period, media = 'bok'):
    wordlist =   [x.strip() for x in words.split(',')]
    # check if trailing comma, or comma in succession, if so count comma in
    if '' in wordlist:
        wordlist = [','] + [y for y in wordlist if y != '']
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
def ngbok(x, period, ddk = None):
    try:
        r = nb.frame(nb.unigram(x, period, media='bok', ddk=ddk), x)
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
st.markdown('Se mer om å drive analytisk DH på [DHLAB-siden](https://nbviewer.jupyter.org/github/DH-LAB-NB/DHLAB/blob/master/DHLAB_ved_Nasjonalbiblioteket.ipynb), og korpusanalyse via web [her](https://beta.nb.no/korpus/)')


st.title('Ordsøk for revisjonsprosjektet')

word = st.text_input('Fyll in ett ord med jokertegnet *, eller flere ord skilt med komma. Om bare ett ord er fylt inn søkes det i paradigmet for ordet, for alle former i alle passende paradigmer. Søket skiller mellom store og små bo', "frum*")

st.sidebar.header('Parametre for jokertegnsøk')
faktor = st.sidebar.number_input('Forskjell i ordlengde', min_value = 0, value = 2)
frekvens = st.sidebar.number_input('Frekvensgrense', min_value = 1, value = 50)
limit = st.sidebar.number_input('Antall treff', min_value = 5, value = 10)

using_wildcard = True

if ',' in word and not '*' in word:
    words = [w.strip() for w in word.split(',')]
    if '' in words:
        words = [','] + [y for y in words if y != '']
    resultat = pd.DataFrame(words).set_index(0)
    using_wildcard = False
elif not ',' in word and not '*' in word:
    using_wildcard = False
    resultat = pd.DataFrame(list(set([word] + [x for y in nb.word_paradigm(word) for x in y[1]]))).set_index(0) 
else:
    resultat = wildcard(word = word, faktor = faktor, frekvens = frekvens, antall = limit)

st.sidebar.header('Relativisering')
st.sidebar.markdown('Relativiser til summen av et sett ord, standard er punktum og komma, som gir ca en tiendedel av relativfreksensen. Sett inn ord adskilt med komma, for å få med komma, skrive to eller fler komma etter hverandre, eller avslutt med komma')
sammenlign = st.sidebar.text_input("", ".,")

st.sidebar.header('Periode i år')
st.sidebar.markdown('Se på trender fra første til siste år')
period_slider = st.sidebar.slider(
    '',
    1900, 2020, (1900, 2010)
)

st.sidebar.header('Visning')
st.sidebar.markdown('Grafen glattes til gjennomsnittsverdien av årene foran og etter, fra 1 til 8')
smooth_slider = st.sidebar.slider('', 1, 8, 3)



dfb = pd.concat([ngbok(x, period=(period_slider[0], period_slider[1]))  for x in resultat.index], axis = 1)
dfa = pd.concat([ngavis(x, period=(period_slider[0], period_slider[1]))  for x in resultat.index], axis = 1)

# update result
# if not using wildcard

#if not using_wildcard:
r0 = dfb.sum(axis=0).transpose()
r1 = dfa.sum(axis = 0).transpose()
ddk = pd.concat([ngbok(x, ddk = '4%', period=(period_slider[0], period_slider[1]))  for x in resultat.index], axis = 1).sum(axis = 0).transpose()
resultat = pd.concat([r0, r1, ddk], axis = 1).fillna(0)
resultat.columns = ['bok', 'avis', 'ddk4']
    


# Råfrekvenser unigram
if sammenlign != "":
    totb = sumword(sammenlign, period=(period_slider[0], period_slider[1]))
    tota = sumword(sammenlign, media = 'avis', period=(period_slider[0], period_slider[1]))
    for x in dfb:
        dfb[x] = dfb[x]/totb
    for x in dfa:
        dfa[x] = dfa[x]/tota

        
dfb.index = pd.to_datetime(dfb.index, format='%Y')
dfa.index = pd.to_datetime(dfa.index, format='%Y')


dfb = dfb.rolling(window= smooth_slider).mean()
dfa = dfa.rolling(window= smooth_slider).mean()




# draw the trendlines
st.header('Trendlinjer')
st.subheader('Bøker')




axb = dfb.plot(figsize = (8, 4), lw = 5, alpha=0.8)
axb.spines["top"].set_visible(False)
axb.spines["right"].set_visible(False)

axb.spines["bottom"].set_color("grey")
axb.spines["left"].set_color("grey")
axb.spines["bottom"].set_linewidth(3)
axb.spines["left"].set_linewidth(3)

figfile = StringIO()
plt.savefig(figfile, format='svg')  # rewind to beginning of file

#st.write(figfile.getvalue())
#st.pyplot()
st.markdown(figfile.getvalue(), unsafe_allow_html=True)

st.subheader('Aviser')

axa = dfa.plot(figsize = (8, 4), lw = 5, alpha=0.8)
axa.spines["top"].set_visible(False)
axa.spines["right"].set_visible(False)

axa.spines["bottom"].set_color("grey")
axa.spines["left"].set_color("grey")
axa.spines["bottom"].set_linewidth(3)
axa.spines["left"].set_linewidth(3)

figfile = StringIO()
plt.savefig(figfile, format='svg')  # rewind to beginning of file
st.markdown(figfile.getvalue(), unsafe_allow_html=True)

#st.line_chart(dfa)


# draw frequencies - will use them to select afterwards
st.header('Frekvenser')
st.write(resultat)


#words_to_print = [w for w in resultat.index]

#check_boxes = [st.checkbox(word_to_print, key = word_to_print) for word_to_print in words_to_print]

#st.write([w for w, checked in zip(words_to_print, check_boxes) if checked])



# show concordances
st.header('Konkordanser')
konk_ord = st.text_input('konkordanseord', list(resultat.index)[0])
#media_type = st.radio('Mediatype', ['bok', 'avis'])
konks = nb.concordance(konk_ord, corpus= 'bok', yearfrom = period_slider[0], yearto = period_slider[1], size = 20, kind='json')

st.markdown('\n\n'.join([ str(j['before']) + ' _' + str(j['word']) + '_ ' + str(j['after']) \
            + ' $\\bullet$  [' + str(j['title']) + '](' + str(j['urn']) + '?searchText=' + konk_ord + '), ' + \
          j['author'] + ', ' + str(j['year']) for j in konks]
                       ))
#st.write(konks)
