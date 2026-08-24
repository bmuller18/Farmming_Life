import flet as ft


class PlotCard(ft.Container):

    def __init__(self, plot_number):

        super().__init__()

        self.width = 180
        self.height = 180
        self.bgcolor = ft.Colors.GREY_200
        self.border_radius = 10

        self.content = ft.Column(
            controls=[
                ft.Text(
                    f"Plot {plot_number}",
                    size=20,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(
                    "Empty",
                    size=16,
                    color=ft.Colors.GREY,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )