import flet as ft


class PlotCard(ft.Container):

    def __init__(self, plot):
        super().__init__()

        self.plot = plot

        self.width = 80
        self.height = 80
        self.bgcolor = ft.Colors.GREY_200
        self.border_radius = 10

        plot_name = plot.get("name", "Plot")
        status = plot.get("status", "empty")

        if status == "empty":
            status_text = "Empty"
        else:
            status_text = status.capitalize()

        self.content = ft.Column(
            controls=[
                ft.Text(
                    plot_name,
                    size=20,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(
                    status_text,
                    size=16,
                    color=ft.Colors.GREY,
                ),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )