class GenericResponse:
    def __init__(self, status: str, message: str, data: dict):
        self.status = status
        self.message = message
        self.data = data

    def to_dict(self):
        return {
            "status": self.status,
            "message": self.message,
            "data": self.data
        }