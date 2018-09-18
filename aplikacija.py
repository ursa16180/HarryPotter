#!/usr/bin/python
# -*- encoding: utf-8 -*-

# uvozimo bottle.py
from bottle import *

# uvozimo ustrezne podatke za povezavo
import auth_public as auth

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
import copy

import hashlib

psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)  # se znebimo problemov s šumniki

# odkomentiraj, če želiš sporočila o napakah
debug(True)

skrivnost = "To je ultimativni urok za skrivanje skrivnosti. Ne povedati Hagridu. Bljuz43988asjjjdskazzzzz"


def zakodiraj_geslo(geslo):
    hashko = hashlib.md5()
    hashko.update(geslo.encode('utf-8'))
    return hashko.hexdigest()


@get('/static/<filename:path>')
def static(filename):
    return static_file(filename, root='static')


@get('/')
def index():
    return template('zacetna_stran.html', vseKljucne=vse_kljucne, zanri=vsi_zanri, uporabnik=uporabnik())


@post('/isci')
def iskanje_get():
    kljucne = request.POST.getall('kljucne_besede')
    parametri = copy.copy(kljucne)
    if request.forms.get('dolzinaInput') is None:
        dolzina = 0
    else:
        dolzina = int(request.forms.get('dolzinaInput'))
        parametri.append(str(dolzina) + '+ pages')

    zanri = request.POST.getall('zanri')
    parametri += zanri
    je_del_zbirke = request.forms.get('zbirka')
    parametri_sql = ()
    # ~~~~~~~~~~~~~~ Če so izbrane ključne besede, jih doda
    if kljucne == []:
        niz = "SELECT DISTINCT knjiga.id, naslov, avtor.id, avtor.ime, zanr, url_naslovnice FROM knjiga"
    else:
        vmesni_niz = ''
        for kljucna_beseda in kljucne:
            vmesni_niz += """ AND EXISTS (SELECT * FROM knjiga_kljucne_besede WHERE kljucna_beseda = %s 
                              AND knjiga_kljucne_besede.id_knjige=knjiga1.id_knjige)"""
            parametri_sql += (kljucna_beseda,)
        niz = "SELECT DISTINCT knjiga.id, naslov, avtor.id, avtor.ime, zanr, url_naslovnice FROM knjiga " \
              "JOIN (SELECT DISTINCT * FROM knjiga_kljucne_besede knjiga1 WHERE " + vmesni_niz[5:] \
              + ") pomozna_tabela ON knjiga.id=pomozna_tabela.id_knjige"

    # ~~~~~~~~~~~~~~ če so izbrani zanri, jih doda
    if zanri != []:
        vmesni_niz = ''
        for zanr in zanri:
            vmesni_niz += """ AND EXISTS (SELECT * FROM zanr_knjige WHERE zanr = %s AND id_knjige=knjiga2.id_knjige)"""
            parametri_sql += (zanr,)
        niz += " JOIN (SELECT DISTINCT * FROM zanr_knjige knjiga2 WHERE " + vmesni_niz[5:] + \
               ") pomozna_tabela2 ON knjiga.id=pomozna_tabela2.id_knjige"
    else:
        niz += " JOIN zanr_knjige ON knjiga.id=zanr_knjige.id_knjige"
    # ~~~~~~~~~~~~~~~Tukaj se doda avtor
    niz += " JOIN avtor_knjige ON knjiga.id = avtor_knjige.id_knjige JOIN avtor ON avtor_knjige.id_avtorja = avtor.id"
    # ~~~~~~~~~~~~~~Če želi da je del serije, se združi s tabelo serij
    print(je_del_zbirke)
    if je_del_zbirke == 'Yes':
        print('je v zbirki')
        niz += " JOIN del_serije ON knjiga.id=del_serije.id_knjige WHERE"
        parametri += ['In series']
    elif je_del_zbirke == 'No':
        print('ni v zbirki')
        niz += " WHERE knjiga.id NOT IN (SELECT id_knjige FROM del_serije) AND"
        parametri += ['Not in series']
    else:
        niz += " WHERE"
    # ~~~~~~~~~~~~~~Tukaj se doda pogoj o dolžini knjige
    niz += " dolzina>=%s ORDER BY knjiga.id, avtor.id"
    print(niz)
    parametri_sql += (dolzina,)
    cur.execute(niz, parametri_sql)
    vse_vrstice = cur.fetchall()
    if vse_vrstice == []:
        return template('ni_zadetkov.html', vseKljucne=vse_kljucne, zanri=vsi_zanri,
                        uporabnik=uporabnik(), parametri=parametri)
    else:
        slovar_slovarjev_knjig = {}
        for vrstica in vse_vrstice:
            id = vrstica[0]
            trenutna_knjiga = slovar_slovarjev_knjig.get(id, {'id': id, 'naslov': None, 'avtorji': set(),
                                                              'zanri': set(), 'url_naslovnice': None})
            trenutna_knjiga['naslov'] = vrstica[1]
            trenutna_knjiga['avtorji'].add((vrstica[2], vrstica[3]))
            trenutna_knjiga['zanri'].add(vrstica[4])
            trenutna_knjiga['url_naslovnice'] = vrstica[5]
            slovar_slovarjev_knjig[id] = trenutna_knjiga
        return template('izpis_knjiznih_zadetkov.html', vseKljucne=vse_kljucne, zanri=vsi_zanri, uporabnik=uporabnik(),
                        knjige=list(slovar_slovarjev_knjig.values()), stran=1,
                        poizvedba=(niz, parametri_sql), parametri=parametri)


