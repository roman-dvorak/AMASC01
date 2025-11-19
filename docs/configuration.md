# Konfigurace AMASC01

Tento dokument popisuje možnosti konfigurace kamery AMASC01.

## Konfigurační soubor

Hlavní konfigurační soubor je umístěn v `config/camera_config.yaml`. Příklad konfigurace naleznete v `config/camera_config.example.yaml`.

## Základní nastavení

### Parametry kamery

```yaml
camera:
  # Expozice v sekundách
  exposure: 10.0
  
  # Zisk (gain) - 0-100
  gain: 50
  
  # Rozlišení snímku
  resolution:
    width: 1920
    height: 1080
  
  # Formát výstupu
  format: "fits"  # fits, jpg, png
```

### Ukládání snímků

```yaml
storage:
  # Cesta pro ukládání snímků
  output_path: "/var/amasc01/images"
  
  # Vzor jména souboru
  filename_pattern: "amasc01_%Y%m%d_%H%M%S"
  
  # Automatické vytváření podadresářů podle data
  organize_by_date: true
```

### Automatické snímání

```yaml
capture:
  # Automatické snímání
  auto_capture: true
  
  # Interval mezi snímky (v sekundách)
  interval: 60
  
  # Snímání pouze v noci
  night_only: true
  
  # Geografická poloha pro výpočet soumraku
  location:
    latitude: 50.0755
    longitude: 14.4378
    elevation: 200
```

## Pokročilé nastavení

### Kalibrace

Pokyny pro kalibraci kamery naleznete v sekci [Kalibrace](calibration.md).

### Zpracování obrazu

```yaml
processing:
  # Automatické odečtení dark frame
  subtract_dark: true
  dark_frame_path: "/var/amasc01/calibration/dark.fits"
  
  # Flat field korekce
  flat_field: true
  flat_frame_path: "/var/amasc01/calibration/flat.fits"
  
  # Úprava jasu a kontrastu
  auto_stretch: true
```

### Síťové nastavení

```yaml
network:
  # Aktivovat webové rozhraní
  web_interface: true
  port: 8080
  
  # Vzdálený přístup
  remote_access: false
  
  # Nahrávání na server
  upload:
    enabled: false
    server: "ftp.example.com"
    username: "user"
    password: "password"
```

## Aplikace změn

Po úpravě konfiguračního souboru restartujte službu:

```bash
sudo systemctl restart amasc01
```

nebo spusťte manuálně:

```bash
python3 scripts/capture.py --config config/camera_config.yaml
```

## Záloha konfigurace

Doporučujeme pravidelně zálohovat konfiguraci:

```bash
cp config/camera_config.yaml config/camera_config.yaml.backup
```
