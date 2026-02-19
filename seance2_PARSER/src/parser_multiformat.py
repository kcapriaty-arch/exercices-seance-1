import sys
import json
import xml.etree.ElementTree as ET
from pathlib import Path


class ParseError(Exception):
    pass


def read_text(file_path: str) -> str:
    p = Path(file_path)

    if not p.exists():
        raise ParseError(f"❌ Fichier introuvable : {p}")

    content = p.read_text(encoding="utf-8").strip()

    if content == "":
        raise ParseError("❌ Fichier vide.")

    return content


def detect_format(content: str) -> str:
    if content.startswith("{") or content.startswith("["):
        return "json"

    if content.startswith("<"):
        return "xml"

    raise ParseError("❌ Format inconnu : le fichier n'est ni JSON ni XML.")


def parse_json(content: str):
    try:
        return json.loads(content)
    except json.JSONDecodeError as e:
        raise ParseError(f"❌ JSON invalide : {e}") from e


def parse_xml(content: str):
    try:
        root = ET.fromstring(content)
    except ET.ParseError as e:
        raise ParseError(f"❌ XML invalide : {e}") from e

    books = []

    for book in root.findall("book"):
        id_el = book.find("id")
        title_el = book.find("title")
        author_el = book.find("author")

        if id_el is None or title_el is None or author_el is None:
            raise ParseError("❌ XML : champ manquant (id/title/author).")

        if not id_el.text or not title_el.text or not author_el.text:
            raise ParseError("❌ XML : champ vide (id/title/author).")

        books.append({
            "id": int(id_el.text.strip()),
            "title": title_el.text.strip(),
            "author": author_el.text.strip()
        })

    return books


def parse_file(file_path: str):
    content = read_text(file_path)
    fmt = detect_format(content)

    if fmt == "json":
        return parse_json(content)
    else:
        return parse_xml(content)


# ✅ NOUVEAU : sauvegarde des données au format JSON
def save_as_json(data, out_path: str):
    out = Path(out_path)
    out.parent.mkdir(parents=True, exist_ok=True)  # crée output/ si besoin

    with open(out, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    # 1) Vérifier qu'on a bien un fichier en argument
    if len(sys.argv) < 2:
        print("❌ Usage : python src/parser_multiformat.py <input_file> [output_file]")
        print("✅ Exemple : python src/parser_multiformat.py data/data.xml")
        sys.exit(1)

    input_file = sys.argv[1]

    try:
        # 2) Parser le fichier
        result = parse_file(input_file)

        print("\n✅ Fichier:", input_file)
        print("➡️ Type:", type(result).__name__)
        print("➡️ Données:", result)

        # 3) Sauvegarder en JSON standard
        output_file = sys.argv[2] if len(sys.argv) >= 3 else "output/standard.json"
        save_as_json(result, output_file)
        print(f"💾 Sauvegardé dans {output_file}")

        print("💾 Sauvegardé dans output/standard.json")

    except ParseError as e:
        print("\nErreur :", e)
        sys.exit(1)

