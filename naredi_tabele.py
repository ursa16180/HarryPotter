# uvozimo ustrezne podatke za povezavo
import auth

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


conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

knjiga = ["knjiga",
          """
        CREATE TABLE knjiga (
            ISBN TEXT PRIMARY KEY,
            naslov TEXT NOT NULL,
            ocena FLOAT,
            stevilo_ocen INTEGER,
            leto_izdaje INTEGER, 
            dolzina INTEGER NOT NULL,
            povzetek TEXT NOT NULL

        );
    """,
          """
                INSERT INTO knjiga
                (ISBN, naslov, ocena, stevilo_ocen, leto_izdaje, dolzina, povzetek)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING ISBN
            """]

avtor = ["avtor",
         """
        CREATE TABLE avtor (
            id TEXT PRIMARY KEY,
            ime_priimek TEXT NOT NULL,
            povprecna_ocena FLOAT,
            datum_rojstva DATE,
            kraj_rojstva TEXT
        );
    """,
         """
                INSERT INTO avtor
                (id, ime_priimek, povprecna_ocena, datum_rojstva, kraj_rojstva)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """]

zanr = ["zanr",
        """
        CREATE TABLE zanr (
            ime TEXT PRIMARY KEY,
            opis TEXT NOT NULL
        );
    """,
        """
                INSERT INTO zanr
                (ime, opis)
                VALUES (%s, %s)
                RETURNING (ime,opis)
            """]

serija = ["serija", """CREATE TABLE serija (id TEXT PRIMARY KEY, ime TEXT NOT NULL);""",
          """INSERT INTO serija (id, ime) VALUES (%s, %s) RETURNING id"""]

del_serije = ["del_serije",
              """
        CREATE TABLE del_serije (
            id_serije TEXT NOT NULL REFERENCES serija(id),
            ISBN_knjige TEXT NOT NULL REFERENCES knjiga(ISBN),
            zaporedna_stevilka INTEGER NOT NULL,
            PRIMARY KEY (id_serije, zaporedna_stevilka)
        );
    """,
              """
                INSERT INTO del_serije
                (id_serije, ISBN_knjige, zaporedna_stevilka)
                VALUES (%s, %s, %s)
                RETURNING id_serije
            """]

avtor_knjige = ["avtor_knjige",
                """
        CREATE TABLE avtor_knjige (
            id_avtorja TEXT NOT NULL REFERENCES avtor(id),
            ISBN_knjige TEXT NOT NULL REFERENCES knjiga(ISBN),
            PRIMARY KEY (id_avtorja, ISBN_knjige)
        );
    """, """
                INSERT INTO avtor_knjige
                (id_avtorja, ISBN_knjige)
                VALUES (%s, %s)
                RETURNING id_avtorja
            """]

zanr_knjige = ["zanr_knjige",  ###TODO Kako dodati vse zanre se v tabelo zanr
               """
         CREATE TABLE zanr_knjige (
             ISBN_knjige TEXT NOT NULL REFERENCES knjiga(ISBN),
             ime_zanra TEXT NOT NULL REFERENCES zanr(ime),
             PRIMARY KEY (ISBN_knjige, ime_zanra)
         );
     """, """
                INSERT INTO zanr_knjige
                (ISBN_knjige, ime_zanra)
                VALUES (%s, %s)
                RETURNING (ISBN_knjige, ime_zanra)
            """]
avtorjev_zanr = ["avtorjev_zanr",  ###TODO Kako dodati vse zanre se v tabelo zanr
                 """
           CREATE TABLE avtorjev_zanr (
               id_avtorja TEXT NOT NULL REFERENCES avtor(id),
               ime_zanra TEXT NOT NULL REFERENCES zanr(ime),
               PRIMARY KEY (id_avtorja, ime_zanra)
           );
       """, """
                INSERT INTO avtorjev_zanr
                (id_avtorja, ime_zanra)
                VALUES (%s, %s)
                RETURNING (id_avtorja, ime_zanra)
            """]

seznamVseh = [knjiga, avtor, zanr, serija, del_serije, avtor_knjige, zanr_knjige, avtorjev_zanr]


def ustvari_vse_tabele():
    for seznam in seznamVseh:
        ustvari_tabelo(seznam)


def izbrisi_vse_tabele():
    for seznam in seznamVseh:
        pobrisi_tabelo(seznam)

# ustvari_tabelo(avtorjev_zanr)
# uvozi_podatke(avtorjev_zanr)
