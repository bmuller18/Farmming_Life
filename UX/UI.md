# PROMPT MAESTRO — FARMING LIFE UI/UX DESIGN

Diseña la interfaz completa de un videojuego web llamado **Farming Life**.

## 1. CONCEPTO DEL JUEGO

**Farming Life** es un juego de simulación de vida y agricultura con elementos de economía, progresión y multiplayer.

El jugador comienza con una pequeña propiedad agrícola y va construyendo progresivamente su vida dentro de un mundo virtual.

La experiencia comienza principalmente con agricultura:

* Comprar y plantar semillas.
* Esperar el crecimiento de los cultivos.
* Aplicar fertilizantes y boosts.
* Cosechar.
* Obtener productos y nuevas semillas.
* Vender productos.
* Ganar dinero.
* Comprar nuevos terrenos.
* Comprar casas que desbloquean más plots.
* Progresar económicamente.
* Eventualmente interactuar con otros jugadores.
* Crear una economía entre jugadores.
* Comprar y vender propiedades.
* Tener diferentes tipos de propiedades y actividades.

El juego debe sentirse como una combinación de:

**cozy farming game + life simulation + economy game + multiplayer management game.**

No debe parecer un juego infantil. Debe sentirse como un producto moderno, pulido y potencialmente escalable.

---

# 2. OBJETIVO VISUAL

Quiero utilizar **NEUMORPHISM** como lenguaje visual principal.

La interfaz debe transmitir:

* tranquilidad
* progreso
* comodidad
* naturaleza
* tecnología
* organización
* sensación de propiedad
* economía
* crecimiento

El jugador debe sentir que está administrando su propia pequeña vida dentro de un mundo vivo.

El diseño debe ser moderno y limpio, pero no excesivamente minimalista.

Debe tener suficiente personalidad para sentirse como un videojuego y no como un dashboard empresarial.

---

# 3. ESTILO NEUMORFISTA

Utiliza neumorfismo de manera elegante y moderada.

NO quiero una interfaz completamente plana.

Utiliza:

* superficies suaves
* tarjetas elevadas
* sombras externas suaves
* sombras internas sutiles
* botones con apariencia física
* bordes redondeados
* profundidad visual
* iluminación suave
* pequeños cambios de elevación al interactuar

Los componentes deben parecer ligeramente elevados sobre la superficie.

Los botones deben dar la sensación de que pueden ser presionados físicamente.

Cuando un botón está activo:

* reducir ligeramente la sombra exterior
* agregar una sombra interior
* generar sensación de "pressed state"

Cuando una tarjeta está seleccionada:

* aumentar ligeramente el contraste
* utilizar una sombra más definida
* agregar un pequeño acento de color

Evitar el neumorfismo extremo que dificulte la accesibilidad.

El texto debe mantener excelente contraste.

---

# 4. PALETA DE COLORES

La paleta debe estar inspirada en naturaleza y agricultura, pero combinada con tonos pastel modernos.

### COLOR BASE

Utiliza como base un **verde salvia muy claro / verde grisáceo**.

Color principal de superficie:

`#DDE7DF`

Alternativas cercanas:

`#E2EBE4`
`#D8E3DA`

Este color debe dominar:

* background
* paneles
* tarjetas
* sidebar
* superficies principales

---

## COLORES PRINCIPALES

### Verde agrícola

`#6FAF78`

Utilizar para:

* acciones principales
* cultivos saludables
* progreso
* botones principales
* dinero ganado
* estados positivos

### Verde oscuro

`#315C3C`

Utilizar para:

* títulos
* textos importantes
* iconos principales
* navegación activa

---

## ACENTOS

### Amarillo / dorado

`#F2C75C`

Representa:

* dinero
* monedas
* recompensas
* crecimiento
* acciones especiales

### Naranja

`#E99A5B`

Representa:

* advertencias
* acciones secundarias
* cultivos listos
* eventos

### Azul cielo

`#72AFC4`

Representa:

* información
* estadísticas
* agua
* tiempo
* sistemas secundarios

### Rosa suave

`#D98FA3`

Utilizar ocasionalmente para:

* eventos
* elementos sociales
* decoración
* interacción entre jugadores

