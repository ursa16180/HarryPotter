# uvozimo ustrezne podatke za povezavo
import auth

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras

psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)  # se znebimo problemov s šumniki

import csv


def ustvari_tabelo():
    cur.execute("""
        CREATE TABLE del_serije (
            id_serije TEXT NOT NULL REFERENCES serija(id),
            ISBN_knjige TEXT NOT NULL REFERENCES knjiga(ISBN),
            zaporedna_stevilka INTEGER NOT NULL,
            PRIMARY KEY (id_serije, zaporedna_stevilka)
        );
    """)
    ### zanr TEXT NOT NULL FOREIGN KEY, zbirka TEXT FOREIGN KEY, kljucne_besede TEXT FOREIGN KEY, avtor TEXT NOT NULL FOREIGN KEY,
    print("Narejena tabela DEL_SERIJE")
    conn.commit()


def pobrisi_tabelo():
    cur.execute("""
        DROP TABLE del_serije;
    """)
    print("Izbrisna tabela DEL_SERIJE")
    conn.commit()


def uvozi_podatke():
    with open("csv/del_serije_poskus.csv") as f:
        rd = csv.reader(f)
        next(rd)  # izpusti naslovno vrstico ###TODO?
        for r in rd:
            r = [None if x in ('', '-') else x for x in r]
            cur.execute("""
                INSERT INTO del_serije
                (id_serije, ISBN_knjige, zaporedna_stevilka)
                VALUES (%s, %s, %s)
            """, r)
            rid, = cur.fetchone()
            print("Uvožen knjiga z ISBNjem %s v serijo z IDjem %s" % (r[1], r[0]))
    conn.commit()


conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
#ustvari_tabelo()
#uvozi_podatke()
#pobrisi_tabelo()
