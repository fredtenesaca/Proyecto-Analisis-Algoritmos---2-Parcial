#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import sys
import random
import csv  
from collections import defaultdict

LANG_MAX_WORDS = {
    "SP": 24,
    "EN": 14,
    "PT": 20,
    "DT": 10,
}

VALID_LANGS = set(LANG_MAX_WORDS.keys())
ID_REGEX = re.compile(r'^(SP|EN|PT|DT)(\d{6})$')

class Carton:
    def __init__(self, id_str: str, words):
        self.id = id_str.strip()
        m = ID_REGEX.match(self.id)
        if not m:
            raise ValueError(f"ID inválido: {id_str}")
        self.lang = m.group(1)
        cleaned = [w.strip().lower() for w in words if w and w.strip() != ""]
        self.words = set(cleaned)
        if len(self.words) == 0:
            raise ValueError(f"El cartón {self.id} no tiene palabras válidas.")
        max_allowed = LANG_MAX_WORDS[self.lang]
        if len(self.words) > max_allowed:
            raise ValueError(f"El cartón {self.id} tiene {len(self.words)} palabras (máx {max_allowed} para {self.lang}).")
        self.marked = set()

    def mark(self, word: str):
        w = word.strip().lower()
        if w in self.words and w not in self.marked:
            self.marked.add(w)

    def is_winner(self) -> bool:
        return self.words == self.marked

    def remaining(self):
        return self.words - self.marked

    def __repr__(self):
        return f"Carton(id={self.id}, lang={self.lang}, words={len(self.words)})"


def cargar_cartones_desde_txt(path):
    cartones = []
    line_no = 0
    try:
        with open(path, 'r', encoding='utf-8') as f:
            for line in f:
                line_no += 1
                line = line.strip()
                if not line:
                    continue
                parts = line.split()
                if len(parts) < 2:
                    print(f"[WARN] Línea {line_no}: formato inválido (se requiere ID y >=1 palabra). Línea ignorada.")
                    continue
                id_str = parts[0].strip()
                palabras = parts[1:]
                try:
                    c = Carton(id_str, palabras)
                    cartones.append(c)
                except ValueError as e:
                    print(f"[ERROR] Línea {line_no}: {e}. Línea ignorada.")
    except FileNotFoundError:
        print(f"[ERROR] No se encontró el archivo TXT: {path}")
    return cartones


def cargar_cartones_desde_csv(path):
    cartones = []
    line_no = 1
    try:
        with open(path, 'r', encoding='utf-8') as f:
            # Detectar dialecto (separador , o ;)
            sample = f.read(1024)
            f.seek(0)
            try:
                dialect = csv.Sniffer().sniff(sample)
            except csv.Error:
                dialect = csv.excel
            
            reader = csv.DictReader(f, dialect=dialect)
            
            reader.fieldnames = [name.strip().lower() for name in reader.fieldnames]
            
            col_id = next((x for x in reader.fieldnames if x in ['id', 'identificador']), None)
            col_words = next((x for x in reader.fieldnames if x in ['conjunto de palabras', 'palabras', 'words']), None)

            if not col_id or not col_words:
                print(f"[ERROR] El CSV no tiene las columnas esperadas ('id', 'conjunto de palabras'). Columnas encontradas: {reader.fieldnames}")
                return []

            for row in reader:
                line_no += 1
                id_str = row[col_id]
                words_str = row[col_words]
                
                palabras = words_str.split()
                
                try:
                    c = Carton(id_str, palabras)
                    cartones.append(c)
                except ValueError as e:
                    print(f"[ERROR] CSV línea {line_no}: {e}")
                    
    except FileNotFoundError:
        print(f"[ERROR] No se encontró el archivo CSV: {path}")
    except Exception as e:
        print(f"[ERROR] Fallo al leer CSV: {e}")
        
    return cartones


def ingreso_manual_carton():
    print("Ingreso manual de un cartón. Escribe 'cancel' para cancelar el ingreso.")
    id_str = input("ID del cartón (ej: SP000001): ").strip()
    if id_str.lower() == 'cancel':
        return None
    palabras = input("Introduce las palabras separadas por espacios: ").strip().split()
    try:
        c = Carton(id_str, palabras)
        return c
    except ValueError as e:
        print(f"[ERROR] {e}")
        return None


def agrupar_por_id(cartones):
    ids = [c.id for c in cartones]
    dupes = set([x for x in ids if ids.count(x) > 1])
    if dupes:
        raise ValueError(f"IDs duplicados detectados: {', '.join(sorted(dupes))}")
    return {c.id: c for c in cartones}

def greedy_mark_and_check(word: str, cartones_lista):
    if not word:
        return []
    w = word.strip().lower()
    winners = []
    for c in cartones_lista:
        if w in c.words and w not in c.marked:
            c.marked.add(w)
    for c in cartones_lista:
        if c.is_winner():
            winners.append(c)
    return winners


