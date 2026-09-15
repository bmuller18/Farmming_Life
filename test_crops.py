"""
Test script para demostrar el sistema de Crops.
"""
from backend.services.crop_service import (
    get_all_crop_types,
    get_active_crop,
    plant_crop_in_plot,
    harvest_crop_from_plot,
)
from backend.services.house_service import get_houses_by_player
from backend.services.plot_service import get_plots_by_house

PLAYER_ID = 2  # Cambiar al ID de tu jugador

print("=" * 60)
print("🌾 SISTEMA DE CROPS - TEST")
print("=" * 60)

# 1. Obtener tipos de cultivos
print("\n1️⃣  Tipos de cultivos disponibles:")
crop_types = get_all_crop_types()
for ct in crop_types:
    hours = ct['growth_time'] // 3600
    minutes = (ct['growth_time'] % 3600) // 60
    print(f"   - {ct['name']}: {hours}h {minutes}m, Yield: {ct['base_yield']}")

# 2. Obtener casas del jugador
print(f"\n2️⃣  Casas del jugador {PLAYER_ID}:")
houses = get_houses_by_player(PLAYER_ID)
if not houses:
    print("   ❌ No houses found")
    exit(1)

for house in houses:
    print(f"   - {house['name']} (ID: {house['id']})")

# 3. Obtener plots
house_id = houses[0]['id']
print(f"\n3️⃣  Plots de la casa {house_id}:")
plots = get_plots_by_house(house_id)

if not plots:
    print("   ❌ No plots found")
    exit(1)

for plot in plots:
    active_crop = get_active_crop(plot['id'])
    if active_crop:
        crop_type = active_crop.get('crop_types', {})
        print(f"   - {plot['name']}: {crop_type.get('name', 'Unknown')} (Growing)")
    else:
        print(f"   - {plot['name']}: Empty")

# 4. Plantar un cultivo
plot_id = plots[0]['id']
crop_type_id = crop_types[0]['id']

print(f"\n4️⃣  Plantando {crop_types[0]['name']} en {plots[0]['name']}...")
try:
    crop = plant_crop_in_plot(plot_id, crop_type_id)
    print(f"   ✅ Cultivo plantado!")
    print(f"   ID: {crop['id']}")
    print(f"   Plantado: {crop['planted_at']}")
    print(f"   Listo para cosechar: {crop['ready_at']}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("✅ Test completado!")
print("=" * 60)
