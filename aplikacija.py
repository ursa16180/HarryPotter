#!/usr/bin/python
# -*- encoding: utf-8 -*-

# uvozimo bottle.py
from bottle import *

# uvozimo ustrezne podatke za povezavo
import auth_public as auth

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras

psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)  # se znebimo problemov s šumniki

# odkomentiraj, če želiš sporočila o napakah
debug(True)


@get('/static/<filename:path>')
def static(filename):
    return static_file(filename, root='static')


@get('/')
def index():
    cur.execute("SELECT id, naslov, dolzina FROM knjiga ORDER BY naslov LIMIT 20")
    return template('tabela_knjig.html', knjige=cur, vseKljucne=vseKljucne, zanri=vsiZanri)


@post('/isci')
def iskanje_get():
    kljucne = request.POST.getall('kljucne_besede')
    print(kljucne)
    if request.forms.get('dolzinaInput') is None:
        dolzina = 0
    else:
        dolzina = int(request.forms.get('dolzinaInput'))
    # print(request.POST.getall('kljucne_besede'))

    zanri = request.POST.getall('zanri')
    jeDelZbirke = request.forms.get('jeDelZbirke')

    # ~~~~~~~~~~~~~~Če so izbrane ključne besede, jih doda
    if kljucne == []:
        niz = "SELECT DISTINCT knjiga.id, naslov, avtor.id, avtor.ime, zanr FROM knjiga"
    else:  # TODO: išči po ključnih besedah - ni lepo ampak mislim da dela
        vmesni_niz = " AND ".join(
            'EXISTS (SELECT * FROM knjiga_kljucne_besede WHERE kljucna_beseda = \'%s\' AND knjiga_kljucne_besede.id_knjige=knjiga1.id_knjige)' % (
                kljucna_beseda) for kljucna_beseda in kljucne)
        niz = "SELECT DISTINCT knjiga.id, naslov, avtor.id, avtor.ime, zanr FROM knjiga JOIN (SELECT DISTINCT * FROM knjiga_kljucne_besede knjiga1 WHERE " + vmesni_niz + ") pomozna_tabela ON knjiga.id=pomozna_tabela.id_knjige"

    # ~~~~~~~~~~~~~~če so izbrani zanri, jih doda
    if zanri != []:
        print(zanri)
        vmesni_niz = " AND ".join(
            'EXISTS (SELECT * FROM zanr_knjige WHERE zanr = \'%s\' AND id_knjige=knjiga2.id_knjige)' % (zanr) for zanr
            in zanri)
        niz += " JOIN (SELECT DISTINCT * FROM zanr_knjige knjiga2 WHERE " + vmesni_niz + ") pomozna_tabela2 ON knjiga.id=pomozna_tabela2.id_knjige"
    else:
        niz += " JOIN zanr_knjige ON knjiga.id=zanr_knjige.id_knjige"

    # ~~~~~~~~~~~~~~Če želi da je del serije, se združi s tabelo serij
    # TODO Ali če se združi že izloči tiste ki niso v serijah?
    # TODO tukaj izbere če želi da je v zbirki ali če mu je vseeno... kaj pa če prou noče da je v zbirki?
    if jeDelZbirke is not None:
        niz += " JOIN del_serije ON knjiga.id=del_serije.id_knjige "
        # cur.execute("SELECT id, naslov, dolzina FROM knjiga WHERE dolzina>=%s", [dolzina])

    # ~~~~~~~~~~~~~~~Tukaj se doda avtor
    niz += " JOIN avtor_knjige ON knjiga.id = avtor_knjige.id_knjige JOIN avtor ON avtor_knjige.id_avtorja = avtor.id"
    # ~~~~~~~~~~~~~~Tukaj se doda pogoj o dolžini knjige
    niz += " WHERE dolzina>=%s ORDER BY knjiga.id, avtor.id" % dolzina
    print(niz)
    cur.execute(niz)
    vse_vrstice = cur.fetchall()
    slovar_slovarjev_knjig = {}

    for vrstica in vse_vrstice:
        id = vrstica[0]
        trenutna_knjiga = slovar_slovarjev_knjig.get(id, {'id': id, 'naslov': None, 'avtorji': set(), 'zanri': set()})
        trenutna_knjiga['naslov'] = vrstica[1]
        trenutna_knjiga['avtorji'].add((vrstica[2], vrstica[3]))
        trenutna_knjiga['zanri'].add(vrstica[4])
        slovar_slovarjev_knjig[id] = trenutna_knjiga
    return template('izpis_knjiznih_zadetkov.html', vseKljucne=vseKljucne, zanri=vsiZanri,
                    knjige=slovar_slovarjev_knjig.values())


