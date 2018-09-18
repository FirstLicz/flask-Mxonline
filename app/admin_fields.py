from wtforms import TextAreaField
from wtforms.widgets.core import HTMLString, html_params, text_type, TextArea

try:
    from html import escape
except ImportError:
    from cgi import escape


class UEditor(object):
    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        if 'required' not in kwargs and 'required' in getattr(field, 'flags', []):
            kwargs['required'] = True
        kwargs['style'] = 'visibility: hidden; display: none;'
        return HTMLString('<textarea %s>%s</textarea>'
                          '<div %s></div>' % (
                              html_params(name=field.name, **kwargs),
                              escape(text_type(field._value()), quote=False),
                              'id="editor" type="text/plain" style="height:240px;"',

                          ))


class UEditorField(TextAreaField):
    widget = UEditor()