@post('/avtor/:x')
def avtor(x):
    cur.execute("SELECT id, ime, povprecna_ocena, datum_rojstva, kraj_rojstva FROM avtor WHERE id=%s", (x,))
    avtor = cur.fetchone()
    cur.execute("SELECT zanr FROM avtorjev_zanr WHERE id = %s", (x,))
    zanri_avtorja = cur.fetchall()
    zanri_avtorja = set([x[0] for x in zanri_avtorja])
    if zanri_avtorja == {None}:
        zanri_avtorja = set()
    cur.execute("""SELECT knjiga.id, knjiga.naslov, zanr_knjige.zanr, serija.id, serija.ime, serija.stevilo_knjig 
    FROM avtor_knjige 
    LEFT JOIN knjiga ON knjiga.id = avtor_knjige.id_knjige 
    LEFT JOIN zanr_knjige ON zanr_knjige.id_knjige = knjiga.id
    LEFT JOIN del_serije ON knjiga.id = del_serije.id_knjige
    LEFT JOIN serija ON del_serije.id_serije = serija.id
    WHERE id_avtorja =%s""", (x,))
    vrstice_knjig = cur.fetchall()
    knjige = set()
    serije_avtorja = {}
    for vrstica in vrstice_knjig:
        id = vrstica[0]
        knjige.add((id, vrstica[1]))
        if vrstica[2] is not None:
            zanri_avtorja.add(vrstica[2])
        if vrstica[3] is not None:
            serije_avtorja[vrstica[3]] = (vrstica[4], vrstica[5])
    return template('avtor.html', vseKljucne=vse_kljucne, zanri=vsi_zanri, uporabnik=uporabnik(),
                    avtor=avtor, knjige=list(knjige), zanriAvtorja=list(zanri_avtorja), serijeAvtorja=serije_avtorja)


@post('/zanr/:x')
def zanr(x):
    cur.execute("SELECT ime_zanra, opis FROM zanr WHERE ime_zanra=%s;", (x,))
    zanr = cur.fetchone()
    cur.execute("SELECT id, naslov FROM knjiga JOIN zanr_knjige ON knjiga.id = zanr_knjige.id_knjige WHERE zanr=%s "
                "ORDER BY knjiga.povprecna_ocena DESC LIMIT 50;", (x,))
    knjige = cur.fetchall()
    cur.execute("SELECT avtor.id, avtor.ime FROM avtor JOIN avtorjev_zanr ON avtor.id = avtorjev_zanr.id "
                "WHERE avtorjev_zanr.zanr=%s;", (x,))
    avtorji = cur.fetchall()
    return template('zanr.html', vseKljucne=vse_kljucne, zanri=vsi_zanri, uporabnik=uporabnik(),
                    zanr=zanr, knjige=knjige, avtorji=avtorji)

@post('/zbirka/:x')
def zbirka(x):
    cur.execute("""SELECT serija.ime, del_serije.zaporedna_stevilka_serije, knjiga.id, knjiga.naslov, avtor.id, avtor.ime FROM serija
JOIN del_serije ON del_serije.id_serije=serija.id
JOIN knjiga ON del_serije.id_knjige = knjiga.id
JOIN avtor_knjige ON knjiga.id = avtor_knjige.id_knjige
JOIN avtor ON avtor_knjige.id_avtorja =  avtor.id
WHERE serija.id = %s
ORDER BY zaporedna_stevilka_serije;""", (x, ))
    # knjiga ima lahko več avtorjev, več knjig ima iste avtorje
    knjige_ponovitve = cur.fetchall()
    knjige = {}
    avtorji = {}
    serija = knjige_ponovitve[0][0]
    for knjiga in knjige_ponovitve:
        knjiga_id = knjiga[2]
        avtor_id = knjiga[4]
        knjige[knjiga_id] = [knjiga_id, knjiga[3], knjiga[1]]
        avtorji[avtor_id] = [avtor_id, knjiga[5]]
    return template('zbirka.html', vseKljucne=vse_kljucne, zanri=vsi_zanri, uporabnik=uporabnik(),
                    knjige=list(knjige.values()), avtorji=list(avtorji.values()), serija=serija)


