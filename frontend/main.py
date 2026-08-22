import flet as ft

from backend.services.player_service import create_new_player


def main(page: ft.Page):
    page.title = "Farming Life"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # Input for creating a new player
    name_input = ft.TextField(
        label="Player Name",
        value="",
        width=300,
    )

    # Display area
    player_info = ft.Column(
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )

    # Create new player
    def create_player_clicked(e):
        try:
            name = name_input.value.strip()

            if not name:
                name = "New Player"

            new_player = create_new_player(name=name)

            player_info.controls.clear()

            player_info.controls.append(
                ft.Text(
                    "Player created!",
                    size=24,
                    color="green",
                )
            )

            player_info.controls.append(
                ft.Text(
                    f"Name: {new_player['name']}",
                    size=20,
                )
            )

            player_info.controls.append(
                ft.Text(
                    f"Money: ${new_player['money']}",
                    size=20,
                )
            )

            player_info.controls.append(
                ft.Text(
                    f"Level: {new_player['level']}",
                    size=20,
                )
            )

            # Clear input
            name_input.value = ""

            page.update()

        except ValueError as ex:
            player_info.controls.clear()

            player_info.controls.append(
                ft.Text(
                    str(ex),
                    size=20,
                    color="red",
                )
            )

            page.update()

        except Exception as ex:
            player_info.controls.clear()

            player_info.controls.append(
                ft.Text(
                    f"Error creating player: {str(ex)}",
                    size=20,
                    color="red",
                )
            )

            page.update()

    create_button = ft.ElevatedButton(
        "Create Player",
        on_click=create_player_clicked,
    )

    page.add(
        ft.Column(
            [
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
                    [
                        name_input,
                        create_button,
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),

                ft.Divider(),

                player_info,
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )


if __name__ == "__main__":
    ft.app(target=main)