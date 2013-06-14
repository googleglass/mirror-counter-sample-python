import json
import os

import jinja2

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))


class CustomItemFields(object):
  
  """
  A CustomItemFields object overwrites the sourceItemId field of a timeline item to enable
  custom fields (i.e. variables) for the timeline item. Each custom field is a key->value pair
  encapsulated in a dictionary self._fields. The dictionary is JSON serialized and stored in 
  the sourceItemId field of a timeline item. 
  
  Additionally, a possible use of a CustomitemFields is to use the custom fields to render the
  HTML of a timeline item. This class takes care of this using jinja templates.
  """
  DEFAULT_TEMPLATE_URL = 'templates/card.html'

  def __init__(self, dictionary={}, template_url=DEFAULT_TEMPLATE_URL):
    self._fields = dictionary
    # Set template_url to '' to turn templating off
    if template_url != '':
      self.template = jinja_environment.get_template(template_url)
    else:
      self.template = False

  @classmethod
  def get_fields_from_json(cls, json_input):
    """Constructs a new CustomitemFields object from json_input."""
    fields = json.loads(json_input)
    return cls(fields)

  @classmethod
  def get_fields_from_item(cls, item):
    """
    Constructs a new CustomitemFields object from json_input
    assuming that input JSON is in item['sourceItemId']
    """

    key = 'sourceItemId'
    if key in item:
      return cls.get_fields_from_json(item[key])
    else:
      return cls()

  def get_json(self):
    """Returns JSON for object."""
    return json.dumps(self._fields)

  def render_html(self):
    """
    Returns html rendering of timeline item with self._fields data.
    Returns empty string if object does not have a template.
    """
    if self.template:
      return self.template.render(self._fields)
    else:
      return ''

  def get(self, key):
    """Returns value associated with in input key."""
    return self._fields[key]

  def set(self, key, val):
    """Sets key->value in dictionary"""
    self._fields[key] = val

  def update_item(self, item):
    """
    Updates a timeline item's sourceItemId and, if enabled, template html.
    It is good practice to update_item() before pushing a timeline item.
    """
    item['sourceItemId'] = self.get_json()
    if self.template:
      item['html'] = self.render_html()
    return item

  def get_dict(self):
    """Returns encapsulated dictionary self._fields."""
    return self._fields
