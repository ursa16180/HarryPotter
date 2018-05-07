import re
import orodja

vzorec_naslov_url_avtorja_serije = re.compile("""metacol" class="last col">\s*?<h1\sid="bookTitle"\sclass="bookTitle"\sitemprop="name">\s*(?P<naslov>.*?)\s*?(<a class="greyText" href="(?P<url_serije>.+?)">(\s|.)*?</a>)?</h1>\s*?<div id="bookAuthors" class="stacked">\s*?<span class='by smallText'>by</span>\s*?<span itemprop='author' itemscope='' itemtype='http://schema.org/Person'>\s*?<div class=('|")authorName__container('|")>\s*?<a class="authorName" itemprop="url" href="(?P<url_avtorja1>.*?(?P<id_avtorja1>\d+?)\D*?)"><span itemprop="name">.+?</span></a>(\s?<span class="greyText">\(Goodreads Author\)</span>\s*?)?(\s?<span class="authorName greyText smallText role">\(.+?\)</span>\s?)?,?\s*?</div>\s*?(,\s*?)?(\s*?<div class=('|")authorName__container('|")>\s*?<a class="authorName" itemprop="url" href="(?P<url_avtorja2>.*?(?P<id_avtorja2>\d+?)\D*?)"><span itemprop="name">.+?</span></a>(\s?<span class="greyText">\(Goodreads Author\)</span>\s*?)?(\s?<span class="authorName greyText smallText role">\(.+?\)</span>\s?)?,?\s*?</div>\s*?(,\s*?)?)?(\s*?<div class=('|")authorName__container('|")>\s*?<a class="authorName" itemprop="url" href="(?P<url_avtorja3>.*?(?P<id_avtorja3>\d+?)\D*?)"><span itemprop="name">.+?</span></a>(\s?<span class="greyText">\(Goodreads Author\)</span>\s*?)?(\s?<span class="authorName greyText smallText role">\(.+?\)</span>\s?)?,?\s*?</div>\s*?(,\s*?)?)?</span>\s*?</div>\s*?<div id="bookMeta""")

vzorec_ocene = re.compile("""stars staticStars"(\stitle="really liked it")?>(<span size="12x12" class="staticStar p\d\d?">.*?</span>){5}</span>\s*?<span class="value rating"><span class="average" itemprop="ratingValue">(?P<povprecna_ocena>.*?)</span></span>\s*?<span class="greyText">&nbsp;&middot;&nbsp;</span>""")

vzorec_stevilo_ocen_opis = re.compile("""#other_reviews\">\s*?<meta itemprop=\"ratingCount\" content=\".*?\">\s*?<span class=\"votes value-title\" title=\".*?\">\s*(?P<stevilo_ocen>.*?)\s*?</span>\s*?Ratings\s*?</a><span class=\"greyText\">&nbsp;&middot;&nbsp;</span>\s+?<a class="gr-hyperlink" href="#other_reviews">\s+?<span class="count value-title" title="\d+?">\s+?.+?\s+?</span>\s+?Reviews\s+?</a>\s+?</div>\s+?<div id="descriptionContainer">\s+?<div id="description" class="readable stacked" style="right:0">\s+?<span id="freeTextContainer\d+?">(?P<opis1>.+?)</span>(\s+?<span id="freeText\d+?" style="display:none">(Alternate Cover Edition can be found <a href=".*?" rel="nofollow">here</a>.)?(<strong>\s+?<i>This is an adaptation. For the editions of the original book, see <a href=".*?" rel="nofollow">here</a></i>\s+?</strong>.<br /><br />)?(?P<opis>.+?)(</p>)?</span>\s+?<a data-text-id="\d+?" href="#" onclick)?""")

vzorec_stevilo_strani_leto = re.compile("""bookFormat">(.*?)</span>,\s*?<span itemprop="numberOfPages">(?P<stevilo_strani>\d\d\d?\d?) pages</span></div>\s*?<div class="row">\s*?Published(\s|.)*?(<nobr class="greyText">\s*?\(first published (?P<leto_izdaje>\d\d\d\d)\)\s*?</nobr>)?\s*?</div>\s*?<div class="buttons">\s*?<a id="bookDataBoxShow" class="left inter""")
# leta nimajo vse knjige

