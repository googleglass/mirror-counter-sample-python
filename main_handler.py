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

"""Request Handler for /main endpoint."""

__author__ = 'alainv@google.com (Alain Vongsouvanh)'


import io
import jinja2
import logging
import os
import webapp2
import json

from google.appengine.api import memcache
from google.appengine.api import urlfetch

import httplib2
from apiclient.http import HttpError
from apiclient import errors
from apiclient.http import MediaIoBaseUpload
from apiclient.http import BatchHttpRequest
from oauth2client.appengine import StorageByKeyName

from model import Credentials
import util

from CustomCardFields import CustomCardFields 

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


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

    timeline_items = self.mirror_service.timeline().list().execute()
    template_values['timelineItems'] = sorted(timeline_items.get('items', []))

    template_values['subscriptions'] = self.mirror_service.subscriptions().list().execute().get('items', []);
    for i in range(len(template_values['timelineItems'])):
      item = template_values['timelineItems'][i]
      fields = CustomCardFields.getFieldsFromItem(item)
      template_values['timelineItems'][i] = dict(fields.fields.items() + item.items())

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
        'updateCounter': self._update_counter,
        'clearSubscriptions': self._clear_subscriptions
    }
    if operation in operations:
      message = operations[operation]()
    else:
      message = "I don't know how to " + operation
    # Store the flash message for 5 seconds.
    memcache.set(key=self.userid, value=message, time=5)
    self.redirect('/')

  def _delete_counter(self):
    self.mirror_service.timeline().delete(id=self.request.get('itemId')).execute();
    return 'Counter Deleted';

  def _clear_subscriptions(self):
    """Unsubscribe from notifications."""

    subscriptions = self.mirror_service.subscriptions().list().execute()
    for subscription in subscriptions.get('items', []):
      self.mirror_service.subscriptions().delete(id=subscription.get('id')).execute()
    return 'Application has been unsubscribed.'

  def _update_counter(self):
    item = self.mirror_service.timeline().get(id=self.request.get('itemId')).execute()

    fields = CustomCardFields({'name': self.request.get('name'), 'num': self.request.get('num')});
    fields.updateItem(item)

    logging.info(item);

    if 'notification' in item:
      item.pop('notification');
    self.mirror_service.timeline().update(id=self.request.get('itemId'), body=item).execute()
    return 'Counter Updated'
    
  def _reset_counter(self):
    item = self.mirror_service.timeline().get(id=self.request.get('itemId')).execute()
    fields = CustomCardFields.getFieldsFromItem(item)
    fields.set('num',  0);
    fields.updateItem(item)

    if 'notification' in item:
      item.pop('notification');
    self.mirror_service.timeline().update(id=self.request.get('itemId'), body=item).execute()
    return 'Counter Reset'

  def _new_counter(self):
    """Insert a timeline item."""
    logging.info('Inserting timeline item')
    body = {
      'notification': {'level': 'DEFAULT'},
      'menuItems': [
	{
        'action': 'CUSTOM',
	'id': 'increment',
	'values': [{
	    'displayName':"Increment",
	    'iconUrl': 'http://www.iaza.com/work/130421C/iaza14708834550500.gif'}]
	},
	{
        'action': 'CUSTOM',
	'id': 'decrement',
	'values': [{
	    'displayName':"Decrement",
	    'iconUrl': 'http://www.iaza.com/work/130421C/iaza14708834550500.gif'}]
	},
	{
        'action': 'CUSTOM',
	'id': 'reset',
	'values': [{
	    'displayName':"Reset",
	    'iconUrl': 'http://www.iaza.com/work/130421C/iaza14708834550500.gif'}]
	},
	{'action': 'SHARE'},
	{'action': 'TOGGLE_PINNED'},
	{'action': 'DELETE'}
      ]
    }
    fields = CustomCardFields({'name': self.request.get('name'), 'num': self.request.get('num')});
    body = fields.updateItem(body);

    # self.mirror_service is initialized in util.auth_required.
    self.mirror_service.timeline().insert(body=body).execute()

    """Subscribe the app."""
    subscriptions = self.mirror_service.subscriptions().list().execute()
    needSubscribe = True;
    for subscription in subscriptions.get('items', []):
    	if subscription.get('collection') == 'timeline':
    	    needSubscribe = False;

    if needSubscribe:
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
	    return 'A new counter was created, but notifications were not enabled. HTTPS connection required.'

    return  'A new counter has been created.'

MAIN_ROUTES = [
    ('/', MainHandler)
]
