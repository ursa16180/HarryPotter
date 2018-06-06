import re
import orodja
import html

vzorec_opis_zanr = re.compile("""mediumText reviewText">\s+?<span id="freeTextContainer\d+?">(?P<opis>.+?)</span>(\s+?<span id="freeText\d+?" style="display:none">(?P<opis_dolg>.+?)</span>)?""")

vzorec_ime_zanra =re.compile("""<div class="genreHeader">\s+<h1 class="left">\s+(?P<ime_zanra>.*?)\s+?</h1>""")

seznam_vseh_zanrov = []

zanri_za_popravit={'Academic': 'School Stories', 'School': 'School Stories', 'Education': 'School Stories',
                   'American Revolution': 'American', 'Animal Fiction':'Animals', 'Children S Young Adult':'Childrens',
                   'Adult': 'Adult Fiction', 'Christian Fantasy':'Christian Fiction', 'Chivalric Romance':'Romance',
                   'Business Investing':'Business', 'Biography Memoir':'Biography', 'Astrophysics':'Science',
                   'Arthurian Romance': 'Arthurian', 'Arts Photography': 'Art', 'Christian': 'Christian Fiction',
                   'Christianity':'Christian Fiction', 'Classic Literature': 'Classics', 'Comics Manga':'Comics',
                   'Graphic Novels Comics':'Comics','Dc Comics':'Comics','Cooking Food Wine':'Cookbooks',
                   'Cooking':'Cookbooks', 'Food and Drink': 'Cookbooks',
                   'Epic Fantasy':'Epic','Fables':'Fairy Tales', 'English History':'Historical', 'Fae':'Fairies',
                   'Fairy Tale Retellings':'Fairy Tales', 'Science Fiction Fantasy':'Science Fiction',
                   'Folk Tales':'Folklore','Funny':'Humor','Ghost Stories':'Ghosts', 'Gods': 'Mythology',
                   'Greek Mythology':'Mythology', 'Health Mind Body':'Health', 'High School':'School Stories',
                   'History':'Historical', 'Humor Satire':'Humor', 'Juvenile':'Young Adult', 'Lds Fiction':'Lds',
                   'M M Romance':'Lgbt', 'Mystery Thrillers':'Mystery Thriller','New York':'American',
                   'Northern Africa':'','Paranormal Fiction':'Paranormal','Parenting Families':'Family',
                   'Mental Health':'Psychology', 'Screenplays Plays':'Plays', 'Shojo':'Manga', 'Shonen':'Manga',
                   'Social Science':'Sociology', 'Sports and Games':'Sports','Teen':'Young Adult',
                   'Thriller and Horror':'Thriller','Translations':'','Translation':'','Tudor Period':'Historical',
                   'Did Not Finish':'','Upper Middle Grade':'Young Adult','Middle Grade':'Childrens',
                   'Urban':'Contemporary','Webcomic':'Comics','Wicca':'Witches','Writing Creativity':'Writing',
                   'Ya Paranormal Romance':'Young Adult Paranormal', 'Young Adult Paranormal Fantasy':'Young Adult Paranormal',
                   'Young Adult Contemporary Fiction':'Young Adult Contemporary','Youth Fiction':'Young Adult',
                   'Government':'Politics','18th Century':'Historical','19th Century':'Historical', 'Gay and Lesbian':'Lgbt',
                   'Books About Books':'Writing', 'Literary Fiction':'Fiction', 'Basketball':'Sports', 'Baseball':'Sports',
                   'France':'', 'Cryptozoology':'', 'Childrens Classics':'Classics', 'Fantasy Magic Adventure':'Magic',
                   'Roman':'', 'Asian Literature':'','Japanese Literature':'', 'Adolescence':'Young Adult', 'Canada':'',
                   'Italy':'','Australia':'', 'Chapter Books':'', 'Favorites':'', 'Unfinished':'', 'Africa':'', 'Movies':'',
                   'Reference':'', 'Entertainment':'', 'India':'', 'Egypt':'', 'Multi Genre':'', 'Historical Fiction':'Historical',
                   'Ebooks':'', 'Audiobooks':'', 'Audiobook':'', 'Literature':'', 'Amazon':'','Japan':'','Read For School':'',
                   'British Literature':'', 'Ireland':'', 'Russia':'', 'Glbt':'Lgbt', 'North American Hi...':'Historical',
                   'Kids':'Childrens', 'Sci Fi Fantasy':'Science Fiction' ,'Teen Fiction':'Teen', 'Social Sciences':'Sociology',
                   'Ya Fantasy':'Young Adult Fantasy', 'Dystopian':'Dystopia', 'Fanfiction':'Fan Fiction',
                   'Children\'s, Young Adult':'Childrens'
                   }

mapa = orodja.datoteke("zanri")
def shrani_zanre(mapa):
    for zanr in mapa:
        print(zanr)
        vsebina = orodja.vsebina_datoteke(zanr)
        podatki2={'opis': None}
        for vzorec1 in re.finditer(vzorec_ime_zanra, vsebina):
            podatki1 = vzorec1.groupdict()

        for vzorec2 in re.finditer(vzorec_opis_zanr, vsebina):
            podatki2 = vzorec2.groupdict()
            if podatki2['opis_dolg'] is None: #Opis je takratek
                podatki2['opis'] = orodja.pocisti_niz(html.unescape(podatki2["opis"]))
            else:
                podatki2['opis'] = orodja.pocisti_niz(html.unescape(podatki2["opis_dolg"]))

        ###CSV za zanr
        podatkiZanr = dict()
        zajeti_zanr = html.unescape(podatki1['ime_zanra'])
        if not zajeti_zanr in zanri_za_popravit.keys():
            podatkiZanr['ime_zanra'] = zajeti_zanr
            podatkiZanr['opis'] = podatki2['opis']
            seznam_vseh_zanrov.append(podatkiZanr)
        else:
            print('Nisem dodal {}'.format(zajeti_zanr))

#shrani_zanre(mapa)
#orodja.zapisi_tabelo(seznam_vseh_zanrov,
#                     ['ime_zanra', 'opis'],
#                     'podatki/zanr.csv')