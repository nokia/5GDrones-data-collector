# © 2021 Nokia
#
# Licensed under the Apache license, version 2.0
# SPDX-License-Identifier: Apache-2.0

"""Class to handle connection related information and functions."""
import io
import platform
import socket
import subprocess

import paramiko

from datacollector.collector.iconnection import IConnection


class TerminalConnectionException(Exception):
    """This exception is raised when there is error with ssh connection."""


class TooManyRetriesException(Exception):
    """This exception is raised when there is error with ssh connection."""


class SshConnection(IConnection):
    """Provides terminal and some functionality for specific node."""

    def __init__(self, hostname, port, username, password, pkey=None):
        """Initialize."""
        super().__init__(hostname, port, username, password, pkey=None)
        self._ssh_client = paramiko.SSHClient()
        self._ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self._transport = None
        self._retries = 4

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

    def is_active(self):
        """Check if transport is active."""
        return self._transport.is_active()

    def add_key(self, key):
        """Public interface to add a private key to the object."""
        temp = io.StringIO(key)
        self._key = paramiko.RSAKey.from_private_key(temp)
        temp.close()

    def check_ip(self, addr):
        """Check if ip is valid or not."""
        try:
            temp = socket.inet_aton(addr)
            return True
        except socket.error:
            return False

    def test_connection(self):
        """Simple test for the connection. returns true if connection works."""
        try:
            data = self._execute_command('echo hello')
            if data == ['hello\n']:
                return True
            else:
                return False
        except Exception:
            return False

    def close_session(self):
        """Close the ssh connection."""
        self._ssh_client.close()

    def execute(self, command):
        """Wrap the execution function."""
        try:
            return self._execute_command(command)
        except Exception as e:
            raise e

    def connect(self, via=None):
        """Handle connecting and reconnecting."""
        while self._retries > 0:
            self._retries = self._retries - 1
            try:
                self._open_session(via)
                if self.test_connection():
                    self._transport = self._ssh_client.get_transport()
                    self._retries = 4
                    return
                else:
                    pass
            except socket.timeout:
                pass

        raise TooManyRetriesException

    def create_channel_for_via(self, dest_hostname):
        """Create a channel for nested SSH connection."""
        if self.is_active():
            return self._transport.open_channel("direct-tcpip", (dest_hostname, 22), (self._hostname, 22))

    def _open_session(self, via=None):
        """Opens ssh channel, either directly or via an open channel.
        Chooses password or private key for authentication.
        """
        try:
            if via is None:
                self._ssh_client.connect(hostname=self._hostname, port=self._port,
                                         username=self._username, password=self._password,
                                         timeout=5, allow_agent=False, look_for_keys=False)
            else:
                if self._key is not None:
                    self._ssh_client.connect(hostname=self._hostname, port=self._port,
                                             username=self._username, pkey=self._key,
                                             timeout=5, allow_agent=False, look_for_keys=False, sock=via)
                else:
                    if self._password is not None:
                        self._ssh_client.connect(hostname=self._hostname, port=self._port,
                                                 username=self._username, password=self._password,
                                                 timeout=5, allow_agent=False, look_for_keys=False, sock=via)
                    else:
                        raise paramiko.ssh_exception.AuthenticationException
        except (TimeoutError, socket.error):
            raise TerminalConnectionException("Timeout when connecting with ssh to {ip}".format(ip=self._hostname))
        except (
            paramiko.ssh_exception.BadHostKeyException,
            paramiko.ssh_exception.AuthenticationException,
            paramiko.ssh_exception.SSHException,
        ) as ex:
            raise TerminalConnectionException(
                "Paramiko exception encountered when connecting to {ip}, exception: {ex}".format(ip=self._hostname, ex=ex)
            )
        except Exception as e:
            raise TerminalConnectionException("Error when opening channel to target. Error:" + str(e))

    def _ping_via_open_channel(self, ip_address):
        """Send ping command through open channel. Returns boolean."""
        output = self._execute_command("ping -c 1 -w 1 %s" % ip_address)

        for line in output:
            if "1 received" in line or "1 packets received" in line:
                return True
        return False

    def _ping_without_channel(self, ip_address):
        """Send ping command without an open SSH-connection."""
        try:
            option = '-n' if platform.system().lower() == 'windows' else '-c'
            command = ['ping', option, '1', ip_address]
            return subprocess.call(command) == 0
        except Exception:
            return False

    def _execute_command(self, command):
        """Execute command on the remote host."""
        stdin, stdout, stderr = self._ssh_client.exec_command(command)
        stdout.channel.recv_exit_status()
        output = stdout.readlines()
        return output