@post('/avtor/:x')
def avtor(x):
    #print(x)
    cur.execute("SELECT id, ime, povprecna_ocena, datum_rojstva, kraj_rojstva FROM avtor WHERE id='%s'" % x)
    avtor = cur.fetchone()
    cur.execute("SELECT zanr FROM avtorjev_zanr WHERE id = '%s'" % x)
    zanriAvtorja=cur.fetchall()
    cur.execute("""SELECT knjiga.id, knjiga.naslov FROM avtor_knjige LEFT JOIN knjiga ON knjiga.id = avtor_knjige.id_knjige WHERE id_avtorja ='%s'""" % x)
    knjige = cur.fetchall()
    #print(avtor, zanriAvtorja, knjige)
    return template('avtor.html', vseKljucne=vseKljucne, zanri=vsiZanri,
                    avtor=avtor, knjige=knjige, zanriAvtorja=zanriAvtorja)


@post('/zanr/:x')
def zanr(x):
    #print(x)
    cur.execute("SELECT ime_zanra, opis FROM zanr WHERE ime_zanra='%s'" % x)
    zanr = cur.fetchone()
    cur.execute("SELECT id, naslov FROM knjiga JOIN zanr_knjige on knjiga.id = zanr_knjige.id_knjige WHERE zanr='%s'"%x)
    knjige = cur.fetchall()
    return template('zanr.html', vseKljucne=vseKljucne, zanri=vsiZanri,
                    zanr=zanr, knjige=knjige)

@post('/zbirka/:x')
def zbirka(x):
    print(x)
    cur.execute("""SELECT serija.ime, del_serije.zaporedna_stevilka_serije, knjiga.id, knjiga.naslov FROM serija
JOIN del_serije ON del_serije.id_serije=serija.id
JOIN knjiga ON del_serije.id_knjige = knjiga.id
WHERE serija.id = '%s'
ORDER BY zaporedna_stevilka_serije""" % x)
    #print(cur.fetchall())
    return template('zbirka.html', vseKljucne=vseKljucne, zanri=vsiZanri,
                    knjige=cur.fetchall())


@post('/knjiga/:x')
def knjiga(x):
    #print(x)
    cur.execute("""SELECT knjiga.id, isbn, naslov, dolzina, knjiga.povprecna_ocena, stevilo_ocen, leto, knjiga.opis, 
    avtor.id, avtor.ime, serija.id, serija.ime, del_serije.zaporedna_stevilka_serije, kljucna_beseda, ime_zanra FROM knjiga
LEFT JOIN avtor_knjige ON knjiga.id=avtor_knjige.id_knjige
LEFT JOIN avtor ON avtor_knjige.id_avtorja = avtor.id
LEFT JOIN del_serije ON knjiga.id=del_serije.id_knjige
LEFT JOIN serija ON serija.id=del_serije.id_serije
LEFT JOIN knjiga_kljucne_besede ON knjiga.id = knjiga_kljucne_besede.id_knjige
LEFT JOIN zanr_knjige ON zanr_knjige.id_knjige = knjiga.id
LEFT JOIN zanr ON zanr_knjige.zanr = zanr.ime_zanra
WHERE knjiga.id ='%s'""" % x)
    vseVrstice = cur.fetchall()
    knjiga = {'id':vseVrstice[0][0],
              'isbn':vseVrstice[0][1],
              'naslov':vseVrstice[0][2],
              'dolzina':vseVrstice[0][3],
              'povprecna_ocena':vseVrstice[0][4],
              'stevilo_ocen':vseVrstice[0][5],
              'leto':vseVrstice[0][6],
              'opis':vseVrstice[0][7],
              'avtor':set(),
              'serija':set(),
              'kljucna_beseda':set(),
              'zanri':set()}
    for vrstica in vseVrstice:
        knjiga['avtor'].add((vrstica[8],vrstica[9]))
        knjiga['serija'].add((vrstica[10],vrstica[11], vrstica[12]))
        knjiga['kljucna_beseda'].add(vrstica[13])
        knjiga['zanri'].add(vrstica[14])
    #print(knjiga)
    return template('knjiga.html', vseKljucne=vseKljucne, zanri=vsiZanri,
                    knjiga=knjiga)

