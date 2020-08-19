class JsonPyClassConfig:
    def __init__(self,
                 *,
                 output_name: str,
                 mode: str,
                 disable_optionals: bool) -> None:
        self.output_name = output_name
        self.mode = mode
        self.disable_optionals = disable_optionals
