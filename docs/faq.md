# FAQ - Často kladené otázky

## Obecné otázky

### Co je AMASC01?

AMASC01 je All-Sky kamera od AstroMeters.eu určená pro sledování celé oblohy. Kamera je vhodná pro astronomická pozorování, monitoring světelného znečištění a zachycení přechodných jevů.

### Jaké jsou systémové požadavky?

- Operační systém: Linux (doporučeno), Windows, nebo macOS
- RAM: Minimálně 4 GB
- Místo na disku: 100+ GB doporučeno
- USB 3.0 port nebo síťové připojení

### Je možné použít kameru pro automatické pozorování?

Ano, kamera podporuje plně automatický režim s možností nastavení časování a podmínek pro snímání.

## Technické otázky

### Jak nastavím automatické snímání pouze v noci?

V konfiguračním souboru nastavte:

```yaml
capture:
  night_only: true
  location:
    latitude: VAŠE_ZEMĚPISNÁ_ŠÍŘKA
    longitude: VAŠE_ZEMĚPISNÁ_DÉLKA
```

### Jak mohu změnit expozici?

Expozici můžete změnit v konfiguračním souboru `config/camera_config.yaml`:

```yaml
camera:
  exposure: 10.0  # v sekundách
```

### Jaké formáty snímků jsou podporovány?

Kamera podporuje následující formáty:
- FITS (doporučeno pro vědecké zpracování)
- JPEG (pro sdílení a náhled)
- PNG (pro archivaci s bezztrátovou kompresí)

### Jak mohu zpracovat zachycené snímky?

V adresáři `scripts/` naleznete nástroje pro základní zpracování:
- `process_images.py` - Dávkové zpracování snímků
- `stack_images.py` - Skládání více snímků
- `create_timelapse.py` - Vytvoření časosběrného videa

## Problémy a jejich řešení

### Kamera není rozpoznána

1. Zkontrolujte USB připojení
2. Ověřte instalaci ovladačů
3. Zkontrolujte oprávnění (Linux: udev pravidla)
4. Restartujte počítač

### Snímky jsou příliš tmavé

1. Zvyšte expozici v konfiguraci
2. Zvyšte gain (zisk)
3. Zkontrolujte, zda není nasazený kryt objektivu
4. Ověřte nastavení automatické expozice

### Vysoká spotřeba místa na disku

1. Použijte kompresi (JPEG místo FITS pro archivaci)
2. Nastavte automatické mazání starých snímků
3. Implementujte externí úložiště
4. Zvyšte interval mezi snímky

### Webové rozhraní nefunguje

1. Zkontrolujte, zda je aktivováno v konfiguraci
2. Ověřte, že port není blokován firewallem
3. Zkontrolujte, zda služba běží: `systemctl status amasc01`

## Podpora komunity

### Kde mohu najít další pomoc?

- GitHub Issues: https://github.com/roman-dvorak/AMASC01/issues
- Oficiální web: https://astrometers.eu
- Komunitní fórum: (link bude doplněn)

### Jak mohu přispět do projektu?

Příspěvky jsou vítány! Můžete:
- Nahlásit chyby přes GitHub Issues
- Navrhovat nové funkce
- Přispět kódem přes Pull Requests
- Vylepšit dokumentaci
- Sdílet své zkušenosti s komunitou

### Kde najdu příklady použití?

Příklady skriptů a konfigurací naleznete v adresáři `examples/`.
