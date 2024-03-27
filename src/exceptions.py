class ServerNotRunning(Exception):
    """Raised when trying to interface with a stopped server."""

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

    def __repr__(self):
        return f"<ServerNotRunning message={self.message}>"