No utilizar todos los colores al mismo tiempo.

La interfaz debe mantener una apariencia coherente y tranquila.

---

# 5. SOMBRAS

El neumorfismo debe utilizar sombras suaves.

Ejemplo conceptual:

Dark shadow:

`rgba(110, 125, 115, 0.25)`

Light shadow:

`rgba(255, 255, 255, 0.75)`

No utilizar sombras negras fuertes.

Las sombras deben integrarse con el color del background.

---

# 6. TIPOGRAFÍA

Utilizar una fuente moderna, amigable y altamente legible.

Preferencias:

* Nunito Sans
* Inter
* Manrope
* DM Sans

Los títulos pueden utilizar una variante ligeramente más redondeada.

Evitar fuentes excesivamente infantiles.

Jerarquía:

### H1

Nombre de la sección / jugador.

### H2

Nombre de tarjetas y propiedades.

### Body

Información general.

### Small

Información secundaria.

### Numbers

Los números importantes como dinero, nivel, producción y tiempo deben tener una presencia visual fuerte.

---

# 7. LAYOUT PRINCIPAL

La interfaz está diseñada principalmente para **pantallas de computadora / desktop**.

Utilizar aproximadamente:

**1440 × 900 px**

La aplicación debe tener tres grandes zonas:

### SIDEBAR IZQUIERDO

Ancho aproximado:

**230–260 px**

Debe contener:

* Farming Life logo
* perfil del jugador
* navegación
* botones principales

Ejemplo:

Dashboard
Farm
Properties
Market
Inventory
Community
Jobs
Settings

El elemento activo debe destacarse mediante:

* fondo ligeramente elevado
* color verde
* icono
* pequeña sombra

---

# 8. HEADER

En la parte superior:

### izquierda

Título de la página.

Ejemplo:

**My Farm**

### derecha

Mostrar:

* dinero
* nivel
* avatar
* notificaciones
* configuración

El dinero debe ser visualmente importante.

Ejemplo:

`$ 1,250`

con un pequeño icono de moneda.

---

# 9. PÁGINA PRINCIPAL — FARM

La pantalla principal debe mostrar la propiedad del jugador.

Diseñar una gran sección de agricultura.

Debe contener:

### PROPERTY HEADER

Nombre de la propiedad:

**Green Valley Farm**

Información:

Level 3
12 plots
$2,450 value

---

# 10. SISTEMA DE PLOTS

Los plots son el elemento central del juego.

Mostrar los terrenos como tarjetas o pequeños módulos agrícolas.

Cada plot debe ser claramente identificable.

Ejemplo:

┌─────────────────┐
│     PLOT 01     │
│                 │
│    🌱 Crop      │
│                 │
│   Growing...    │
│                 │
│  24m 35s        │
└─────────────────┘

Cada plot puede tener diferentes estados.

### EMPTY

Mostrar:

🌱

**Empty Plot**

Botón:

**Plant**

---

### GROWING

Mostrar:

* cultivo
* progreso
* tiempo restante
* progreso visual

Ejemplo:

**Carrot**

Growing...

`72%`

`12m 32s`

---

### READY

El plot debe destacar visualmente.

Mostrar:

**Ready to Harvest**

Botón grande:

**HARVEST**

Utilizar el color verde / amarillo de forma llamativa pero elegante.

---

# 11. PLANTAR

Cuando el usuario presiona **Plant**, abrir un modal neumorfista.

Título:

**Choose a Crop**

Mostrar una cuadrícula de cultivos.

Cada cultivo debe ser una tarjeta:

### CARROT

🌱

Growth
15 min

Yield
x4

Seeds
Available

Button:

**Plant**

Los cultivos bloqueados NO deben estar ocultos.

Todos los cultivos están desbloqueados desde el comienzo, pero deben tener diferentes precios de semillas.

Los cultivos caros deben mostrar claramente su precio.

---

# 12. COSECHA

Cuando un cultivo está listo:

El usuario presiona:

**Harvest**

Mostrar una pequeña animación visual:

* crop icon
* coins
* seeds
* yield

Ejemplo:

**Harvest Complete**

+5 Carrots
+2 Carrot Seeds
+$25

