# Copyright (C) 2013 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Request Handler for /notify endpoint."""

__author__ = 'jenniferwang@google.com (Jennifer Wang)'


import util
import jinja2
import logging
import os
import webapp2

from google.appengine.api import memcache
from apiclient.http import HttpError

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(os.path.dirname((__file__)))))

class SubscriptionHandler(webapp2.RequestHandler):
    """Request Handler for notification pings."""

    def _render_template(self, message=None):
        """Render the main page template."""
        template_values = {'userId': self.userid}
        if message:
            template_values['message'] = message
        # self.mirror_service is initialized in util.auth_required.

        template_values['subscriptions'] = self.mirror_service.subscriptions().list().execute().get('items', [])
        template_values['subscriptionUrl'] = util.get_full_url(self, '/notify')

        template = jinja_environment.get_template('templates/subscription.html')
        self.response.out.write(template.render(template_values))

    @util.auth_required
    def get(self):
        """Render the main page."""
        # Get the flash message and delete it.
        message = memcache.get(key=self.userid)
        memcache.delete(key=self.userid)
        self._render_template(message)

    @util.auth_required
    def post(self):
        """Execute the request and render the template."""
        operation = self.request.get('operation')
        # Dict of operations to easily map keys to methods.
        operations = {
          'clearSubscriptions': self._clear_subscriptions,
          'makeSubscription': self._make_subscription
        }
        if operation in operations:
            message = operations[operation]()
        else:
            message = "I don't know how to " + operation
        # Store the flash message for 5 seconds.
        memcache.set(key=self.userid, value=message, time=5)
        self.redirect('/subscription')

    def _clear_subscriptions(self):
        """Unsubscribe from notifications."""

        subscriptions = self.mirror_service.subscriptions().list().execute()
        for subscription in subscriptions.get('items', []):
            self.mirror_service.subscriptions().delete(id=subscription.get('id')).execute()
        return 'Application has been unsubscribed.'

    def _make_subscription(self):
        """Subscribe to timeline"""
        logging.info('Subscribing to Timeline')
        # self.userid is initialized in util.auth_required.
        body = {'collection': 'timeline',
          'userToken': self.userid,
          'callbackUrl': util.get_full_url(self, '/notify')
        }
        # self.mirror_service is initialized in util.auth_required.

        try:
            self.mirror_service.subscriptions().insert(body=body).execute()
        except HttpError:
            return 'Notifications were not enabled. HTTPS connection required.'
        return 'Successfully subscribed to timeline.'

SUBSCRIPTION_ROUTES = [
    ('/subscription', SubscriptionHandler)
]
