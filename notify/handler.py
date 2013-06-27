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

__author__ = 'jewang.net (Jennifer Wang)'


import json
import logging
import webapp2

from oauth2client.appengine import StorageByKeyName

from model import Credentials
import custom_item_fields
from main_handler import TIMELINE_ITEM_TEMPLATE_URL
import util


PROCESS_OPTIONS = {
    'increment': lambda num: num + 1,
    'decrement': lambda num: num - 1,
    'reset': lambda num: 0
}


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
    """Handle timeline notification.

    This method handles when a user chooses to perform a custom menu optio
    (increment, decrement, reset).
    """
    # TODO: Race conditions occur if a user rapidly selects a menu item many
    #       times (concurrently reading and writing the same timeline item).
    #       Resolve this issue
    for user_action in data.get('userActions', []):
      logging.info(user_action)
      option = user_action.get('payload')
      if user_action.get('type') == 'CUSTOM' and option in PROCESS_OPTIONS:
        data = json.loads(self.request.body)
        item = self.mirror_service.timeline().get(id=data['itemId']).execute()
        num = util.get_num(custom_item_fields.get(item, 'num'))
        # possible actions are functions listed in PROCESS_OPTIONS
        custom_item_fields.set(
            item, 'num',
            PROCESS_OPTIONS[option](num), TIMELINE_ITEM_TEMPLATE_URL)
        if 'notification' in item:
          item.pop('notification')
        self.mirror_service.timeline().update(
            id=data['itemId'], body=item).execute()
	# Only handle the first successful action.
        break
      else:
        logging.info(
            "I don't know what to do with this notification: %s", user_action)


NOTIFY_ROUTES = [
    ('/notify', NotifyHandler)
]
