class EnvError(Exception):
    """
    An exception occurs when there are errors
    related to environment variables.
    """
    pass


class EmptyDataError(Exception):
    """An exception means there is no data where it should be."""
