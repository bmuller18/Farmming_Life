import flet as ft


class CropSelectionDialog(ft.AlertDialog):

    def __init__(self, crop_types, on_select=None):
        super().__init__()

        self.crop_types = crop_types
        self.on_select = on_select
        self.title = ft.Text("Plant a Crop")

        # Crear botones para cada tipo de cultivo
        crop_buttons = []
        for crop_type in crop_types:
            name = crop_type.get("name", "Unknown")
            growth_time = crop_type.get("growth_time", 0)
            base_yield = crop_type.get("base_yield", 0)

            hours = growth_time // 3600
            minutes = (growth_time % 3600) // 60

            btn = ft.ElevatedButton(
                f"{name}\n({hours}h {minutes}m, Yield: {base_yield})",
                on_click=lambda e, ctype=crop_type: self._on_crop_selected(ctype),
                width=200,
            )
            crop_buttons.append(btn)

        self.content = ft.Column(
            controls=crop_buttons,
            scroll=ft.ScrollMode.AUTO,
            spacing=10,
        )

        self.actions = [
            ft.TextButton("Cancel", on_click=self._on_cancel),
        ]

    def _on_crop_selected(self, crop_type):
        if self.on_select:
            self.on_select(crop_type["id"])
        self.open = False

    def _on_cancel(self, e):
        self.open = False
