import flet as ft
from backend.supabase_client import get_player_by_id, get_supabase_client

def main(page: ft.Page):
    page.title = "Supabase Player Viewer"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER

    # Input for player ID
    player_id_input = ft.TextField(label="Player ID", value="0", width=200)

    # Display area for player info
    player_info = ft.Column()

    # Button to fetch player data
    def fetch_player(e):
        try:
            player_id = int(player_id_input.value)
            player = get_player_by_id(player_id)

            player_info.controls.clear()

            if player:
                player_info.controls.append(
                    ft.Text(f"ID: {player['id']}", size=20)
                )
                player_info.controls.append(
                    ft.Text(f"Name: {player['name']}", size=20)
                )
                player_info.controls.append(
                    ft.Text(f"Money: {player['money']}", size=20)
                )
                player_info.controls.append(
                    ft.Text(f"Level: {player['level']}", size=20)
                )
            else:
                player_info.controls.append(
                    ft.Text("Player not found", size=20, color=ft.colors.RED)
                )

            page.update()
        except ValueError:
            player_info.controls.clear()
            player_info.controls.append(
                ft.Text("Please enter a valid player ID", size=20, color=ft.colors.RED)
            )
            page.update()
        except Exception as ex:
            player_info.controls.clear()
            player_info.controls.append(
                ft.Text(f"Error: {str(ex)}", size=20, color=ft.colors.RED)
            )
            page.update()

    fetch_button = ft.ElevatedButton("Get Player", on_click=fetch_player)

    # Initial load with player ID 0
    fetch_player(None)

    page.add(
        ft.Column(
            [
                ft.Text("Supabase Player Viewer", size=30, weight=ft.FontWeight.BOLD),
                ft.Row([player_id_input, fetch_button], alignment=ft.MainAxisAlignment.CENTER),
                ft.Divider(),
                player_info
            ],
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        )
    )

if __name__ == "__main__":
    ft.app(target=main)