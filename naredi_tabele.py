# uvozimo ustrezne podatke za povezavo
import auth
import fileinput

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras

psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)  # se znebimo problemov s šumniki

import csv
import hashlib

from delamo_csv_zanr import zanri_za_popravit
def ustvari_tabelo(seznam):
    cur.execute(seznam[1])
    print("Narejena tabela %s" % seznam[0])
    conn.commit()

def zakodiraj_geslo(geslo):
    hashko=hashlib.md5()
    hashko.update(geslo.encode('utf-8'))
    return hashko.hexdigest()

def daj_pravice():
    cur.execute("GRANT CONNECT ON DATABASE sem2018_ursap TO javnost;"
                "GRANT USAGE ON SCHEMA public TO javnost;"
                "GRANT SELECT ON ALL TABLES IN SCHEMA public TO javnost;"
                "GRANT UPDATE, INSERT, DELETE ON uporabnik, wishlist, prebrana_knjiga TO javnost;"
                "GRANT UPDATE(vsota_ocen, stevilo_ocen) ON knjiga TO javnost;"
                "GRANT ALL ON SEQUENCE uporabnik_id_seq TO javnost;"
                "GRANT ALL ON SCHEMA public TO ursap; "
                "GRANT ALL ON SCHEMA public TO ninast;"
                "GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO ursap;"
                "GRANT ALL ON ALL TABLES IN SCHEMA public TO ursap;"
                "GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO ninast;"
                "GRANT ALL ON ALL TABLES IN SCHEMA public TO ninast;")
    print("Dodane pravice")
    conn.commit()

def pobrisi_tabelo(seznam):
    cur.execute("""
        DROP TABLE %s CASCADE;
    """ % seznam[0])
    print("Izbrisna tabela %s" % seznam[0])
    conn.commit()

def izprazni_tabelo(seznam):
    cur.execute("""
            DELETE FROM %s;
        """ % seznam[0])
    print("Izpraznjena tabela %s" % seznam[0])
    conn.commit()

def uvozi_podatke(seznam):
    if seznam[0] in ["zanr_knjige","avtorjev_zanr"]:
        popravi_zanre("podatki/%s.csv" % seznam[0])
    if seznam[0] in ['knjiga', 'avtor', 'zanr', 'serija', 'del_serije', 'avtor_knjige', 'zanr_knjige', 'avtorjev_zanr', 'knjiga_kljucne_besede']:
        izbrisi_podovojene_vrstice("podatki/%s.csv" % seznam[0])
    with open("podatki/%s.csv" % seznam[0], encoding="utf8") as f:
        rd = csv.reader(f, delimiter=';')
        print("berem")
        next(rd)  # izpusti naslovno vrstico ###TODO če mava res vedno prvo vrstico kr nekej
        for r in rd:
            print(r)
            r = [None if x in ('', '-') else x for x in r]
            cur.execute(seznam[2], r)
            rid, = cur.fetchone()
            print("Uvožen/a %s" % (r[0]))
    conn.commit()


def izbrisi_podovojene_vrstice(datoteka):
    vse_razlice_vrstice=set()
    seznam_vrstic = []
    for vrstica in open(datoteka, "r", encoding="utf8"):
        if vrstica not in vse_razlice_vrstice and vrstica!='Abandoned;\n':
            seznam_vrstic.append(vrstica)
            vse_razlice_vrstice.add(vrstica)
    izhodna_datoteka = open(datoteka, "w", encoding="utf8")
    for vrstica in seznam_vrstic:
        izhodna_datoteka.write(vrstica)
    izhodna_datoteka.close()

