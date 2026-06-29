"""
Eelarverakendus — terminalis töötav isikliku eelarve tööriist.
Andmed salvestatakse eelarve_andmed.json faili.
Käivita: python eelarve.py
"""

import json
import os
from datetime import datetime

ANDMEFAIL = "eelarve_andmed.json"


def laadi_andmed():
    if os.path.exists(ANDMEFAIL):
        with open(ANDMEFAIL, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"tulud": [], "kulud": [], "eelarve": {}}


def salvesta_andmed(andmed):
    with open(ANDMEFAIL, "w", encoding="utf-8") as f:
        json.dump(andmed, f, ensure_ascii=False, indent=2)


def praegune_kuu():
    return datetime.now().strftime("%Y-%m")


def prindi_pealkiri(tekst):
    print("\n" + "=" * 45)
    print(f"  {tekst}")
    print("=" * 45)


def lisa_tulu(andmed):
    prindi_pealkiri("LISA TULU")
    kirjeldus = input("Kirjeldus (nt palk, lisatöö): ").strip()
    if not kirjeldus:
        print("Tühjendatud.")
        return
    try:
        summa = float(input("Summa (€): ").replace(",", "."))
    except ValueError:
        print("Vale summa.")
        return
    kuu = praegune_kuu()
    andmed["tulud"].append({"kirjeldus": kirjeldus, "summa": summa, "kuu": kuu})
    salvesta_andmed(andmed)
    print(f"✓ Lisatud: {kirjeldus} {summa:.2f} €")


def lisa_kulu(andmed):
    prindi_pealkiri("LISA KULU")
    # Näita olemasolevaid kategooriaid
    olemasolevad = sorted(set(k["kategooria"] for k in andmed["kulud"]))
    if olemasolevad:
        print("Olemasolevad kategooriad:", ", ".join(olemasolevad))
    kategooria = input("Kategooria (nt toit, transport, meelelahutus): ").strip()
    if not kategooria:
        print("Tühjendatud.")
        return
    kirjeldus = input("Kirjeldus (nt Rimi, bussikuu): ").strip()
    try:
        summa = float(input("Summa (€): ").replace(",", "."))
    except ValueError:
        print("Vale summa.")
        return
    kuu = praegune_kuu()
    andmed["kulud"].append({
        "kategooria": kategooria,
        "kirjeldus": kirjeldus,
        "summa": summa,
        "kuu": kuu
    })
    salvesta_andmed(andmed)
    print(f"✓ Lisatud: {kategooria} / {kirjeldus} {summa:.2f} €")


def sea_eelarve(andmed):
    prindi_pealkiri("SEA KUUEELARVE KATEGOORIALE")
    kategooria = input("Kategooria: ").strip()
    if not kategooria:
        return
    try:
        plaan = float(input(f"Plaan {kategooria} jaoks (€/kuu): ").replace(",", "."))
    except ValueError:
        print("Vale summa.")
        return
    kuu = praegune_kuu()
    võti = f"{kuu}_{kategooria}"
    andmed["eelarve"][võti] = plaan
    salvesta_andmed(andmed)
    print(f"✓ Eelarve seatud: {kategooria} → {plaan:.2f} €/kuu")


