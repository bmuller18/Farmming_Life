import flet as ft
from datetime import datetime


class CropCard(ft.Container):

	def __init__(self, crop, on_harvest=None):
		super().__init__()

		self.crop = crop
		self.on_harvest = on_harvest

		self.width = 150
		self.height = 120
		self.border_radius = 10
		self.padding = 10

		crop_type = crop.get("crop_types", {})
		crop_name = crop_type.get("name", "Unknown")
		planted_at = crop.get("planted_at", "")
		ready_at = crop.get("ready_at", "")
		harvested_at = crop.get("harvested_at")
		yield_amount = crop.get("yield_amount", 0)

		# Determinar estado
		if harvested_at:
			self.bgcolor = ft.Colors.GREY_200
			status = "Harvested"
			status_color = ft.Colors.GREY
			details = f"Yield: {yield_amount}"
		else:
			ready_at_dt = datetime.fromisoformat(ready_at.replace("Z", "+00:00"))
			now = datetime.utcnow().replace(tzinfo=ready_at_dt.tzinfo)

			if now >= ready_at_dt:
				self.bgcolor = ft.Colors.AMBER_100
				status = "Ready!"
				status_color = ft.Colors.ORANGE
				details = "Click to harvest"
			else:
				self.bgcolor = ft.Colors.GREEN_100
				status = "Growing"
				status_color = ft.Colors.GREEN
				time_left = ready_at_dt - now
				hours = time_left.seconds // 3600
				minutes = (time_left.seconds % 3600) // 60
				details = f"{hours}h {minutes}m left"

		self.content = ft.Column(
			controls=[
				ft.Text(
					crop_name,
					size=18,
					weight=ft.FontWeight.BOLD,
				),
				ft.Text(
					status,
					size=14,
					color=status_color,
					weight=ft.FontWeight.BOLD,
				),
				ft.Text(
					details,
					size=12,
					color=ft.Colors.GREY_700,
				),
			],
			alignment=ft.MainAxisAlignment.CENTER,
			horizontal_alignment=ft.CrossAxisAlignment.CENTER,
			spacing=5,
		)

		# Si está listo, hacer clickeable
		if not harvested_at and now >= ready_at_dt:
			self.on_click = lambda e: self._harvest_click()

	def _harvest_click(self):
		if self.on_harvest:
			self.on_harvest(self.crop["id"])
