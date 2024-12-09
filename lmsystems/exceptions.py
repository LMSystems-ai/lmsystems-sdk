class LmsystemsError(Exception):
    """Base exception for lmsystems SDK.

    All exceptions specific to the lmsystems SDK inherit from this base class.
    """
    pass

class AuthenticationError(LmsystemsError):
    """Raised when there are authentication or authorization issues.

    This exception occurs when:
    - The API key is missing, invalid, or revoked
    - The access token is invalid or expired
    - The user doesn't have permission to access a graph

    To get your API key, visit: https://www.lmsystems.ai/account
    """
    def __init__(self, message: str):
        super().__init__(f"{message} To get your API key, visit: https://www.lmsystems.ai/account")

class GraphError(LmsystemsError):
    """Raised when there are issues with graph operations.

    This exception occurs when:
    - The graph doesn't exist
    - The graph hasn't been purchased
    - There are issues executing the graph
    - Graph configuration is invalid
    """
    pass

class InputError(LmsystemsError):
    """Raised when there are issues with the input provided.

    This exception occurs when:
    - Required input parameters are missing
    - Input values are invalid
    - State values are incompatible
    - Configuration values are incorrect
    """
    pass

class APIError(LmsystemsError):
    """Raised when there are issues with API communication.

    This exception occurs when:
    - The backend service returns an error
    - Network connectivity issues occur
    - Rate limits are exceeded
    - Unexpected API responses are received
    """
    pass
