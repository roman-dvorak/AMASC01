# Příklady použití AMASC01

Tento adresář obsahuje příklady použití kamery AMASC01.

## Dostupné příklady

### basic_capture.py

Základní příklad zachycení snímku.

```bash
python3 examples/basic_capture.py
```

### automated_capture.py

Příklad automatického snímání s použitím časového plánovače.

```bash
python3 examples/automated_capture.py
```

### night_sky_monitoring.py

Příklad kontinuálního sledování noční oblohy.

```bash
python3 examples/night_sky_monitoring.py
```

### web_viewer.py

Jednoduchý webový prohlížeč pro živé zobrazení.

```bash
python3 examples/web_viewer.py
```

## Jupyter Notebooky

Adresář `notebooks/` obsahuje interaktivní Jupyter notebooky s příklady:

- `01_Getting_Started.ipynb` - Začínáme s AMASC01
- `02_Image_Processing.ipynb` - Zpracování obrazu
- `03_Timelapse_Creation.ipynb` - Vytváření časosběrů
- `04_Data_Analysis.ipynb` - Analýza dat

Pro spuštění notebooků:

```bash
pip3 install jupyter
jupyter notebook examples/notebooks/
```

## Konfigurace

Všechny příklady lze upravit pomocí konfiguračních souborů v adresáři `config/`.

## Poznámky

- Příklady jsou samostatné a lze je spouštět nezávisle
- Každý příklad obsahuje dokumentaci v kódu
- Pro použití příkladů je potřeba nejprve nakonfigurovat kameru
- Některé příklady vyžadují další Python balíčky

## Přizpůsobení

Příklady můžete upravit podle svých potřeb. Doporučujeme:

1. Zkopírovat příklad do vlastního souboru
2. Upravit parametry podle vašeho nastavení
3. Testovat s jednotlivými snímky před spuštěním dlouhodobého sledování
