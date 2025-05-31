from typing import Dict


class BaseValidator:
    def validate(self, data: Dict, request) -> Dict:
        raise NotImplementedError
