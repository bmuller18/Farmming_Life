# Farming Life

Farming Life es un RPG agrícola multiplayer en el que los jugadores pueden adquirir casas de campo y utilizar sus plots para cultivar diferentes crops. El sistema está diseñado para expandirse posteriormente hacia economía, trabajos, propiedades y otras actividades.

## Current Status

**Status:** 🟢 Core Farming Design  
**Version:** 0.1  
**Database:** Supabase  
**Frontend:** Flet  
**Architecture:** Expandable  
**Plots:** Designed  
**Country Houses:** Designed  
**Crops:** Partially Designed  
**Crop Boosts:** Partially Designed  
**Property Sales:** Future
**Rentals:** Future  
**Jobs:** Future  
**Multiplayer Interaction:** Future  

---

# 1. 🌍 Game Vision

Farming como una de las bases principales del juego.  
Los jugadores pueden adquirir casas de campo.  
Las casas contienen una cantidad determinada de plots.  
Los plots se utilizan exclusivamente para agricultura.  
Los crops se cultivan individualmente en los plots.  
El sistema debe poder crecer hacia futuras mecánicas multiplayer y económicas.

---

# 2. 🏡 Country Houses

Una Casa de Campo es una propiedad que el jugador puede adquirir.  
Cada casa tiene:  
* ID  
* Nombre  
* Precio inicial  
* Cantidad determinada de plots  
* Propietario  

Características:  
* Cada casa tiene una cantidad fija de plots.  
* Los plots vienen incorporados a la casa.  
* Los plots se crean automáticamente cuando el jugador adquiere la casa.  
* La cantidad de plots no puede aumentar.  
* Un jugador puede adquirir varias casas de campo.  
* Una casa puede cultivar cualquier crop.  
* La casa es la propiedad principal; los plots no se compran individualmente.  
* La venta de casas se implementará en el futuro y NO debe diseñarse todavía.

### Representación visual
```
PLAYER
↓
COUNTRY HOUSE
↓
PLOTS
↓
CROPS
```

> **NOTE**  
> Un jugador puede poseer múltiples Country Houses, cada una con su propio conjunto fijo de plots.

---

# 3. 🌱 Plots

Un Plot es una superficie destinada exclusivamente al cultivo.  
Características actuales:  
* Todos los plots tienen el mismo tamaño.  
* No tienen posición dentro del mundo.  
* No tienen edificios.  
* No tienen almacenamiento.  
* No tienen animales.  
* No tienen decoración.  
* No pueden venderse individualmente.  
* Pertenecen a una Country House.  
* Cada Plot puede tener un solo crop activo a la vez.  
* Después de cosechar, el Plot queda disponible para plantar nuevamente.  
* Puede plantarse el mismo crop u otro crop posteriormente.  

Datos actualmente definidos:  
* ID  
* House ID  
* Name  
* Created At  
* Updated At  

El nombre del Plot debe tener un nombre por defecto, por ejemplo:  
* Plot 1  
* Plot 2  
* Plot 3  

El jugador podrá cambiar el nombre posteriormente.

> **IMPORTANTE**  
> No agregues `player_id` al Plot en esta etapa.  
> El propietario del Plot se determina mediante:  
> Plot → Country House → Player

---

# 4. 🌾 Crops

Una Country House puede cultivar cualquier crop.  
Cada Plot puede tener solamente un crop activo simultáneamente.  

Ejemplo:  
```
Country House
├── Plot 1 → Wheat
├── Plot 2 → Corn
├── Plot 3 → Wheat
├── Plot 4 → Potato
└── Plot 5 → Empty
```

Dos o más plots pueden cultivar el mismo crop simultáneamente.  
Después de cosechar:  
```
Crop
↓
Harvest
↓
Plot becomes available
↓
New crop can be planted
```

El sistema de crops deberá guardar posteriormente información relacionada con el ciclo de cultivo, como:  
* crop type  
* planted time  
* ready time  
* harvest information  

Pero NO inventes todavía el esquema final de la base de datos de crops.

---

# 5. 🚀 Crop Boosts

Los Boosts afectan al **crop**, no al Plot.  
Actualmente existen dos conceptos de boost:

### Yield Boost
Aumenta la cantidad obtenida al cosechar.  
Ejemplo conceptual:  
Normal: 5 crops  
Con boost: +20% yield  

### Growth Time Reduction
Reduce el tiempo necesario para que el crop esté listo.  
Ejemplo conceptual:  
Normal: 60 minutos  
Con boost: -20% growth time  

