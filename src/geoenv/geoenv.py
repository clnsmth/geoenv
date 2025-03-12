"""For geoenv related operations."""


def hello_world(message: str, emphasize: bool = False) -> str:
    """
    :param: message: str: The message to be returned.
    :param: emphasize: bool: Whether to emphasize the message.

    :returns: str: The message.
    """
    if emphasize:
        return message + "!"
    return message
