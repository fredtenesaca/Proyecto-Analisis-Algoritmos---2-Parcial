import random
from typing import Dict, List, Set, Tuple
from collections import defaultdict

import os #para verificar existencia de archivos

class BingoP:
    """Sistema de gestión de partidas de bingo con palabras"""
    
    # Configuración de idiomas
    IDIOMAS = {
        'SP': {'nombre': 'Español', 'max_palabras': 24},
        'EN': {'nombre': 'Inglés', 'max_palabras': 14},
        'PT': {'nombre': 'Portugués', 'max_palabras': 20},
        'DT': {'nombre': 'Dutch', 'max_palabras': 10}
    }
    
    def __init__(self):
        """Inicializa el sistema de bingo"""
        self.cartones: Dict[str, Dict] = {}
        self.palabras_marcadas: Dict[str, Set[str]] = defaultdict(set)
        self.orden_rondas: List[str] = []
        
    #------------- SE AGREGÓ ESTA NUEVA FUNCIÓN PARA CARGA MASIVA DE CARTONES MEDIANTE ARCHIVO .TXT----------------------------#
    
    def cargar_cartones_archivo(self, nombre_archivo: str) -> bool:
        """Carga cartones masivamente desde un archivo de texto"""
        if not os.path.exists(nombre_archivo):
            print(f" Error: El archivo '{nombre_archivo}' no existe.")
            return False
        
        try:
            # Abre el archivo en modo lectura con soporte para caracteres especiales
            with open(nombre_archivo, 'r', encoding='utf-8') as f:
                lineas = f.readlines()
                for linea in lineas:
                    # Divide la línea: partes[0] es el ID, partes[1:] son las palabras
                    partes = linea.strip().split()
                    if len(partes) >= 2:
                        id_carton = partes[0]
                        palabras = partes[1:]
                        # Intenta registrar el cartón usando la validación existente
                        self.agregar_carton(id_carton, palabras)
            return True
        
        except Exception as e:
            # Captura errores de permisos o de lectura de disco
            print(f"Error al leer el archivo {e}")
            return False
     #---------------------------------------------------------------------------------------------------------------------------#   
        
    
        
    def validar_id_carton(self, id_carton: str) -> bool:
        """Valida el formato del identificador del cartón"""
        if len(id_carton) != 8:
            return False
        
        idioma = id_carton[:2].upper()
        numeros = id_carton[2:]
        
        if idioma not in self.IDIOMAS:
            return False
        
        if not numeros.isdigit():
            return False
            
        return True
    
    def agregar_carton(self, id_carton: str, palabras: List[str]) -> bool:
        """Agrega un cartón al sistema"""
        id_carton = id_carton.upper()
        
        if not self.validar_id_carton(id_carton):
            print(f" Error: ID de cartón inválido '{id_carton}'")
            return False
        
        idioma = id_carton[:2]
        max_palabras = self.IDIOMAS[idioma]['max_palabras']
        
        if len(palabras) > max_palabras:
            print(f" Error: Cartón {id_carton} excede el máximo de {max_palabras} palabras")
            return False
        
        # Convertir palabras a minúsculas y eliminar duplicados
        palabras_unicas = list(set(p.lower().strip() for p in palabras if p.strip()))
        
        self.cartones[id_carton] = {
            'idioma': idioma,
            'palabras': set(palabras_unicas),
            'total_palabras': len(palabras_unicas)
        }
        
        self.palabras_marcadas[id_carton] = set()
        
        print(f"✓ Cartón {id_carton} agregado con {len(palabras_unicas)} palabras")
        return True
    
    def iniciar_partida(self):
        """Inicializa una nueva partida estableciendo orden aleatorio de rondas"""
        if not self.cartones:
            print(" No hay cartones registrados para iniciar la partida")
            return False
        
        # Determinar qué idiomas están presentes
        idiomas_presentes = set(carton['idioma'] for carton in self.cartones.values())
        
        # Establecer orden aleatorio
        self.orden_rondas = list(idiomas_presentes)
        random.shuffle(self.orden_rondas)
        
        # Reiniciar palabras marcadas
        self.palabras_marcadas = {id_c: set() for id_c in self.cartones.keys()}
        
        print("\n" + "="*60)
        print("NUEVA PARTIDA INICIADA")
        print("="*60)
        print(f"Cartones registrados: {len(self.cartones)}")
        print(f"Orden de rondas: {' → '.join([self.IDIOMAS[i]['nombre'] for i in self.orden_rondas])}")
        print("="*60 + "\n")
        
        return True
    
    def procesar_palabra(self, palabra: str) -> List[str]:
        """Procesa una palabra anunciada y retorna los cartones ganadores"""
        palabra = palabra.lower().strip()
        ganadores = []
        
        print(f"\n Palabra anunciada: '{palabra}'")
        
        # Marcar la palabra en todos los cartones que la contengan
        cartones_marcados = 0
        for id_carton, datos_carton in self.cartones.items():
            if palabra in datos_carton['palabras']:
                self.palabras_marcadas[id_carton].add(palabra)
                cartones_marcados += 1
                
                # Verificar si el cartón es ganador
                if len(self.palabras_marcadas[id_carton]) == datos_carton['total_palabras']:
                    ganadores.append(id_carton)
        
        if cartones_marcados > 0:
            print(f"   ✓ Marcada en {cartones_marcados} cartón(es)")
        else:
            print(f"   ✗ No encontrada en ningún cartón")
        
        return ganadores
    
    def jugar_ronda(self, palabras_anunciadas: List[str], nombre_ronda: str = ""):
        """Procesa una ronda completa con múltiples palabras"""
        if nombre_ronda:
            print(f"\n{'='*60}")
            print(f"RONDA: {nombre_ronda}")
            print(f"{'='*60}")
        
        ganadores_ronda = []
        
        for palabra in palabras_anunciadas:
            ganadores = self.procesar_palabra(palabra)
            ganadores_ronda.extend(ganadores)
            
            if ganadores:
                break  # Si hay ganadores, termina la ronda
        
        print(f"\n{'─'*60}")
        if ganadores_ronda:
            print(f"GANADOR(ES) DE LA RONDA:")
            for ganador in ganadores_ronda:
                idioma = self.IDIOMAS[self.cartones[ganador]['idioma']]['nombre']
                print(f"   • {ganador} ({idioma})")
        else:
            print("   No hubo cartones ganadores en esta ronda")
        print(f"{'─'*60}\n")
        
        return ganadores_ronda
    
    def mostrar_estado_carton(self, id_carton: str):
        """Muestra el estado actual de un cartón"""
        if id_carton not in self.cartones:
            print(f"Cartón {id_carton} no encontrado")
            return
        
        datos = self.cartones[id_carton]
        marcadas = self.palabras_marcadas[id_carton]
        
        print(f"\n{'='*60}")
        print(f"Cartón: {id_carton}")
        print(f"Idioma: {self.IDIOMAS[datos['idioma']]['nombre']}")
        print(f"Progreso: {len(marcadas)}/{datos['total_palabras']} palabras")
        print(f"{'='*60}")
        
        print("\nPalabras marcadas:")
        if marcadas:
            for palabra in sorted(marcadas):
                print(f"  ✓ {palabra}")
        else:
            print("  (ninguna)")
        
        print("\nPalabras pendientes:")
        pendientes = datos['palabras'] - marcadas
        if pendientes:
            for palabra in sorted(pendientes):
                print(f"  ○ {palabra}")
        else:
            print("  (ninguna - ¡BINGO!)")
        print()
    
    def estadisticas(self):
        """Muestra estadísticas generales del juego"""
        print(f"\n{'='*60}")
        print("ESTADÍSTICAS")
        print(f"{'='*60}")
        print(f"Total de cartones: {len(self.cartones)}")
        
        # Cartones por idioma
        cartones_por_idioma = defaultdict(int)
        for carton in self.cartones.values():
            cartones_por_idioma[carton['idioma']] += 1
        
        print("\nCartones por idioma:")
        for idioma, cantidad in sorted(cartones_por_idioma.items()):
            print(f"  • {self.IDIOMAS[idioma]['nombre']}: {cantidad}")
        
        # Cartones ganadores
        ganadores = [id_c for id_c, marcadas in self.palabras_marcadas.items()
                     if len(marcadas) == self.cartones[id_c]['total_palabras']]
        
        print(f"\nCartones ganadores: {len(ganadores)}")
        if ganadores:
            for ganador in ganadores:
                print(f"   {ganador}")
        
        print(f"{'='*60}\n")


