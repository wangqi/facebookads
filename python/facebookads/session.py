# Copyright 2014 Facebook, Inc.

# You are hereby granted a non-exclusive, worldwide, royalty-free license to
# use, copy, modify, and distribute this software in source code or binary
# form for use in connection with the web services and APIs provided by
# Facebook.

# As with any software that integrates with the Facebook platform, your use
# of this software is subject to the Facebook Developer Principles and
# Policies [http://developers.facebook.com/policy/]. This copyright notice
# shall be included in all copies or substantial portions of the software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

"""
The purpose of the session module is to encapsulate authentication classes and
utilities.
"""
import hashlib
import hmac
import requests
import os
from sys import version_info


class FacebookSession(object):
    """
    FacebookSession manages the the Graph API authentication and https
    connection.

    Attributes:
        GRAPH (class): The graph url without an ending forward-slash.
        app_id: The application id.
        app_secret: The application secret.
        access_token: The access token.
        appsecret_proof: The application secret proof.
        requests: The python requests object through which calls to the api can
            be made.
    """
    GRAPH = 'https://graph.facebook.com'

    def __init__(self, app_id, app_secret, access_token):
        """
        Initializes and populates the instance attributes with app_id,
        app_secret, access_token, appsecret_proof, and requests given arguments
        app_id, app_secret, and access_token.
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = access_token

        if version_info < (3, 0):
            h = hmac.new(
                bytes(self.app_secret),
                msg=bytes(self.access_token),
                digestmod=hashlib.sha256
            )
        else:
            h = hmac.new(
                bytes(self.app_secret, 'utf-8'),
                msg=bytes(self.access_token, 'utf-8'),
                digestmod=hashlib.sha256
            )

        self.appsecret_proof = h.hexdigest()

        self.requests = requests.Session()
        self.requests.verify = os.path.join(
            os.path.dirname(__file__),
            'fb_ca_chain_bundle.crt',
        )
        self.requests.params.update({
            'access_token': self.access_token,
            'appsecret_proof': self.appsecret_proof,
        })