def popravi_zanre(ime_datoteke):
    seznam_vrstic = []
    slovar_napacnih ={'Children\'s Books':'Childrens', 'Comics & Graphic Novels':'Comics',
                      'Children\'s':'Childrens', 'Arts & Photography':'Art',
                      'Literature & Fiction':'Fiction','Mystery & Thrillers':'Mystery Thrillers',
                      'Science Fiction & Fantasy':'Science Fiction', 'Biographies & Memoirs':'Biography',
                      'Screenplays & Plays':'Plays','Ya Fantasy':'Young Adult Fantasy',
                      'Humor and Comedy':'Humor','Gay and Lesbian':'Lgbt','North American Hi...':'Historical',
                      'Religion & Spirituality':'Spirituality', 'Mystery & Thriller':'Mystery Thriller',
                      'Young Adult Paranormal & Fantasy':'Young Adult Paranormal Fantasy',
                      'Health, Mind & Body':'Health', 'Glbt':'Lgbt', 'Kids':'Childrens',
                      'Sci Fi Fantasy':'Science Fiction', 'Crafts & Hobbies':'Crafts Hobbies',
                      'Business & Investing':'Business Investing','Gay & Lesbian':'Lgbt', 'Teen Fiction':'Teen',
                      'Professional & Technical':'Professional Technical', 'Social Sciences':'Sociology',
                      'Computers & Internet':'Computers Internet', 'Fantasy, Magic, Adventure':'Magic',
                      'Cooking, Food & Wine':'Cookbooks', 'Dystopian':'Dystopia', 'Fanfiction':'Fan Fiction',
                      'Women & Gender Studies':'Women Gender Studies','Audiobooks':'',
                      'Parenting & Families':'Family','Outdoors & Nature': 'Outdoors Nature',
                      'Fantasy & Science Fiction':'Science Fiction','Children\'s, Young Adult':'Childrens',
                      'Humor & Satire':'Humor', 'Writing & Creativity':'Writing','Academic': 'School Stories',
                      'School': 'School Stories', 'Education': 'School Stories'}
    slovar_napacnih.update(zanri_za_popravit) #TODO Aboriginal Astronomy ne obstaja(avtor 5175986 ima)
    with open(ime_datoteke, 'r') as moj_csv:
        bralec_csvja = csv.reader(moj_csv, delimiter=';')
        for vrstica in bralec_csvja:
            if vrstica[1] in ['Aboriginal Astronomy', ''] or slovar_napacnih.get(vrstica[1],'nič') == '':
                continue
            if vrstica[1] in slovar_napacnih.keys():
                seznam_vrstic.append(vrstica[0]+";"+slovar_napacnih[vrstica[1]]+'\n')
            else:
                seznam_vrstic.append(vrstica[0]+";"+ vrstica[1] +'\n')
    moj_csv.close()
    izhodna_datoteka = open(ime_datoteke, "w", encoding="utf8")
    for vrstica in seznam_vrstic:
        izhodna_datoteka.write(vrstica)
    izhodna_datoteka.close()



conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

# 884288 nima opisa, zato not null ni več  pri opisu
knjiga = ["knjiga",
          """
        CREATE TABLE knjiga (
            id INTEGER PRIMARY KEY,
            ISBN TEXT,
            naslov TEXT NOT NULL,
            dolzina INTEGER,
            povprecna_ocena FLOAT,
            stevilo_ocen INTEGER,
            leto INTEGER, 
            opis TEXT,
            url_naslovnice TEXT

        );
    """,
          """
                INSERT INTO knjiga
                (id, ISBN, naslov, dolzina, povprecna_ocena, stevilo_ocen, leto, opis, url_naslovnice)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """]

avtor = ["avtor",
         """
        CREATE TABLE avtor (
            id INTEGER PRIMARY KEY,
            ime TEXT NOT NULL,
            povprecna_ocena FLOAT,
            datum_rojstva DATE,
            kraj_rojstva TEXT
        );
    """,
         """
                INSERT INTO avtor
                (id, ime, povprecna_ocena, datum_rojstva, kraj_rojstva)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """]

serija = ["serija", """CREATE TABLE serija (id INTEGER PRIMARY KEY, ime TEXT NOT NULL, stevilo_knjig INTEGER NOT NULL);""",
          """INSERT INTO serija (id, ime, stevilo_knjig) VALUES (%s, %s, %s) RETURNING id"""]

