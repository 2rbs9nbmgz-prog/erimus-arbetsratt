#!/usr/bin/env python3
"""
Sökverktyg för svensk arbetsrättslig rättsfallsdatabas
"""
import sqlite3
import sys
from datetime import datetime

class RattsfallDB:
    def __init__(self, db_path='arbetsratt_rattsfall.db'):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        
    def sok_rattsfall(self, sokord=None, lagomrade=None, tema=None, ar=None):
        """Sök rättsfall baserat på olika kriterier"""
        query = """
            SELECT DISTINCT r.* 
            FROM rattsfall r
            LEFT JOIN rattsfall_teman rt ON r.id = rt.rattsfall_id
            LEFT JOIN teman t ON rt.tema_id = t.id
            WHERE 1=1
        """
        params = []
        
        if sokord:
            query += """ AND (r.rubrik LIKE ? OR r.sammanfattning LIKE ? 
                            OR r.nyckelord LIKE ?)"""
            sokterm = f'%{sokord}%'
            params.extend([sokterm, sokterm, sokterm])
        
        if lagomrade:
            query += " AND r.lagomrade = ?"
            params.append(lagomrade)
        
        if tema:
            query += " AND t.tema LIKE ?"
            params.append(f'%{tema}%')
        
        if ar:
            query += " AND strftime('%Y', r.avgorande_datum) = ?"
            params.append(str(ar))
        
        query += " ORDER BY r.avgorande_datum DESC"
        
        cursor = self.conn.execute(query, params)
        return cursor.fetchall()
    
    def hamta_rattsfall(self, malnummer):
        """Hämta ett specifikt rättsfall med fullständig information"""
        cursor = self.conn.execute("""
            SELECT * FROM rattsfall WHERE malnummer = ?
        """, (malnummer,))
        rattsfall = cursor.fetchone()
        
        if not rattsfall:
            return None
        
        # Hämta lagrum
        cursor = self.conn.execute("""
            SELECT lag, paragraf, stycke FROM lagrum 
            WHERE rattsfall_id = ?
        """, (rattsfall['id'],))
        lagrum = cursor.fetchall()
        
        # Hämta teman
        cursor = self.conn.execute("""
            SELECT t.tema, t.beskrivning FROM teman t
            JOIN rattsfall_teman rt ON t.id = rt.tema_id
            WHERE rt.rattsfall_id = ?
        """, (rattsfall['id'],))
        teman = cursor.fetchall()
        
        return {
            'rattsfall': rattsfall,
            'lagrum': lagrum,
            'teman': teman
        }
    
    def lista_teman(self):
        """Lista alla tillgängliga teman"""
        cursor = self.conn.execute("""
            SELECT t.tema, t.beskrivning, COUNT(rt.rattsfall_id) as antal
            FROM teman t
            LEFT JOIN rattsfall_teman rt ON t.id = rt.tema_id
            GROUP BY t.id
            ORDER BY t.tema
        """)
        return cursor.fetchall()
    
    def statistik(self):
        """Få statistik över databasen"""
        stats = {}
        
        cursor = self.conn.execute("SELECT COUNT(*) as antal FROM rattsfall")
        stats['totalt_rattsfall'] = cursor.fetchone()['antal']
        
        cursor = self.conn.execute("""
            SELECT lagomrade, COUNT(*) as antal 
            FROM rattsfall 
            GROUP BY lagomrade
        """)
        stats['per_lagomrade'] = cursor.fetchall()
        
        cursor = self.conn.execute("""
            SELECT domstol, COUNT(*) as antal 
            FROM rattsfall 
            GROUP BY domstol
        """)
        stats['per_domstol'] = cursor.fetchall()
        
        return stats
    
    def lagg_till_rattsfall(self, data):
        """Lägg till nytt rättsfall i databasen"""
        cursor = self.conn.execute("""
            INSERT INTO rattsfall 
            (malnummer, domstol, avgorande_datum, rubrik, lagomrade, 
             huvudsaklig_lag, sammanfattning, utfall, nyckelord, fulltext_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data['malnummer'],
            data['domstol'],
            data['avgorande_datum'],
            data['rubrik'],
            data['lagomrade'],
            data.get('huvudsaklig_lag'),
            data.get('sammanfattning'),
            data.get('utfall'),
            data.get('nyckelord'),
            data.get('fulltext_url')
        ))
        self.conn.commit()
        return cursor.lastrowid
    
    def close(self):
        self.conn.close()


def skriv_ut_rattsfall(rattsfall):
    """Formatera och skriv ut ett rättsfall"""
    print(f"\n{'='*80}")
    print(f"Målnummer: {rattsfall['malnummer']}")
    print(f"Domstol: {rattsfall['domstol']}")
    print(f"Datum: {rattsfall['avgorande_datum']}")
    print(f"\nRubrik: {rattsfall['rubrik']}")
    print(f"Lagområde: {rattsfall['lagomrade']}")
    if rattsfall['huvudsaklig_lag']:
        print(f"Huvudsaklig lag: {rattsfall['huvudsaklig_lag']}")
    print(f"\nSammanfattning:\n{rattsfall['sammanfattning']}")
    print(f"\nUtfall: {rattsfall['utfall']}")
    if rattsfall['nyckelord']:
        print(f"Nyckelord: {rattsfall['nyckelord']}")
    if rattsfall['fulltext_url']:
        print(f"URL: {rattsfall['fulltext_url']}")
    print(f"{'='*80}\n")


def main():
    db = RattsfallDB()
    
    if len(sys.argv) < 2:
        print("Användning:")
        print("  python sok_rattsfall.py sok <sökord>")
        print("  python sok_rattsfall.py tema <tema>")
        print("  python sok_rattsfall.py visa <målnummer>")
        print("  python sok_rattsfall.py teman")
        print("  python sok_rattsfall.py statistik")
        sys.exit(1)
    
    kommando = sys.argv[1]
    
    if kommando == 'sok' and len(sys.argv) > 2:
        sokord = ' '.join(sys.argv[2:])
        resultat = db.sok_rattsfall(sokord=sokord)
        print(f"\nHittade {len(resultat)} rättsfall:")
        for r in resultat:
            skriv_ut_rattsfall(r)
    
    elif kommando == 'tema' and len(sys.argv) > 2:
        tema = ' '.join(sys.argv[2:])
        resultat = db.sok_rattsfall(tema=tema)
        print(f"\nHittade {len(resultat)} rättsfall för tema '{tema}':")
        for r in resultat:
            skriv_ut_rattsfall(r)
    
    elif kommando == 'visa' and len(sys.argv) > 2:
        malnummer = sys.argv[2]
        data = db.hamta_rattsfall(malnummer)
        if data:
            skriv_ut_rattsfall(data['rattsfall'])
            if data['lagrum']:
                print("Relevanta lagrum:")
                for l in data['lagrum']:
                    paragraf_text = f"§ {l['paragraf']}"
                    if l['stycke']:
                        paragraf_text += f" st. {l['stycke']}"
                    print(f"  - {l['lag']} {paragraf_text}")
            if data['teman']:
                print("\nTeman:")
                for t in data['teman']:
                    print(f"  - {t['tema']}: {t['beskrivning']}")
        else:
            print(f"Rättsfall {malnummer} hittades inte")
    
    elif kommando == 'teman':
        teman = db.lista_teman()
        print("\nTillgängliga teman:")
        for t in teman:
            print(f"  - {t['tema']}: {t['beskrivning']} ({t['antal']} rättsfall)")
    
    elif kommando == 'statistik':
        stats = db.statistik()
        print(f"\nStatistik för databasen:")
        print(f"Totalt antal rättsfall: {stats['totalt_rattsfall']}")
        print("\nPer lagområde:")
        for s in stats['per_lagomrade']:
            print(f"  - {s['lagomrade']}: {s['antal']}")
        print("\nPer domstol:")
        for s in stats['per_domstol']:
            print(f"  - {s['domstol']}: {s['antal']}")
    
    else:
        print("Okänt kommando")
    
    db.close()


if __name__ == '__main__':
    main()
