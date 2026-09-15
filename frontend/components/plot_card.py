import flet as ft
from datetime import datetime


class PlotCard(ft.Container):

    def __init__(self, plot, active_crop=None, on_click_plant=None, on_click_harvest=None):
        super().__init__()

        self.plot = plot
        self.active_crop = active_crop
        self.on_click_plant = on_click_plant
        self.on_click_harvest = on_click_harvest

        self.width = 100
        self.height = 100
        self.border_radius = 10
        self.padding = 8

        plot_name = plot.get("name", "Plot")

        # Si tiene cultivo activo
        if active_crop:
            crop_type = active_crop.get("crop_types", {})
            crop_name = crop_type.get("name", "Unknown")
            ready_at = active_crop.get("ready_at", "")

            ready_at_dt = datetime.fromisoformat(ready_at.replace("Z", "+00:00"))
            now = datetime.utcnow().replace(tzinfo=ready_at_dt.tzinfo)

            if now >= ready_at_dt:
                self.bgcolor = ft.Colors.AMBER_100
                status_text = "Ready!"
                status_color = ft.Colors.ORANGE
                self.on_click = lambda e: self._on_harvest_click()
            else:
                self.bgcolor = ft.Colors.GREEN_100
                status_text = "Growing"
                status_color = ft.Colors.GREEN
                time_left = ready_at_dt - now
                hours = time_left.seconds // 3600
                minutes = (time_left.seconds % 3600) // 60
                crop_name = f"{crop_name} ({hours}h {minutes}m)"

            self.content = ft.Column(
                controls=[
                    ft.Text(
                        plot_name,
                        size=14,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Text(
                        crop_name,
                        size=12,
                    ),
                    ft.Text(
                        status_text,
                        size=11,
                        color=status_color,
                        weight=ft.FontWeight.BOLD,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=2,
            )
        else:
            self.bgcolor = ft.Colors.GREY_200
            self.on_click = lambda e: self._on_plant_click()

            self.content = ft.Column(
                controls=[
                    ft.Text(
                        plot_name,
                        size=14,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Text(
                        "Empty",
                        size=12,
                        color=ft.Colors.GREY,
                    ),
                    ft.Text(
                        "Click to plant",
                        size=10,
                        color=ft.Colors.GREY_700,
                        italic=True,
                    ),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=2,
            )

    def _on_plant_click(self):
        if self.on_click_plant:
            self.on_click_plant(self.plot["id"])

    def _on_harvest_click(self):
        if self.on_click_harvest:
            self.on_click_harvest(self.active_crop["id"])
