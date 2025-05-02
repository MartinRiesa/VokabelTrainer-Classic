# TTS‑Upgrade für VokabelTrainer‑Classic

Dieses Paket ergänzt den VokabelTrainer um automatische Sprachausgabe
des Erklärungstextes nach bestandenem Level.

## Inhalt des ZIP
| Datei | Beschreibung |
|-------|--------------|
| `tts_engine.py` | Initialisiert *pyttsx3* und stellt `speak(text)` bereit |
| `patch_levelwechsel.diff` | Git‑Patch, fügt TTS‑Aufruf in `levelwechsel.py` ein |
| `README_TTS.md` | Diese Anleitung |

## Schnelleinrichtung (Windows PowerShell ≥ 5)

```powershell
# 1. In Projektordner wechseln
Set-Location .\VokabelTrainer-Classic

# 2. Abhängigkeiten installieren
python -m pip install --upgrade pip
python -m pip install pyttsx3
python -m pip install pypiwin32  # nur Windows nötig

# 3. Dateien aus ZIP entpacken
Expand-Archive .\vokabeltrainer_tts_update.zip -DestinationPath .

# 4. Patch anwenden (oder manuell Code einfügen)
git apply .\patch_levelwechsel.diff

# 5. Test
python - <<EOF
from tts_engine import speak
speak("Text‑to‑Speech erfolgreich eingerichtet.")
EOF

# 6. Spiel starten
python .\main.py
```

## Alternative ohne Git
Öffne `levelwechsel.py`, finde die Zeile mit
`karte.set_text(erklaerung, color="blue")` und füge direkt
darunter Folgendes ein:

```python
from tts_engine import speak
speak(erklaerung)
```

Fertig – der Erklärungstext wird nun angezeigt **und** vorgelesen.
