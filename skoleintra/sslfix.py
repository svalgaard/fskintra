#
# -*- encoding: utf-8 -*-
#

#
# Fix (Mac) HTTPS (SSL) issues
# - see https://github.com/svalgaard/fskintra/issues/15
#
# http://askubuntu.com/questions/116020/python-https-requests-urllib2-to-some-sites-fail-on-ubuntu-12-04-without-proxy
#
import httplib
from httplib import HTTPConnection, HTTPS_PORT
import ssl
import socket


class HTTPSConnection(HTTPConnection):
    'This class allows communication via SSL.'
    default_port = HTTPS_PORT

    def __init__(self, host, port=None, key_file=None, cert_file=None,
                 strict=None, timeout=socket._GLOBAL_DEFAULT_TIMEOUT,
                 source_address=None):
        HTTPConnection.__init__(self, host, port, strict, timeout,
                                source_address)
        self.key_file = key_file
        self.cert_file = cert_file

    def connect(self):
        "Connect to a host on a given (SSL) port."
        sock = socket.create_connection((self.host, self.port),
                                        self.timeout, self.source_address)
        if self._tunnel_host:
            self.sock = sock
            self._tunnel()
        # this is the only line we modified from the httplib.py file
        # we added the ssl_version variable
        self.sock = ssl.wrap_socket(sock, self.key_file, self.cert_file,
                                    ssl_version=ssl.PROTOCOL_TLSv1)


def override():
    '''Override the standard HTTPSConnection as used in httplib'''
    httplib.HTTPSConnection = HTTPSConnection
