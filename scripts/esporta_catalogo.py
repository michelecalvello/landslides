#!/usr/bin/env python3
"""Esporta il catalogo quotidiano delle frane in franeaggiornamentoquotidiano.json.

Uso:
    python3 scripts/esporta_catalogo.py CARTELLA_JSON [FILE_USCITA]

CARTELLA_JSON contiene un file .json per ogni notizia del catalogo, con i campi
url, titolo, data_pubblicazione, luoghi, effetti, classe_conseguenze,
numero_frane, data_frana, ora_frana, accuratezza_temporale, lat, lon,
accuratezza_spaziale e inserito_il. FILE_USCITA vale per default
franeaggiornamentoquotidiano.json nella radice del repository.
"""
import datetime
import glob
import json
import os
import sys
from zoneinfo import ZoneInfo

CAMPI = ["url", "titolo", "data_pubblicazione", "luoghi", "effetti",
         "classe_conseguenze", "numero_frane", "data_frana", "ora_frana",
         "accuratezza_temporale", "lat", "lon", "accuratezza_spaziale",
         "inserito_il"]
OBBLIGATORI = ["url", "titolo", "data_pubblicazione", "classe_conseguenze", "lat", "lon"]


def pulisci(d):
    for k in OBBLIGATORI:
        if d.get(k) in (None, ""):
            raise ValueError(f"campo {k} mancante in {d.get('url')}")
    r = {k: d.get(k, "") for k in CAMPI}
    r["lat"] = round(float(r["lat"]), 5)
    r["lon"] = round(float(r["lon"]), 5)
    if isinstance(r["luoghi"], str):
        r["luoghi"] = [r["luoghi"]] if r["luoghi"] else []
    n = r["numero_frane"]
    if isinstance(n, str) and n.strip().isdigit():
        r["numero_frane"] = int(n)
    if r["classe_conseguenze"] not in ("C1", "C2", "C3"):
        raise ValueError(f"classe non valida in {r['url']}")
    return r


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cartella = sys.argv[1]
    radice = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    uscita = sys.argv[2] if len(sys.argv) > 2 else os.path.join(radice, "franeaggiornamentoquotidiano.json")
    file = sorted(glob.glob(os.path.join(cartella, "**", "*.json"), recursive=True))
    frane, visti = [], set()
    for f in file:
        with open(f, encoding="utf-8") as h:
            d = json.load(h)
        if not isinstance(d, dict) or "url" not in d:
            continue
        r = pulisci(d)
        if r["url"] in visti:
            continue
        visti.add(r["url"])
        frane.append(r)
    if not frane:
        sys.exit("nessuna notizia trovata: il file non viene sovrascritto")
    frane.sort(key=lambda r: (r["data_pubblicazione"], r["data_frana"] or "", r["titolo"]), reverse=True)
    out = {
        "aggiornato": datetime.datetime.now(ZoneInfo("Europe/Rome")).isoformat(timespec="minutes"),
        "n": len(frane),
        "frane": frane,
    }
    with open(uscita, "w", encoding="utf-8") as h:
        json.dump(out, h, ensure_ascii=False, separators=(",", ":"))
        h.write("\n")
    print(f"{len(frane)} notizie scritte in {uscita}")


if __name__ == "__main__":
    main()
