"""
 Copyright (C) 2013 Digium, Inc.

 Erin Spiceland <espiceland@digium.com>

 See http://www.asterisk.org for more information about
 the Asterisk project. Please do not directly contact
 any of the maintainers of this project for assistance;
 the project provides a web site, mailing lists and IRC
 channels for your use.

 This program is free software, distributed under the terms of
 the GNU General Public License Version 2. See the LICENSE file
 at the top of the source tree.

"""

class Bridge:
    def __init__(self, api):
        """Initialize the Bridge object."""
        self.id = 1
        self._api = api

    def get_id(self):
        """Return the Bridge object's id."""
        return self.id

    def add_event_handler(self, event_name, handler):
        """Add an event handler for Stasis events on this object.
        For general events, use Asterisk.add_event_handler instead.
        """
        pass

    def remove_event_handler(self, event_name, handler):
        """Remove an event handler for Stasis events on this object.
        For general events, use Asterisk.remove_event_handler instead.
        """
        pass

    def new(self):
        """Active bridges

        Create a new bridge

        """
        params = {}

        self._api.call('/api/bridges', http_method='POST', api_method='new', parameters=params)
        is_success = True
        return is_success

    def delete(self):
        """Individual bridge

        Delete bridge

        """
        params = {}

        self._api.call('/api/bridges/%s', http_method='DELETE', api_method='delete', parameters=params, object_id=self.id)
        is_success = True
        return is_success

    def add_channel_to(self, channel_string_list=None):
        """Add a channel to a bridge

        Add a channel to a bridge

        """
        params = {}
        if channel_string_list:
            params['channel'] = channel_string_list

        self._api.call('/api/bridges/%s/addChannel', http_method='POST', api_method='add_channel_to', parameters=params, object_id=self.id)
        is_success = True
        return is_success

    def remove_channel_from(self, channel_string_list=None):
        """Remove a channel from a bridge

        Remove a channel from a bridge

        """
        params = {}
        if channel_string_list:
            params['channel'] = channel_string_list

        self._api.call('/api/bridges/%s/removeChannel', http_method='POST', api_method='remove_channel_from', parameters=params, object_id=self.id)
        is_success = True
        return is_success

    def record(self, name_string=None, maxDurationSeconds_number='0', maxSilenceSeconds_number='0', append_boolean='False', beep_boolean='False', terminateOn_string='none'):
        """Record audio to/from a bridge

        Start a recording

        """
        params = {}
        if name_string:
            params['name'] = name_string
        if maxDurationSeconds_number:
            params['maxDurationSeconds'] = maxDurationSeconds_number
        if maxSilenceSeconds_number:
            params['maxSilenceSeconds'] = maxSilenceSeconds_number
        if append_boolean:
            params['append'] = append_boolean
        if beep_boolean:
            params['beep'] = beep_boolean
        if terminateOn_string:
            params['terminateOn'] = terminateOn_string

        self._api.call('/api/bridges/%s/record', http_method='POST', api_method='record', parameters=params, object_id=self.id)
        is_success = True
        return is_success
