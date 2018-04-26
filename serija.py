# uvozimo ustrezne podatke za povezavo
import auth

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras

psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)  # se znebimo problemov s šumniki

import csv


def ustvari_tabelo():
    cur.execute("""
        CREATE TABLE serija (
            id TEXT PRIMARY KEY,
            ime TEXT NOT NULL
        );
    """)
    ### zanr TEXT NOT NULL FOREIGN KEY, zbirka TEXT FOREIGN KEY, kljucne_besede TEXT FOREIGN KEY, avtor TEXT NOT NULL FOREIGN KEY,
    print("Narejena tabela SERIJA")
    conn.commit()


def pobrisi_tabelo():
    cur.execute("""
        DROP TABLE serija;
    """)
    print("Izbrisna tabela SERIJA")
    conn.commit()


def uvozi_podatke():
    with open("csv/serija_poskus.csv") as f:
        rd = csv.reader(f)
        next(rd)  # izpusti naslovno vrstico ###TODO?
        for r in rd:
            r = [None if x in ('', '-') else x for x in r]
            cur.execute("""
                INSERT INTO serija
                (id, ime)
                VALUES (%s, %s)
                RETURNING id
            """, r)
            rid, = cur.fetchone()
            print("Uvožena serija %s z id-jem %s" % (r[1], rid))
    conn.commit()


conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
#ustvari_tabelo()
#uvozi_podatke()
#pobrisi_tabelo()
