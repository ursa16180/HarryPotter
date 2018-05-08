import zajemi_podatke as zp
import delamo_csv as dc
import delamo_csv_avtor as dca
import delamo_csv_serija as dcs
import orodja

zp.zajemi_knjige()
# v mapo knjige shrani knjige s seznama (z vseh strani naceloma)
mapa_knjige = orodja.datoteke("knjige/test")
dc.shrani_knjige(mapa_knjige)
# ~~~~~~~~~~~~~ sedaj se generirajo te zadeve:~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# PODATKI ZA ZAPIS: (nekoncni)
# seznam_vseh_knjig vsebuje vse, kar potrebujemo za zapis knjig s seznama v csv tabelo
# seznam_avtor_knjiga vsebuje podatke avtor-knjiga za zapis te relacije
# seznam_zanr_knjiga vsebuje podatke zanr-knjiga za zapis te relacije
# seznam_serija_knjiga vsebuje podatke serija-knjiga-stevilka za to relacijo
#
# Pomoc:
# idji_knjig - shranjuje samo id-je knjig na goodreadsu, da ne zajemava dvakrat knjig kasneje pri serijah.
#
# PODATKI ZA NADALJNI ZAJEM:
# slovar_url_serij vsebuje url naslove spletnih strani za zajem ostalih knjig v seriji
# slovar_url_avtorjev vsebuje url naslove spletnih strani za zajem podatkov o avtorjih
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ do tu~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

zp.zajemi_avtorje()
# v mapo avtorji shrani avtorje
mapa_avtorji = orodja.datoteke("avtorji/test")
dca.shrani_avtorje(mapa_avtorji)
# ~~~~~~~~~~~Tu se zgodi:~~~~~~~~~~~~~~~~~~
# PODATKI ZA ZAPIS: koncni - novih avtorjev ne bo, ker vse knjige v seriji pise isti avtor
# seznam_vseh_avtorjevih_zanrov vsebuje kombinacije avtor-zanr za to relacijo (6000)
# seznam_vseh_avtorjev vsebuje podatke o avtorjih za zapis glavne tabele (9000)
#
# Pomoc:
# mnozica_vseh_zanrov vsebuje vse zanre, ki jih pisejo avtorji

# TODO: zgenerira se csv avtorjev - premakni semž
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

zp.zajemi_serije()
mapa_serije = orodja.datoteke("serije")
dcs.shrani_serije(mapa_serije)
# ~~~~~~~~~ Tu dobimo: ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# PODATKI ZA ZAPIS: koncni
# seznam_vseh_serij podatki o serijah za tabelo serija

# PODATKI ZA NADALJNI ZAJEM:
# urlji_knjig_iz_serij  - seznam novih knjig za zajem
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

zp.zajemi_dodatne_knjige()
# zajamemo se te nove knjige: njihove spletne strani shranimo v mapo dodatne
# PAZI: vedno jo izbrisi, ce delas od zacetka:
mapa_dodatne_knjige = orodja.datoteke("knjige/dodatne")
dc.shrani_knjige(mapa_dodatne_knjige, prvic=False)
# ~~~~~~~~~~~~~~~~~~~~ DOBIMO: ~~~~~~~~~~~~~~~~~~~~~~~~~
# PODATKI ZA ZAPIS: koncni
# seznam_vseh_knjig vsebuje vse, kar potrebujemo za zapis knjig s seznama v csv tabelo
# seznam_avtor_knjiga vsebuje podatke avtor-knjiga za zapis te relacije
# seznam_zanr_knjiga vsebuje podatke zanr-knjiga za zapis te relacije
# seznam_serija_knjiga vsebuje podatke serija-knjiga-stevilka za to relacijo
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# TODO: seznam žanrov za svojo tabelo. + je to sploh treba? je smiselno?
# Mogoče zato da ne bi blo vedno delat ksne poizvedbe al pa kej tazga.

zanri_knjig = {}
for vnos in dc.seznam_zanr_knjiga:
    zanri_knjig.add(vnos['žanr'])
vsi_zanri = dc.mnozica_vseh_zanrov | zanri_knjig
# na enem mestu zbrani vsi zanri. Spremenimo v seznam slovarjev:
seznam_vseh_zanrov = [{x} for x in list(vsi_zanri)]


# naredimo csv datoteke iz zbranih podatkov:
# KNJIGA
orodja.zapisi_tabelo(dc.seznam_vseh_knjig,
                     ['ISBN', 'naslov', 'dolžina', 'povprečna ocena', 'št. ocen' , 'leto', 'opis'],
                     'podatki/knjiga.csv')
# AVTOR
orodja.zapisi_tabelo(dca.seznam_vseh_avtorjev,
                     ['ID', 'ime', 'povprecna_ocena', 'datum_rojstva', 'kraj_rojstva'],
                     'podatki/avtor.csv')
# SERIJA
orodja.zapisi_tabelo(seznam_vseh_serij,
                     ['id', 'ime', 'število knjig'],
                     'podatki/serija.csv')
# ŽANR
orodja.zapisi_tabelo(seznam_vseh_zanrov,
                     ['žanr'],
                     'podatki/zanr.csv')
# knjiga-avtor:
orodja.zapisi_tabelo(seznam_avtor_knjiga, ['ISBN', 'id'], 'podatki/avtor_knjige.csv')
# knjiga-zanr:
orodja.zapisi_tabelo(seznam_zanr_knjiga, ['ISBN', 'žanr'], 'podatki/zanr_knjige.csv')
# knjiga-serija:
orodja.zapisi_tabelo(seznam_serija_knjiga, ['ISBN', 'id_serije', 'zaporedna_stevilka_serije'], 'podatki/del_serije.csv')
# avtor_zanr:
orodja.zapisi_tabelo(seznam_vseh_avtorjevih_zanrov, ['id', 'zanr'], 'podatki/avtorjev_zanr.csv')


# TODO: uskladit imena stolpcev v tabelah...