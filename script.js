// Datos globales
const cartones = [];
const ganadores = [];
let juegoActivo = false;
let idiomasOrden = [];
let idiomaActualIndex = 0;
let mazoActual = [];

const LANG_MAX_WORDS = {
    "SP": 24,
    "EN": 14,
    "PT": 20,
    "DT": 10
};

const VOCABULARIO = {
    "SP": "casa perro gato arbol flor libro mesa silla lapiz papel agua fuego tierra aire nube sol luna mar rio lago pan queso leche carne rojo azul verde negro blanco gris rosa lila cafe oro plata cobre hierro zinc plomo gas luz sonido eco voz grito canto risa norte sur este oeste arriba abajo centro izquierda derecha frente atras lejos cerca dentro fuera alto bajo largo corto ancho fino grueso duro blando uno dos tres cuatro cinco seis siete ocho nueve diez once doce trece catorce quince diecisiete dieciocho veinte treinta cuarenta cincuenta sesenta setenta ochenta lunes martes miercoles jueves viernes sabado domingo enero febrero marzo abril mayo junio julio agosto septiembre octubre noviembre diciembre primavera verano otoño invierno año siglo".split(" "),
    "EN": "computer mouse keyboard screen laptop phone tablet wifi internet code data file folder drive red blue green yellow black white orange purple pink brown gray gold silver bronze apple banana orange grape melon berry lemon lime pear peach plum cherry kiwi mango dog cat bird fish horse cow pig sheep goat duck chicken rabbit mouse snake car bus train plane bike boat ship truck van taxi metro tram rocket jet one two three four five six seven eight nine ten".split(" "),
    "PT": "pai mae irmao irma avo tio tia primo sobrinho filho filha neto neta sogro sogra genro nora marido esposa amigo pão queijo leite carne peixe frango arroz feijao batata salada fruta doce bolo torta sorvete agua suco vinho cerveja cafe ola adeus bom dia boa tarde noite obrigado por favor desculpe sim nao talvez quem onde quando como porque qual quanto cabeca olho nariz boca orelha mao pe perna braco dedo unha cabelo dente lingua pele osso sangue coracao pulmao figado casa porta janela parede teto chao sala quarto cozinha banheiro jardim garagem rua cidade pais mundo terra sol lua estrela".split(" "),
    "DT": "hallo doei dank je wel ja nee alsjeblieft meneer mevrouw naam een twee drie vier vijf zes zeven acht negen tien rood blauw groen geel zwart wit oranje paars roze bruin maandag dinsdag woensdag donderdag vrijdag zaterdag zondag dag week maand hond kat vogel vis paard koe varken schaap geit eend tafel stoel boek pen papier water vuur aarde lucht".split(" ")
};

// Clase Carton
class Carton {
    constructor(id, words) {
        const regex = /^(SP|EN|PT|DT)(\d{6})$/;
        const match = id.match(regex);
        if (!match) throw new Error(`ID inválido: ${id}`);
        
        this.id = id.trim();
        this.lang = match[1];
        this.words = new Set(words.map(w => w.trim().toLowerCase()).filter(w => w));
        this.marked = new Set();

        if (this.words.size === 0) throw new Error(`Cartón sin palabras`);
        
        const maxAllowed = LANG_MAX_WORDS[this.lang];
        if (this.words.size > maxAllowed) throw new Error(`Exceso de palabras`);
    }

    mark(word) {
        const w = word.trim().toLowerCase();
        if (this.words.has(w) && !this.marked.has(w)) {
            this.marked.add(w);
            return true;
        }
        return false;
    }

    isWinner() {
        return this.words.size === this.marked.size;
    }
}

// Funciones de UI
function showSection(sectionId) {
    hideAllSections();
    document.getElementById(sectionId).classList.add('active');
    if (sectionId === 'ver') mostrarCartones();
    if (sectionId === 'ganadores') mostrarGanadores();
}

function hideAllSections() {
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
    });
}

function showMessage(elementId, message, type) {
    const el = document.getElementById(elementId);
    el.innerHTML = `<div class="message ${type}">${message}</div>`;
    if(type !== 'error') setTimeout(() => el.innerHTML = '', 5000);
}

