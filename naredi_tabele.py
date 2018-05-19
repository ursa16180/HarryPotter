# uvozimo ustrezne podatke za povezavo
import auth
import fileinput

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras

psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)  # se znebimo problemov s šumniki

import csv


def ustvari_tabelo(seznam):
    cur.execute(seznam[1])
    print("Narejena tabela %s" % seznam[0])
    conn.commit()


def pobrisi_tabelo(seznam):
    cur.execute("""
        DROP TABLE %s;
    """ % seznam[0])
    print("Izbrisna tabela %s" % seznam[0])
    conn.commit()


def uvozi_podatke(seznam):
    if seznam[0] == "zanr":
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
        if vrstica not in vse_razlice_vrstice:
            seznam_vrstic.append(vrstica)
            vse_razlice_vrstice.add(vrstica)
    izhodna_datoteka = open(datoteka, "w", encoding="utf8")
    for vrstica in seznam_vrstic:
        izhodna_datoteka.write(vrstica)
    izhodna_datoteka.close()




conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

knjiga = ["knjiga",
          """
        CREATE TABLE knjiga (
            id TEXT PRIMARY KEY,
            ISBN TEXT,
            naslov TEXT NOT NULL,
            dolzina INTEGER NOT NULL,
            povprecna_ocena FLOAT,
            stevilo_ocen INTEGER,
            leto INTEGER, 
            opis TEXT NOT NULL

        );
    """,
          """
                INSERT INTO knjiga
                (id, ISBN, naslov, dolzina, povprecna_ocena, stevilo_ocen, leto, opis)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """]

avtor = ["avtor",
         """
        CREATE TABLE avtor (
            id TEXT PRIMARY KEY,
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

serija = ["serija", """CREATE TABLE serija (id TEXT PRIMARY KEY, ime TEXT NOT NULL, stevilo_knjig INTEGER NOT NULL);""",
          """INSERT INTO serija (id, ime, stevilo_knjig) VALUES (%s, %s, %s) RETURNING id"""]

zanr = ["zanr",
        """
        CREATE TABLE zanr (
            ime_zanra TEXT PRIMARY KEY,
            opis TEXT NOT NULL
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
            id_knjige TEXT NOT NULL REFERENCES knjiga(id),
            id_serije TEXT NOT NULL REFERENCES serija(id),
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
            id_knjige TEXT NOT NULL REFERENCES knjiga(id),
            id_avtorja TEXT NOT NULL REFERENCES avtor(id),
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
             id_knjige TEXT NOT NULL REFERENCES knjiga(id),
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
               id TEXT NOT NULL REFERENCES avtor(id),
               zanr TEXT NOT NULL REFERENCES zanr(ime_zanra),
               PRIMARY KEY (id, zanr)
           );
       """, """
                INSERT INTO avtorjev_zanr
                (id, zanr)
                VALUES (%s, %s)
                RETURNING (id, zanr)
            """]

seznamVseh = [knjiga, avtor, zanr, serija, del_serije, avtor_knjige, zanr_knjige, avtorjev_zanr]


def ustvari_vse_tabele():
    for seznam in seznamVseh:
        ustvari_tabelo(seznam)

def uvozi_vse_podatke():
    for seznam in seznamVseh:
        uvozi_podatke(seznam)


def izbrisi_vse_tabele():
    for seznam in seznamVseh:
        pobrisi_tabelo(seznam)

# ustvari_tabelo(avtorjev_zanr)
# uvozi_podatke(avtorjev_zanr)

#ustvari_vse_tabele()
#uvozi_vse_podatke()