@post('/knjiga/:x')
def knjiga(x):
    cur.execute(  # SELECT knjiga.id, isbn, naslov, dolzina, knjiga.vsota_ocen, stevilo_ocen, leto, knjiga.opis,
        """SELECT knjiga.id, isbn, naslov, dolzina, knjiga.vsota_ocen, stevilo_ocen, leto, knjiga.opis, 
    avtor.id, avtor.ime, serija.id, serija.ime, del_serije.zaporedna_stevilka_serije, kljucna_beseda, ime_zanra, 
    knjiga.url_naslovnice FROM knjiga
LEFT JOIN avtor_knjige ON knjiga.id=avtor_knjige.id_knjige
LEFT JOIN avtor ON avtor_knjige.id_avtorja = avtor.id
LEFT JOIN del_serije ON knjiga.id=del_serije.id_knjige
LEFT JOIN serija ON serija.id=del_serije.id_serije
LEFT JOIN knjiga_kljucne_besede ON knjiga.id = knjiga_kljucne_besede.id_knjige
LEFT JOIN zanr_knjige ON zanr_knjige.id_knjige = knjiga.id
LEFT JOIN zanr ON zanr_knjige.zanr = zanr.ime_zanra
WHERE knjiga.id =%s;""", (x,))
    vse_vrstice = cur.fetchall()
    knjiga = {'id': vse_vrstice[0][0],
              'isbn': vse_vrstice[0][1],
              'naslov': vse_vrstice[0][2],
              'dolzina': vse_vrstice[0][3],
              'vsota_ocen': vse_vrstice[0][4],
              'stevilo_ocen': vse_vrstice[0][5],
              'leto': vse_vrstice[0][6],
              'opis': vse_vrstice[0][7],
              'avtor': set(),
              'serija': set(),
              'kljucna_beseda': set(),
              'zanri': set(),
              'url_naslovnice': vse_vrstice[0][15]}
    if knjiga['vsota_ocen'] == 0:
        knjiga['povprecna_ocena'] = 0
    else:
        knjiga['povprecna_ocena'] = round(knjiga['vsota_ocen'] / knjiga['stevilo_ocen'], 2)
    for vrstica in vse_vrstice:
        knjiga['avtor'].add((vrstica[8], vrstica[9]))
        knjiga['serija'].add((vrstica[10], vrstica[11], vrstica[12]))
        knjiga['kljucna_beseda'].add(vrstica[13])
        knjiga['zanri'].add(vrstica[14])

    trenutni_uporabnik = uporabnik()

    # ~~~~~~~~~~~~~~~~~~~ GUMBI PREBRANO / WISHLIST ~~~~~~~~~~~~~~~~~~~~~~

    if trenutni_uporabnik[1] is None:
        prebrano = False
        zelja = False
    else:
        cur.execute("SELECT id_knjige FROM prebrane WHERE id_uporabnika=%s AND id_knjige=%s;",
                    (trenutni_uporabnik[0], knjiga['id']))
        prebrano = len(cur.fetchall()) > 0
        cur.execute("SELECT id_knjige FROM zelje WHERE id_uporabnika=%s AND id_knjige=%s;",
                    (trenutni_uporabnik[0], knjiga['id']))
        zelja = len(cur.fetchall()) > 0

        if not prebrano:
            request.forms.get('')

    # ~~~~~~~~~~~~~~~~~~ OCENE ~~~~~~~~~~~~~~~~~~~~~~~~~


    if prebrano:
        cur.execute("SELECT ocena FROM prebrane WHERE id_uporabnika=%s AND id_knjige=%s;",
                    (trenutni_uporabnik[0], knjiga['id']))
        stara_ocena = cur.fetchone()
        stara_ocena = stara_ocena[0]
        nova_ocena = request.forms.get('ocena')
        if stara_ocena is not None:
            # knjigo je uporabnik že ocenil, preverimo, ali je oceno spremenil:
            if nova_ocena is None:
                nova_ocena = stara_ocena
            elif stara_ocena != int(nova_ocena):
                #print(knjiga['vsota_ocen'], nova_ocena, stara_ocena)
                cur.execute("UPDATE prebrane SET ocena = %s WHERE id_knjige = %s AND id_uporabnika = %s;",
                            (nova_ocena, knjiga['id'], trenutni_uporabnik[0]))
                nova_vsota_ocen = knjiga['vsota_ocen'] + int(nova_ocena) - stara_ocena
                cur.execute("UPDATE knjiga SET vsota_ocen = %s WHERE id = %s;",
                            (nova_vsota_ocen, knjiga['id']))
                conn.commit()
            ocena_uporabnika = int(nova_ocena)
        else:
            if nova_ocena is not None:
                nova_ocena = int(nova_ocena)
                # uporabnik je knjigo na novo ocenil
                cur.execute("UPDATE prebrane SET ocena = %s WHERE id_knjige = %s AND id_uporabnika = %s;",
                           (nova_ocena, knjiga['id'], trenutni_uporabnik[0]))
                cur.execute("UPDATE knjiga SET vsota_ocen = %s, stevilo_ocen = %s WHERE id = %s;",
                            (knjiga['vsota_ocen'] + nova_ocena, knjiga['stevilo_ocen'] + 1, knjiga['id']))
                conn.commit()
                ocena_uporabnika = nova_ocena
            else:
                ocena_uporabnika = None
    else:
        # uporabnik knjige še ni prebral, ali nihče ni vpisan
        ocena_uporabnika = None
    return template('knjiga.html', vseKljucne=vse_kljucne, zanri=vsi_zanri, uporabnik=trenutni_uporabnik,
                    knjiga=knjiga, ocena=ocena_uporabnika, prebrano=prebrano, zelja=zelja)


