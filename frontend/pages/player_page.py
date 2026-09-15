import flet as ft

from backend.services.house_service import get_houses_by_player
from backend.services.plot_service import get_plots_by_house
from backend.services.crop_service import (
    get_all_crop_types,
    get_active_crop,
    plant_crop_in_plot,
    harvest_crop_from_plot,
)

from frontend.components.player_header import PlayerHeader
from frontend.components.plot_card import PlotCard
from frontend.components.crop_selection_dialog import CropSelectionDialog


class PlayerPage(ft.Column):

    def __init__(self, player):
        super().__init__()

        self.player = player
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        self.controls = [
            PlayerHeader(player),
            ft.Divider(),
            ft.Text(
                "My Farms",
                size=20,
                weight=ft.FontWeight.BOLD,
            ),
        ]

        self.status_message = ft.Text("")
        self.load_houses()
        self.controls.append(self.status_message)

    def load_houses(self):

        player_id = self.player["id"]

        houses = get_houses_by_player(player_id)

        if not houses:
            self.controls.append(
                ft.Text(
                    "You don't own any houses yet.",
                    size=18,
                )
            )
            return

        for house in houses:

            house_name = house.get("name", "House")

            self.controls.append(
                ft.Text(
                    house_name,
                    size=22,
                    weight=ft.FontWeight.BOLD,
                )
            )

            plots = get_plots_by_house(house["id"])

            plot_cards = []

            for plot in plots:
                # Obtener cultivo activo de este plot
                active_crop = get_active_crop(plot["id"])

                plot_card = PlotCard(
                    plot,
                    active_crop=active_crop,
                    on_click_plant=self._on_plant_crop,
                    on_click_harvest=self._on_harvest_crop,
                )
                plot_cards.append(plot_card)

            self.controls.append(
                ft.Row(
                    controls=plot_cards,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20,
                    wrap=True,
                )
            )

    def _on_plant_crop(self, plot_id: int):
        """Mostrar diálogo para seleccionar cultivo a plantar."""

        try:
            # Obtener tipos de cultivos disponibles
            crop_types = get_all_crop_types()

            if not crop_types:
                self._show_message("No crops available", error=True)
                return

            # Crear y mostrar diálogo
            dialog = CropSelectionDialog(
                crop_types,
                on_select=lambda crop_type_id: self._plant_selected_crop(plot_id, crop_type_id),
            )

            self.page.dialog = dialog
            dialog.open = True
            self.page.update()

        except Exception as e:
            self._show_message(f"Error: {str(e)}", error=True)

    def _plant_selected_crop(self, plot_id: int, crop_type_id: int):
        """Plantar el cultivo seleccionado."""

        try:
            crop = plant_crop_in_plot(plot_id, crop_type_id)
            self._show_message("Crop planted successfully! 🌱", error=False)

            # Recargar la página
            self.refresh_farms()

        except Exception as e:
            self._show_message(f"Error planting crop: {str(e)}", error=True)

    def _on_harvest_crop(self, crop_id: int):
        """Cosechar un cultivo."""

        try:
            crop = harvest_crop_from_plot(crop_id)
            yield_amount = crop.get("yield_amount", 0)
            self._show_message(f"Crop harvested! Yield: {yield_amount} 🌾", error=False)

            # Recargar la página
            self.refresh_farms()

        except Exception as e:
            self._show_message(f"Error harvesting crop: {str(e)}", error=True)

    def _show_message(self, message: str, error: bool = False):
        """Mostrar mensaje temporal."""
        self.status_message.value = message
        self.status_message.color = "red" if error else "green"
        self.page.update()

    def refresh_farms(self):
        """Recargar la lista de granjas."""
        # Limpiar controles excepto header, divider y título
        self.controls = self.controls[:3]
        self.load_houses()
        self.status_message = ft.Text("")
        self.controls.append(self.status_message)
        self.page.update()
