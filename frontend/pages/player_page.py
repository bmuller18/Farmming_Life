import flet as ft

from frontend.components.player_header import PlayerHeader
from frontend.components.plot_card import PlotCard


class PlayerPage(ft.Column):

    def __init__(self, player):

        super().__init__()

        self.player = player
        self.horizontal_alignment = ft.CrossAxisAlignment.CENTER

        self.controls = [
            PlayerHeader(player),

            ft.Divider(),

            ft.Text(
                "My Farm",
                size=26,
                weight=ft.FontWeight.BOLD,
            ),

            ft.Row(
                controls=[
                    PlotCard(1),
                    PlotCard(2),
                    PlotCard(3),
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20,
            ),
        ]