@post('/kazaloAvtorja')
def kazalo_avtorja():
    cur.execute("""SELECT id, ime FROM avtor;""")
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
    return template('kazalo_avtorjev.html', vseKljucne=vse_kljucne, zanri=vsi_zanri,
                    uporabnik=uporabnik(), avtorji=avtorji)


@post('/kazaloZanra')
def kazalo_zanra():
    cur.execute("""SELECT ime_zanra FROM zanr;""")
    vsi_zanri_iz_baze = cur.fetchall()
    return template('kazalo_zanrov.html', vseKljucne=vse_kljucne, zanri=vsi_zanri,
                    uporabnik=uporabnik(), zanri_kazalo=vsi_zanri_iz_baze)


@post('/rezultatiIskanja')
def rezultati_iskanja():
    if request.forms.get('iskaniIzrazKnjige') != '':
        iskani_izraz = request.forms.get('iskaniIzrazKnjige')
        velik_izraz = iskani_izraz[0].upper() + iskani_izraz[1:]
        iskani_izrazi = [' ' + iskani_izraz + ' ', ' ' + velik_izraz + ' ', ' ' + iskani_izraz + 's ', ' ' + velik_izraz + 's ']
        vse_vrstice = []
        for izraz in iskani_izrazi:
            niz = ("SELECT knjiga.id, knjiga.naslov, avtor.id, avtor.ime, zanr_knjige.zanr, knjiga.url_naslovnice "
               "FROM knjiga LEFT JOIN avtor_knjige ON knjiga.id=avtor_knjige.id_knjige LEFT JOIN avtor "
               "ON avtor_knjige.id_avtorja=avtor.id LEFT JOIN zanr_knjige ON knjiga.id=zanr_knjige.id_knjige "
               "WHERE CONCAT_WS('|', knjiga.naslov, knjiga.opis) LIKE %s", ('%' + izraz + '%',))
            cur.execute(niz[0], niz[1])
            trenutne_vrstice = cur.fetchall()
            vse_vrstice += trenutne_vrstice
        if vse_vrstice != []:
            slovar_slovarjev_knjig = {}
            for vrstica in vse_vrstice:
                id = vrstica[0]
                trenutna_knjiga = slovar_slovarjev_knjig.get(id, {'id': id, 'naslov': None, 'avtorji': set(),
                                                                  'zanri': set(), 'url_naslovnice': None})
                trenutna_knjiga['naslov'] = vrstica[1]
                trenutna_knjiga['avtorji'].add((vrstica[2], vrstica[3]))
                trenutna_knjiga['zanri'].add(vrstica[4])
                trenutna_knjiga['url_naslovnice'] = vrstica[5]
                slovar_slovarjev_knjig[id] = trenutna_knjiga
            return template('izpis_knjiznih_zadetkov.html', vseKljucne=vse_kljucne, zanri=vsi_zanri,
                            uporabnik=uporabnik(), knjige=list(slovar_slovarjev_knjig.values()),
                            stran=1, poizvedba=niz, parametri=[])
    elif request.forms.get('iskaniIzrazAvtorji') != '':
        iskani_izraz = request.forms.get('iskaniIzrazAvtorji')
        niz = ("""SELECT avtor.id, avtor.ime, avtorjev_zanr.zanr FROM avtor LEFT JOIN avtorjev_zanr ON 
                  avtor.id=avtorjev_zanr.id WHERE avtor.ime LIKE %s""", ('%' + iskani_izraz + '%',))
        cur.execute(niz[0], niz[1])
        vse_vrstice = cur.fetchall()
        if vse_vrstice != []:
            zadetki_avtorjev = {}
            for vrstica in vse_vrstice:
                id = vrstica[0]
                trenutni_avtor = zadetki_avtorjev.get(id, {'id': id, 'ime': None, 'zanri': set()})
                trenutni_avtor['ime'] = vrstica[1]
                trenutni_avtor['zanri'].add(vrstica[2])
                zadetki_avtorjev[id] = trenutni_avtor
            return template('izpis_zadetkov_avtorjev.html', vseKljucne=vse_kljucne, zanri=vsi_zanri,
                            uporabnik=uporabnik(), avtorji=list(zadetki_avtorjev.values()), stran=1, poizvedba=niz)
    # če sta obe polji prazni ali če ni zadetkov
    else:
        iskani_izraz = 'You havent searched for any keyword or author.'
    return template('ni_zadetkov.html', vseKljucne=vse_kljucne, zanri=vsi_zanri,
                    uporabnik=uporabnik(), parametri=[iskani_izraz])