# Arts Photography, null ---> zato opis lahko null
zanr = ["zanr",
        """
        CREATE TABLE zanr (
            ime_zanra TEXT PRIMARY KEY,
            opis TEXT
        );
    """,
        """
                INSERT INTO zanr
                (ime_zanra, opis)
                VALUES (%s, %s)
                RETURNING ime_zanra
            """]


#TODO zaporedni deli serij nimajo vedno zaporedne številke- NOT NULL??? + ne more bit primarni ključ če null (Primary key(id_serije, zaporedna_stevila_serije))    zaporedna_stevilka_serije INTEGER NOT NULL,
del_serije = ["del_serije",
              """
        CREATE TABLE del_serije (
            id_knjige INTEGER NOT NULL REFERENCES knjiga(id),
            id_serije INTEGER NOT NULL REFERENCES serija(id),
            zaporedna_stevilka_serije INTEGER,
            PRIMARY KEY (id_serije, id_knjige)
        );
    """,
              """
                INSERT INTO del_serije
                (id_knjige, id_serije, zaporedna_stevilka_serije)
                VALUES (%s, %s, %s)
                RETURNING id_serije
            """]

avtor_knjige = ["avtor_knjige",
                """
        CREATE TABLE avtor_knjige (
            id_knjige INTEGER NOT NULL REFERENCES knjiga(id),
            id_avtorja INTEGER NOT NULL REFERENCES avtor(id),
            PRIMARY KEY (id_avtorja, id_knjige)
        );
    """, """
                INSERT INTO avtor_knjige
                (id_knjige, id_avtorja)
                VALUES (%s, %s)
                RETURNING (id_knjige, id_avtorja)
            """]

zanr_knjige = ["zanr_knjige",
               """
         CREATE TABLE zanr_knjige (
             id_knjige INTEGER NOT NULL REFERENCES knjiga(id),
             zanr TEXT NOT NULL REFERENCES zanr(ime_zanra),
             PRIMARY KEY (id_knjige, zanr)
         );
     """, """
                INSERT INTO zanr_knjige
                (id_knjige, zanr)
                VALUES (%s, %s)
                RETURNING (id_knjige, zanr)
            """]
avtorjev_zanr = ["avtorjev_zanr",
                 """
           CREATE TABLE avtorjev_zanr (
               id_avtorja INTEGER NOT NULL REFERENCES avtor(id),
               zanr TEXT NOT NULL REFERENCES zanr(ime_zanra),
               PRIMARY KEY (id_avtorja, zanr)
           );
       """, """
                INSERT INTO avtorjev_zanr
                (id_avtorja, zanr)
                VALUES (%s, %s)
                RETURNING (id_avtorja, zanr)
            """]

kljucna_beseda=["kljucna_beseda",
               """
         CREATE TABLE kljucna_beseda (
             pojem TEXT PRIMARY KEY,
             skupina TEXT NOT NULL
         );
     """, """
                INSERT INTO kljucna_beseda
                (pojem, skupina)
                VALUES (%s, %s)
                RETURNING (pojem)
            """]

knjiga_kljucne_besede= ["knjiga_kljucne_besede",
                 """
           CREATE TABLE knjiga_kljucne_besede (
               id_knjige INTEGER NOT NULL REFERENCES knjiga(id),
               kljucna_beseda TEXT NOT NULL REFERENCES kljucna_beseda(pojem),
               PRIMARY KEY (id_knjige, kljucna_beseda)
           );
       """, """
                INSERT INTO knjiga_kljucne_besede
                (id_knjige, kljucna_beseda)
                VALUES (%s, %s)
                RETURNING (id_knjige, kljucna_beseda)
            """]



