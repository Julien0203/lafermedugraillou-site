#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Estampille les ressources avec une empreinte de leur contenu.

Le probleme resolu : les pages demandaient style.css?v=4 et le numero
etait incremente a la main. Il a fini par ne plus l'etre, et les
visiteurs ont continue de recevoir une feuille de style perimee pendant
que le fichier changeait. Une empreinte calculee sur le contenu ne peut
pas se desynchroniser : elle change si et seulement si le fichier change.

Usage : python3 tools/versionner-assets.py [--verifier]
"""
import glob, hashlib, os, re, sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESSOURCES = ['style.css', 'gsap-animations.js']

def empreinte(chemin):
    return hashlib.sha256(open(chemin, 'rb').read()).hexdigest()[:8]

def main():
    os.chdir(RACINE)
    verif = '--verifier' in sys.argv
    marques = {r: empreinte(r) for r in RESSOURCES if os.path.exists(r)}
    pages = sorted(glob.glob('*.html')) + sorted(glob.glob('blog/*.html'))
    perimees, touchees = [], 0

    for p in pages:
        t = open(p, encoding='utf-8').read()
        o = t
        for res, h in marques.items():
            # accepte ?v=<n'importe quoi> ou aucune query
            t = re.sub(rf'({re.escape(res)})(\?v=[^"\']*)?(["\'])', rf'\1?v={h}\3', t)
        if t != o:
            perimees.append(p)
            if not verif:
                open(p, 'w', encoding='utf-8').write(t); touchees += 1

    for r, h in marques.items():
        print(f"  {r:22s} -> v={h}")
    if verif:
        print(f"\n{len(perimees)} page(s) avec une version perimee"
              + (f" : {', '.join(perimees)}" if perimees else ""))
        sys.exit(1 if perimees else 0)
    print(f"\n{touchees} page(s) mise(s) a jour sur {len(pages)}")

if __name__ == '__main__':
    main()
