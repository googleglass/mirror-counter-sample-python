import json
import jinja2
import os

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

class CustomCardFields(object):
    """Object represents custom fields in a timeline card. These fields are stored in 
    the sourceItemId field of a timeline card via JSON serialization. This class also
    takes care of rendering timeline card HTML for a given set up custom field parameters. """

    TEMPLATE = jinja_environment.get_template('templates/card.html')

    def __init__(self, dictionary={}):
        self.fields = dictionary

    @classmethod
    def get_fields_from_json(cls, json_input):
        """Loads JSON in json_input and constructs a CustomCardFields object."""
        fields = json.loads(json_input)
        return cls(fields)

    @classmethod
    def get_fields_from_item(cls, item):
        """Creates a CustomCardFields object assuming that input JSON is in item["sourceItemId"]"""
        key = 'sourceItemId'
        if key in item:
            return cls.get_fields_from_json(item[key])
        else:
            return cls()

    def get_json(self):
        """Returns json for object"""
        return json.dumps(self.fields)

    def render_html(self):
        """Returns html rendering of timeline card with self.fields data"""
        return CustomCardFields.TEMPLATE.render(self.fields)

    def get(self, key):
        """Returns element in dictionary, self.fields"""
        return self.fields[key]

    def set(self, key, val):
        """Sets element in dictionary, self.fields"""
        self.fields[key] = val

    def update_item(self, item):
        """Updates a timeline card item's sourceItemId and html with self.fields data"""
        item['sourceItemId'] = self.get_json()
        item['html'] = self.render_html()
        return item
