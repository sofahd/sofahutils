"""
Shared exceptions for the SOFAH framework.

These used to be re-declared in every module (recon/utils, log-api/utils,
api/honeypot). They live here now so there is a single definition.
"""


class PathIsNoFileException(Exception):
    """Exception raised when a path does not point to a file."""
    pass


class WrongFileTypeException(Exception):
    """Exception raised when a file does not have the expected extension."""
    pass


class InvalidConfigException(Exception):
    """Exception raised when a config is missing an expected section/option."""
    pass
