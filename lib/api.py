"""
 Copyright (C) 2013 Digium, Inc.

 Erin Spiceland <espiceland@digium.com>

 See http://www.asterisk.org for more information about
 the Asterisk project. Please do not directly contact
 any of the maintainers of this project for assistance;
 the project provides a web site, mailing lists and IRC
 channels for your use.

 This program is free software, distributed under the terms
 detailed in the the LICENSE file at the top of the source tree.

"""
import re
from utils import get_file_content


class APIClassMethod():
    """Make an APIMethod out of operations in the Swagger description .json

    """
    def __init__(self, param_obj):
        """Initiate APIClassMethod instance

        """
        self.http_method = param_obj['http_method']
        self.path = param_obj['path']
        self.file_name = param_obj['file_name']
        self.lang = param_obj['lang']
        self.lang_tools = param_obj['lang_tools']
        self.method_params = ['self']
        self.required_id = False
        self.api_summary = ''
        self.method_summary = ''
        self.method_name = ''

        obj_id_re = re.compile('\{\w+\}')
        if obj_id_re.search(self.path):
            self.required_id = True
            self.path = re.sub(obj_id_re, '%s', self.path)

        self.param_lines = [get_file_content(
                            '%s/templates/method_params_def.proto'
                            % self.lang)]

    def set_method_summary(self, summary):
        """Set the method summary"""
        self.method_summary = summary

    def set_api_summary(self, summary):
        """Set the class summary"""
        self.api_summary = summary

    def set_parameters(self, param_obj):
        """Construct an array of required and optional method parameters
        in the format: name_type[_list][=None]
             objectId_number
             query='both'

        """
        t_attr = get_file_content('%s/templates/method_params_attr.proto'
                                  % self.lang)
        for p in param_obj:
            if p['name'] == "%sId" % (self.file_name):
                continue

            param_name = "%s_%s" % (p['name'], p['dataType'])

            if 'allowMultiple' in p and p['allowMultiple']:
                param_name = param_name + "_list"

            param_name = re.sub('([A-Z]{1,1})', r'_\1', param_name)
            param_name = param_name.lower()
            attr = re.sub('\{ATTR_NAME\}', param_name, t_attr)
            attr = re.sub('\{ATTR_ORIG_NAME\}', p['name'], attr)
            self.param_lines.append(attr)

            if 'defaultValue' in p:
                p['defaultValue'] = "'%s'" % (p['defaultValue'])
            else:
                p['defaultValue'] = None

            param = "%s=%s" % (param_name, p['defaultValue'])

            self.method_params.append(param)

    def get_param_string(self):
        """Return the string of all method parameters for method definition"""
        return ', '.join(self.method_params)

    def construct_file_contents(self):
        """Construct and return the contents of the method definition"""
        t_method = get_file_content('%s/templates/method_def.proto'
                                    % self.lang)
        t_method = re.sub('\{API_METHOD_NAME\}', self.method_name, t_method)
        t_method = re.sub('\{PARAMS\}', self.get_param_string(), t_method)
        params = ["'%s'" % (self.path),
                  "http_method='%s'" % (self.http_method)]
        if self.method_name:
            params.append("api_method='%s'" % (self.method_name))
        if self.method_params:
            params.append("parameters=params")
        if self.required_id:
            params.append("object_id=self.object_id")

        t_method = re.sub('\{API_CALL_PARAMS\}', ', '.join(params), t_method)
        method_comment = self.lang_tools.make_method_comment(
            self.api_summary, self.method_summary)
        t_method = re.sub('\{METHOD_COMMENTS\}', method_comment, t_method)
        t_method = re.sub('\{BUILD_API_CALL_PARAMS\}',
                          ''.join(self.param_lines), t_method)

        return t_method


class APIClass():
    """Make a collection of APIMethods and collect other information
    necessary to write out class file.

    """
    def __init__(self, param_obj):
        """Initiate new APIClass object"""
        self.methods = []
        self.lang = param_obj['lang']

        try:
            resource = param_obj['resourcePath']
            match = re.search('/(\w+)', resource)
            self.file_name = match.group(1)
        except KeyError:
            print "param obj has no attr resourcePath \n %s" % (param_obj)
            try:
                path = param_obj[0]['path']
                match = re.search('/api/(\w+)', path)
                self.file_name = match.group(1)
            except KeyError:
                #print "param obj has no attr [0]['path']"
                pass

        if self.file_name is None:
            raise AttributeError("No file name.")

        lang_tools = __import__(self.lang)
        self.file_name = lang_tools.make_filename(self.file_name)
        self.class_name = lang_tools.make_class_name(self.file_name)

        for api in param_obj['apis']:
            if 'operations' not in api:
                continue

            for op in api['operations']:
                method = APIClassMethod({
                    'http_method': op['httpMethod'],
                    'file_name': self.file_name,
                    'path': api['path'],
                    'lang': self.lang,
                    'lang_tools': lang_tools,
                })
                if 'parameters' in op:
                    method.set_parameters(op['parameters'])
                if 'description' in api:
                    method.set_api_summary(api['description'])
                if 'summary' in op:
                    method.set_method_summary(op['summary'])
                if 'nickname' in op:
                    method.method_name = lang_tools.make_method_name(
                        op['nickname'], self.class_name)

                self.methods.append(method)

    def construct_file_contents(self):
        """Construct and return the class definition for the file
        We can't construct methods here, because we need to move some
        methods to the Asterisk class.

        """
        template = get_file_content('%s/templates/class_def.proto' % self.lang)
        template = re.sub('\{CLASS_NAME\}', self.class_name, template)
        template = re.sub('\{FILE_NAME\}', self.file_name, template)
        return template
