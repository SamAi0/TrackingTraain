class RailwayAPIException(Exception):
    def __init__(self, message, error_code="EXTERNAL_SERVICE_ERROR", status_code=503):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        super().__init__(self.message)