#daj_pravice()
#for x in [knjiga_kljucne_besede]:
#    izprazni_tabelo(x)
# for x in [ knjiga_kljucne_besede]:
#     #ustvari_tabelo(x)
#     uvozi_podatke(x)
#uvozi_podatke(knjiga_kljucne_besede) # TODO Knjige 33570856 ni v knjigah?!?!
#ustvari_vse_tabele()

#uvozi_vse_podatke()
#izbrisi_podovojene_vrstice('podatki/zanr.csv')

#~~~~~~~~~~~~~~~~~~~~~~~~~UPORABNIKI
uporabnik=['uporabnik',
           # CREATE TYPE spol AS ENUM('Female', 'Male');
           #  CREATE TYPE dom AS ENUM('Gryffindor', 'Slytherin', 'Hufflepuff', 'Ravenclaw');
           """           
           CREATE TABLE uporabnik (
               id SERIAL PRIMARY KEY,
               vzdevek TEXT NOT NULL UNIQUE,
               geslo TEXT NOT NULL,
               email TEXT NOT NULL UNIQUE,
               dom dom NOT NULL,
               spol spol NOT NULL
           );
       """, """
                INSERT INTO uporabnik
                (id, vzdevek, geslo, email, dom, spol)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING (id_uporabnika)
            """
           ]

wishlist=['wishlist',
           """
           CREATE TABLE wishlist (
               id_uporabnika INTEGER NOT NULL REFERENCES uporabnik(id),
               id_knjige INTEGER NOT NULL REFERENCES knjiga(id),
               PRIMARY KEY(id_uporabnika, id_knjige)
           );
       """, """
                INSERT INTO wishlist
                (id_uporabnika, id_knjige)
                VALUES (%s, %s)
                RETURNING (id_uporabnika, id_knjige)
            """
           ]

prebrana_knjiga=['prebrana_knjiga',
           """
           CREATE TABLE prebrana_knjiga (
               id_uporabnika INTEGER NOT NULL REFERENCES uporabnik(id),
               id_knjige INTEGER NOT NULL REFERENCES knjiga(id),
               ocena INTEGER,
               PRIMARY KEY(id_uporabnika, id_knjige)
           );
       """, """
                INSERT INTO prebrana_knjiga
                (id_uporabnika, id_knjige, ocena)
                VALUES (%s, %s, %s)
                RETURNING (id_uporabnika, id_knjige)
            """
           ]
#
seznamVseh = [knjiga, avtor, zanr, serija, del_serije, avtor_knjige, zanr_knjige, avtorjev_zanr, kljucna_beseda, knjiga_kljucne_besede, uporabnik, wishlist, prebrana_knjiga]


def ustvari_vse_tabele():
    for seznam in seznamVseh:
        ustvari_tabelo(seznam)
    daj_pravice()

def uvozi_vse_podatke():
    for seznam in seznamVseh[:-3]:
        uvozi_podatke(seznam)


def izbrisi_vse_tabele():
    for seznam in seznamVseh:
        pobrisi_tabelo(seznam)

#izbrisi_vse_tabele()
#ustvari_vse_tabele()
#uvozi_vse_podatke()

#ustvari_tabelo(uporabnik)
#ustvari_tabelo(ocena_knjige)
#ustvari_tabelo(prebrana_knjiga)
#ustvari_tabelo(wishlist)
#ustvari_tabelo(zanr_knjige)

#pobrisi_tabelo(uporabnik)
#pobrisi_tabelo(zelje)
#pobrisi_tabelo(ocena_knjige)
#pobrisi_tabelo(prebrane)
#daj_pravice()


#NAKNADNO DODANI SQL-stavki
# ALTER TABLE knjiga ADD vsota_ocen float;
# UPDATE knjiga SET vsota_ocen = stevilo_ocen * povprecna_ocena;
# ALTER TABLE knjiga DROP COLUMN povprecna_ocena;
#UPDATE knjiga SET stevilo_ocen = COALESCE(stevilo_ocen,0);
#UPDATE knjiga SET vsota_ocen = COALESCE(vsota_ocen,0);

