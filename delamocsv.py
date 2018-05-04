import re
import orodja

vzorec_naslov_url_avtorja_serije = re.compile("""metacol" class="last col">\s*?<h1\sid="bookTitle"\sclass="bookTitle"\sitemprop="name">\s*(?P<naslov>.*?)\s*?(<a class="greyText" href="(?P<url_serije>.+?)">(\s|.)*?</a>)?</h1>\s*?<div id="bookAuthors" class="stacked">\s+?<span class='by smallText'>by</span>\s+?<span itemprop='author' itemscope='' itemtype='http://schema\.org/Person'>\s(<div class=("|')authorName__container("|')>\s?)?<a class="authorName" itemprop="url" href="(?P<url_avtorja1>.+?)"><span itemprop="name">\D+?</span></a>(\s<span class="greyText">\(Goodreads Author\)</span>)?(\s*?<span class="authorName greyText smallText role">.+?</span>)?(,(\s*?</div>\s*?<div class=("|')authorName__container("|')>)?\s*?<a class="authorName" itemprop="url" href="(?P<url_avtorja2>.+?)"><span itemprop="name">\D+?</span></a>(\s<span class="greyText">\(Goodreads Author\)</span>)?(\s?<span class="authorName greyText smallText role">.+?</span>)?)?((\s?</div>\s?<div class=("|')authorName__container("|')>)?\s*?<a class="authorName" itemprop="url" href="(?P<url_avtorja3>.+?)"><span itemprop="name">\D+?</span></a>(\s<span class="greyText">\(Goodreads Author\)</span>)? (<span class="authorName greyText smallText role">.+?</span>)?)?(\s*?</div>)?\s*?</span>\s+?</div>\s+?<div id="bookMeta""")

vzorec_ocene = re.compile("""stars staticStars"(\stitle="really liked it")?>(<span size="12x12" class="staticStar p\d\d?">.*?</span>){5}</span>\s*?<span class="value rating"><span class="average" itemprop="ratingValue">(?P<povprecna_ocena>.*?)</span></span>\s*?<span class="greyText">&nbsp;&middot;&nbsp;</span>""")

vzorec_stevilo_ocen_opis = re.compile("""#other_reviews\">\s*?<meta itemprop=\"ratingCount\" content=\".*?\">\s*?<span class=\"votes value-title\" title=\".*?\">\s*(?P<stevilo_ocen>.*?)\s*?</span>\s*?Ratings\s*?</a><span class=\"greyText\">&nbsp;&middot;&nbsp;</span>\s+?<a class="gr-hyperlink" href="#other_reviews">\s+?<span class="count value-title" title="\d+?">\s+?.+?\s+?</span>\s+?Reviews\s+?</a>\s+?</div>\s+?<div id="descriptionContainer">\s+?<div id="description" class="readable stacked" style="right:0">\s+?<span id="freeTextContainer\d+?">(?P<opis1>.+?)</span>(\s+?<span id="freeText\d+?" style="display:none">(<strong>\s+?<i>This is an adaptation. For the editions of the original book, see <a href=".*?" rel="nofollow">here</a></i>\s+?</strong>.<br /><br />)?(?P<opis>.+?)(</p>)?</span>\s+?<a data-text-id="\d+?" href="#" onclick)?""")

vzorec_stevilo_strani_leto = re.compile("""bookFormat">(.*?)</span>,\s*?<span itemprop="numberOfPages">(?P<stevilo_strani>\d\d\d?\d?) pages</span></div>\s*?<div class="row">\s*?Published(\s|.)*?(<nobr class="greyText">\s*?\(first published (?P<leto_izdaje>\d\d\d\d)\)\s*?</nobr>)?\s*?</div>\s*?<div class="buttons">\s*?<a id="bookDataBoxShow" class="left inter""")
# leto izdaje še manjka pri nekaterih

#Kindle knjige nimajo ISBN-ja ampak ASIN. Tako da je za njih treba različno pobrat.
# vzorec_ISBN = re.compile("""<div class="clearFloats">\s*?<div class="infoBoxRowTitle">ISBN</div>\s*?<div class="infoBoxRowItem">\s*?\d+?\s*?<span class="greyText">\(ISBN13: <span itemprop='isbn'>(?P<ISBN>\d+?)</span>\)</span>\s.*?</div>""")

