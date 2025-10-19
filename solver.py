import collections  # Pentru Counter (calcul frecvență litere)

# Funcție pentru compararea a două litere (cu suport complet pentru diacritice)
def same_letter(guess, actual):
    #Compară două litere în mod case-insensitive, ținând cont și de diacritice
    return guess.lower() == actual.lower()

# Funcție pentru citirea jocurilor din fișier .txt
def load_games(filename):
    games = []
    invalid_lines = []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            for line_no, line in enumerate(f, 1):
                parts = line.strip().split(',')
                if len(parts) != 3:
                    invalid_lines.append((line_no, line.strip(), "Număr incorect de câmpuri"))
                    continue
                game_id, pattern_initial, cuvant_tinta = parts
                pattern_initial = pattern_initial.strip()
                cuvant_tinta = cuvant_tinta.strip()
                if len(pattern_initial) != len(cuvant_tinta):
                    invalid_lines.append((line_no, line.strip(), "Lungimi neconcordante"))
                    continue
                games.append({
                    "game_id": game_id.strip(),
                    "pattern_initial": pattern_initial,
                    "cuvant_tinta": cuvant_tinta
                })
        return games, invalid_lines
    except FileNotFoundError:
        print(f"Eroare: fișierul '{filename}' nu există.")
        return [], []

# Funcție pentru filtrarea candidaților pe baza pattern-ului și literelor ghicite
def filter_candidates(candidates, pattern, corecte, gresite):
    filtered = []
    for word in candidates:
        match = True
        for i, ch in enumerate(pattern):
            if ch != '*' and word[i].lower() != ch.lower():
                match = False
                break
            if ch == '*' and word[i].lower() in corecte:
                match = False
                break
        if match and all(g not in word.lower() for g in gresite):
            filtered.append(word)
    return filtered

# Funcție principală care rezolvă un joc
def solve_game(pattern_initial, cuvant_tinta, wordlist):
    pattern = list(pattern_initial)
    corecte = set(ch.lower() for ch in pattern if ch != '*')
    gresite = set()
    secventa_incercari = []
    incercari = 0

    # Construim lista inițială de candidați
    candidates = [w for w in wordlist if len(w) == len(pattern)]

    # Bucla principală
    while '*' in pattern:
        candidates = filter_candidates(candidates, pattern, corecte, gresite)
        if not candidates:
            break

        # Calculăm frecvența literelor necunoscute
        counter = collections.Counter()
        for word in candidates:
            for i, ch in enumerate(word):
                if pattern[i] == '*':
                    counter[ch.lower()] += 1

        if not counter:
            break
        lit = counter.most_common(1)[0][0]

        incercari += 1
        secventa_incercari.append(lit)
        gasit = False

        for i, ch in enumerate(cuvant_tinta):
            if same_letter(lit, ch):
                pattern[i] = cuvant_tinta[i]
                gasit = True

        if gasit:
            corecte.add(lit)
        else:
            gresite.add(lit)

    cuvant_gasit = ''.join(pattern)
    status = "OK" if cuvant_gasit.lower() == cuvant_tinta.lower() else "FAIL"
    return {
        "total_incercari": incercari,
        "cuvant_gasit": cuvant_gasit,
        "status": status,
        "secventa_incercari": ' '.join(secventa_incercari)
    }

# Funcția principală
def main():
    input_file = "jocuri.txt"
    output_file = "rezultate.txt"

    games, invalid_lines = load_games(input_file)

    if invalid_lines:
        print("Linii invalide găsite:")
        for line_no, line, motiv in invalid_lines:
            print(f"Linia {line_no}: '{line}' -> {motiv}")

    wordlist = [game["cuvant_tinta"] for game in games]

    rezultate = []
    total_incercari = 0

    for game in games:
        result = solve_game(game["pattern_initial"], game["cuvant_tinta"], wordlist)
        row = f"{game['game_id']},{result['total_incercari']},{result['cuvant_gasit']},{result['status']},{result['secventa_incercari']}"
        rezultate.append(row)
        total_incercari += result['total_incercari']

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("game_id,total_incercari,cuvant_gasit,status,secventa_incercari\n")
        for row in rezultate:
            f.write(row + "\n")

    print(f"\nRezultatele au fost salvate în '{output_file}'.")
    print(f"Suma totală a încercărilor: {total_incercari}")
    if total_incercari > 1200:
        print("⚠️ Atenție: suma încercărilor depășește 1200!")

if __name__ == "__main__":
    main()