La animación debe sentirse satisfactoria.

---

# 13. FERTILIZER / BOOST

Cada plot puede recibir fertilizante.

Mostrar una pequeña acción:

**Boost**

Al abrir:

**Choose Fertilizer**

Ejemplo:

### BASIC FERTILIZER

Growth time:

-10%

### PREMIUM FERTILIZER

Growth time:

-25%

### YIELD BOOST

Yield:

+20%

El sistema debe ser visualmente fácil de entender.

---

# 14. CASAS Y PROPIEDADES

El jugador comienza con una pequeña propiedad.

Inicialmente tiene:

**3 plots**

Para conseguir más terrenos, necesita comprar propiedades/casas.

Crear una sección:

**Properties**

Mostrar propiedades como tarjetas grandes.

Ejemplo:

### COUNTRY HOUSE

🏡

Plots:

+5

Price:

$2,500

Button:

**Buy**

Tipos de propiedades:

* Country houses
* Suburban houses
* Apartments
* Offices
* State buildings

Cada propiedad debe tener una identidad visual diferente.

No es necesario mostrar una posición física dentro de un mapa.

Las propiedades funcionan como paquetes que proporcionan determinada cantidad de plots.

---

# 15. ECONOMÍA

Crear una sección **Market**.

Debe permitir visualizar:

* productos
* semillas
* precios
* inventario
* comprar
* vender

Ejemplo de tarjeta:

### CARROT

Current price:

$5

Your stock:

24

Buttons:

**SELL**

**BUY**

El dinero debe estar siempre visible en la interfaz.

---

# 16. INVENTARIO

Crear una página:

**Inventory**

Organizada por categorías:

### Seeds

### Crops

### Fertilizers

### Resources

### Items

Utilizar tarjetas neumorfistas pequeñas.

Cada item debe mostrar:

icono
nombre
cantidad
valor

---

# 17. PLAYER PROFILE

El jugador debe tener un perfil visible.

Mostrar:

Avatar

**Briant**

Level 4

Experience:

`████████░░ 80%`

Money:

`$4,520`

Properties:

3

Plots:

12

Crops harvested:

248

El perfil debe sentirse como una identidad dentro del mundo del juego.

---

# 18. PROGRESIÓN

Crear un sistema de nivel.

El jugador debe poder ver claramente:

Current Level

Experience

Next Level

Rewards

Ejemplo:

### LEVEL 5

Next reward:

+2 plots

`1,250 / 2,000 XP`

Utilizar una barra de progreso neumorfista.

---

# 19. MULTIPLAYER

Aunque la agricultura es el núcleo inicial, el diseño debe estar preparado para multiplayer.

Crear navegación para:

**Community**

Mostrar:

* jugadores
* amigos
* rankings
* actividad
* mercado
* propiedades
* trabajos

Ejemplo:

### PLAYER MARKET

Briant is selling:

50 Wheat

$4 each

**BUY**

---

# 20. SISTEMA DE TRABAJOS

Más adelante los jugadores podrán trabajar para otros jugadores.

Crear una sección:

**Jobs**

Ejemplos:

Farm Worker
Harvest Assistant
Delivery
Construction
Property Manager

Cada trabajo debe mostrarse como una tarjeta.

Ejemplo:

### HARVEST ASSISTANT

Farm:

Green Valley

Reward:

$75

Duration:

20 min

Button:

**Apply**

---

# 21. DASHBOARD

Crear un dashboard que resuma la vida del jugador.

Debe mostrar:

### MONEY

$4,520

### LEVEL

Level 4

### FARM

12 plots

### READY CROPS

3

### ACTIVE CROPS

7

### DAILY INCOME

+$320

Después:

**Farm Overview**

Mostrar los plots.

Después:

**Recent Activity**

* Harvested Wheat
* Bought Carrot Seeds
* Purchased Country House
* Sold Corn

---

# 22. COMPONENTES

Todos los componentes deben compartir el mismo lenguaje visual.

Crear:

* neumorphic cards
* neumorphic buttons
* toggle switches
* sliders
* progress bars
* modals
* dropdowns
* input fields
* navigation items
* badges
* notifications
* tooltips
* inventory cards
* crop cards
* property cards
* player cards

