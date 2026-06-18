#!/usr/bin/env python3
"""
migrate_images.py — Rivera / patologieortopediche.com
Copia la cartella uploads di WordPress nel progetto Astro
e aggiorna tutti i path nelle pagine .md e .astro.

Uso:
  python3 migrate_images.py \
    --uploads /percorso/alla/cartella/uploads \
    --astro   /percorso/al/progetto/patologieortopediche

Esempio:
  python3 migrate_images.py \
    --uploads ~/Desktop/wp-uploads \
    --astro   ~/Projects/patologieortopediche
"""

import argparse
import shutil
import re
from pathlib import Path

# ── Argomenti ─────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="Migra le immagini WP → Astro")
parser.add_argument("--uploads", required=True,
                    help="Percorso alla cartella uploads scaricata via FTP")
parser.add_argument("--astro", required=True,
                    help="Percorso root del progetto Astro")
parser.add_argument("--dry-run", action="store_true",
                    help="Simula senza copiare né modificare file")
args = parser.parse_args()

UPLOADS_DIR = Path(args.uploads).expanduser().resolve()
ASTRO_DIR   = Path(args.astro).expanduser().resolve()
DRY_RUN     = args.dry_run

# Destinazione immagini nel progetto Astro
IMG_DEST = ASTRO_DIR / "public" / "img"

# Pattern URL vecchio (tutto ciò che viene dopo /uploads/)
OLD_BASE = "https://www.patologieortopediche.com/wp-content/uploads/"
NEW_BASE = "/img/"

# Estensioni immagine da copiare
IMG_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"}

# File da aggiornare nel progetto Astro
FILE_PATTERNS = ["src/**/*.md", "src/**/*.astro"]

# ── Validazione input ──────────────────────────────────────────────────────────
if not UPLOADS_DIR.exists():
    print(f"❌ Cartella uploads non trovata: {UPLOADS_DIR}")
    exit(1)

if not ASTRO_DIR.exists():
    print(f"❌ Progetto Astro non trovato: {ASTRO_DIR}")
    exit(1)

print(f"\n{'🔍 DRY RUN — nessun file verrà modificato' if DRY_RUN else '🚀 Migrazione immagini'}")
print(f"   Uploads: {UPLOADS_DIR}")
print(f"   Astro:   {ASTRO_DIR}")
print(f"   Dest:    {IMG_DEST}\n")

# ── 1. Copia immagini ──────────────────────────────────────────────────────────
print("── Step 1: Copia immagini ────────────────────────────────────────────")

copied = 0
skipped = 0
errors = []

for src_file in UPLOADS_DIR.rglob("*"):
    if not src_file.is_file():
        continue
    if src_file.suffix.lower() not in IMG_EXTENSIONS:
        continue

    # Percorso relativo rispetto alla cartella uploads
    rel_path = src_file.relative_to(UPLOADS_DIR)
    dest_file = IMG_DEST / rel_path

    if dest_file.exists():
        skipped += 1
        continue

    if DRY_RUN:
        print(f"   [dry] copierebbe → {rel_path}")
        copied += 1
        continue

    dest_file.parent.mkdir(parents=True, exist_ok=True)
    try:
        shutil.copy2(src_file, dest_file)
        copied += 1
    except Exception as e:
        errors.append(f"{src_file}: {e}")

print(f"   ✅ Copiate: {copied}  |  Già presenti: {skipped}  |  Errori: {len(errors)}")
for e in errors:
    print(f"   ❌ {e}")

# ── 2. Aggiorna path nei file sorgente ────────────────────────────────────────
print("\n── Step 2: Aggiorna path nei file sorgente ───────────────────────────")

pattern_url    = re.compile(re.escape(OLD_BASE) + r"([^\s\"'<>)]+)")
pattern_wp_src = re.compile(r'(/wp-content/uploads/)([^\s\"\'<>)]+)')

files_updated = 0
replacements_total = 0

for glob_pattern in FILE_PATTERNS:
    for filepath in ASTRO_DIR.glob(glob_pattern):
        original = filepath.read_text(encoding="utf-8")
        updated  = original

        # Sostituisce URL assoluti WP
        def replace_abs(m):
            return NEW_BASE + m.group(1)
        updated = pattern_url.sub(replace_abs, updated)

        # Sostituisce path relativi /wp-content/uploads/ residui
        def replace_rel(m):
            return NEW_BASE + m.group(2)
        updated = pattern_wp_src.sub(replace_rel, updated)

        if updated != original:
            n = len(re.findall(re.escape(NEW_BASE), updated)) - \
                len(re.findall(re.escape(NEW_BASE), original))
            count = original.count(OLD_BASE) + original.count("/wp-content/uploads/")
            replacements_total += count

            rel = filepath.relative_to(ASTRO_DIR)
            print(f"   📝 {rel}  ({count} sostituzioni)")

            if not DRY_RUN:
                filepath.write_text(updated, encoding="utf-8")
            files_updated += 1

print(f"\n   ✅ File aggiornati: {files_updated}  |  Sostituzioni totali: {replacements_total}")

# ── 3. Genera mappa immagini mancanti ─────────────────────────────────────────
print("\n── Step 3: Verifica immagini mancanti ────────────────────────────────")

missing = []
for glob_pattern in FILE_PATTERNS:
    for filepath in ASTRO_DIR.glob(glob_pattern):
        content = filepath.read_text(encoding="utf-8")
        refs = re.findall(r'/img/([^\s"\'<>)]+)', content)
        for ref in refs:
            img_path = IMG_DEST / ref
            if not img_path.exists():
                missing.append((filepath.relative_to(ASTRO_DIR), ref))

if missing:
    print(f"   ⚠️  {len(missing)} immagini referenziate ma non trovate:")
    for src, ref in missing:
        print(f"      {src}: /img/{ref}")
else:
    print("   ✅ Tutte le immagini referenziate sono presenti")

# ── Riepilogo finale ───────────────────────────────────────────────────────────
print(f"""
{'─'*60}
{'DRY RUN completato — riesegui senza --dry-run per applicare' if DRY_RUN else 'Migrazione completata ✅'}

Prossimi passi:
  1. Verifica le immagini in {IMG_DEST}
  2. npm run dev — controlla che le immagini appaiano correttamente
  3. Controlla i post con immagini "giganti" (slide embedded):
       - La protesi di ginocchio nel paziente giovane
       - American Academy Annual Meeting 2014
       - Protesi di ginocchio dolorosa
     Questi non hanno immagini nel Markdown ma probabilmente
     avevano PDF/slide embedded — da gestire manualmente.
{'─'*60}
""")
