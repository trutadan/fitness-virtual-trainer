class LandmarkExtractionError(Exception):
    """Exception raised for errors in the landmark extraction process."""
    def __init__(self, message="Error extracting landmarks"):
        self.message = message
        super().__init__(self.message)


class AngleComputationError(Exception):
    """Exception raised for errors in the angle computation process."""
    def __init__(self, message="Error computing angles"):
        self.message = message
        super().__init__(self.message)