@post('/kazaloAvtorja')
def kazalo_avtorja():
    cur.execute("""SELECT id, ime FROM avtor""")
    neurejeni_avtorji = cur.fetchall()
    urejeni_avtorji = {}
    for avtor in neurejeni_avtorji:
        priimek = avtor[1].split(' ')[-1]
        crka = priimek[0]
        urejeni_avtorji[crka] = urejeni_avtorji.get(crka, []) + [(priimek, avtor)]
    for avtorji_na_crko in urejeni_avtorji.values():
        avtorji_na_crko.sort()
    avtorji = list(urejeni_avtorji.items())
    avtorji.sort()
    print(avtorji)
    return template('kazalo_avtorjev.html', vseKljucne=vseKljucne, zanri=vsiZanri, avtorji=avtorji)


@post('/kazaloZanra')
def kazalo_zanra():
    cur.execute("""SELECT ime_zanra FROM zanr""")
    vsi_zanri_iz_baze = cur.fetchall()
    return template('kazalo_zanrov.html', vseKljucne=vseKljucne, zanri=vsiZanri, zanri_kazalo=vsi_zanri_iz_baze)
# @get('/transakcije/:x/')
# def transakcije(x):
#     cur.execute("SELECT * FROM transakcija WHERE znesek > %s ORDER BY znesek, id", [int(x)])
#     return template('transakcije.html', x=x, transakcije=cur)
#
#
# @get('/dodaj_transakcijo')
# def dodaj_transakcijo():
#     return template('dodaj_transakcijo.html', znesek='', racun='', opis='', napaka=None)
#
#
# @post('/dodaj_transakcijo')
# def dodaj_transakcijo_post():
#     znesek = request.forms.znesek
#     racun = request.forms.racun
#     opis = request.forms.opis
#     try:
#         cur.execute("INSERT INTO transakcija (znesek, racun, opis) VALUES (%s, %s, %s)",
#                     (znesek, racun, opis))
#     except Exception as ex:
#         return template('dodaj_transakcijo.html', znesek=znesek, racun=racun, opis=opis,
#                         napaka='Zgodila se je napaka: %s' % ex)
#     redirect("/")

######################################################################
# Glavni program

# priklopimo se na bazo
conn = psycopg2.connect(database=auth.db, host=auth.host, user=auth.user, password=auth.password)
# conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT) # onemogočimo transakcije
cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

# ~~~~~~~~~~~~~~~~~~~~~Pridobi 50 najpogostejših žanrov
cur.execute("""SELECT sum(stevilo) AS stevilo_skupaj, ime_zanra FROM (
 SELECT count(*) AS stevilo, ime_zanra FROM zanr AS zanr1
 JOIN zanr_knjige ON zanr1.ime_zanra=zanr_knjige.zanr
 GROUP BY ime_zanra
 UNION ALL
 SELECT count(*) AS stevilo, ime_zanra FROM zanr AS zanr2
 JOIN avtorjev_zanr ON zanr2.ime_zanra=avtorjev_zanr.zanr
 GROUP BY ime_zanra
) AS tabela
GROUP BY ime_zanra
ORDER BY stevilo_skupaj DESC
LIMIT 50""")

zanri_iz_baze=cur.fetchall()
vsiZanri=[]
for vrstica in zanri_iz_baze:
    vsiZanri.append(vrstica[1])
vsiZanri.sort()

#~~~~~~~~~~~~~~~~~~~~~Pridobi vse skupine ključnih besed
#vseKljucne = {'Magija': ['Magic', 'Flying'], 'Bitja': ['Centaur', 'Troll']}
cur.execute("""SELECT skupina, pojem FROM kljucna_beseda""")
kljucne_iz_baze = cur.fetchall()
vseKljucne = {}
for vrstica in kljucne_iz_baze:
    skupina = vrstica[0]
    #pojmi = vseKljucne.get(skupina, list())
    #print(pojmi, vrstica)
    vseKljucne[skupina] = vseKljucne.get(skupina, list()) + [vrstica[1]]

# poženemo strežnik na portu 8080, glej http://localhost:8080/
run(host='localhost', port=8080, reloader=True)