vzorec_zanri = re.compile("""stacked">\s*?<div class=" clearFloats bigBox"><div class="h2Container gradientHeaderContainer"><h2 class="brownBackground"><a href="/work/shelves/\d+?">Genres</a></h2></div><div class="bigBoxBody"><div class="bigBoxContent containerWithHeaderContent">\s*?<div class="elementList (elementListLast)?">\s*?<div class="left">\s*?<a class="actionLinkLite bookPageGenreLink" href="/genres/.*?">(?P<zanr1>.*?)</a>( &gt;\s*?<a class="actionLinkLite bookPageGenreLink" href=".*?">(?P<zanr15>.*?)</a>)?\s*?</div>\s*?<div class="right">\s*?<a title="\d+? people shelved this book as .*?;" class="actionLinkLite greyText bookPageGenreLink" rel="nofollow" href=".*?">.+? users?</a>\s*?</div>\s*?<div class="clear"></div>\s*?</div>\s*?<div class="elementList (elementListLast)?">\s*?<div class="left">\s*?<a class="actionLinkLite bookPageGenreLink" href="/genres/.*?">(?P<zanr2>.*?)</a>( &gt;\s*?<a class="actionLinkLite bookPageGenreLink" href=".*?">(?P<zanr25>.*?)</a>)?\s*?</div>\s*?<div class="right">\s*?<a title="\d+? people shelved this book as .*?;" class="actionLinkLite greyText bookPageGenreLink" rel="nofollow" href=".*?">.+? users?</a>\s*?</div>\s*?<div class="clear"></div>\s*?</div>\s*?<div class="elementList (elementListLast)?">\s*?<div class="left">\s*?<a class="actionLinkLite bookPageGenreLink" href="/genres/.*?">(?P<zanr3>.*?)</a>( &gt;\s*?<a class="actionLinkLite bookPageGenreLink" href=".*?">(?P<zanr35>.*?)</a>)?\s*?</div>\s*?<div class="right">\s*?<a title="\d+? people shelved this book as .*?;" class="actionLinkLite greyText bookPageGenreLink" rel="nofollow" href=".*?">.+? users?</a>\s*?</div>\s*?<div class="clear"></div>\s*?</div>\s*?(<div class="elementList (elementListLast)?">\s*?<div class="left">\s*?<a class="actionLinkLite bookPageGenreLink" href="/genres/.*?">(?P<zanr4>.*?)</a>( &gt;\s*?<a class="actionLinkLite bookPageGenreLink" href=".*?">(?P<zanr45>.*?)</a>)?\s*?</div>\s*?<div class="right">\s*?<a title="\d+? people shelved this book as .*?;" class="actionLinkLite greyText bookPageGenreLink" rel="nofollow" href=".*?">.+? users?</a>\s*?</div>\s*?<div class="clear"></div>\s*?</div>\s*?)?(<div class="elementList (elementListLast)?">\s*?<div class="left">\s*?<a class="actionLinkLite bookPageGenreLink" href="/genres/.*?">(?P<zanr5>.*?)</a>( &gt;\s*?<a class="actionLinkLite bookPageGenreLink" href=".*?">(?P<zanr55>.*?)</a>)?\s*?</div>\s*?<div class="right">\s*?<a title="\d+? people shelved this book as .*?;" class="actionLinkLite greyText bookPageGenreLink" rel="nofollow" href=".*?">.+? users?</a>\s*?</div>\s*?<div class="clear"></div>\s*?</div>\s*?)?(<div class="elementList (elementListLast)?">\s*?<div class="left">\s*?<a class="actionLinkLite bookPageGenreLink" href="/genres/.*?">(?P<zanr6>.*?)</a>( &gt;\s*?<a class="actionLinkLite bookPageGenreLink" href=".*?">(?P<zanr65>.*?)</a>)?\s*?</div>\s*?<div class="right">\s*?<a title="\d+? people shelved this book as .*?;" class="actionLinkLite greyText bookPageGenreLink" rel="nofollow" href=".*?">.+? users?</a>\s*?</div>\s*?<div class="clear"></div>\s*?</div>\s*?)?(<div class="elementList (elementListLast)?">\s*?<div class="left">\s*?<a class="actionLinkLite bookPageGenreLink" href="/genres/.*?">(?P<zanr7>.*?)</a>( &gt;\s*?<a class="actionLinkLite bookPageGenreLink" href=".*?">(?P<zanr75>.*?)</a>)?\s*?</div>\s*?<div class="right">\s*?<a title="\d+? people shelved this book as .*?;" class="actionLinkLite greyText bookPageGenreLink" rel="nofollow" href=".*?">.+? users?</a>\s*?</div>\s*?<div class="clear"></div>\s*?</div>\s*?)?(<div class="elementList (elementListLast)?">\s*?<div class="left">\s*?<a class="actionLinkLite bookPageGenreLink" href="/genres/.*?">(?P<zanr8>.*?)</a>( &gt;\s*?<a class="actionLinkLite bookPageGenreLink" href=".*?">(?P<zanr85>.*?)</a>)?\s*?</div>\s*?<div class="right">\s*?<a title="\d+? people shelved this book as .*?;" class="actionLinkLite greyText bookPageGenreLink" rel="nofollow" href=".*?">.+? users?</a>\s*?</div>\s*?<div class="clear"></div>\s*?</div>\s*?)?(<div class="elementList (elementListLast)?">\s*?<div class="left">\s*?<a class="actionLinkLite bookPageGenreLink" href="/genres/.*?">(?P<zanr9>.*?)</a>( &gt;\s*?<a class="actionLinkLite bookPageGenreLink" href=".*?">(?P<zanr95>.*?)</a>)?\s*?</div>\s*?<div class="right">\s*?<a title="\d+? people shelved this book as .*?;" class="actionLinkLite greyText bookPageGenreLink" rel="nofollow" href=".*?">.+? users?</a>\s*?</div>\s*?<div class="clear"></div>\s*?</div>\s*?)?(<div class="elementList (elementListLast)?">\s*?<div class="left">\s*?<a class="actionLinkLite bookPageGenreLink" href="/genres/.*?">(?P<zanr10>.*?)</a>( &gt;\s*?<a class="actionLinkLite bookPageGenreLink" href=".*?">(?P<zanr105>.*?)</a>)?\s*?</div>\s*?<div class="right">\s*?<a title="\d+? people shelved this book as .*?;" class="actionLinkLite greyText bookPageGenreLink" rel="nofollow" href=".*?">.+? users?</a>\s*?</div>\s*?<div class="clear"></div>\s*?</div>\s*?)?(<div class="elementList (elementListLast)?">\s*?<div class="left">\s*?<a class="actionLinkLite bookPageGenreLink" href="/genres/.*?">(?P<zanr11>.*?)</a>( &gt;\s*?<a class="actionLinkLite bookPageGenreLink" href=".*?">(?P<zanr115>.*?)</a>)?\s*?</div>\s*?<div class="right">\s*?<a title="\d+? people shelved this book as .*?;" class="actionLinkLite greyText bookPageGenreLink" rel="nofollow" href=".*?">.+? users?</a>\s*?</div>\s*?<div class="clear"></div>\s*?</div>\s*?)?<a class="actionLink right bookPageGenreLink__seeMoreLink" href=".*?">See top shelves…""")

