# Změny v thermal_control

## Failsafe režim
- Aplikace nyní pokračuje v běhu i když senzory nejsou dostupné
- Při nedostupnosti senzorů se nastaví bezpečné hodnoty:
  - Heater: 0% (vypnuto)
  - Fan: 100% (plný výkon pro chlazení)
  - CPU Fan: ON
- Status obsahuje nová pole: `failsafe_mode`, `dome_available`, `body_available`, `envi_available`

## Inverted PWM
- PWM výstupy lze invertovat nastavením v config.py:
  - `PWM_HEATER_INVERTED = True/False`
  - `PWM_FAN_INVERTED = True/False`
- Když je inverted=True: 100% PWM = vypnuto, 0% PWM = zapnuto

## Konfigurace (thermal/config.py)
Nové konstanty:
- `PWM_HEATER_INVERTED` - inverze PWM heateru
- `PWM_FAN_INVERTED` - inverze PWM ventilátoru
- `FAILSAFE_HEATER_PWM` - hodnota heateru v nouzovém režimu (0%)
- `FAILSAFE_FAN_PWM` - hodnota ventilátoru v nouzovém režimu (100%)
- `FAILSAFE_CPU_FAN_STATE` - stav CPU ventilátoru v nouzovém režimu (True)

## Použití
Pro invertování PWM upravte v config.py:
```python
PWM_HEATER_INVERTED = True  # Heater inverted
PWM_FAN_INVERTED = False    # Fan normal
```

## Testování
Všechny soubory mají platnou Python syntax.
Zálohy původních souborů: *.backup
