import flet as ft

from backend.services.player_service import (
    get_player,
    create_new_player,
)


def main(page: ft.Page):
    page.title = "Supabase Player Viewer"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # Input for player ID
    player_id_input = ft.TextField(
        label="Player ID",
        value="0",
        width=200,
    )

    # Input for creating a new player
    name_input = ft.TextField(
        label="Name",
        value="New Player",
        width=200,
    )

    # Display area
    player_info = ft.Column()

    # Get player
    def fetch_player(e):
        try:
            player_id = int(player_id_input.value)

            player = get_player(player_id)

            player_info.controls.clear()

            if player:
                player_info.controls.append(
                    ft.Text(f"ID: {player['id']}", size=20)
                )
                player_info.controls.append(
                    ft.Text(f"Name: {player['name']}", size=20)
                )
                player_info.controls.append(
                    ft.Text(f"Money: ${player['money']}", size=20)
                )
                player_info.controls.append(
                    ft.Text(f"Level: {player['level']}", size=20)
                )
            else:
                player_info.controls.append(
                    ft.Text(
                        "Player not found",
                        size=20,
                        color="red",
                    )
                )

            page.update()

        except ValueError:
            player_info.controls.clear()
            player_info.controls.append(
                ft.Text(
                    "Please enter a valid player ID",
                    size=20,
                    color="red",
                )
            )
            page.update()

        except Exception as ex:
            player_info.controls.clear()
            player_info.controls.append(
                ft.Text(
                    f"Error: {str(ex)}",
                    size=20,
                    color="red",
                )
            )
            page.update()

    fetch_button = ft.ElevatedButton(
        "Get Player",
        on_click=fetch_player,
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
                    size=20,
                    color="green",
                )
            )

            player_info.controls.append(
                ft.Text(
                    f"ID: {new_player['id']}",
                    size=20,
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

            name_input.value = "New Player"

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
        bgcolor="green",
        color="black",
    )

    # Initial load
    fetch_player(None)

    page.add(
        ft.Column(
            [
                ft.Text(
                    "Supabase Player Viewer",
                    size=30,
                    weight=ft.FontWeight.BOLD,
                ),

                ft.Row(
                    [player_id_input, fetch_button],
                    alignment=ft.MainAxisAlignment.CENTER,
                ),

                ft.Divider(),

                ft.Text(
                    "Create New Player",
                    size=20,
                    weight=ft.FontWeight.W_500,
                ),

                ft.Row(
                    [name_input, create_button],
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