@get('/izpis_zadetkov/:x')
def izpis_zadetkov(x):
    [tip, stran, niz] = x.split('&')
    niz1, niz2 = niz.split(", ('")
    parametri_sql = ()
    for param in niz2[:-2]. split(','):
        if param != '':
            if " " == param[0]:
                param = param[1:]
            try:
                param = int(param)
                parametri_sql += (param,)
            except:
                if "'" == param[-1]:
                    param = param[:-1]
                if "'" == param[0]:
                    param = param[1:]
                parametri_sql += (param,)
    cur.execute(niz1[2:-1], parametri_sql)
    vse_vrstice = cur.fetchall()
    if vse_vrstice == []:
        return template('ni_zadetkov.html', vseKljucne=vse_kljucne, zanri=vsi_zanri,
                        uporabnik=uporabnik(), parametri=niz2[:-3])
    else:
        if tip == 'knjiga':
            slovar_slovarjev_knjig = {}
            for vrstica in vse_vrstice:
                id = vrstica[0]
                trenutna_knjiga = slovar_slovarjev_knjig.get(id,
                                                             {'id': id, 'naslov': None, 'avtorji': set(),
                                                              'zanri': set(), 'url_naslovnice': None})
                trenutna_knjiga['naslov'] = vrstica[1]
                trenutna_knjiga['avtorji'].add((vrstica[2], vrstica[3]))
                trenutna_knjiga['zanri'].add(vrstica[4])
                trenutna_knjiga['url_naslovnice'] = vrstica[5]
                slovar_slovarjev_knjig[id] = trenutna_knjiga
            return template('izpis_knjiznih_zadetkov.html', vseKljucne=vse_kljucne, zanri=vsi_zanri,
                            uporabnik=uporabnik(), knjige=list(slovar_slovarjev_knjig.values()),
                            stran=stran, poizvedba=niz, parametri=[])
        elif tip == 'avtor':
            zadetki_avtorjev = {}
            for vrstica in vse_vrstice:
                id = vrstica[0]
                trenutni_avtor = zadetki_avtorjev.get(id, {'id': id, 'ime': None, 'zanri': set()})
                trenutni_avtor['ime'] = vrstica[1]
                trenutni_avtor['zanri'].add(vrstica[2])
                zadetki_avtorjev[id] = trenutni_avtor
            return template('izpis_zadetkov_avtorjev.html', vseKljucne=vse_kljucne, zanri=vsi_zanri,
                            uporabnik=uporabnik(), avtorji=list(zadetki_avtorjev.values()), stran=stran, poizvedba=niz)


@post('/add_wishlist/:x')
def dodaj_zeljo(x):
    cur.execute(  # SELECT knjiga.id, isbn, naslov, dolzina, knjiga.vsota_ocen, stevilo_ocen, leto, knjiga.opis,
        """SELECT knjiga.id, isbn, naslov, dolzina, knjiga.vsota_ocen, stevilo_ocen, leto, knjiga.opis, 
    avtor.id, avtor.ime, serija.id, serija.ime, del_serije.zaporedna_stevilka_serije, kljucna_beseda, ime_zanra, 
    knjiga.url_naslovnice FROM knjiga
LEFT JOIN avtor_knjige ON knjiga.id=avtor_knjige.id_knjige
LEFT JOIN avtor ON avtor_knjige.id_avtorja = avtor.id
LEFT JOIN del_serije ON knjiga.id=del_serije.id_knjige
LEFT JOIN serija ON serija.id=del_serije.id_serije
LEFT JOIN knjiga_kljucne_besede ON knjiga.id = knjiga_kljucne_besede.id_knjige
LEFT JOIN zanr_knjige ON zanr_knjige.id_knjige = knjiga.id
LEFT JOIN zanr ON zanr_knjige.zanr = zanr.ime_zanra
WHERE knjiga.id =%s;""", (x,))
    vse_vrstice = cur.fetchall()
    knjiga = {'id': vse_vrstice[0][0],
              'isbn': vse_vrstice[0][1],
              'naslov': vse_vrstice[0][2],
              'dolzina': vse_vrstice[0][3],
              'vsota_ocen': vse_vrstice[0][4],
              'stevilo_ocen': vse_vrstice[0][5],
              'leto': vse_vrstice[0][6],
              'opis': vse_vrstice[0][7],
              'avtor': set(),
              'serija': set(),
              'kljucna_beseda': set(),
              'zanri': set(),
              'url_naslovnice': vse_vrstice[0][15]}
    if knjiga['vsota_ocen'] == 0:
        knjiga['povprecna_ocena'] = 0
    else:
        knjiga['povprecna_ocena'] = round(knjiga['vsota_ocen'] / knjiga['stevilo_ocen'], 2)
    for vrstica in vse_vrstice:
        knjiga['avtor'].add((vrstica[8], vrstica[9]))
        knjiga['serija'].add((vrstica[10], vrstica[11], vrstica[12]))
        knjiga['kljucna_beseda'].add(vrstica[13])
        knjiga['zanri'].add(vrstica[14])

    trenutni_uporabnik = uporabnik()

    # ~~~~~~~~~~~~~~~~~~~ GUMBI PREBRANO / WISHLIST ~~~~~~~~~~~~~~~~~~~~~~

    cur.execute("""INSERT TO zelje (id_uporabnika, id_knjige) VALUES (%s,%s)""", (trenutni_uporabnik[0], x))
    cur.commit()

    return template('knjiga.html', vseKljucne=vse_kljucne, zanri=vsi_zanri, uporabnik=trenutni_uporabnik,
                    knjiga=knjiga, ocena=None, prebrano=False, zelja=True)


