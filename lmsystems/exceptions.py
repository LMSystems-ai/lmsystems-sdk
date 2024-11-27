class LmsystemsError(Exception):
    """Base exception for lmsystems SDK."""
    pass

class InvalidAPIKeyError(LmsystemsError):
    """Raised when an invalid API key is provided."""
    pass

class GraphNotPurchasedError(LmsystemsError):
    """Raised when the graph has not been purchased by the user."""
    pass

class GraphNotFoundError(LmsystemsError):
    """Raised when the graph does not exist."""
    pass

class BackendAPIError(LmsystemsError):
    """Raised for generic backend API errors."""
    pass
