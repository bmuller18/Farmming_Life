import flet as ft
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.services.player_service import get_player
from frontend.pages.player_page import PlayerPage


# Player que queremos cargar al iniciar la aplicación
PLAYER_ID = 2


def main(page: ft.Page):

    page.title = "Farming Life"

    app_view = ft.Container(
        expand=True,
    )

    try:
        player = get_player(PLAYER_ID)

        if player is None:
            app_view.content = ft.Column(
                controls=[
                    ft.Text(
                        "Farming Life",
                        size=32,
                        weight=ft.FontWeight.BOLD,
                    ),
                    ft.Text(
                        f"Player {PLAYER_ID} no encontrado.",
                        size=20,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            )
        else:
            print("PLAYER LOADED:", player)

            app_view.content = PlayerPage(player)

    except Exception as ex:
        print("ERROR:", ex)

        app_view.content = ft.Column(
            controls=[
                ft.Text(
                    "Farming Life",
                    size=32,
                    weight=ft.FontWeight.BOLD,
                ),
                ft.Text(
                    f"Error loading player: {ex}",
                    color=ft.Colors.RED,
                ),
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )

    page.add(app_view)


if __name__ == "__main__":
    ft.run(main)