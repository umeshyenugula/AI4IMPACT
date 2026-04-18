"""In-memory platform state used to connect all capabilities in one runtime."""


class PlatformState:
    def __init__(self) -> None:
        self.artisans: dict[int, dict] = {}
        self.portfolios: dict[int, list[dict]] = {}
        self.learning_paths: dict[int, list[dict]] = {}
        self.demand_forecasts: dict[int, dict] = {}
        self.telemetry_batches: list[dict] = []
        self.provenance_certificates: dict[str, dict] = {}
        self.escrow_contracts: dict[str, dict] = {}
        self.next_artisan_id = 1
        self.next_portfolio_id = 1
        self.next_learning_path_id = 1


state = PlatformState()
