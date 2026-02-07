import datetime
import json
import os

# Globale per memorizzare la mappatura dei comuni carichi dal file JSON
_comuni_cache = None

def load_comuni():
    global _comuni_cache
    if _comuni_cache is not None:
        return _comuni_cache
        
    map_path = os.path.join(os.path.dirname(__file__), 'comuni_map.json')
    if os.path.exists(map_path):
        try:
            with open(map_path, 'r', encoding='utf-8') as f:
                _comuni_cache = json.load(f)
            return _comuni_cache
        except Exception as e:
            print(f"Errore nel caricamento dei comuni: {e}")
    
    # Fallback se il file non esiste
    return {
        "H501": "ROMA",
        "F205": "MILANO",
        "L219": "TORINO",
        "F839": "NAPOLI",
        "A944": "BOLOGNA",
        "D612": "FIRENZE",
        "B157": "BRESCIA",
        "H575": "SASSARI",
        "G273": "PALERMO",
        "D969": "GENOVA",
        "G388": "PAVIA"
    }

def get_comune_name(code):
    comuni = load_comuni()
    return comuni.get(code.upper(), code.upper())

def parse_cf(cf):
    """
    Estratto base da Codice Fiscale Italiano:
    - Data di nascita
    - Sesso
    - Comune di nascita (codice catastale)
    """
    if not cf or len(cf) != 16:
        return None

    try:
        # 1. Data di Nascita
        year_part = int(cf[6:8])
        month_char = cf[8].upper()
        day_part = int(cf[9:11])

        # Mappatura Mese
        months = {
            'A': 1, 'B': 2, 'C': 3, 'D': 4, 'E': 5, 'H': 6,
            'L': 7, 'M': 8, 'P': 9, 'R': 10, 'S': 11, 'T': 12
        }
        month = months.get(month_char)
        if not month: return None

        # Sesso e Giorno
        gender = "M"
        if day_part > 40:
            gender = "F"
            day_part -= 40
        
        # Anno (assumiamo 1900 o 2000)
        current_year = datetime.date.today().year % 100
        if year_part <= current_year:
            year = 2000 + year_part
        else:
            year = 1900 + year_part

        birth_date = datetime.date(year, month, day_part)

        # 2. Comune di Nascita (Codice Catastale)
        comune_code = cf[11:15].upper()

        return {
            "birth_date": birth_date,
            "gender": gender,
            "comune_code": comune_code
        }
    except Exception as e:
        print(f"Errore parsing CF {cf}: {e}")
        return None
