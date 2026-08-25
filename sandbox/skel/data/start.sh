#!/bin/bash
# Startovací skript rakety. Zatím ho nejde spustit – chybí mu právo 'x'.
echo "🚀 3... 2... 1... START!"
echo "Raketa odstartovala v $(date '+%H:%M:%S')" >> "$HOME/starty.log"
echo "Zápis o startu byl uložen do souboru starty.log"
