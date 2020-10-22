# custom_template_filters.py

from flask import Blueprint
import re
from jinja2 import evalcontextfilter, Markup, escape

blueprint = Blueprint('custom_template_filters', __name__)

@evalcontextfilter
@blueprint.app_template_filter()
def newline_to_br(context, value: str) -> str:
    result = "<br />".join(re.split(r'(?:\r\n|\r|\n){1,}', escape(value)))

    if context.autoescape:
        result = Markup(result)

    return result