# Přispívání do projektu AMASC01

Děkujeme za váš zájem o přispění do projektu AMASC01! Tato příručka vás provede procesem přispívání.

## Jak přispět

### Hlášení chyb

Pokud najdete chybu:

1. Zkontrolujte [Issues](https://github.com/roman-dvorak/AMASC01/issues), zda již není nahlášena
2. Pokud ne, vytvořte nový issue s:
   - Popisným názvem
   - Detailním popisem problému
   - Kroky pro reprodukci
   - Očekávaným a skutečným chováním
   - Informacemi o prostředí (OS, Python verze, atd.)

### Návrhy na vylepšení

Pro návrh nové funkce:

1. Otevřete issue s označením "enhancement"
2. Popište navrhovanou funkcionalitu
3. Vysvětlete, proč by byla užitečná
4. Případně navrhněte implementaci

### Pull Requesty

1. **Fork** repozitáře
2. **Clone** vašeho forku:
   ```bash
   git clone https://github.com/VASE_JMENO/AMASC01.git
   cd AMASC01
   ```

3. Vytvořte **novou větev** pro vaši změnu:
   ```bash
   git checkout -b feature/moje-nova-funkce
   ```

4. Proveďte změny a **commitněte**:
   ```bash
   git add .
   git commit -m "Přidání nové funkce XYZ"
   ```

5. **Pushněte** změny do vašeho forku:
   ```bash
   git push origin feature/moje-nova-funkce
   ```

6. Otevřete **Pull Request** na GitHubu

## Coding Standards

### Python

- Používejte Python 3.6+
- Dodržujte PEP 8
- Přidejte docstringy ke všem funkcím a třídám
- Pište jasné a srozumitelné komentáře
- Přidejte testy pro novou funkcionalitu

Příklad:

```python
def capture_image(exposure, gain):
    """
    Capture image from camera.
    
    Args:
        exposure (float): Exposure time in seconds
        gain (int): Gain value (0-100)
    
    Returns:
        numpy.ndarray: Captured image
    
    Raises:
        CameraError: If capture fails
    """
    # Implementation
    pass
```

### Dokumentace

- Dokumentace je v češtině
- Aktualizujte dokumentaci při změně funkcionality
- Používejte Markdown pro formátování
- Přidejte příklady použití

### Commity

- Pište srozumitelné commit messages
- Používejte české nebo anglické názvy
- První řádek: stručný popis (max 50 znaků)
- Pokud je potřeba, přidejte detailnější popis

Příklady dobrých commit messages:
```
Přidání podpory pro FITS formát
Oprava chyby v zpracování obrazu
Aktualizace dokumentace instalace
```

## Testování

Před odesláním pull requestu:

1. Zkontrolujte, že kód funguje:
   ```bash
   python3 scripts/test_camera.py
   ```

2. Otestujte vaše změny manuálně

3. Pokud přidáváte novou funkcionalitu, přidejte testy

## Review proces

1. Maintainer zkontroluje váš pull request
2. Může požádat o změny nebo vylepšení
3. Po schválení bude změna začleněna do main větve

## Otázky?

Pokud máte otázky ohledně přispívání:

- Otevřete issue s označením "question"
- Kontaktujte maintainera
- Navštivte [FAQ](docs/faq.md)

## Kodex chování

- Buďte přátelští a respektující
- Přijímejte konstruktivní kritiku
- Zaměřte se na to, co je nejlepší pro komunitu
- Pomozte vytvořit otevřené a přátelské prostředí

Děkujeme za vaše příspěvky! 🎉
