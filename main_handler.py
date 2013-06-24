# Copyright (C) 2013 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Request Handler for /main endpoint."""

__author__ = 'jewang.net (Jennifer Wang)'

import logging
import os

from apiclient.http import HttpError
import jinja2
import webapp2

import CustomItemFields
import util

from google.appengine.api import memcache


jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

TIMELINE_ITEM_TEMPLATE_URL = '/templates/card.html'


class _BatchCallback(object):
  """Class used to track batch request responses."""

  def __init__(self):
    """Initialize a new _BatchCallbaclk object."""
    self.success = 0
    self.failure = 0

  def callback(self, request_id, response, exception):
    """Method called on each HTTP Response from a batch request.

    For more information, see
      https://developers.google.com/api-client-library/python/guide/batch
    """
    if exception is None:
      self.success += 1
    else:
      self.failure += 1
      logging.error(
          'Failed to insert item for user %s: %s', request_id, exception)


class MainHandler(webapp2.RequestHandler):
  """Request Handler for the main endpoint."""

  def _render_template(self, message=None):
    """Render the main page template."""
    template_values = {'userId': self.userid}
    if message:
      template_values['message'] = message
    # self.mirror_service is initialized in util.auth_required.

    timeline = self.mirror_service.timeline().list().execute()
    timeline_items = timeline.get('items', [])

    # sort timeline items
    timeline_items = timeline_items.sort(key=lambda x: x['created'])

    # turn sourceItemId JSON string into a dictionary for templating
    for item in timeline_items:
      fields = CustomCardFields.get_fields_from_item(item)
      item['sourceItemId'] = fields

    template_values['timelineItems'] = timeline_items
    template = jinja_environment.get_template('templates/index.html')
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
        'newCounter': self._new_counter,
        'deleteCounter': self._delete_counter,
        'resetCounter': self._reset_counter,
        'updateCounter': self._update_counter
    }
    if operation in operations:
      message = operations[operation]()
    else:
      message = "I don't know how to " + operation
    # Store the flash message for 5 seconds.
    memcache.set(key=self.userid, value=message, time=5)
    self.redirect('/')

  def _delete_counter(self):
    """Deletes the user-specified timeline item."""
    self.mirror_service.timeline().delete(
        id=self.request.get('itemId')).execute()
    return 'Counter Deleted'

  @staticmethod
  def _get_num(num):
    """Parses num into int. Returns 0 if num is invalid."""
    try:
      return int(num)
    except ValueError:
      return 0

  def _update_counter(self):
    """Updates the counter to user input for given timeline item."""
    item = self.mirror_service.timeline(
        ).get(id=self.request.get('itemId')).execute()

    new_fields = {
        'name': self.request.get('name'),
        'num': self._get_num(self.request.get('num'))
        }
    CustomItemFields.set_multiple(
        item, new_fields, TIMELINE_ITEM_TEMPLATE_URL)

    if 'notification' in item:
      item.pop('notification')
    self.mirror_service.timeline().update(
        id=self.request.get('itemId'), body=item).execute()
    return 'Counter Updated'

  def _reset_counter(self):
    """Resets the counter for given timeline item."""
    item = self.mirror_service.timeline().get(
        id=self.request.get('itemId')).execute()

    item = CustomItemFields.set(
        item, 'num', 0, TIMELINE_ITEM_TEMPLATE_URL)

    if 'notification' in item:
      item.pop('notification')
    self.mirror_service.timeline().update(
        id=self.request.get('itemId'), body=item).execute()
    return 'Counter Reset'

  def _new_counter(self):
    """Insert a timeline item."""
    logging.info('Inserting timeline item')
    # Note that icons will not show up when making counters on a
    # locally hosted web interface.
    body = {
        'notification': {'level': 'DEFAULT'},
        'menuItems': [
            {
                'action': 'CUSTOM',
                'id': 'increment',
                'values': [{
                    'displayName': 'Increment',
                    'iconUrl': util.get_full_url(
                        self, '/static/images/up.png')}]
            },
            {
                'action': 'CUSTOM',
                'id': 'decrement',
                'values': [{
                    'displayName': 'Decrement',
                    'iconUrl': util.get_full_url(
                        self, '/static/images/down.png')}]
            },
            {
                'action': 'CUSTOM',
                'id': 'reset',
                'values': [{
                    'displayName': 'Set Counter to 0',
                    'iconUrl': util.get_full_url(
                        self, '/static/images/reset.png')}]
            },
            {'action': 'SHARE'},
            {'action': 'TOGGLE_PINNED'},
            {'action': 'DELETE'}
        ]
    }
    new_fields = {
        'name': self.request.get('name'),
        'num': self._get_num(self.request.get('num'))
        }
    CustomItemFields.set_multiple(
        body, new_fields, TIMELINE_ITEM_TEMPLATE_URL)

    # self.mirror_service is initialized in util.auth_required.
    self.mirror_service.timeline().insert(body=body).execute()

    # Subscribe to timeline notifications if needed
    subscriptions = self.mirror_service.subscriptions().list().execute()
    need_subscribe = True
    for subscription in subscriptions.get('items', []):
      if subscription.get('collection') == 'timeline':
        need_subscribe = False

    if need_subscribe:
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
        return ('A new counter was created, but notifications were not '
            'enabled. HTTPS connection required.')

    return  'A new counter has been created.'

MAIN_ROUTES = [
    ('/', MainHandler)
]
