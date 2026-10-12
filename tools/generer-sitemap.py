#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Genere sitemap.xml a partir de la verite du depot.

Principes :
  - l'URL d'une page est sa balise <link rel="canonical">, jamais une URL
    reconstruite a partir du chemin : si les deux divergeaient, le sitemap
    enverrait Google sur une adresse que la page elle-meme desavoue ;
  - <lastmod> est la date du dernier commit ayant touche le fichier, pas
    la date du jour : une date inventee est un signal faux ;
  - les pages en noindex sont exclues ;
  - ni <changefreq> ni <priority> : Google a confirme les ignorer.

Usage : python3 tools/generer-sitemap.py [--verifier]
        --verifier controle sans ecrire (code de sortie 1 si anomalie).
"""
import glob, html, os, re, subprocess, sys

DOMAINE = "https://www.fermedugraillou.fr"
RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMAGES_MAX = 4          # par page, pour rester lisible
EXCLUS = re.compile(r'(^|/)(404|test|draft|_)')

def lastmod(chemin):
    r = subprocess.run(['git', 'log', '-1', '--format=%cI', '--', chemin],
                       cwd=RACINE, capture_output=True, text=True)
    return r.stdout.strip() or None

def modifie_non_commite(chemin):
    r = subprocess.run(['git', 'status', '--porcelain', '--', chemin],
                       cwd=RACINE, capture_output=True, text=True)
    return bool(r.stdout.strip())

# Ordre de parcours : accueil, pages du site, puis le Carnet. Sans effet sur
# le referencement, mais un sitemap se relit a la main en cas de probleme.
ORDRE = ['index.html', 'histoire.html', 'exploitation.html', 'produits.html',
         'auberge.html', 'contact.html', 'blog/index.html']

def _rang(p):
    return (ORDRE.index(p), '') if p in ORDRE else (len(ORDRE), p)

def pages():
    tous = sorted(glob.glob('*.html')) + sorted(glob.glob('blog/*.html'))
    for p in sorted(tous, key=_rang):
        if EXCLUS.search(p):
            continue
        t = open(p, encoding='utf-8').read()
        rob = re.search(r'<meta name="robots" content="([^"]*)"', t)
        if rob and 'noindex' in rob.group(1).lower():
            continue
        can = re.search(r'rel="canonical" href="([^"]+)"', t)
        if not can:
            print(f"  ! {p} : aucune balise canonical, page ignoree", file=sys.stderr)
            continue
        yield p, can.group(1), t

def images_de(texte):
    """Images reellement affichees sur la page, avec leur alt comme titre.

    On n'y met pas l'og:image : elle sert aux apercus sociaux et n'est pas
    rendue dans la page. Le dedoublonnage se fait sur le nom de base, pour
    qu'une meme photo ne figure pas deux fois sous deux largeurs ou deux
    formats."""
    vues, sortie = set(), []
    for tag in re.findall(r'<img\b[^>]*>', texte, re.S):
        if 'logo' in tag or 'favicon' in tag:
            continue
        src = re.search(r'\ssrc="([^"]+)"', tag)
        alt = re.search(r'\salt="([^"]*)"', tag)
        if not src:
            continue
        chemin = src.group(1).lstrip('./').replace('../', '')
        base = re.sub(r'-\d+\.(webp|jpg|jpeg|png)$', '', os.path.basename(chemin))
        if base in vues:
            continue
        vues.add(base)
        sortie.append((DOMAINE + '/' + chemin, alt.group(1) if alt else None))
        if len(sortie) >= IMAGES_MAX:
            break
    return sortie

def construire():
    anomalies = []
    blocs = []
    for chemin, url, texte in pages():
        if not url.startswith(DOMAINE):
            anomalies.append(f"{chemin} : canonical hors domaine canonique -> {url}")
            continue
        if not url.startswith('https://'):
            anomalies.append(f"{chemin} : canonical non https -> {url}")
            continue
        if modifie_non_commite(chemin):
            anomalies.append(f"{chemin} : modifie mais non commite, la date serait perimee")
        d = lastmod(chemin)
        if not d:
            anomalies.append(f"{chemin} : aucun commit, date introuvable")
            continue
        lignes = [f"    <loc>{html.escape(url)}</loc>", f"    <lastmod>{d}</lastmod>"]
        for u, alt in images_de(texte):
            local = u[len(DOMAINE) + 1:]
            if not os.path.exists(local):
                anomalies.append(f"{chemin} : image absente du depot -> {local}")
                continue
            lignes.append("    <image:image>")
            lignes.append(f"      <image:loc>{html.escape(u)}</image:loc>")
            if alt:
                lignes.append(f"      <image:title>{html.escape(alt)}</image:title>")
            lignes.append("    </image:image>")
        blocs.append("  <url>\n" + "\n".join(lignes) + "\n  </url>")

    xml = ('<?xml version="1.0" encoding="UTF-8"?>\n'
           '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
           '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n\n'
           + "\n\n".join(blocs) + "\n\n</urlset>\n")
    return xml, anomalies, len(blocs)

if __name__ == '__main__':
    os.chdir(RACINE)
    xml, anomalies, n = construire()
    for a in anomalies:
        print("  ANOMALIE :", a, file=sys.stderr)
    if '--verifier' in sys.argv:
        actuel = open('sitemap.xml', encoding='utf-8').read() if os.path.exists('sitemap.xml') else ''
        a_jour = (actuel == xml)
        print(f"{n} URL — sitemap {'a jour' if a_jour else 'PERIME, relancer sans --verifier'}")
        sys.exit(0 if (a_jour and not anomalies) else 1)
    open('sitemap.xml', 'w', encoding='utf-8').write(xml)
    print(f"sitemap.xml ecrit : {n} URL, {xml.count('<image:image>')} images")
    sys.exit(1 if anomalies else 0)
