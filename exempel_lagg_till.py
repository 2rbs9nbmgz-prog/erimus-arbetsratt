#!/usr/bin/env python3
"""
Exempel på hur man lägger till nya rättsfall i databasen
"""
import sqlite3
from datetime import datetime

def lagg_till_exempelfall():
    """Exempel på hur man lägger till ett nytt rättsfall"""
    
    conn = sqlite3.connect('arbetsratt_rattsfall.db')
    cursor = conn.cursor()
    
    # Exempel 1: Ett nytt LAS-fall
    print("Lägger till nytt LAS-fall...")
    cursor.execute("""
        INSERT INTO rattsfall 
        (malnummer, domstol, avgorande_datum, rubrik, lagomrade, 
         huvudsaklig_lag, sammanfattning, utfall, nyckelord, fulltext_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        'AD 2022 nr 30',
        'Arbetsdomstolen',
        '2022-05-18',
        'Uppsägning - alkoholmissbruk',
        'LAS',
        'Lag om anställningskydd (1982:80)',
        'Arbetsdomstolen prövade om arbetsgivarens uppsägning av arbetstagare med alkoholproblem var sakligt grundad. Domstolen fann att arbetsgivaren först skulle ha erbjudit rehabilitering och stöd innan uppsägning kunde bli aktuell.',
        'Uppsägningen ogiltigförklarades',
        'uppsägning, personliga skäl, alkoholmissbruk, rehabilitering, omplacering',
        'https://lagen.nu/dom/ad/2022:30'
    ))
    rattsfall_id = cursor.lastrowid
    
    # Lägg till lagrum för detta fall
    cursor.execute("""
        INSERT INTO lagrum (rattsfall_id, lag, paragraf, stycke)
        VALUES (?, ?, ?, ?)
    """, (rattsfall_id, 'Lag om anställningskydd (1982:80)', '7', '1'))
    
    # Koppla till tema "Personliga skäl"
    cursor.execute("""
        INSERT INTO rattsfall_teman (rattsfall_id, tema_id)
        SELECT ?, id FROM teman WHERE tema = 'Personliga skäl'
    """, (rattsfall_id,))
    
    print(f"Lagt till rättsfall med ID: {rattsfall_id}")
    
    # Exempel 2: Ett diskrimineringsfall
    print("\nLägger till nytt diskrimineringsfall...")
    cursor.execute("""
        INSERT INTO rattsfall 
        (malnummer, domstol, avgorande_datum, rubrik, lagomrade, 
         huvudsaklig_lag, sammanfattning, utfall, nyckelord, fulltext_url)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        'AD 2022 nr 45',
        'Arbetsdomstolen',
        '2022-09-21',
        'Diskriminering på grund av religion',
        'Diskrimineringslagen',
        'Diskrimineringslag (2008:567)',
        'Arbetstagare nekades ledighet för religiös högtid trots att detta var möjligt att ordna. Arbetsdomstolen fann att detta utgjorde diskriminering på grund av religion.',
        'Diskriminering fastställdes, 75 000 kr i ersättning',
        'religionsdiskriminering, ledighet, religiös högtid, skäliga åtgärder',
        'https://lagen.nu/dom/ad/2022:45'
    ))
    rattsfall_id2 = cursor.lastrowid
    
    # Lägg till lagrum
    cursor.execute("""
        INSERT INTO lagrum (rattsfall_id, lag, paragraf, stycke)
        VALUES (?, ?, ?, ?)
    """, (rattsfall_id2, 'Diskrimineringslag (2008:567)', '1 kap. 4', None))
    
    cursor.execute("""
        INSERT INTO lagrum (rattsfall_id, lag, paragraf, stycke)
        VALUES (?, ?, ?, ?)
    """, (rattsfall_id2, 'Diskrimineringslag (2008:567)', '2 kap. 1', None))
    
    print(f"Lagt till rättsfall med ID: {rattsfall_id2}")
    
    conn.commit()
    conn.close()
    
    print("\n✓ Båda rättsfallen har lagts till i databasen!")


def lagg_till_tema():
    """Exempel på hur man lägger till ett nytt tema"""
    
    conn = sqlite3.connect('arbetsratt_rattsfall.db')
    cursor = conn.cursor()
    
    # Lägg till nytt tema
    cursor.execute("""
        INSERT OR IGNORE INTO teman (tema, beskrivning)
        VALUES (?, ?)
    """, (
        'Diskriminering religion',
        'Diskriminering på grund av religion eller annan trosuppfattning'
    ))
    
    if cursor.rowcount > 0:
        print("Nytt tema 'Diskriminering religion' har lagts till")
    else:
        print("Temat finns redan i databasen")
    
    conn.commit()
    conn.close()


def visa_senaste_rattsfallen():
    """Visa de 5 senaste rättsfallen i databasen"""
    
    conn = sqlite3.connect('arbetsratt_rattsfall.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT malnummer, rubrik, avgorande_datum, lagomrade
        FROM rattsfall
        ORDER BY avgorande_datum DESC
        LIMIT 5
    """)
    
    print("\nDe 5 senaste rättsfallen:")
    print("-" * 80)
    for row in cursor.fetchall():
        print(f"{row['malnummer']:20} {row['avgorande_datum']:12} {row['lagomrade']:20}")
        print(f"  {row['rubrik']}")
        print()
    
    conn.close()


if __name__ == '__main__':
    print("=" * 80)
    print("EXEMPEL: Lägga till nya rättsfall i databasen")
    print("=" * 80)
    
    # Lägg till nytt tema först
    lagg_till_tema()
    
    # Lägg till exempel-rättsfall
    lagg_till_exempelfall()
    
    # Visa resultat
    visa_senaste_rattsfallen()
    
    print("\nTips: Använd 'python sok_rattsfall.py statistik' för att se uppdaterad statistik")
