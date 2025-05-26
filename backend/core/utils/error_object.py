from typing import Optional, Dict, Any


class ErrorObject:
    def __init__(self, code: int, message: str, field: Optional[str] = None, details: Optional[str] = None):
        self.code = code
        self.message = message
        self.field = field
        self.details = details

    def to_dict(self) -> Dict[str, Any]:
        error = {
            "code": self.code,
            "message": self.message,
            "field": self.field,
        }
        if self.details:
            error["details"] = self.details
        return error
