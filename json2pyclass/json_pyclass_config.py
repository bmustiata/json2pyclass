class JsonPyClassConfig:
    def __init__(self,
                 *,
                 output_name: str,
                 mode: str,
                 optionals: bool) -> None:
        self.output_name = output_name
        self.mode = mode
        self.optionals = optionals