Todos deben tener:

* border-radius consistente
* sombras suaves
* spacing consistente
* tipografía consistente

---

# 23. ICONOGRAFÍA

Utilizar iconos simples y modernos.

Preferir:

* outline icons
* rounded icons
* minimal icons

Evitar iconos excesivamente detallados.

Los iconos deben utilizarse como apoyo visual, no reemplazar completamente el texto.

---

# 24. ILUSTRACIONES

La agricultura debe tener pequeños elementos visuales.

Utilizar ilustraciones suaves de:

* carrots
* wheat
* corn
* tomato
* trees
* houses
* tools
* coins
* fertilizer

Estilo:

**soft 2D illustration / modern cozy game UI**

No utilizar un estilo cartoon infantil.

---

# 25. ANIMACIONES

El diseño debe considerar microinteracciones.

Ejemplos:

Button press:

`scale 0.97`

Harvest:

crop → coins + seeds

Plant:

seed → growing crop

Purchase:

money decreases → property appears

Level up:

progress bar fills → level badge changes

Las animaciones deben ser rápidas y satisfactorias.

---

# 26. RESPONSIVE DESIGN

Aunque el diseño principal es desktop, debe poder adaptarse.

Desktop:

1440 × 900

Tablet:

1024 × 768

Mobile:

390 × 844

En mobile:

* sidebar → bottom navigation
* plots → 2-column grid
* dashboard → vertical cards
* market → stacked cards

---

# 27. UX

La interfaz debe ser extremadamente clara.

El usuario siempre debe saber:

1. Qué tiene.
2. Qué puede hacer.
3. Cuánto cuesta.
4. Qué está creciendo.
5. Cuándo estará listo.
6. Cuánto dinero tiene.
7. Qué puede comprar.
8. Qué recompensa recibirá.

No esconder acciones importantes dentro de menús innecesarios.

La acción principal de cada pantalla debe ser obvia.

---

# 28. PERSONALIDAD DEL DISEÑO

El diseño debe transmitir:

**"This is my little life."**

No debe parecer simplemente un juego de agricultura.

Debe parecer un mundo donde el jugador está construyendo algo propio.

La progresión visual debe pasar de:

🌱 Small farm

↓

🏡 Property

↓

🌾 Bigger farm

↓

🏘️ Multiple properties

↓

🏢 Business

↓

🌎 Multiplayer economy

El diseño debe poder crecer junto con el juego.

---

# 29. REFERENCIA DE ATMÓSFERA

Imaginar una mezcla visual entre:

* modern farming simulator
* cozy game
* financial dashboard
* life simulation
* modern web application
* soft neumorphism

Pero NO copiar ninguna interfaz existente.

Crear una identidad visual completamente original para **Farming Life**.

---

# 30. REGLAS IMPORTANTES

NO utilizar:

* fondos completamente blancos
* negro puro
* sombras negras fuertes
* exceso de gradientes
* glassmorphism como estilo principal
* exceso de colores
* interfaces demasiado infantiles
* demasiados bordes
* demasiadas animaciones
* texto pequeño
* exceso de información

SÍ utilizar:

* neumorfismo
* verde salvia
* verde agrícola
* amarillo dorado
* naranja suave
* azul cielo
* superficies suaves
* sombras naturales
* grandes espacios
* rounded corners
* jerarquía visual clara
* ilustraciones agrícolas
* microinteracciones
* sensación de profundidad

---

# 31. ENTREGABLE VISUAL

Genera un **high-fidelity desktop UI design** para Farming Life.

Mostrar como mínimo:

1. Dashboard
2. Farm / Plots
3. Plant Crop Modal
4. Harvest State
5. Properties / Houses
6. Market
7. Inventory
8. Player Profile
9. Jobs
10. Community

La pantalla principal debe ser la pieza visual más importante.

Utilizar una resolución conceptual de:

**1440 × 900**

El resultado debe parecer un videojuego real que podría convertirse en un producto comercial.

Prioridad absoluta:

**UI/UX + neumorphism + claridad + agricultura + economía + progresión + personalidad.**

La interfaz debe verse **premium, moderna, acogedora y jugable**.
