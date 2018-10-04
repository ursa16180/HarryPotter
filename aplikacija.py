from bottle import *

# uvozimo ustrezne podatke za povezavo
import auth_public as auth

# uvozimo psycopg2
import psycopg2, psycopg2.extensions, psycopg2.extras
from operator import itemgetter

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
        cur.execute("SELECT id_knjige FROM prebrana_knjiga WHERE id_uporabnika=%s AND id_knjige=%s;",
                    (trenutni_uporabnik[0], knjiga['id']))
        prebrano = len(cur.fetchall()) > 0
        cur.execute("SELECT id_knjige FROM wishlist WHERE id_uporabnika=%s AND id_knjige=%s;",
                    (trenutni_uporabnik[0], knjiga['id']))
        zelja = len(cur.fetchall()) > 0

        if not prebrano:
            request.forms.get('')

    # ~~~~~~~~~~~~~~~~~~ OCENE ~~~~~~~~~~~~~~~~~~~~~~~~~

    if prebrano:
        cur.execute("SELECT ocena FROM prebrana_knjiga WHERE id_uporabnika=%s AND id_knjige=%s;",
                    (trenutni_uporabnik[0], knjiga['id']))
        stara_ocena = cur.fetchone()
        stara_ocena = stara_ocena[0]
        nova_ocena = request.forms.get('ocena')
        if stara_ocena is not None:
            # knjigo je uporabnik že ocenil, preverimo, ali je oceno spremenil:
            if nova_ocena is None:
                nova_ocena = stara_ocena
            elif stara_ocena != int(nova_ocena):
                cur.execute("UPDATE prebrana_knjiga SET ocena = %s WHERE id_knjige = %s AND id_uporabnika = %s;",
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
                cur.execute("UPDATE prebrana_knjiga SET ocena = %s WHERE id_knjige = %s AND id_uporabnika = %s;",
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


@get('/avtor/:x')
def avtor(x):
    cur.execute("SELECT id, ime, povprecna_ocena, datum_rojstva, kraj_rojstva FROM avtor WHERE id=%s", (x,))
    avtor = cur.fetchone()
    cur.execute("SELECT zanr FROM avtorjev_zanr WHERE id_avtorja = %s", (x,))
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


@get('/zanr/:x')
def zanr(x):
    cur.execute("SELECT ime_zanra, opis FROM zanr WHERE ime_zanra=%s;", (x,))
    zanr = cur.fetchone()
    cur.execute("SELECT id, naslov FROM knjiga JOIN zanr_knjige ON knjiga.id = zanr_knjige.id_knjige WHERE zanr=%s "
                "ORDER BY knjiga.stevilo_ocen DESC LIMIT 50;", (x,)) #TODO da razvrsti najboljše in ne najpopularnejše
    knjige = cur.fetchall()
    cur.execute("SELECT avtor.id, avtor.ime FROM avtor JOIN avtorjev_zanr ON avtor.id = avtorjev_zanr.id_avtorja "
                "WHERE avtorjev_zanr.zanr=%s ORDER BY avtor.povprecna_ocena DESC LIMIT 50;", (x,)) #TODO omejeno število avtorjev za posamezn žanr
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


@post('/isci/')
@post('/isci/<dolzina>/<kljucne>/<zanri>/<je_del_zbirke>/<stran:int>')
def iskanje_get(dolzina=200, kljucne='[]', zanri='[]', je_del_zbirke='Either way', stran=0):
    stran = int(stran)
    dolzina = int(dolzina)
    kljucne_v_delu = []
    if kljucne != '[]':
        for kljucna_string in kljucne[1:-1].split(', '):
            kljucne_v_delu.append(kljucna_string[1:-1])
        kljucne = kljucne_v_delu
    else:
        kljucne = []
    if zanri != '[]':
        zanri_v_delu = []
        for zanr_string in zanri[1:-1].split(', '):
            zanri_v_delu.append(zanr_string[1:-1])
        zanri = zanri_v_delu
    else:
        zanri = []

    na_stran = 10
    offset = stran * na_stran

    dobljena_dolzina = request.forms.get('dolzinaInput')
    if dobljena_dolzina is not None:
        dolzina = dobljena_dolzina
    dobljene_kljucne = request.POST.getall('kljucne_besede')
    if dobljene_kljucne != []:
        kljucne = dobljene_kljucne
    dobljeni_zanri = request.POST.getall('zanri')
    if dobljeni_zanri != []:
        zanri = dobljeni_zanri
    dobljene_zbirke = request.forms.get('zbirka')
    if dobljene_zbirke is not None:
        je_del_zbirke = dobljene_zbirke
    parametri_sql = ()
    parametri = []
    # ~~~~~~~~~~~~~~ Če so izbrane ključne besede, jih doda
    if kljucne == []:
        niz = "SELECT DISTINCT knjiga.id, naslov, avtor.id, avtor.ime, zanr, url_naslovnice, " \
              "vsota_ocen, stevilo_ocen FROM knjiga"
    else:
        vmesni_niz = ''
        for kljucna_beseda in kljucne:
            vmesni_niz += """ AND EXISTS (SELECT * FROM knjiga_kljucne_besede WHERE kljucna_beseda = %s 
                              AND knjiga_kljucne_besede.id_knjige=knjiga1.id_knjige)"""
            parametri_sql += (kljucna_beseda,)
        niz = "SELECT DISTINCT knjiga.id, naslov, avtor.id, avtor.ime, zanr, url_naslovnice, vsota_ocen, stevilo_ocen" \
              " FROM knjiga JOIN (SELECT DISTINCT * FROM knjiga_kljucne_besede knjiga1 WHERE " + vmesni_niz[5:] \
              + ") pomozna_tabela ON knjiga.id=pomozna_tabela.id_knjige"
        parametri += kljucne

    # ~~~~~~~~~~~~~~ če so izbrani zanri, jih doda
    if zanri != []:
        vmesni_niz = ''
        for zanr in zanri:
            vmesni_niz += """ AND EXISTS (SELECT * FROM zanr_knjige WHERE zanr = %s AND id_knjige=knjiga2.id_knjige)"""
            parametri_sql += (zanr,)
        niz += " JOIN (SELECT DISTINCT * FROM zanr_knjige knjiga2 WHERE " + vmesni_niz[5:] + \
               ") pomozna_tabela2 ON knjiga.id=pomozna_tabela2.id_knjige"
        parametri += zanri
    else:
        niz += " JOIN zanr_knjige ON knjiga.id=zanr_knjige.id_knjige"
    # ~~~~~~~~~~~~~~~Tukaj se doda avtor
    niz += " JOIN avtor_knjige ON knjiga.id = avtor_knjige.id_knjige JOIN avtor ON avtor_knjige.id_avtorja = avtor.id"
    # ~~~~~~~~~~~~~~Če želi da je del serije, se združi s tabelo serij
    if je_del_zbirke == 'Yes':
        niz += " JOIN del_serije ON knjiga.id=del_serije.id_knjige WHERE"
        parametri += ['Part of series']
    elif je_del_zbirke == 'No':
        parametri += ['Not part of series']
        niz += " WHERE knjiga.id NOT IN (SELECT id_knjige FROM del_serije) AND"
    else:
        niz += " WHERE"
    # ~~~~~~~~~~~~~ Tukaj se doda pogoj o dolžini knjige
    niz += " dolzina>=%s ORDER BY knjiga.id, avtor.id "
    parametri_sql += (dolzina,)
    parametri.append(str(dolzina) + ' pages')
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
            if vrstica[7] != 0:
                trenutna_knjiga['povprecna_ocena'] = vrstica[6] / vrstica[7]
            else:
                trenutna_knjiga['povprecna_ocena'] = 0
            slovar_slovarjev_knjig[id] = trenutna_knjiga
        vse_knjige = sorted(list(slovar_slovarjev_knjig.values()), key=itemgetter('povprecna_ocena'))
        stevilo_knjig = len(vse_knjige)
        st_strani = stevilo_knjig // 10 + 1
        if stevilo_knjig % 10 == 0:
            st_strani -= 1
        return template('izpis_knjiznih_zadetkov.html', vseKljucne=vse_kljucne, zanri=vsi_zanri, uporabnik=uporabnik(),
                        knjige=vse_knjige[offset: offset + na_stran], stran=stran, iskane_dolzine=dolzina,
                        iskane_kljucne=kljucne, iskani_zanri=zanri, iskano_zbirka=je_del_zbirke, parametri=parametri,
                        ima_naslednjo=stran+1 < st_strani, ima_prejsnjo=stran != 0, st_strani=st_strani,
                        st_zadetkov=stevilo_knjig, veliki_mali='veliki')

def poisci_kombinacije(besede):
    if besede == []:
        return []
    prva_beseda = besede[0]
    if len(besede) == 1:
        return [prva_beseda, prva_beseda[0].upper() + prva_beseda[1:]]
    kombinacije = []
    for kombinacija in poisci_kombinacije(besede[1:]):
        kombinacije += [prva_beseda + ' ' + kombinacija]
        kombinacije += [prva_beseda[0].upper() + prva_beseda[1:] + ' ' + kombinacija]
    return kombinacije

@post('/rezultati_iskanja_knjiga/')
@post('/rezultati_iskanja_knjiga/<iskani_izraz>/<stran>')
def rezultati_iskanja_knjiga(iskani_izraz="You haven't searched for any keyword.", stran=0):
    stran = int(stran)
    na_stran = 10
    offset = stran * na_stran
    dobljen_izraz = request.forms.get('iskaniIzrazKnjige')
    if dobljen_izraz is not None:
        iskani_izraz = dobljen_izraz
    if iskani_izraz != '':
        nizi = [('% ' + iskani_izraz + ' %',), ('% ' + iskani_izraz[0].upper() + iskani_izraz[1:] + ' %',),
                ('% ' + iskani_izraz + 's %',), ('% ' + iskani_izraz[0].upper() + iskani_izraz[1:] + 's %',)]
        besede = iskani_izraz.split(' ')
        if len(besede) > 1:
            vse_moznosti = poisci_kombinacije(besede)
            for izraz in vse_moznosti:
                nizi += [('% ' + izraz + ' %',)]

        vse_vrstice = []
        for niz in nizi:
            cur.execute("SELECT knjiga.id, knjiga.naslov, avtor.id, avtor.ime, zanr_knjige.zanr, knjiga.url_naslovnice "
                 "FROM knjiga LEFT JOIN avtor_knjige ON knjiga.id=avtor_knjige.id_knjige LEFT JOIN avtor "
                 "ON avtor_knjige.id_avtorja=avtor.id LEFT JOIN zanr_knjige ON knjiga.id=zanr_knjige.id_knjige "
                 "WHERE knjiga.opis LIKE %s;", niz)
            nove_vrstice = cur.fetchall()
            vse_vrstice += nove_vrstice
        cur.execute("SELECT knjiga.id, knjiga.naslov, avtor.id, avtor.ime, zanr_knjige.zanr, knjiga.url_naslovnice "
                    "FROM knjiga LEFT JOIN avtor_knjige ON knjiga.id=avtor_knjige.id_knjige LEFT JOIN avtor "
                    "ON avtor_knjige.id_avtorja=avtor.id LEFT JOIN zanr_knjige ON knjiga.id=zanr_knjige.id_knjige "
                    "WHERE knjiga.naslov LIKE %s;", ('%' + iskani_izraz + '%',))
        nove_vrstice = cur.fetchall()
        vse_vrstice += nove_vrstice
        if vse_vrstice != []:
            slovar_slovarjev_knjig = {}
            for vrstica in vse_vrstice:
                id_knjige = vrstica[0]
                trenutna_knjiga = slovar_slovarjev_knjig.get(id_knjige, {'id': id_knjige, 'naslov': None,
                                                                         'avtorji': set(), 'zanri': set(),
                                                                         'url_naslovnice': None})
                trenutna_knjiga['naslov'] = vrstica[1]
                trenutna_knjiga['avtorji'].add((vrstica[2], vrstica[3]))
                trenutna_knjiga['zanri'].add(vrstica[4])
                trenutna_knjiga['url_naslovnice'] = vrstica[5]
                slovar_slovarjev_knjig[id_knjige] = trenutna_knjiga
            vse_knjige = list(slovar_slovarjev_knjig.values())
            st_zadetkov = len(vse_knjige)
            st_strani = st_zadetkov//10 + 1
            if st_zadetkov % 10 == 0:
                st_strani -= 1
            return template('izpis_knjiznih_zadetkov.html', vseKljucne=vse_kljucne, zanri=vsi_zanri,
                            uporabnik=uporabnik(), knjige=vse_knjige[offset: offset + na_stran],
                            stran=stran, parametri=[iskani_izraz], iskani_izraz_knjiga=iskani_izraz, st_zadetkov=st_zadetkov,
                            st_strani=st_strani, ima_naslednjo=stran+1 < st_strani, ima_prejsnjo=stran != 0,
                            veliki_mali='mali')
    return template('ni_zadetkov.html', vseKljucne=vse_kljucne, zanri=vsi_zanri,
                    uporabnik=uporabnik(), parametri=[iskani_izraz])


@post('/rezultati_iskanja_avtor/')
@post('/rezultati_iskanja_avtor/<iskani_izraz>/<stran>')
def rezultati_iskanja_avtor(iskani_izraz="You haven't searched for any author.", stran=0):
    stran = int(stran)
    na_stran = 10
    offset = na_stran * stran

    dobljeni_izraz = request.forms.get('iskaniIzrazAvtorji')
    if dobljeni_izraz is not None:
        iskani_izraz = dobljeni_izraz
    if iskani_izraz != '':
        nizi = [("""SELECT avtor.id, avtor.ime, avtorjev_zanr.zanr FROM avtor LEFT JOIN avtorjev_zanr ON 
                  avtor.id=avtorjev_zanr.id_avtorja WHERE avtor.ime LIKE %s """, ('%' + iskani_izraz + '%', )),
                ("""SELECT avtor.id, avtor.ime, avtorjev_zanr.zanr FROM avtor LEFT JOIN avtorjev_zanr ON 
                  avtor.id=avtorjev_zanr.id_avtorja WHERE avtor.ime LIKE %s """, ('%' + iskani_izraz[0].upper() + iskani_izraz[1:] + '%', )),]
        vse_vrstice = []
        for niz in nizi:
            cur.execute(niz[0], niz[1])
            vse_vrstice += cur.fetchall()
        if vse_vrstice != []:
            zadetki_avtorjev = {}
            for vrstica in vse_vrstice:
                id_avtorja = vrstica[0]
                trenutni_avtor = zadetki_avtorjev.get(id_avtorja, {'id': id_avtorja, 'ime': None, 'zanri': set()})
                trenutni_avtor['ime'] = vrstica[1]
                trenutni_avtor['zanri'].add(vrstica[2])
                zadetki_avtorjev[id_avtorja] = trenutni_avtor
            vsi_avtorji = list(zadetki_avtorjev.values())
            st_zadetkov = len(vsi_avtorji)
            st_strani = st_zadetkov// 10 + 1
            if st_zadetkov%10 == 0:
                st_strani -= 1
            return template('izpis_zadetkov_avtorjev.html', vseKljucne=vse_kljucne, zanri=vsi_zanri,
                            uporabnik=uporabnik(), avtorji=vsi_avtorji[offset:offset + na_stran], stran=stran,
                            iskani_izraz_avtor=iskani_izraz, st_zadetkov=st_zadetkov,
                            st_strani=st_strani, ima_naslednjo=stran + 1 < st_strani, ima_prejsnjo=stran != 0
                            )
    # če je polje prazno ali če ni zadetkov
    return template('ni_zadetkov.html', vseKljucne=vse_kljucne, zanri=vsi_zanri,
                    uporabnik=uporabnik(), parametri=[iskani_izraz])



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

    cur.execute("""SELECT * FROM wishlist WHERE id_uporabnika = %s AND id_knjige = %s;""", (trenutni_uporabnik[0], x))
    zelja = len(cur.fetchall()) > 0
    if zelja:
        return template('knjiga.html', vseKljucne=vse_kljucne, zanri=vsi_zanri, uporabnik=trenutni_uporabnik,
                        knjiga=knjiga, ocena=None, prebrano=False, zelja=True)
    # ~~~~~~~~~~~~~~~~~~~ GUMBI PREBRANO / WISHLIST ~~~~~~~~~~~~~~~~~~~~~~


    cur.execute("""INSERT INTO wishlist (id_uporabnika, id_knjige) VALUES (%s,%s)""", (trenutni_uporabnik[0], x))
    conn.commit()

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
    cur.execute("""SELECT * FROM wishlist WHERE id_uporabnika = %s AND id_knjige = %s;""", (trenutni_uporabnik[0], x))
    zelja = len(cur.fetchall()) > 0
    if not zelja:
        return template('knjiga.html', vseKljucne=vse_kljucne, zanri=vsi_zanri, uporabnik=trenutni_uporabnik,
                        knjiga=knjiga, ocena=None, prebrano=False, zelja=False)
    # ~~~~~~~~~~~~~~~~~~~ GUMBI PREBRANO / WISHLIST ~~~~~~~~~~~~~~~~~~~~~~

    cur.execute("""DELETE FROM wishlist WHERE id_uporabnika = %s AND id_knjige = %s""", (trenutni_uporabnik[0], x))
    conn.commit()

    return template('knjiga.html', vseKljucne=vse_kljucne, zanri=vsi_zanri, uporabnik=trenutni_uporabnik,
                    knjiga=knjiga, ocena=None, prebrano=False, zelja=False)


@post('/read/:x')
def prebral(x):
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
    cur.execute("""SELECT * FROM prebrana_knjiga WHERE id_uporabnika = %s AND id_knjige = %s;""", (trenutni_uporabnik[0], x))
    prebrano = len(cur.fetchall()) > 0
    if prebrano:
        return template('knjiga.html', vseKljucne=vse_kljucne, zanri=vsi_zanri, uporabnik=trenutni_uporabnik,
                        knjiga=knjiga, ocena=None, prebrano=True, zelja=False)
    # ~~~~~~~~~~~~~~~~~~~ GUMBI PREBRANO / WISHLIST ~~~~~~~~~~~~~~~~~~~~~~

    cur.execute("""DELETE FROM wishlist WHERE id_uporabnika = %s AND id_knjige = %s;
    INSERT INTO prebrana_knjiga (id_uporabnika, id_knjige, ocena) VALUES (%s, %s, %s)""", (trenutni_uporabnik[0], x, trenutni_uporabnik[0], x, None))

    conn.commit()

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
    nov_vzdevek = cur.fetchone() is None
    cur.execute("SELECT email FROM uporabnik WHERE email=%s;", (email,))
    nov_mail = cur.fetchone() is None
    if not nov_vzdevek:
        return template("registracija.html", vseKljucne=vse_kljucne, zanri=vsi_zanri, uporabnik=uporabnik(),
                        sporocilo='Unfortunately this nickname is taken. Good one though.',
                        email=email, username='', house=dom, sex=spol)
    if not nov_mail:
        return template("registracija.html", vseKljucne=vse_kljucne, zanri=vsi_zanri, uporabnik=uporabnik(),
                        sporocilo='Unfortunately someone has already used this email to sign up to our library.',
                        username=vzdevek, house=dom, sex=spol, email='')
    elif not geslo1 == geslo2:
        return template("registracija.html", vseKljucne=vse_kljucne, zanri=vsi_zanri, uporabnik=uporabnik(),
                        sporocilo='The passwords do not match. Check them again.',
                        email=email, username=vzdevek, house=dom, sex=spol)
    geslo_kodirano = zakodiraj_geslo(geslo1)
    cur.execute("INSERT INTO uporabnik (vzdevek, geslo, email, dom, spol) VALUES(%s,%s,%s,%s,%s);",
                (vzdevek, geslo_kodirano, email, dom, spol))
    conn.commit()
    return template('prijava.html', vseKljucne=vse_kljucne, zanri=vsi_zanri, uporabnik=uporabnik(),
                    sporocilo='Great, you are now member of our community. You can sign in here.')


@post('/profile/:x')
def profil(x):
    # TODO: tudi zdej sploh ne rabva pisat ker profil je, ker je to vse v cookijih shranjeno
    cur.execute("SELECT knjiga.id, knjiga.naslov FROM knjiga JOIN prebrana_knjiga "
                "ON knjiga.id= prebrana_knjiga.id_knjige WHERE prebrana_knjiga.id_uporabnika=%s;", (uporabnik()[0],))
    prebrane = cur.fetchall()

    cur.execute("SELECT knjiga.id, knjiga.naslov FROM knjiga JOIN wishlist ON knjiga.id= wishlist.id_knjige "
                "WHERE wishlist.id_uporabnika=%s;", (uporabnik()[0],))
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
    cur.execute("SELECT knjiga.id, knjiga.naslov FROM knjiga JOIN prebrana_knjiga "
                "ON knjiga.id= prebrana_knjiga.id_knjige WHERE prebrana_knjiga.id_uporabnika=%s;",
                (uporabnik()[0],))
    prebrane = cur.fetchall()
    cur.execute("SELECT knjiga.id, knjiga.naslov FROM knjiga JOIN wishlist "
                "ON knjiga.id= wishlist.id_knjige WHERE wishlist.id_uporabnika=%s;",
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


# TODO: Strani se izpišejo v stolpec (pri iskanju) ????
# TODO: lepše narejena razdelitev na strani (zdej se notri pošilja cel SQL) - Vprašaj Ines
# TODO: popravi ER diagram
# TODO: barva napisa se pri ravenclaw ne vidi - barve linkov in ozadij
# TODO: gumbi preberi/wishlist pri zadetkih
# TODO: na profilu odstranjevanje iz wishlista in prebrano
# TODO: slike ne delajo, ko se premakneš na naslednjo stran zadetkov