> **IMPORTANTE**  
> Todavía no hemos definido:  
> * cómo se obtienen los boosts  
> * cuánto duran  
> * si son consumibles  
> * si son permanentes  
> * si pueden combinarse  
> * qué valores máximos tienen  
> No inventes esas reglas.

---

# 6. 🧩 Current Relationships

```
PLAYER
↓ owns
COUNTRY HOUSE
↓ contains
PLOTS
↓ grows
CROP
```

* Un Player puede tener múltiples Country Houses.  
* Una Country House tiene una cantidad fija de Plots.  
* Una Country House puede cultivar cualquier Crop.  
* Un Plot pertenece a una sola Country House.  
* Un Plot puede tener un solo Crop activo.  
* Un Crop puede repetirse en diferentes Plots.

---

# 7. 🗄️ Current Data Model

### Player
Sistema existente.

### Country House
Campos actualmente definidos:  
* id  
* name  
* price  
* plot_count  
* player_id  
* created_at  
* updated_at  

### Plot
Campos actualmente definidos:  
* id  
* house_id  
* name  
* created_at  
* updated_at  

### Crop
Todavía en diseño.  
No inventar campos definitivos.  

> Database implementation will be designed separately after the gameplay model is approved.

---

# 8. 🔐 Ownership

Actualmente:  
```
Player
↓
owns
Country House
↓
contains
Plots
```

No agregar todavía:  
* rentals  
* contracts  
* marketplace  
* transfers  
* direct player-to-player sales  

Esas mecánicas serán diseñadas posteriormente.

---

# 9. 🔮 Future Systems

<details>
<summary>Property Sales</summary>
Venta de Country Houses entre jugadores.  
El propietario podrá establecer un precio de venta.  
Una casa se vende junto con todos sus plots.
</details>

<details>
<summary>Rentals</summary>
Sistema de alquiler.  
Todavía no definido.
</details>

<details>
<summary>Contracts</summary>
Sistema de contratos.  
Todavía no definido.
</details>

<details>
<summary>Jobs</summary>
Los jugadores podrán trabajar en determinadas Country Houses.  
Todavía no definido.  
> Los trabajos no estarán inicialmente disponibles en los tres sistemas de farming iniciales; estarán relacionados con Country Houses adquiridas.
</details>

<details>
<summary>Multiplayer Interaction</summary>
Los jugadores podrán visitar las propiedades de otros jugadores en el futuro.  
Todavía no definido.
</details>

<details>
<summary>Buildings</summary>
Los edificios se implementarán posteriormente y serán sistemas independientes de los plots.
</details>

<details>
<summary>Storage / Farms</summary>
Los depósitos y otras estructuras agrícolas serán sistemas separados de los plots.
</details>

<details>
<summary>World Position</summary>
Los plots actualmente no tienen posición física en el mundo.  
Esto podría cambiar en el futuro.
</details>

---

# 10. 📋 Design Rules

1. A Plot is always part of a Country House.  
2. A Plot cannot be purchased independently.  
3. A Country House determines the number of Plots it contains.  
4. Plot quantity cannot be upgraded.  
5. All Plots currently have the same size.  
6. A Plot can grow only one active Crop at a time.  
7. A Crop can be replaced after harvesting.  
8. Any Crop can be planted in any Country House.  
9. Crop Boosts affect the Crop.  
10. Buildings are not part of the Plot system.  
11. Storage is not part of the Plot system.  
12. Future mechanics should not unnecessarily complicate the current Plot model.

> **NOTE**  
> Estas reglas son invariables para la versión actual del sistema de farming.

---

# 11. 🧠 Design Decisions

| Decision                     | Status   | Notes                         |
| ---------------------------- | -------- | ----------------------------- |
| Plots belong to houses       | Approved | Core design                   |
| Houses have fixed plot count | Approved | Cannot be increased           |
| Plots have no world position | Approved | Current version               |
| All plots have same size     | Approved | Current version               |
| One active crop per plot     | Approved | Crop can change after harvest |
| Houses can grow any crop     | Approved | No crop restrictions          |
| Plot can be renamed          | Approved | Default name required         |
| Plot status field            | Removed  | Add only if needed later      |
| Plot player_id               | Not used | Ownership comes through house |
| House sales                  | Future   | Not designed yet              |
| Rentals                      | Future   | Not designed yet              |
| Contracts                  | Future   | Not designed yet              |
| Jobs                         | Future   | Not designed yet              |