def jugar(cartones):
    lang_to_cartones = defaultdict(list)
    for c in cartones:
        lang_to_cartones[c.lang].append(c)

    idiomas = list(LANG_MAX_WORDS.keys())  
    random.shuffle(idiomas)
    print("\nOrden aleatorio de rondas por idioma:")
    print(" -> ".join(idiomas))
    print("\nINSTRUCCIONES:")
    print(" - Para terminar la ronda actual y pasar a la siguiente escribe 'END'.")
    print(" - Para detener todo el juego escribe 'STOP'.")
    print(" - Las comparaciones son case-insensitive.")
    print()

    for idioma in idiomas:
        print(f"\n--- RONDA: {idioma} ---")
        total_cartones = len(lang_to_cartones.get(idioma, []))
        print(f"Cartones en esta ronda: {total_cartones}")
        if total_cartones == 0:
            print("No hay cartones de este idioma. Se omite la ronda.")
            continue

        while True:
            entrada = input("Palabra extraída (o 'END' para finalizar ronda, 'STOP' para terminar juego): ").strip()
            if not entrada:
                continue
            cmd = entrada.strip()
            if cmd.upper() == 'END':
                # Revisión final de ronda
                ganadores = [c for c in lang_to_cartones[idioma] if c.is_winner()]
                if ganadores:
                    print("\n=== GANADORES EN ESTA RONDA (evaluación END) ===")
                    for g in ganadores:
                        print(g.id)
                    print("El juego finaliza porque hubo uno o más cartones ganadores.")
                    return
                else:
                    print("No hubo cartones ganadores en esta ronda.")
                break
            if cmd.upper() == 'STOP':
                print("Juego detenido por el usuario.")
                return

            palabra = cmd.strip()
            ganadores = greedy_mark_and_check(palabra, lang_to_cartones[idioma])

            if ganadores:
                print("\n=== GANADORES DETECTADOS ===")
                for g in ganadores:
                    print(g.id)
                print("El juego finaliza inmediatamente por aparición de ganador(es).")
                return
            else:
                beneficiados = sum(1 for c in lang_to_cartones[idioma] if palabra.strip().lower() in c.marked)
                print(f"Palabra procesada. Cartones que la marcaron: {beneficiados}")

    print("\nSe completaron todas las rondas programadas. No se detectaron ganadores.")
    mostrar_estado_final = input("¿Deseas ver el estado final de los cartones? (s/n): ").strip().lower()
    if mostrar_estado_final.startswith('s'):
        for c in cartones:
            rem = c.remaining()
            print(f"{c.id} ({c.lang}) - faltan {len(rem)} palabras")


def main():
    print("Bingo_P - Gestor de partidas (Versión CSV + TXT)")
    cartones = []
    while True:
        print("\nOpciones de entrada:")
        print(" 1) Cargar cartones desde archivo .TXT")
        print(" 2) Cargar cartones desde archivo .CSV")
        print(" 3) Ingresar cartón manualmente")
        print(" 4) Listar cartones cargados")
        print(" 5) Comenzar juego")
        print(" 6) Salir")
        opcion = input("Elige una opción (1-6): ").strip()
        
        if opcion == '1':
            path = input("Ruta al archivo .TXT: ").strip()
            nuevos = cargar_cartones_desde_txt(path)
            if nuevos:
                existing_ids = {c.id for c in cartones}
                uniques = [c for c in nuevos if c.id not in existing_ids]
                if len(uniques) < len(nuevos):
                    print(f"[INFO] Se omitieron {len(nuevos)-len(uniques)} cartones duplicados.")
                cartones.extend(uniques)
                print(f"{len(uniques)} cartones añadidos.")

        elif opcion == '2':
            path = input("Ruta al archivo .CSV: ").strip()
            nuevos = cargar_cartones_desde_csv(path)
            if nuevos:
                existing_ids = {c.id for c in cartones}
                uniques = [c for c in nuevos if c.id not in existing_ids]
                if len(uniques) < len(nuevos):
                    print(f"[INFO] Se omitieron {len(nuevos)-len(uniques)} cartones duplicados.")
                cartones.extend(uniques)
                print(f"{len(uniques)} cartones añadidos.")

        elif opcion == '3':
            c = ingreso_manual_carton()
            if c:
                if any(existing.id == c.id for existing in cartones):
                    print(f"[ERROR] Ya existe un cartón con ID {c.id}. No se añadió.")
                else:
                    cartones.append(c)
                    print("Cartón añadido.")

        elif opcion == '4':
            if not cartones:
                print("No hay cartones cargados.")
            else:
                print(f"Cartones cargados ({len(cartones)}):")
                mostrar = cartones if len(cartones) < 20 else cartones[:10] + cartones[-10:]
                for c in mostrar:
                    print(f" - {c.id} ({c.lang}) palabras: {len(c.words)}")
                if len(cartones) >= 20:
                    print(f"   ... (y {len(cartones)-20} más)")

        elif opcion == '5':
            if not cartones:
                print("No hay cartones cargados. Carga al menos uno antes de comenzar.")
                continue
            try:
                agrupar_por_id(cartones)
                jugar(cartones)
            except ValueError as e:
                print(f"[ERROR] {e}")

        elif opcion == '6':
            print("Saliendo.")
            sys.exit(0)
        else:
            print("Opción inválida.")

if __name__ == '__main__':
    main()
