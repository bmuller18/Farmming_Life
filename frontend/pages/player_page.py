import flet as ft

from backend.services.house_service import get_houses_by_player
from backend.services.plot_service import get_plots_by_house

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
                "My Farms",
                size=6,
                weight=ft.FontWeight.BOLD,
            ),
        ]

        self.load_houses()

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
                plot_cards.append(
                    PlotCard(plot)
                )

            self.controls.append(
                ft.Row(
                    controls=plot_cards,
                    alignment=ft.MainAxisAlignment.CENTER,
                    spacing=20,
                    wrap=True,
                )
            )