// Cargar archivo
function cargarArchivo(event) {
    const file = event.target.files[0];
    if (!file) return;

    document.getElementById('fileName').textContent = `Archivo: ${file.name}`;
    const reader = new FileReader();
    
    reader.onload = function(e) {
        const lines = e.target.result.split('\n');
        let cargados = 0;
        let errores = [];

        lines.forEach((line, index) => {
            const parts = line.trim().split(/\s+/);
            if (parts.length < 2) return;

            try {
                if (cartones.some(c => c.id === parts[0])) throw new Error('ID duplicado');
                cartones.push(new Carton(parts[0], parts.slice(1)));
                cargados++;
            } catch (error) {
                errores.push(`Línea ${index + 1}: ${error.message}`);
            }
        });

        let mensaje = `${cargados} cartones cargados.`;
        if (errores.length) mensaje += `<br>Errores: ${errores.length}`;
        showMessage('cargarMessage', mensaje, cargados > 0 ? 'success' : 'error');
    };
    reader.readAsText(file);
}

// Agregar cartón manual
function agregarCarton() {
    const id = document.getElementById('cartonId').value.trim();
    const words = document.getElementById('cartonWords').value.trim().split(/\s+/);

    try {
        if (cartones.some(c => c.id === id)) throw new Error('ID existente');
        cartones.push(new Carton(id, words));
        showMessage('cargarMessage', `Cartón ${id} agregado`, 'success');
        document.getElementById('cartonId').value = '';
        document.getElementById('cartonWords').value = '';
    } catch (error) {
        showMessage('cargarMessage', error.message, 'error');
    }
}

// Limpiar cartones
function limpiarCartones() {
    if (cartones.length === 0) {
        showMessage('cargarMessage', 'No hay cartones.', 'error');
        return;
    }
    if (confirm('¿Eliminar TODOS los cartones?')) {
        cartones.length = 0;
        document.getElementById('cartonList').innerHTML = '';
        document.getElementById('fileName').textContent = '';
        document.getElementById('fileInput').value = '';
        document.getElementById('gameStatus').innerHTML = `
            <h4>Estado del Juego</h4>
            <p>Presiona "Comenzar Juego" para iniciar</p>
        `;
        document.getElementById('gameMessage').innerHTML = '';
        showMessage('cargarMessage', 'Cartones eliminados.', 'info');
    }
}

// Mostrar cartones en lista
function mostrarCartones(){
    const list = document.getElementById('cartonList');
    if (!cartones.length) {
        list.innerHTML = '<div class="message info">Vacío</div>';
        return;
    }
    list.innerHTML = cartones.map(c => `
        <div class="carton-item">
            <div><strong>${c.id}</strong> (${c.lang}) - ${c.marked.size}/${c.words.size}</div>
        </div>
    `).join('');
}

// Lógica del Juego: Inicio
function comenzarJuego(){
    if (cartones.length === 0) {
        showMessage('gameMessage', 'Carga cartones primero.', 'error');
        return;
    }

    cartones.forEach(c => c.marked.clear());
    //ganadores.length = 0;
    idiomasOrden = ['SP', 'EN', 'PT', 'DT'].sort(() => Math.random() - 0.5);
    idiomaActualIndex = 0;
    juegoActivo = true;

    document.getElementById('startGameBtn').style.display = 'none';
    document.getElementById('gameControls').style.display = 'block';
    document.getElementById('inputArea').style.display = 'flex';
    document.getElementById('continueArea').style.display = 'none';
    document.getElementById('gameMessage').innerHTML = '';
    //document.getElementById('ganadoresList').innerHTML = '';
    document.getElementById('tituloJuego').textContent = 'Partida en Curso';
    document.getElementById('palabraMostrada').textContent = '---';
    inicializarMazo(idiomasOrden[idiomaActualIndex]);
    actualizarEstadoJuego();
}

// Prepara las palabras disponibles para el idioma actual
function inicializarMazo(idioma){
    if(VOCABULARIO[idioma]){
        mazoActual = [...VOCABULARIO[idioma]];
    } else{
        mazoActual = [];
        console.error("No hay vocabulario para " + idioma);
    }
}

function sacarPalabraRandom(){
    if (!juegoActivo) return;
    
    if (mazoActual.length === 0){
        document.getElementById('palabraMostrada').textContent = "FIN MAZO";
        showMessage('gameMessage', '¡Se acabaron las palabras de este idioma!', 'error');
        return;
    }

    const randomIndex = Math.floor(Math.random() * mazoActual.length);
    const palabra = mazoActual[randomIndex];
    mazoActual.splice(randomIndex, 1);
    const pantalla = document.getElementById('palabraMostrada');
    pantalla.textContent = palabra;
    pantalla.style.color = 'rgb(255, 206, 8)';
    pantalla.animate([
        { transform: 'scale(1.2)' },
        { transform: 'scale(1)' }
    ], { duration: 200 });
    actualizarEstadoJuego();
}