def main():
    """Función principal para demostrar el sistema"""
    bingo = BingoP()
    
    print("="*60)
    print("         SISTEMA BINGO_P - GESTIÓN DE CARTONES")
    print("="*60)
    
    # Menú principal
    while True:
        print("\n MENU PRINCIPAL")
        print("1. Agregar cartOn manualmente")
        print("2. Carga masiva desde archivo (.txt)") # MODIFICACIÓN: Nueva opción en el menú
        print("3. Iniciar partida")
        print("4. Anunciar palabra")
        print("5. Ver estado de cartOn")
        print("6. Ver estadisticas")
        print("7. Salir")
        
        opcion = input("\nSeleccione una opción: ").strip()
        
        if opcion == '1':
            print("\n--- AGREGAR CARTON MANUAL ---")
            id_carton = input("ID del cartón (ej: SP123456): ").strip()
            palabras_input = input("Palabras (separadas por espacios): ").strip()
            palabras = palabras_input.split()
            bingo.agregar_carton(id_carton, palabras)
        
        # --- MODIFICACIÓN: Implementación de la opción de carga masiva ---
        
        elif opcion == '2':
            print("\n--- CARGA MASIVA DESDE ARCHIVO ---")
            # Captura el nombre del archivo y limpia espacios en blanco sobrantes
            nombre_archivo = input(r"Ruta del archivo (C:/Users/Dell/Proyecto/cartones.txt): ").strip()
            # Ejecuta la lógica de lectura y registro de cartones desde el archivo
            bingo.cargar_cartones_archivo(nombre_archivo)
            
        # -----------------------------------------------------------------    
            
        elif opcion == '3':
            bingo.iniciar_partida()
            
        elif opcion == '4':
            if not bingo.orden_rondas:
                print(" Debe iniciar una partida primero")
                continue
            
            palabra = input("\nPalabra anunciada: ").strip()
            ganadores = bingo.procesar_palabra(palabra)
            
            if ganadores:
                print(f"\n🎉 ¡BINGO! Ganador(es):")
                for ganador in ganadores:
                    print(f"    {ganador}")
            
        elif opcion == '5':
            id_carton = input("\nID del cartón: ").strip().upper()
            bingo.mostrar_estado_carton(id_carton)
            
        elif opcion == '6':
            bingo.estadisticas()
            
        elif opcion == '7':
            print("\n¡Hasta luego!")
            break
            
        else:
            print(" Opción inválida")


if __name__ == "__main__":
    main()