#Kindle knjige nimajo ISBN-ja ampak ASIN. Tako da je za njih treba različno pobrat.
# vzorec_ISBN = re.compile("""<div class="clearFloats">\s*?<div class="infoBoxRowTitle">ISBN</div>\s*?<div class="infoBoxRowItem">\s*?\d+?\s*?<span class="greyText">\(ISBN13: <span itemprop='isbn'>(?P<ISBN>\d+?)</span>\)</span>\s.*?</div>""")
###Vzame ali ISBN ali ASIN:
vzorec_ISBN = re.compile("""itemprop='isbn'>(?P<ISBN>(\w{10}|\d{13}))""")


knjige = orodja.datoteke("knjige")


seznam_vseh_knjig = []
seznam_vseh_avtorjev=[]
seznam_vseh_zanrov = []
slovar_url_avtorjev =dict()

for knjiga in knjige:
    vsebina = orodja.vsebina_datoteke(knjiga)
    print(knjiga)
    for vzorec1 in re.finditer(vzorec_naslov_url_avtorja_serije, vsebina):
        podatki1 = vzorec1.groupdict()
        #print(podatki1)
    #print('prvega sm')
    for vzorec2 in re.finditer(vzorec_ocene, vsebina):
        podatki2 = vzorec2.groupdict()
        #print(podatki2)
    #print('druzga sm')
    for vzorec3 in re.finditer(vzorec_stevilo_ocen_opis, vsebina):
        podatki3 = vzorec3.groupdict()
        if podatki3['opis'] is None:
            podatki3['opis'] = orodja.pocisti_niz(podatki3['opis1'])
        else:
            podatki3['opis'] = orodja.pocisti_niz(podatki3['opis'])
        #print(podatki3)
    #print('tretji je')
    for vzorec4 in re.finditer(vzorec_stevilo_strani_leto, vsebina):
        podatki4 = vzorec4.groupdict()
        #print(podatki4)
    #print('četrti je')
    for vzorec5 in re.finditer(vzorec_ISBN, vsebina):
        podatki5 = vzorec5.groupdict()
        #print(podatki5)
    for vzorec6 in re.finditer(vzorec_zanri, vsebina):
        podatki6 = vzorec6.groupdict()
        #print(podatki6)
    ###CSV za tabelo KNJIGA
    podatkiKnjiga = dict()
    podatkiKnjiga['naslov']=podatki1['naslov']
    podatkiKnjiga['povprečna ocena'] = podatki2['povprecna_ocena']
    podatkiKnjiga['št. ocen'] = int(re.sub('[,]','',podatki3['stevilo_ocen']))###to spremeni niz glasov v integer brez vejc
    #print(podatkiKnjiga['št. ocen'])
    podatkiKnjiga['opis'] = podatki3['opis']
    podatkiKnjiga['št. strani'] = podatki4['stevilo_strani']
    podatkiKnjiga['leto'] = podatki4['leto_izdaje']
    podatkiKnjiga['ISBN'] = podatki5['ISBN']
    seznam_vseh_knjig += [podatkiKnjiga]


    ###CSV za tabelo AVTORKNJIGE
    podatkiAvtor1 = dict()
    podatkiAvtor2 = dict()
    podatkiAvtor3 = dict()
    podatkiAvtor1['ISBN'] = podatki5['ISBN']
    podatkiAvtor1['id'] = podatki1['id_avtorja1']

    podatkiAvtor2['ISBN'] = podatki5['ISBN']
    podatkiAvtor2['id'] = podatki1['id_avtorja2']
    #url_avtorja2 = podatki1['url_avtorja2']
    podatkiAvtor3['ISBN'] = podatki5['ISBN']
    podatkiAvtor3['id'] = podatki1['id_avtorja3']
    #url_avtorja3 = podatki1['url_avtorja3']

    if podatkiAvtor2['id'] is not None:
        seznam_vseh_avtorjev.extend([podatkiAvtor1, podatkiAvtor2])
        slovar_url_avtorjev[podatki1['id_avtorja1']]= podatki1['url_avtorja1']
        slovar_url_avtorjev[podatki1['id_avtorja2']] = podatki1['url_avtorja2']
        if podatkiAvtor3['id'] is not None:
            seznam_vseh_avtorjev +=[podatkiAvtor3]
            slovar_url_avtorjev[podatki1['id_avtorja3']] = podatki1['url_avtorja3']
    else:
        seznam_vseh_avtorjev += [podatkiAvtor1]
        slovar_url_avtorjev[podatki1['id_avtorja1']] = podatki1['url_avtorja1']

    #seznam_vseh_avtorjev.extend([podatkiAvtor1, podatkiAvtor2, podatkiAvtor3])
    #seznam_url_avtorjev.extend([url_avtorja1,url_avtorja2,url_avtorja3])

    ###CSV za tabelo ZANRKNJIGE
    podatkiZanr = dict()
    podatkiZanr['ISBN']= podatki5['ISBN']
    i = 1
    while podatki6['zanr{0}'.format(str(i))] is not None:
        podatkiZanr['žanr'] =   podatki6['zanr{0}'.format(str(i))]
        seznam_vseh_zanrov += [podatkiZanr.copy()]
        if podatki6['zanr{0}5'.format(str(i))] is not None:
            podatkiZanr['žanr'] = podatki6['zanr{0}5'.format(str(i))]        
            seznam_vseh_zanrov += [podatkiZanr]
        i += 1

#print(seznam_vseh_knjig)

# orodja.zapisi_tabelo(seznam_vseh_knjig, ['ISBN', 'naslov', 'povprečna ocena', 'št. ocen',
#                                          'leto','št. strani', 'opis'
#                                          ], 'podatki/knjigaTest.csv') ###PAZI Naj se CSV imenuje vedno isto kot tabela, drugale ga naredi tabele ne prepozna
#print(slovar_url_avtorjev)
#print(seznam_vseh_avtorjev)
zanri = set()
for x in  seznam_vseh_zanrov:
    zanri = {x['žanr']} | zanri


print(zanri | zanriAvtor)
# orodja.zapisi_tabelo(seznam_vseh_knjig, ['id', 'avtor', 'naslov', 'št. strani', 'povprečna ocena',
#                                          'št. ocen' , 'leto', 'žanr', 'št. glasov', 'avtor2'
#                                         ], 'podatki/tabela_knjige.csv')



