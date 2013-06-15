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

import json
import logging

from CustomItemFields import CustomItemFields
from main_handler import TIMELINE_ITEM_TEMPLATE_URL
from model import Credentials
from oauth2client.appengine import StorageByKeyName
import util
import webapp2


class NotifyHandler(webapp2.RequestHandler):
  """Request Handler for notification pings."""

  def post(self):
    """Handles notification pings."""
    logging.info('Got a notification with payload %s', self.request.body)
    data = json.loads(self.request.body)
    userid = data['userToken']
    # TODO: Check that the userToken is a valid userToken.
    self.mirror_service = util.create_service(
        'mirror', 'v1',
        StorageByKeyName(Credentials, userid, 'credentials').get())
    if data.get('collection') == 'timeline':
      self._handle_timeline_notification(data)

  def _handle_timeline_notification(self, data):
    """Handle timeline notification."""

    options = {
        'increment': self._increment,
        'decrement': self._decrement,
        'reset': self._reset
    }
    for user_action in data.get('userActions', []):
      logging.info(user_action)
      option = user_action.get('payload')
      if (user_action.get('type') == 'CUSTOM' and
          option in options):

        options[option]()
	# Only handle the first successful action.
        break

      else:
        logging.info(
            "I don't know what to do with this notification: %s", user_action)

  def _increment(self):
    """Increments the counter for given timeline item."""
    data = json.loads(self.request.body)
    item = self.mirror_service.timeline().get(id=data['itemId']).execute()
    try:
      num = int(CustomItemFields.get(item, 'num'))
    except ValueError:
      # if an invalid int is this field, just use 0 instead
      num = 0

    CustomItemFields.set(item, 'num', num + 1, TIMELINE_ITEM_TEMPLATE_URL)
    if 'notification' in item:
      item.pop('notification')
    self.mirror_service.timeline().update(
        id=data['itemId'], body=item).execute()

  def _decrement(self):
    """Decrements the counter for given timeline item."""
    data = json.loads(self.request.body)
    item = self.mirror_service.timeline().get(id=data['itemId']).execute()
    try:
      num = int(CustomItemFields.get(item, 'num'))
    except ValueError:
      # if an invalid int is this field, just use 0 instead
      num = 0

    CustomItemFields.set(item, 'num', num - 1, TIMELINE_ITEM_TEMPLATE_URL)
    if 'notification' in item:
      item.pop('notification')
    self.mirror_service.timeline().update(
        id=data['itemId'], body=item).execute()

  def _reset(self):
    """Resets the counter for given timeline item."""
    # could not simply call main_handler._reset_counter() because it is a
    # private method
    data = json.loads(self.request.body)
    item = self.mirror_service.timeline().get(id=data['itemId']).execute()
    CustomItemFields.set(item, 'num', 0, TIMELINE_ITEM_TEMPLATE_URL)
    if 'notification' in item:
      item.pop('notification')
    self.mirror_service.timeline().update(
        id=data['itemId'], body=item).execute()

NOTIFY_ROUTES = [
    ('/notify', NotifyHandler)
]
