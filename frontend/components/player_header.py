import flet as ft


class PlayerHeader(ft.Container):

    def __init__(self, player):

        super().__init__()

        self.padding = 20

        self.content = ft.Row(
            controls=[
                ft.Column(
                    controls=[
                        ft.Text(
                            player["name"],
                            size=28,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Row(
                            controls=[
                                ft.Text(
                                    f"Level {player['level']}",
                                    size=18,
                                ),
                                ft.Text(
                                    f"${player['money']}",
                                    size=18,
                                ),
                            ],
                            spacing=30,
                        ),
                    ],
                    spacing=5,
                ),

                ft.Container(
                    expand=True,
                ),

                ft.ElevatedButton(
                    "Menu",
                ),
            ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
        )