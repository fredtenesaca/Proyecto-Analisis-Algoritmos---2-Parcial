#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import sys
import random
from collections import defaultdict

# Máximo de palabras por idioma según enunciado
LANG_MAX_WORDS = {
    "SP": 24,
    "EN": 14,
    "PT": 20,
    "DT": 10,
}

VALID_LANGS = set(LANG_MAX_WORDS.keys())
# ID: prefijo + 6 dígitos
ID_REGEX = re.compile(r'^(SP|EN|PT|DT)(\d{6})$')

class Carton:
    def __init__(self, id_str: str, words):
        self.id = id_str.strip()
        m = ID_REGEX.match(self.id)
        if not m:
            raise ValueError(f"ID inválido: {id_str}")
        self.lang = m.group(1)
        # normalizar: quitar espacios y pasar a minúsculas
        cleaned = [w.strip().lower() for w in words if w and w.strip() != ""]
        self.words = set(cleaned)
        if len(self.words) == 0:
            raise ValueError(f"El cartón {self.id} no tiene palabras válidas.")
        max_allowed = LANG_MAX_WORDS[self.lang]
        if len(self.words) > max_allowed:
            raise ValueError(f"El cartón {self.id} tiene {len(self.words)} palabras (máx {max_allowed} para {self.lang}).")
        # marcado inicialmente vacío
        self.marked = set()

    def mark(self, word: str):
        """Marca la palabra si pertence al cartón (no duplica marcas)."""
        w = word.strip().lower()
        if w in self.words and w not in self.marked:
            self.marked.add(w)

    def is_winner(self) -> bool:
        """Un cartón gana cuando todas sus palabras están marcadas."""
        return self.words == self.marked

    def remaining(self):
        return self.words - self.marked

    def __repr__(self):
        return f"Carton(id={self.id}, lang={self.lang}, words={len(self.words)})"


def cargar_cartones_desde_txt(path):
    """Carga cartones desde un archivo .TXT. Formato por línea:
       ID palabra1 palabra2 palabra3 ...
    """
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
        raise
    return cartones


def ingreso_manual_carton():
    """Ingreso interactivo de un cartón por consola."""
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
    """Valida IDs únicos. Retorna dict id->carton si OK; lanza ValueError si hay duplicados."""
    ids = [c.id for c in cartones]
    dupes = set([x for x in ids if ids.count(x) > 1])
    if dupes:
        raise ValueError(f"IDs duplicados detectados: {', '.join(sorted(dupes))}")
    return {c.id: c for c in cartones}


# ===== ESTRATEGIA VORAZ: marcar inmediatamente y verificar ganadores =====
def greedy_mark_and_check(word: str, cartones_lista):
    """
    Estrategia voraz:
    - Marca inmediatamente la palabra en TODOS los cartones del idioma que la contengan.
    - Después de marcar en todos, verifica si alguno alcanzó la condición de victoria.
    - Retorna la lista de cartones ganadores (puede ser vacía).
    """
    if not word:
        return []
    w = word.strip().lower()
    winners = []
    # marcar en todos los cartones (decisión local: marcar siempre que aplique)
    for c in cartones_lista:
        # hacemos la marca solo si la palabra pertenece y no se había marcado
        if w in c.words and w not in c.marked:
            c.marked.add(w)
    # luego verificamos ganadores (podrían ser varios)
    for c in cartones_lista:
        if c.is_winner():
            winners.append(c)
    return winners

# ======================================================================

