from backend.repositories import plot_repository


def get_plots_by_house(house_id: int):
    """Get all plots belonging to a house."""

    return plot_repository.get_plots_by_house(house_id)