def kuva_kokkuvote(andmed):
    kuu = praegune_kuu()
    prindi_pealkiri(f"KOKKUVÕTE — {kuu}")

    # Tulud
    kuu_tulud = [t for t in andmed["tulud"] if t["kuu"] == kuu]
    kokku_tulud = sum(t["summa"] for t in kuu_tulud)
    print(f"\n📥 TULUD: {kokku_tulud:.2f} €")
    for t in kuu_tulud:
        print(f"   {t['kirjeldus']:30s} {t['summa']:>8.2f} €")

    # Kulud kategooriate kaupa
    kuu_kulud = [k for k in andmed["kulud"] if k["kuu"] == kuu]
    kokku_kulud = sum(k["summa"] for k in kuu_kulud)

    print(f"\n📤 KULUD: {kokku_kulud:.2f} €")
    print(f"\n  {'Kategooria':<20} {'Plaan':>8} {'Tegelik':>9} {'Vahe':>8}")
    print("  " + "-" * 47)

    kategooriad = sorted(set(k["kategooria"] for k in kuu_kulud))
    # Lisa ka kategooriad, millel on plaan aga veel pole kulusid
    eelarve_kategooriad = [
        v.split("_", 1)[1] for v in andmed["eelarve"]
        if v.startswith(kuu + "_")
    ]
    kõik = sorted(set(kategooriad + eelarve_kategooriad))

    for kat in kõik:
        tegelik = sum(k["summa"] for k in kuu_kulud if k["kategooria"] == kat)
        plaan = andmed["eelarve"].get(f"{kuu}_{kat}", 0.0)
        vahe = plaan - tegelik
        vahe_märk = "✓" if vahe >= 0 else "⚠"
        plaan_tekst = f"{plaan:.2f} €" if plaan else "    —   "
        print(f"  {kat:<20} {plaan_tekst:>8} {tegelik:>8.2f} € {vahe_märk} {vahe:>+7.2f} €")

    # Bilanss
    bilanss = kokku_tulud - kokku_kulud
    print("\n" + "-" * 45)
    print(f"  BILANSS: {bilanss:+.2f} €")
    if bilanss >= 0:
        print("  ✓ Oled plussis!")
    else:
        print("  ⚠ Oled miinuses!")


def kuva_ajalugu(andmed):
    prindi_pealkiri("KÕIK KULUD (viimased 20)")
    kulud = andmed["kulud"][-20:][::-1]
    if not kulud:
        print("Kulusid pole veel sisestatud.")
        return
    print(f"\n  {'Kuu':<8} {'Kategooria':<18} {'Kirjeldus':<22} {'Summa':>8}")
    print("  " + "-" * 58)
    for k in kulud:
        print(f"  {k['kuu']:<8} {k['kategooria']:<18} {k['kirjeldus']:<22} {k['summa']:>7.2f} €")


def kustuta_viimane(andmed):
    prindi_pealkiri("KUSTUTA VIIMANE KANNE")
    valik = input("Kustuta viimane [t]ulu või [k]ulu? ").strip().lower()
    if valik == "t" and andmed["tulud"]:
        kustutatud = andmed["tulud"].pop()
        salvesta_andmed(andmed)
        print(f"✓ Kustutatud: {kustutatud['kirjeldus']} {kustutatud['summa']:.2f} €")
    elif valik == "k" and andmed["kulud"]:
        kustutatud = andmed["kulud"].pop()
        salvesta_andmed(andmed)
        print(f"✓ Kustutatud: {kustutatud['kategooria']} / {kustutatud['kirjeldus']} {kustutatud['summa']:.2f} €")
    else:
        print("Midagi pole kustutada.")


def main():
    andmed = laadi_andmed()

    while True:
        prindi_pealkiri("EELARVERAKENDUS")
        print("  1  Lisa tulu")
        print("  2  Lisa kulu")
        print("  3  Sea kategooria eelarve (plaan)")
        print("  4  Vaata kuu kokkuvõtet")
        print("  5  Vaata kõiki kulusid")
        print("  6  Kustuta viimane kanne")
        print("  0  Välju")
        print()

        valik = input("  Valik: ").strip()

        if valik == "1":
            lisa_tulu(andmed)
        elif valik == "2":
            lisa_kulu(andmed)
        elif valik == "3":
            sea_eelarve(andmed)
        elif valik == "4":
            kuva_kokkuvote(andmed)
        elif valik == "5":
            kuva_ajalugu(andmed)
        elif valik == "6":
            kustuta_viimane(andmed)
        elif valik == "0":
            print("\nHead eelarvestamist! 👋\n")
            break
        else:
            print("Tundmatu valik.")

        input("\n  [Enter] jätka...")


if __name__ == "__main__":
    main()