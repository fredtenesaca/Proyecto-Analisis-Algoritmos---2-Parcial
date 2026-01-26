import csv
import random

CONFIG = {
    "SP": {"max": 24, "file": "bingo_test_SP.csv", "vocab": "el la los las un una unos unas perro gato casa arbol sol luna agua fuego tierra aire rojo azul verde amarillo blanco negro correr saltar jugar comer dormir soñar reir llorar grande pequeño rapido lento feliz triste amigo familia escuela libro mesa silla"},
    "EN": {"max": 14, "file": "bingo_test_EN.csv", "vocab": "the a an cat dog house tree sun moon star sky blue red green yellow black white run jump play eat sleep dream big small fast slow happy sad friend family school book table chair"},
    "PT": {"max": 20, "file": "bingo_test_PT.csv", "vocab": "o a os as um uma cachorro gato casa arvore sol lua agua fogo terra ar vermelho azul verde amarelo branco preto correr pular brincar comer dormir sonhar grande pequeno rapido lento feliz triste amigo familia escola"},
    "DT": {"max": 10, "file": "bingo_test_DT.csv", "vocab": "de het een kat hond huis boom zon maan ster hemel blauw rood groen geel zwart wit rennen springen spelen eten slapen dromen groot klein snel langzaam blij droevig vriend familie school boek tafel stoel"}
}

def generar_csv_idioma(lang_code, num_cartones=50):
    conf = CONFIG[lang_code]
    palabras_fuente = conf["vocab"].split()
    filename = conf["file"]
    limite = conf["max"]
    
    print(f"Generando {filename} ({num_cartones} cartones)...")
    
    with open(filename, mode='w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['id', 'usuario', 'conjunto de palabras']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        
        for i in range(num_cartones):
            id_str = f"{lang_code}{i:06d}"
            
            usuario = f"User_{lang_code}_{i}"
            
            num_palabras = random.randint(5, limite)
            seleccion = random.sample(palabras_fuente, min(num_palabras, len(palabras_fuente)))
            
            frase = " ".join(seleccion)
            
            writer.writerow({
                'id': id_str,
                'usuario': usuario,
                'conjunto de palabras': frase
            })

if __name__ == "__main__":
    for lang in ["SP", "EN", "PT", "DT"]:
        generar_csv_idioma(lang)
    
    print("\n¡Archivos generados exitosamente!")
    print(" - bingo_test_SP.csv")
    print(" - bingo_test_EN.csv")
    print(" - bingo_test_PT.csv")
    print(" - bingo_test_DT.csv")