def jugar(cartones):
    """Rutina principal de juego: itera rondas por idioma en orden aleatorio,
       procesa palabras con estrategia voraz y termina cuando hay ganadores.
    """
    # organizar cartones por idioma para acceso rápido
    lang_to_cartones = defaultdict(list)
    for c in cartones:
        lang_to_cartones[c.lang].append(c)

    # orden aleatorio de rondas por idioma (si prefieres solo idiomas presentes, cambia esta lista)
    idiomas = list(LANG_MAX_WORDS.keys())  # ['SP','EN','PT','DT']
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
                # Al finalizar la ronda, evaluamos si hay ganadores (aunque con voraz ya se evalúa por palabra)
                # De todas formas, revisamos para cubrir cualquier caso.
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
            # Aplicar estrategia voraz: marcar inmediatamente y comprobar ganadores
            ganadores = greedy_mark_and_check(palabra, lang_to_cartones[idioma])

            if ganadores:
                print("\n=== GANADORES ===")
                for g in ganadores:
                    print(g.id)
                print("El juego finaliza inmediatamente por aparición de ganador(es).")
                return
            else:
                # Información opcional: mostrar cuántos cartones se beneficiaron de la palabra
                beneficiados = sum(1 for c in lang_to_cartones[idioma] if palabra.strip().lower() in c.marked)
                print(f"Palabra procesada. Cartones que ahora la tienen marcada en esta ronda: {beneficiados}")

    # Si se completan todas las rondas sin ganador:
    print("\nSe completaron todas las rondas programadas. No se detectaron ganadores.")
    mostrar_estado_final = input("¿Deseas ver el estado final de los cartones? (s/n): ").strip().lower()
    if mostrar_estado_final.startswith('s'):
        for c in cartones:
            rem = c.remaining()
            print(f"{c.id} ({c.lang}) - faltan {len(rem)} palabras: {', '.join(sorted(rem)[:10])}{'...' if len(rem)>10 else ''}")


def main():
    print("Bingo_P - gestor de partidas con marcado inmediato.")
    cartones = []
    while True:
        print("\nOpciones de entrada:")
        print(" 1) Cargar cartones desde archivo .TXT")
        print(" 2) Ingresar cartón manualmente")
        print(" 3) Listar cartones cargados")
        print(" 4) Comenzar juego")
        print(" 5) Salir")
        opcion = input("Elige una opción (1-5): ").strip()
        if opcion == '1':
            path = input("Ruta al archivo .TXT: ").strip()
            try:
                nuevos = cargar_cartones_desde_txt(path)
                if not nuevos:
                    print("No se cargaron cartones del archivo.")
                else:
                    # comprobar duplicados entre ya cargados y nuevos
                    existing_ids = {c.id for c in cartones}
                    duplicates = [c.id for c in nuevos if c.id in existing_ids]
                    if duplicates:
                        print(f"[ERROR] Los siguientes IDs ya existen y no se añadirán: {', '.join(duplicates)}")
                        # añadimos solo los no duplicados
                        nuevos = [c for c in nuevos if c.id not in existing_ids]
                    cartones.extend(nuevos)
                    print(f"{len(nuevos)} cartones añadidos.")
            except FileNotFoundError:
                print("Archivo no encontrado. Verifica la ruta.")
            except Exception as e:
                print(f"Error al cargar: {e}")
        elif opcion == '2':
            c = ingreso_manual_carton()
            if c:
                if any(existing.id == c.id for existing in cartones):
                    print(f"[ERROR] Ya existe un cartón con ID {c.id}. No se añadió.")
                else:
                    cartones.append(c)
                    print("Cartón añadido.")
        elif opcion == '3':
            if not cartones:
                print("No hay cartones cargados.")
            else:
                print(f"Cartones cargados ({len(cartones)}):")
                for c in cartones[:200]:
                    print(f" - {c.id} ({c.lang}) palabras: {len(c.words)}")
                if len(cartones) > 200:
                    print(f" ... y {len(cartones)-200} más")
        elif opcion == '4':
            if not cartones:
                print("No hay cartones cargados. Carga al menos uno antes de comenzar.")
                continue
            try:
                # validar IDs duplicados
                agrupar_por_id(cartones)
            except ValueError as e:
                print(f"[ERROR] {e}")
                continue
            jugar(cartones)
        elif opcion == '5':
            print("Saliendo.")
            sys.exit(0)
        else:
            print("Opción inválida. Intenta de nuevo.")


if __name__ == '__main__':
    main()
