import flet as ft

from backend.services.player_service import create_new_player
from frontend.pages.player_page import PlayerPage


def main(page: ft.Page):

    page.title = "Farming Life"

    app_view = ft.Container(
        expand=True,
    )

    name_input = ft.TextField(
        label="Player Name",
        width=300,
    )

    message = ft.Text()

    def create_player_clicked(e):

        try:

            name = name_input.value.strip()

            if not name:
                name = "New Player"

            new_player = create_new_player(name=name)

            print("PLAYER CREATED:", new_player)

            app_view.content = PlayerPage(new_player)

            page.update()

        except ValueError as ex:

            message.value = str(ex)
            message.color = ft.Colors.RED

            page.update()

        except Exception as ex:

            print("ERROR:", ex)

            message.value = f"Error creating player: {ex}"
            message.color = ft.Colors.RED

            page.update()

    create_button = ft.ElevatedButton(
    "Create Player",
    on_click=create_player_clicked,
)

    create_view = ft.Column(
        controls=[
            ft.Text(
                "Farming Life",
                size=32,
                weight=ft.FontWeight.BOLD,
            ),

            ft.Text(
                "Create your player",
                size=20,
            ),

            ft.Row(
                controls=[
                    name_input,
                    create_button,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
            ),

            message,
        ],
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    app_view.content = create_view

    page.add(app_view)


if __name__ == "__main__":
    ft.app(target=main)