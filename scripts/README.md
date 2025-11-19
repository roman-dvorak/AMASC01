# Skripty AMASC01

Tento adresář obsahuje pomocné skripty pro práci s kamerou AMASC01.

## Dostupné skripty

### test_camera.py

Testuje připojení kamery a základní funkčnost.

```bash
python3 scripts/test_camera.py
```

### capture.py

Zachytává snímky z kamery.

```bash
# Jeden snímek s výchozí konfigurací
python3 scripts/capture.py

# Použití vlastní konfigurace
python3 scripts/capture.py -c config/camera_config.yaml

# Přepsání parametrů expozice a zisku
python3 scripts/capture.py -e 15 -g 60

# Kontinuální snímání
python3 scripts/capture.py --continuous --interval 120

# Uložení do konkrétního souboru
python3 scripts/capture.py -o /path/to/output.fits
```

### process_images.py

Zpracovává zachycené snímky.

```bash
# Zpracování jednoho snímku
python3 scripts/process_images.py image.fits -o processed.fits

# Dávkové zpracování
python3 scripts/process_images.py input_dir/ -o output_dir/ --batch

# S dark frame odečtením
python3 scripts/process_images.py image.fits --dark dark.fits

# S flat field korekcí
python3 scripts/process_images.py image.fits --flat flat.fits

# Automatické roztažení kontrastu
python3 scripts/process_images.py image.fits --stretch

# Konverze formátu
python3 scripts/process_images.py image.fits --format jpg
```

### create_timelapse.py

Vytváří časosběrná videa ze série snímků.

```bash
# Základní použití
python3 scripts/create_timelapse.py images/ -o timelapse.mp4

# Vlastní FPS
python3 scripts/create_timelapse.py images/ -o timelapse.mp4 --fps 60

# Vlastní rozlišení
python3 scripts/create_timelapse.py images/ -o timelapse.mp4 --width 1920 --height 1080
```

## Instalace závislostí

Všechny skripty vyžadují Python 3.6 nebo novější. Nainstalujte závislosti:

```bash
pip3 install -r requirements.txt
```

Nebo manuálně:

```bash
pip3 install numpy pyyaml astropy opencv-python
```

## Poznámky

- Skripty jsou označeny jako spustitelné (`chmod +x`)
- Na Linuxu můžete skripty spouštět přímo: `./scripts/capture.py`
- Na Windows používejte: `python scripts\capture.py`
- Všechny skripty mají nápovědu dostupnou přes `--help`

## Vývoj

Tyto skripty jsou šablony pro budoucí implementaci. Aktuální verze:
- Načítají a validují konfiguraci
- Zpracovávají argumenty příkazové řádky
- Obsahují komentovanou strukturu pro budoucí funkčnost

Pro přidání skutečné funkčnosti kamery bude potřeba:
1. Implementovat ovladač kamery
2. Připojit zpracování obrazu
3. Přidat podporu FITS a dalších formátů
