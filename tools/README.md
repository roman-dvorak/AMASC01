# Nástroje AMASC01

Tento adresář obsahuje nástroje pro konfiguraci a údržbu kamery AMASC01.

## Dostupné nástroje

### setup_system.sh

Bash skript pro nastavení systému a instalaci závislostí.

```bash
sudo bash tools/setup_system.sh
```

Tento skript:
- Instaluje potřebné systémové balíčky
- Nastavuje udev pravidla pro USB připojení
- Vytváří adresářovou strukturu pro data
- Konfiguruje systemd službu (volitelné)

### calibrate.py

Nástroj pro kalibraci kamery - vytváření dark a flat snímků.

```bash
# Vytvoření dark frame
python3 tools/calibrate.py --dark -e 10 -n 10 -o calibration/dark.fits

# Vytvoření flat frame
python3 tools/calibrate.py --flat -n 10 -o calibration/flat.fits
```

### monitor.py

Monitorovací nástroj pro sledování stavu kamery a systému.

```bash
# Spustit monitoring
python3 tools/monitor.py

# S webovým rozhraním
python3 tools/monitor.py --web --port 8080
```

### backup.sh

Zálohovací skript pro data a konfiguraci.

```bash
# Záloha do lokálního adresáře
bash tools/backup.sh /backup/amasc01

# Záloha na vzdálený server
bash tools/backup.sh user@server:/backup/amasc01
```

## Použití

Většina nástrojů vyžaduje root oprávnění pro systémové úpravy. Použijte `sudo` kde je to potřeba.

```bash
# Udělat nástroje spustitelné
chmod +x tools/*.sh
chmod +x tools/*.py
```

## Poznámky pro správu systému

### Systemd služba

Pro automatické spouštění kamery při startu systému můžete vytvořit systemd službu:

```bash
sudo cp tools/amasc01.service /etc/systemd/system/
sudo systemctl enable amasc01
sudo systemctl start amasc01
```

### Automatické aktualizace

Pro pravidelnou kontrolu aktualizací:

```bash
# Přidat do crontab
0 2 * * * cd /path/to/AMASC01 && git pull
```

### Monitoring logu

Sledování logů kamery:

```bash
tail -f /var/log/amasc01/camera.log
```

## Plánované nástroje

Následující nástroje jsou v plánu pro budoucí verze:

- **diagnostic.py** - Diagnostický nástroj pro řešení problémů
- **update.sh** - Nástroj pro aktualizaci software
- **export.py** - Export dat do různých formátů
- **analyze.py** - Analýza kvality snímků
