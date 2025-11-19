# Konfigurace AMASC01

Tento adresář obsahuje konfigurační soubory pro kameru AMASC01.

## Soubory

- `camera_config.example.yaml` - Vzorová konfigurace s komentáři
- `camera_config.yaml` - Vaše osobní konfigurace (není v gitu)

## Použití

1. Zkopírujte vzorovou konfiguraci:
   ```bash
   cp camera_config.example.yaml camera_config.yaml
   ```

2. Upravte `camera_config.yaml` podle vašich potřeb

3. Ujistěte se, že máte správně nastavené:
   - Geografickou polohu (pro výpočet soumraku)
   - Cesty k výstupním adresářům
   - Parametry expozice a zisku

## Důležité nastavení

### Geografická poloha

Pro správnou funkci automatického nočního snímání nastavte:

```yaml
capture:
  location:
    latitude: VAŠE_ZEMĚPISNÁ_ŠÍŘKA
    longitude: VAŠE_ZEMĚPISNÁ_DÉLKA
    elevation: VAŠE_NADMOŘSKÁ_VÝŠKA
```

### Výstupní adresář

Ujistěte se, že výstupní adresář existuje a máte k němu práva zápisu:

```yaml
storage:
  output_path: "/var/amasc01/images"
```

### Síťové nastavení

Pro vzdálený přístup nastavte:

```yaml
network:
  web_interface: true
  host: "0.0.0.0"
  port: 8080
  auth:
    enabled: true
    username: "admin"
    password: "VAŠE_BEZPEČNÉ_HESLO"
```

**Bezpečnost:** Pokud aktivujete vzdálený přístup, vždy používejte silné heslo a zvažte použití VPN nebo firewallu.

## Tipy

- Začněte s nižšími hodnotami expozice a zisku, postupně je zvyšujte
- Pro vědecké zpracování používejte formát FITS
- Pro sdílení a náhled používejte JPEG
- Pravidelně zálohujte konfiguraci
- Testujte změny v konfiguraci s jedním snímkem před aktivací automatického režimu
