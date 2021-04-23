# © 2021 Nokia
#
# Licensed under the Apache license, version 2.0
# SPDX-License-Identifier: Apache-2.0

"""Abstract class to handle connection related information and functions."""
from abc import ABC, abstractmethod


class TerminalConnectionException(Exception):
    """This exception is raised when there is error with ssh connection."""


class TooManyRetriesException(Exception):
    """This exception is raised when there is error with ssh connection."""


class IConnection(ABC):
    """Abstract class provides terminal and some functionality for specific node."""

    def __init__(self, hostname, port, username, password, pkey=None):
        """Initialize."""
        self._username = username
        self._port = port
        self._hostname = hostname
        self._password = password
        self._key = pkey

    @property
    def hostname(self):
        """Public access for hostname."""
        return self._hostname

    @property
    def username(self):
        """Public access for username."""
        return self._username

    @property
    def password(self):
        """Public access for password."""
        return self._password

    @abstractmethod
    def is_active(self):
        """Check if connection is active."""
        pass

    @abstractmethod
    def close_session(self):
        """Close the connection."""
        pass

    @abstractmethod
    def connect(self, via=None):
        """Interface method for handling connecting and reconnecting.
        Implement needed functionalities and method calls.
        """
        pass

    def execute(self, command):
        """Wrap the execution function."""
        try:
            return self._execute_command(command)
        except Exception as e:
            raise e

    @abstractmethod
    def _execute_command(self, command):
        """Execute command on the remote host.
        Implement needed functionality.
        """
        pass
