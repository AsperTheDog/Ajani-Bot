import json
import sqlite3
from datetime import datetime

def restore():
    with open("magic.json", "r") as file:
        data = json.load(file)

    with open("magic_sets.json", "r") as file:
        sets = json.load(file)

    con = sqlite3.connect("../magic.sqlite")
    cur = con.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS sets (
                code VARCHAR NOT NULL PRIMARY KEY,
                arena_code VARCHAR,
                mgto_code VARCHAR,
                name VARCHAR,
                uri VARCHAR,
                scryfall_uri VARCHAR,
                search_uri VARCHAR,
                released_at DATE,
                set_type VARCHAR,
                card_count INTEGER,
                digital BOOLEAN,
                nonfoil_only BOOLEAN,
                foil_only BOOLEAN,
                icon VARCHAR
            )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS cards (
                id VARCHAR NOT NULL PRIMARY KEY,
                oracle_id VARCHAR,
                mtgo_id INTEGER,
                mtgo_foil_id INTEGER,
                tcgplayer_id INTEGER,
                cardmaker_id INTEGER,
                name VARCHAR,
                lang VARCHAR,
                released_at DATE,
                uri VARCHAR,
                scryfall_uri VARCHAR,
                layout VARCHAR,
                highres_image BOOLEAN,
                png_img VARCHAR,
                art_crop VARCHAR,
                mana_cost VARCHAR,
                cmc FLOAT,
                type_line VARCHAR,
                oracle_text VARCHAR,
                card_power VARCHAR,
                toughness VARCHAR,
                reserved BOOLEAN,
                foil BOOLEAN,
                nonfoil BOOLEAN,
                etched BOOLEAN,
                glossy BOOLEAN,
                oversized BOOLEAN,
                promo BOOLEAN,
                reprint BOOLEAN,
                variation BOOLEAN,
                set_code VARCHAR,
                rarity VARCHAR,
                flavor_text VARCHAR,
                card_back_id VARCHAR,
                artist VARCHAR,
                illust_id VARCHAR,
                border_color VARCHAR,
                frame VARCHAR,
                full_art BOOLEAN,
                textless BOOLEAN,
                booster BOOLEAN,
                story_spotlight BOOLEAN,
                edhrec_rank INTEGER,
                penny_rank INTEGER,
                gatherer VARCHAR,
                colors VARCHAR,
                nonfoil_price FLOAT,
                foil_price FLOAT,
                etched_price FLOAT,
                FOREIGN KEY(set_code) REFERENCES sets(code)
            )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS multiverse (
                card_id VARCHAR NOT NULL,
                mult_id INTEGER NOT NULL,
                FOREIGN KEY(card_id) REFERENCES cards(id),
                PRIMARY KEY(card_id, mult_id)
    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS users (
                id INTEGER NOT NULL PRIMARY KEY,
                level INTEGER NOT NULL DEFAULT 0,
                exp INTEGER NOT NULL DEFAULT 0,
                money FLOAT NOT NULL DEFAULT 0,
                job_count INTEGER NOT NULL DEFAULT 0
    )''')

    cur.execute('''CREATE TABLE IF NOT EXISTS holdings (
                user INTEGER NOT NULL,
                card VARCHAR NOT NULL,
                type VARCHAR NOT NULL,
                count INTEGER NOT NULL,
                FOREIGN KEY(user) REFERENCES users(id),
                FOREIGN KEY(card) REFERENCES cards(id),
                PRIMARY KEY(user, card, type)
    )''')

    for st in sets["data"]:
        cur.execute('''INSERT OR IGNORE INTO sets VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
            st.get('code'),
            st.get('arena_code'),
            st.get('mtgo_code'),
            st.get('name'),
            st.get('uri'),
            st.get('scryfall_uri'),
            st.get('search_uri'),
            datetime.strptime(st['released_at'], '%Y-%m-%d').date() if 'released_at' in st else None,
            st.get('set_type'),
            st.get('card_count'),
            st.get('digital'),
            st.get('nonfoil_only'),
            st.get('foil_only'),
            st.get('icon_svg_uri')
        ))

    for c in data:
        colors = "".join(c["colors"] if "colors" in c else [])
        cur.execute('''INSERT OR IGNORE INTO cards VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
            c.get('id'),
            c.get('oracle_id'),
            c.get('mtgo_id'),
            c.get('mtgo_foil_id'),
            c.get('tcgplayer_id'),
            c.get('cardmaker_id'),
            c.get('name'),
            c.get('lang'),
            datetime.strptime(c['released_at'], '%Y-%m-%d').date() if 'released_at' in c else None,
            c.get('uri'),
            c.get('scryfall_uri'),
            c.get('layout'),
            c.get('highres_image'),
            c['image_uris'].get('png') if 'image_uris' in c else None,
            c['image_uris'].get('art_crop') if 'image_uris' in c else None,
            c.get('mana_cost'),
            c.get('cmc'),
            c.get('type_line'),
            c.get('oracle_text'),
            c.get('power'),
            c.get('toughness'),
            c.get('reserved'),
            c.get('foil'),
            c.get('nonfoil'),
            ("etched" in c["finishes"]) if "finishes" in c else False,
            ("glossy" in c["finishes"]) if "finishes" in c else False,
            c.get('oversized'),
            c.get('promo'),
            c.get('reprint'),
            c.get('variation'),
            c.get('set'),
            c.get('rarity'),
            c.get('flavor_text'),
            c.get('card_back_id'),
            c.get('artist'),
            c.get('illustration_id'),
            c.get('border_color'),
            c.get('frame'),
            c.get('full_art'),
            c.get('textless'),
            c.get('booster'),
            c.get('story_spotlight'),
            c.get('edhrec_rank'),
            c.get('penny_rank'),
            c["related_uris"].get("gatherer") if "related_uris" in c else None,
            colors,
            c["prices"].get("usd") if "prices" in c else None,
            c["prices"].get("usd_foil") if "prices" in c else None,
            c["prices"].get("usd_etched") if "prices" in c else None,
        ))

    for c in data:
        for mult_id in c['multiverse_ids']:
            cur.execute('''INSERT OR IGNORE INTO multiverse VALUES (?, ?)''', (
                c.get('id'),
                mult_id
            ))

    con.commit()
    con.close()


if __name__ == "__main__":
    restore()
