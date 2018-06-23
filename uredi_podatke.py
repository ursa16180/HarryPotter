import zajemi_podatke as zp
import delamo_csv as dc
import delamo_csv_avtor as dca
import delamo_csv_serija as dcs
import delamo_csv_zanr as dcz
import delamo_csv_kljucne_besede as dckb
import orodja


#zp.zajemi_knjige()
# v mapo knjige shrani knjige s seznama (z vseh strani naceloma)
mapa_knjige = orodja.datoteke("knjige")
print('shranjujem knjige')
dc.shrani_knjige(mapa_knjige)
# seznam_vseh_tujih_knjig += dc.seznam_tujih_knjig
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


#zp.zajemi_serije()
mapa_serije = orodja.datoteke("serije")
print('shranjujem serije')
dcs.shrani_serije(mapa_serije)
# ~~~~~~~~~ Tu dobimo: ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# PODATKI ZA ZAPIS: koncni
# seznam_vseh_serij podatki o serijah za tabelo serija
# seznam_serija_knjiga vsebuje drugi del podatkov o knjigah v seriji.
#
# PODATKI ZA NADALJNI ZAJEM:
# urlji_knjig_iz_serij  - seznam novih knjig za zajem
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#zp.zajemi_dodatne_knjige()
# zajamemo nove knjige: njihove spletne strani shranimo v mapo dodatne
mapa_dodatne_knjige = orodja.datoteke("dodatne_knjige")
print('shranjujem dodatne knjige')
dc.shrani_knjige(mapa_dodatne_knjige, prvic=False)
# seznam_vseh_tujih_knjig += dc.seznam_tujih_knjig
# ~~~~~~~~~~~~~~~~~~~~ DOBIMO: ~~~~~~~~~~~~~~~~~~~~~~~~~
# PODATKI ZA ZAPIS: koncni
# seznam_vseh_knjig vsebuje vse, kar potrebujemo za zapis knjig s seznama v csv tabelo
# seznam_avtor_knjiga vsebuje podatke avtor-knjiga za zapis te relacije
# seznam_zanr_knjiga vsebuje podatke zanr-knjiga za zapis te relacije
# seznam_serija_knjiga vsebuje podatke serija-knjiga-stevilka za to relacijo
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# V tabelo del_serije dodamo še tiste dodatne knjige, ki so že v kakšni prej znani seriji:
for knjiga in dc.dodaj_ze_znanim_serijam:
    if knjiga['id_serije'] in dcs.idji_serij:
        dc.seznam_serija_knjiga.append(knjiga)

# Počistimo tuje knjige, ki so se ponesreši dodale v tabelo knjiga - serija in preštejemo knjige v posameznih serijah:
#TODO: odstrani še avtorje tujih knjig
seznam_serija_knjiga = []  # nujno moraš narediti nov seznam, ker če ostranjuješ se zaplete z indeksiranjem in for zanka ne deluje
stejemo_knjige_v_serijah = {}
for knjiga in dcs.seznam_serija_knjiga + dc.seznam_serija_knjiga:
    if knjiga['id_knjige'] not in dc.seznam_tujih_knjig:
        seznam_serija_knjiga.append(knjiga)
        stejemo_knjige_v_serijah[knjiga['id_serije']] = stejemo_knjige_v_serijah.get(knjiga['id_serije'], 0) + 1

# preštejemo knjige v serijah
nov_seznam_serij = []
for serija in dcs.seznam_vseh_serij:
    serija['stevilo_knjig'] = stejemo_knjige_v_serijah.get(serija['id'], 0)
    nov_seznam_serij.append(serija)

#zp.zajemi_avtorje()
# v mapo avtorji shrani avtorje
# mapa_avtorji = orodja.datoteke("avtorji")
# print('shranjujem avtorje')
# dca.shrani_avtorje(mapa_avtorji)
# ~~~~~~~~~~~Tu se zgodi:~~~~~~~~~~~~~~~~~~
# PODATKI ZA ZAPIS: končni
# seznam_vseh_avtorjevih_zanrov vsebuje kombinacije avtor-žanr za to relacijo (6000)
# seznam_vseh_avtorjev vsebuje podatke o avtorjih za zapis glavne tabele (9000)
#
# Pomoč:
# množica_vseh_zanrov vsebuje vse žanre, ki jih pišejo avtorji
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# zp.zajemi_zanre()
# mapa_zanri = orodja.datoteke("zanri")
# dcz.shrani_zanre(mapa_zanri)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#Tukaj zajamemo podatke za tabelo žanrov
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#dckb.poisci_kljucne_besede(dc.seznam_vseh_knjig)
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#Tukaj zajamemo podatke za tabelo knjiga_kljucna_beseda
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~



print('delam csvje')
# naredimo csv datoteke iz zbranih podatkov:
# KNJIGA
orodja.zapisi_tabelo(dc.seznam_vseh_knjig,
                     ['id', 'ISBN', 'naslov', 'dolzina', 'povprecna_ocena', 'stevilo_ocen', 'leto', 'opis', 'url_naslovnice'],
                     'podatki/knjiga.csv')
# AVTOR
# orodja.zapisi_tabelo(dca.seznam_vseh_avtorjev,
#                      ['id', 'ime', 'povprecna_ocena', 'datum_rojstva', 'kraj_rojstva'],
#                      'podatki/avtor.csv')
# SERIJA
orodja.zapisi_tabelo(nov_seznam_serij,
                     ['id', 'ime', 'stevilo_knjig'],
                     'podatki/serija.csv')

# ŽANR (drugi poskus)
#orodja.zapisi_tabelo(dcz.seznam_vseh_zanrov,
#                      ['ime_zanra', 'opis'],
#                      'podatki/zanr.csv')

# knjiga-avtor:
#orodja.zapisi_tabelo(dc.seznam_avtor_knjiga, ['id_knjige', 'id_avtorja'], 'podatki/avtor_knjige.csv')
# knjiga-zanr:
#orodja.zapisi_tabelo(dc.seznam_zanr_knjiga, ['id_knjige', 'zanr'], 'podatki/zanr_knjige.csv')
# knjiga-serija:
orodja.zapisi_tabelo(seznam_serija_knjiga,
                     ['id_knjige', 'id_serije', 'zaporedna_stevilka_serije'],
                     'podatki/del_serije.csv')
# avtor_zanr:
#orodja.zapisi_tabelo(dca.seznam_vseh_avtorjevih_zanrov, ['id', 'zanr'], 'podatki/avtorjev_zanr.csv')

# knjiga_kljucne_besede:
orodja.zapisi_tabelo(dckb.seznam_vseh_knjig_kljucnih_besed, ['id_knjige', 'kljucna_beseda'], 'podatki/knjiga_kljucne_besede.csv')