// Actualizar panel de estado
function actualizarEstadoJuego() {
    if (!juegoActivo) return;
    const idioma = idiomasOrden[idiomaActualIndex];
    const count = cartones.filter(c => c.lang === idioma).length;
    
    document.getElementById('gameStatus').innerHTML = `
        <h4>Ronda: ${idioma}</h4>
        <p>Orden: ${idiomasOrden.join(' → ')}</p>
        <p>Cartones activos: ${count}</p>
        <p style="font-size: 12px; color: #666;">Palabras restantes en mazo: ${mazoActual.length}</p>
    `;
}

// Procesar palabra ingresada
function procesarPalabra() {
    const input = document.getElementById('palabraInput');
    const palabra = input.value.trim();
    if (!palabra) return;

    const idioma = idiomasOrden[idiomaActualIndex];
    const nuevos = [];

    cartones.filter(c => c.lang === idioma).forEach(c => {
        c.mark(palabra);
        const yaGano = ganadores.some(g => g.id === c.id);
        if (c.isWinner() && !yaGano) {
            const hoy = new Date();
            const fechaStr = `${hoy.getDate().toString().padStart(2, '0')}/${(hoy.getMonth() + 1).toString().padStart(2, '0')}/${hoy.getFullYear()}`;
            const datosGanador = { id: c.id, fecha: fechaStr };
            nuevos.push(datosGanador);
            ganadores.push(datosGanador);
        }
    });

    input.value = '';

    if (nuevos.length > 0) {
        mostrarGanadoresEnJuego(nuevos);
        document.getElementById('inputArea').style.display = 'none';
        document.getElementById('continueArea').style.display = 'block';
    } else {
        showMessage('gameMessage', 'Palabra procesada.', 'info');
    }
}

// Finalizar ronda / Continuar
function finalizarRonda() {
    idiomaActualIndex++;
    
    document.getElementById('inputArea').style.display = 'flex';
    document.getElementById('continueArea').style.display = 'none';
    document.getElementById('gameMessage').innerHTML = '';
    document.getElementById('palabraMostrada').textContent = '---';

    if (idiomaActualIndex >= idiomasOrden.length) {
        document.getElementById('gameMessage').innerHTML = '<div class="winners"><h3>¡JUEGO TERMINADO!</h3></div>';
        detenerJuego();
        document.getElementById('gameStatus').innerHTML = '<h4>Fin del Juego</h4>';
        return;
    }

    inicializarMazo(idiomasOrden[idiomaActualIndex]);
    actualizarEstadoJuego();
    showMessage('gameMessage', `¡Iniciando ronda de ${idiomasOrden[idiomaActualIndex]}!`, 'info');
}

// Detener juego completo
function detenerJuego() {
    juegoActivo = false;
    document.getElementById('startGameBtn').style.display = 'block';
    document.getElementById('gameControls').style.display = 'none';
    document.getElementById('palabraInput').value = '';
    document.getElementById('gameStatus').innerHTML = '<h4>Estado del Juego</h4><p>Esperando inicio</p>';
    document.getElementById('tituloJuego').textContent = 'Preparar Partida';
}

// Mostrar alerta de ganadores en partida
function mostrarGanadoresEnJuego(lista) {
    document.getElementById('gameMessage').innerHTML = `
        <div class="winners">
            <h3> ¡GANADORES! </h3>
            ${lista.map(g => `<div class="winner-id">${g.id}</div>`).join('')}
            <p style="margin-top:15px">Pulsa continuar para siguiente ronda</p>
        </div>
    `;
}

// Mostrar historial completo
function mostrarGanadores() {
    const list = document.getElementById('ganadoresList');
    if (!ganadores.length) {
        list.innerHTML = '<div class="message info">Sin ganadores</div>';
        return;
    }
    list.innerHTML = `
        <div class="winners">
            <h3> Historial Global </h3>
            ${ganadores.slice().reverse().map(g => `
                <div class="winner-id">
                    ${g.id} 
                    <span style="display:block; font-size: 14px; font-weight: normal; color: #555;">
                        (Partida del ${g.fecha})
                    </span>
                </div>
            `).join('')}
        </div>
    `;
}