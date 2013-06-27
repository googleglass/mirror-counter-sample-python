Counter for Glass
========================

Sample counter Glassware written in Python.

[Online Demo](https://mirror-counter-sample-python.appspot.com/)

To create a counter, a user accesses a web UI hosted on Google App Engine
and sets a name and starting number. Counters appear on Glass devices as 
timeline items with the options to increment, decrement, reset, share, 
and delete.

This Glassware demonstrates how to use the timelineItem.sourceItemId field 
of a timeline item and JSON serialization to associate variables (custom 
fields) with timeline items. This technique can be used with Jinja2 to 
automatically generate html and display these custom fields. The file 
[custom_item_fields](custom_item_fields.py) provides functions to enable 
this capability. The [main handler](main_handler.py) and 
[notification handler](notify/handler.py) demonstrate how to use these methods.


**Note**: This is a snapshot sample. That means that although we think you will 
find it useful, it is not being actively maintained. Pull requests are always 
apprecaited.

Screenshots
------------------------
In the web interface, users see a list of their counters and can
rename (set counter name and counter number), delete, and reset each counter. 
![The list of counters in the web interface.](/screenshots/web-list.png)
Clicking the green New Counter button will bring up a pop-up. Users can name their 
counter and initialize it at any number.
![The pop-up that appears when users make a new counter.](/screenshots/web-new.png)
A interface at `/subscribe` allows users to debug their Glassware's timeline 
subscription. The Glassware must be subscribed in order for Counter to work
on Glass. This feature is meant for developer testing.
![The subscription debugging page.](/screenshots/web-subscribe.png)
On Glass, each counter is a single timeline card. 
![A counter timeline card on glass.](/screenshots/glass-card.png)
Clicking on the timeline card allows users to scroll through increment, decrement,
and reset to 0 custom menu options as well as the share, pin, and delete built-in
menu options.
![Increment menu option.](/screenshots/glass-inc.png)
![Decrement menu option.](/screenshots/glass-dec.png)
![Reset menu option.](/screenshots/glass-reset.png)
