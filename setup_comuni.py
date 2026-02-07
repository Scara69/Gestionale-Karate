import json
import urllib.request
import os

def setup():
    url = "https://raw.githubusercontent.com/matteocontrini/comuni-json/master/comuni.json"
    target_path = os.path.join(os.path.dirname(__file__), 'comuni_map.json')
    
    print(f"Scaricamento dati comuni da {url}...")
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode('utf-8'))
            
        mapping = {}
        for item in data:
            code = item.get("codiceCatastale")
            name = item.get("nome")
            if code and name:
                mapping[code] = name.upper()
                
        with open(target_path, 'w', encoding='utf-8') as f:
            json.dump(mapping, f, ensure_ascii=False, indent=2)
            
        print(f"Mappatura salvata con successo in {target_path} ({len(mapping)} comuni).")
    except Exception as e:
        print(f"Errore durante il setup dei comuni: {e}")

if __name__ == "__main__":
    setup()