@post('/remove_wishlist/:x')
def odstrani_zeljo(x):
    cur.execute(
        """SELECT knjiga.id, isbn, naslov, dolzina, knjiga.vsota_ocen, stevilo_ocen, leto, knjiga.opis, 
    avtor.id, avtor.ime, serija.id, serija.ime, del_serije.zaporedna_stevilka_serije, kljucna_beseda, ime_zanra, 
    knjiga.url_naslovnice FROM knjiga
LEFT JOIN avtor_knjige ON knjiga.id=avtor_knjige.id_knjige
LEFT JOIN avtor ON avtor_knjige.id_avtorja = avtor.id
LEFT JOIN del_serije ON knjiga.id=del_serije.id_knjige
LEFT JOIN serija ON serija.id=del_serije.id_serije
LEFT JOIN knjiga_kljucne_besede ON knjiga.id = knjiga_kljucne_besede.id_knjige
LEFT JOIN zanr_knjige ON zanr_knjige.id_knjige = knjiga.id
LEFT JOIN zanr ON zanr_knjige.zanr = zanr.ime_zanra
WHERE knjiga.id =%s;""", (x,))
    vse_vrstice = cur.fetchall()
    knjiga = {'id': vse_vrstice[0][0],
              'isbn': vse_vrstice[0][1],
              'naslov': vse_vrstice[0][2],
              'dolzina': vse_vrstice[0][3],
              'vsota_ocen': vse_vrstice[0][4],
              'stevilo_ocen': vse_vrstice[0][5],
              'leto': vse_vrstice[0][6],
              'opis': vse_vrstice[0][7],
              'avtor': set(),
              'serija': set(),
              'kljucna_beseda': set(),
              'zanri': set(),
              'url_naslovnice': vse_vrstice[0][15]}
    if knjiga['vsota_ocen'] == 0:
        knjiga['povprecna_ocena'] = 0
    else:
        knjiga['povprecna_ocena'] = round(knjiga['vsota_ocen'] / knjiga['stevilo_ocen'], 2)
    for vrstica in vse_vrstice:
        knjiga['avtor'].add((vrstica[8], vrstica[9]))
        knjiga['serija'].add((vrstica[10], vrstica[11], vrstica[12]))
        knjiga['kljucna_beseda'].add(vrstica[13])
        knjiga['zanri'].add(vrstica[14])

    trenutni_uporabnik = uporabnik()

    # ~~~~~~~~~~~~~~~~~~~ GUMBI PREBRANO / WISHLIST ~~~~~~~~~~~~~~~~~~~~~~

    cur.execute("""DELETE FROM zelje WHERE id_uporabnika = %s AND id_knjige = %s)""", (trenutni_uporabnik[0], x))
    cur.commit()

    return template('knjiga.html', vseKljucne=vse_kljucne, zanri=vsi_zanri, uporabnik=trenutni_uporabnik,
                    knjiga=knjiga, ocena=None, prebrano=False, zelja=False)


@post('/read/:x')
def odstrani_zeljo(x):
    cur.execute(
        """SELECT knjiga.id, isbn, naslov, dolzina, knjiga.vsota_ocen, stevilo_ocen, leto, knjiga.opis, 
    avtor.id, avtor.ime, serija.id, serija.ime, del_serije.zaporedna_stevilka_serije, kljucna_beseda, ime_zanra, 
    knjiga.url_naslovnice FROM knjiga
LEFT JOIN avtor_knjige ON knjiga.id=avtor_knjige.id_knjige
LEFT JOIN avtor ON avtor_knjige.id_avtorja = avtor.id
LEFT JOIN del_serije ON knjiga.id=del_serije.id_knjige
LEFT JOIN serija ON serija.id=del_serije.id_serije
LEFT JOIN knjiga_kljucne_besede ON knjiga.id = knjiga_kljucne_besede.id_knjige
LEFT JOIN zanr_knjige ON zanr_knjige.id_knjige = knjiga.id
LEFT JOIN zanr ON zanr_knjige.zanr = zanr.ime_zanra
WHERE knjiga.id =%s;""", (x,))
    vse_vrstice = cur.fetchall()
    knjiga = {'id': vse_vrstice[0][0],
              'isbn': vse_vrstice[0][1],
              'naslov': vse_vrstice[0][2],
              'dolzina': vse_vrstice[0][3],
              'vsota_ocen': vse_vrstice[0][4],
              'stevilo_ocen': vse_vrstice[0][5],
              'leto': vse_vrstice[0][6],
              'opis': vse_vrstice[0][7],
              'avtor': set(),
              'serija': set(),
              'kljucna_beseda': set(),
              'zanri': set(),
              'url_naslovnice': vse_vrstice[0][15]}
    if knjiga['vsota_ocen'] == 0:
        knjiga['povprecna_ocena'] = 0
    else:
        knjiga['povprecna_ocena'] = round(knjiga['vsota_ocen'] / knjiga['stevilo_ocen'], 2)
    for vrstica in vse_vrstice:
        knjiga['avtor'].add((vrstica[8], vrstica[9]))
        knjiga['serija'].add((vrstica[10], vrstica[11], vrstica[12]))
        knjiga['kljucna_beseda'].add(vrstica[13])
        knjiga['zanri'].add(vrstica[14])

    trenutni_uporabnik = uporabnik()

    # ~~~~~~~~~~~~~~~~~~~ GUMBI PREBRANO / WISHLIST ~~~~~~~~~~~~~~~~~~~~~~

    cur.execute("""DELETE FROM zelje WHERE id_uporabnika = %s AND id_knjige = %s);
    INSERT TO prebrano (id_uporabnika, id_knjige, ocena) VALUES (%s, %s, %s)""", (trenutni_uporabnik[0], x, None))
    cur.commit()

    return template('knjiga.html', vseKljucne=vse_kljucne, zanri=vsi_zanri, uporabnik=trenutni_uporabnik,
                    knjiga=knjiga, ocena=None, prebrano=True, zelja=False)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~UPORABNIKI~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


