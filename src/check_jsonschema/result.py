import jsonschema

from .parsers import ParseError


class CheckResult:
    def __init__(self):
        self.validation_errors: dict[str, list[jsonschema.ValidationError]] = {}
        self.parse_errors: dict[str, list[ParseError]] = {}

    @property
    def success(self) -> bool:
        return not (bool(self.parse_errors) or bool(self.validation_errors))

    def record_validation_error(
        self, filename: str, err: jsonschema.ValidationError
    ) -> None:
        if filename not in self.validation_errors:
            self.validation_errors[filename] = []
        self.validation_errors[filename].append(err)

    def record_parse_error(self, filename: str, err: ParseError) -> None:
        if filename not in self.parse_errors:
            self.parse_errors[filename] = []
        self.parse_errors[filename].append(err)