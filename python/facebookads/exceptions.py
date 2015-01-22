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
The exceptions module contains Exception subclasses whose instances might be
raised by the sdk.
"""

import json


class FacebookError(Exception):
    """
    All errors specific to Facebook api requests and Facebook ads design will be
    subclassed from FacebookError which is subclassed from Exception.
    """
    pass


class FacebookRequestError(FacebookError):
    """
    Raised when an api request fails. Returned by error() method on a
    FacebookResponse object returned through a callback function (relevant
    only for failure callbacks) if not raised at the core api call method.
    """

    def __init__(
        self, message,
        request_context,
        http_status,
        http_headers,
        body
    ):
        self._message = message
        self._request_context = request_context
        self._http_status = http_status
        self._http_headers = http_headers
        try:
            self._body = json.loads(body)
        except (TypeError, ValueError):
            self._body = body

        self._api_error_code = None
        self._api_error_type = None
        self._api_error_message = None
        self._api_blame_field_specs = None

        if self._body is not None and 'error' in self._body:
            self._error = self._body['error']
            if 'message' in self._error:
                self._api_error_message = self._error['message']
            if 'code' in self._error:
                self._api_error_code = self._error['code']
            if 'type' in self._error:
                self._api_error_type = self._error['type']
            if 'error_data' in self._error:
                self._api_blame_field_specs = \
                    self._error['error_data']['blame_field_specs']
        else:
            self._error = None

        super(FacebookRequestError, self).__init__(
            "%s \n" % self._message +
            "Request:\n\t%s\n" % self._request_context +
            "Response:\n" +
            "\tHTTP Status: %s\n\tHeaders:%s\n\tBody: %s\n" % (
                self._http_status,
                self._http_headers,
                body,
            )
        )

    def request_context(self):
        return self._request_context

    def http_status(self):
        return self._http_status

    def http_headers(self):
        return self._http_headers

    def body(self):
        return self._body

    def api_error_message(self):
        return self._api_error_message

    def api_error_code(self):
        return self._api_error_code

    def api_error_type(self):
        return self._api_error_type

    def api_blame_field_specs(self):
        return self._api_blame_field_specs


class FacebookBadObjectError(FacebookError):
    """Raised when a guarantee about the object validity fails."""
    pass