###Vzame ali ISBN ali ASIN:
vzorec_ISBN = re.compile("""itemprop='isbn'>(?P<ISBN>(\w{10}|\d{13}))""")


knjige = orodja.datoteke("knjige/test")


seznam_vseh_knjig = []
seznam_vseh_avtorjev=[]
seznam_vseh_zanrov = []

for knjiga in knjige:
    vsebina = orodja.vsebina_datoteke(knjiga)
    print(knjiga)
    for vzorec1 in re.finditer(vzorec_naslov_url_avtorja_serije, vsebina):
        podatki1 = vzorec1.groupdict()
        print(podatki1)
    print('prvega sm')
    for vzorec2 in re.finditer(vzorec_ocene, vsebina):
        podatki2 = vzorec2.groupdict()
        print(podatki2)
    print('druzga sm')
    for vzorec3 in re.finditer(vzorec_stevilo_ocen_opis, vsebina):
        podatki3 = vzorec3.groupdict()
        if podatki3['opis'] is None:
            podatki3['opis'] = orodja.pocisti_niz(podatki3['opis1'])
        else:
            podatki3['opis'] = orodja.pocisti_niz(podatki3['opis'])
        # TODO: več presledkov spremeni v enega - orodja.pocisti_niz.
        print(podatki3)
    print('tretji je')
    for vzorec4 in re.finditer(vzorec_stevilo_strani_leto, vsebina):
        podatki4 = vzorec4.groupdict()
        print(podatki4)
    print('četrti je')
    for vzorec5 in re.finditer(vzorec_ISBN, vsebina):
        podatki5 = vzorec5.groupdict()
        print(podatki5)
    ###CSV za tabelo KNJIGA
    podatkiKnjiga = dict()
    podatkiKnjiga['naslov']=podatki1['naslov']
    podatkiKnjiga['povprečna ocena'] = podatki2['povprecna_ocena']
    podatkiKnjiga['št. ocen'] = int(re.sub('[,]','',podatki3['stevilo_ocen']))###to spremeni niz glasov v integer brez vejc
    #print(podatkiKnjiga['št. ocen'])
    podatkiKnjiga['opis'] = podatki3['opis'] ###TODO dve knjigi zapored sta imeli enak opis?!
    podatkiKnjiga['št. strani'] = podatki4['stevilo_strani']
    podatkiKnjiga['leto'] = podatki4['leto_izdaje'] ###TODO letnica ne dela dobr
    podatkiKnjiga['ISBN'] = podatki5['ISBN']#TODO mislim da če ne najde ISBNja uporabi istega kot prejšna knjiga
    seznam_vseh_knjig += [podatkiKnjiga]


    ###CSV za tabelo AVTOR
    podatkiAvtor1 = dict()
    podatkiAvtor2 = dict()
    podatkiAvtor3 = dict()
    podatkiAvtor1['ISBN'] = podatki5['ISBN']
    podatkiAvtor1['url'] = podatki1['url_avtorja1']
    podatkiAvtor2['ISBN'] = podatki5['ISBN']
    podatkiAvtor2['url'] = podatki1['url_avtorja2']
    podatkiAvtor3['ISBN'] = podatki5['ISBN']
    podatkiAvtor3['url'] = podatki1['url_avtorja3']
    seznam_vseh_avtorjev.extend([podatkiAvtor1, podatkiAvtor2, podatkiAvtor3])

    ###CSV za tabelo ZANR
    podatkiZanr = dict()
    podatkiZanr['ISBN']= podatki5['ISBN']
    podatkiZanr['žanr'] = "fantasy"  # TODO
    seznam_vseh_zanrov += [podatkiZanr]

#print(seznam_vseh_knjig)

orodja.zapisi_tabelo(seznam_vseh_knjig, ['ISBN', 'naslov', 'povprečna ocena', 'št. ocen',
                                         'leto','št. strani', 'opis'
                                         ], 'podatki/knjigaTest.csv') ###PAZI Naj se CSV imenuje vedno isto kot tabela, drugale ga naredi tabele ne prepozna

#
#     print('en narjen ' + str(i))
#     i += 1

# orodja.zapisi_tabelo(seznam_vseh_knjig, ['id', 'avtor', 'naslov', 'št. strani', 'povprečna ocena',
#                                          'št. ocen' , 'leto', 'žanr', 'št. glasov', 'avtor2'
#                                         ], 'podatki/tabela_knjige.csv')