def uporabnik():
    # Preveri če je kdo vpisan
    vzdevek = request.get_cookie('vzdevek', secret=skrivnost)
    if vzdevek is not None:  # Preveri če uporabnik obsataja
        cur.execute("SELECT id, vzdevek, dom FROM uporabnik WHERE vzdevek=%s;", (vzdevek,))
        vrstica = cur.fetchone()
        if vrstica is not None:  # TODO ali možno?
            return vrstica
    else:
        return [0, None, None]


@get("/odjava")
def odjava():
    response.delete_cookie('vzdevek', path='/', domain='localhost')
    redirect('/')


@post("/prijava")
def prijava_uporabnika():
    vzdevek = request.forms.vzdevek
    geslo = zakodiraj_geslo(request.forms.geslo)
    # Preverimo če je bila pravilna prijava
    if vzdevek is not None:
        cur.execute("SELECT vzdevek FROM uporabnik WHERE vzdevek=%s;", (vzdevek,))
        if cur.fetchone() is None:
            return template("prijava.html", vseKljucne=vse_kljucne, zanri=vsi_zanri, uporabnik=uporabnik(),
                            sporocilo='This username does not yet exist. You may create a new user here.')
    if vzdevek is not None and geslo is not None:
        cur.execute("SELECT vzdevek FROM uporabnik WHERE vzdevek=%s AND geslo=%s;", (vzdevek, geslo))
        if cur.fetchone() is None:
            return template("prijava.html", vseKljucne=vse_kljucne, zanri=vsi_zanri, uporabnik=uporabnik(),
                            sporocilo='Password you have entered is not correct. Try again.')
        else:
            response.set_cookie('vzdevek', vzdevek, path='/', secret=skrivnost)
            # id = uporabnik()[0]
            # TODO: ko tukaj kličeva naslednjo stran, cookie še ni nastavljen in je prva stran še nepobarvana, zato
            # je trenutno narejen uporabnik na roke.
            cur.execute("SELECT id, vzdevek, dom FROM uporabnik WHERE vzdevek=%s;", (vzdevek,))
            vrstica = cur.fetchone()
            return template("zacetna_stran.html", vseKljucne=vse_kljucne, zanri=vsi_zanri,
                            uporabnik=vrstica)
            # redirect('/profile/' + str(id))


@get('/registracija')
def odpri_registracijo():
    return template('registracija.html', vseKljucne=vse_kljucne, zanri=vsi_zanri, uporabnik=uporabnik(), sporocilo=None,
                    email='', username='', house='Gryffindor', sex='Witch')


@post('/registracija')
def registriraj_uporabnika():
    vzdevek = request.forms.vzdevek
    geslo1 = request.forms.geslo
    geslo2 = request.forms.geslo2
    email = request.forms.email
    dom = request.forms.dom  # TODO request.forms.get("dom")
    spol = request.forms.spol  # TODO request.forms.get("spol")
    if spol == "Witch":
        spol = "Female"
    else:
        spol = "Male"

    cur.execute("SELECT vzdevek FROM uporabnik WHERE vzdevek=%s;", (vzdevek,))
    if cur.fetchone() is not None:
        return template("registracija.html", vseKljucne=vse_kljucne, zanri=vsi_zanri, uporabnik=uporabnik(),
                        sporocilo='Unfortunately this nickname is taken. Good one though.',
                        email=email, username='', house=dom, sex=spol)
    elif not geslo1 == geslo2:
        return template("registracija.html", vseKljucne=vse_kljucne, zanri=vsi_zanri, uporabnik=uporabnik(),
                        sporocilo='The passwords do not match. Check them again.',
                        email=email, username=vzdevek, house=dom, sex=spol)
    # TODO: a pogledava še za unikatne mejle?
    geslo_kodirano = zakodiraj_geslo(geslo1)
    cur.execute("INSERT INTO uporabnik (vzdevek, geslo, email, dom, spol) VALUES(%s,%s,%s,%s,%s);",
                (vzdevek, geslo_kodirano, email, dom, spol))
    conn.commit()
    return template('prijava.html', vseKljucne=vse_kljucne, zanri=vsi_zanri, uporabnik=uporabnik(),
                    sporocilo='Great, you are now member of our community. You can sign in here.')


@post('/profile/:x')
def profil(x):
    # TODO: tudi zdej sploh ne rabva pisat ker profil je, ker je to vse v cookijih shranjeno
    cur.execute("SELECT knjiga.id, knjiga.naslov FROM knjiga JOIN prebrane "
                "ON knjiga.id= prebrane.id_knjige WHERE prebrane.id_uporabnika=%s;", (uporabnik()[0],))
    prebrane = cur.fetchall()

    cur.execute("SELECT knjiga.id, knjiga.naslov FROM knjiga JOIN zelje ON knjiga.id= zelje.id_knjige "
                "WHERE zelje.id_uporabnika=%s;", (uporabnik()[0],))
    zelje = cur.fetchall()

    return template('profile.html', vseKljucne=vse_kljucne, zanri=vsi_zanri, uporabnik=uporabnik(),
                    prebrane=prebrane, zelje=zelje)


@get('/spremeni_profil')
def spremeni():
    cur.execute("SELECT spol FROM uporabnik WHERE id=%s;", (uporabnik()[0],))
    spol = cur.fetchone()[0]
    if spol == 'Female':
        spol = 'Witch'
    else:
        spol = 'Wizard'
    return template('spremeni_profil.html', vseKljucne=vse_kljucne, zanri=vsi_zanri, uporabnik=uporabnik(),
                    spol=spol, sporocilo=None)


@post('/spremeni_profil')
def spremeni():
    (id, vzdevek, dom) = uporabnik()

    geslo_staro = zakodiraj_geslo(request.forms.geslo_trenutno)
    geslo_novo = request.forms.novo_geslo
    geslo_novo2 = request.forms.novo_geslo2
    novi_dom = request.forms.dom  # TODO request.forms.get("dom")
    novi_spol = request.forms.spol  # TODO request.forms.get("spol")
    # Preveri, ali lahko sploh karkoli spreminja:
    cur.execute("SELECT geslo FROM uporabnik WHERE vzdevek=%s;", (vzdevek,))
    pravo_geslo = cur.fetchone()[0]
    if pravo_geslo != geslo_staro:
        return template("spremeni_profil.html", vseKljucne=vse_kljucne, zanri=vsi_zanri, uporabnik=uporabnik(),
                        sporocilo='The current password you typed is not correct, try again.', spol=novi_spol)
    elif geslo_novo == '':
        geslo_novo = geslo_staro
    elif geslo_novo != geslo_novo2:
        return template("spremeni_profil.html", vseKljucne=vse_kljucne, zanri=vsi_zanri, uporabnik=uporabnik(),
                        sporocilo='The new passwords do not match. Check them again.', spol=novi_spol)
    else:
        geslo_novo = zakodiraj_geslo(geslo_novo)
    if novi_spol == "Witch":
        novi_spol = "Female"
    elif novi_spol == "Wizard":
        novi_spol = "Male"
    cur.execute("UPDATE uporabnik SET geslo = %s, dom = %s, spol = %s WHERE id = %s;",
                (geslo_novo, novi_dom, novi_spol, id))
    conn.commit()
    cur.execute("SELECT knjiga.id, knjiga.naslov FROM knjiga JOIN prebrane "
                "ON knjiga.id= prebrane.id_knjige WHERE prebrane.id_uporabnika=%s;",
                (uporabnik()[0],))
    prebrane = cur.fetchall()
    cur.execute("SELECT knjiga.id, knjiga.naslov FROM knjiga JOIN zelje "
                "ON knjiga.id= zelje.id_knjige WHERE zelje.id_uporabnika=%s;",
                (uporabnik()[0],))
    zelje = cur.fetchall()

    return template('profile.html', vseKljucne=vse_kljucne, zanri=vsi_zanri, uporabnik=uporabnik(), prebrane=prebrane,
                    zelje=zelje)



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
 GROUP BY ime_zanra UNION ALL
 SELECT count(*) AS stevilo, ime_zanra FROM zanr AS zanr2
 JOIN avtorjev_zanr ON zanr2.ime_zanra=avtorjev_zanr.zanr
 GROUP BY ime_zanra
) AS tabela
GROUP BY ime_zanra
ORDER BY stevilo_skupaj DESC
LIMIT 50;""")

zanri_iz_baze = cur.fetchall()
vsi_zanri = []
for vrstica in zanri_iz_baze:
    vsi_zanri.append(vrstica[1])
vsi_zanri.sort()

# ~~~~~~~~~~~~~~~~~~~~~Pridobi vse skupine ključnih besed
cur.execute("""SELECT skupina, pojem FROM kljucna_beseda JOIN knjiga_kljucne_besede ON pojem=kljucna_beseda
GROUP BY pojem;""")
kljucne_iz_baze = cur.fetchall()
vse_kljucne = {}
for vrstica in kljucne_iz_baze:
    skupina = vrstica[0]
    vse_kljucne[skupina] = vse_kljucne.get(skupina, list()) + [vrstica[1]]

# poženemo strežnik na portu 8080, glej http://localhost:8080/
run(host='localhost', port=8080, reloader=True)


# TODO: gumbi prebrano, want to read
# TODO: Strani se izpišejo v stolpec (pri iskanju) ????
# TODO: a že išče ok besede? da ne vrača pr iskanju rat tut rattle
# TODO: lepše narejena razdelitev na strani (zdej se notri pošilja cel SQL)
# TODO: popravi ER diagram
# TODO: barva napisa se pri ravenclaw ne vidi
# TODO: če je prebrana knjiga, jo odstrani iz wishlista