from django import template

register = template.Library()

@register.inclusion_tag('components/pagination.html', takes_context=True)
def pagination(context, paginator_page):
    request = context['request']

    full_url = request.path

    if request.GET:
        for index, parameter_key in enumerate(request.GET):
            if parameter_key == 'page':
                continue
            parameter_value = request.GET[parameter_key]
            if index == 0:
                full_url += f'?{parameter_key}={parameter_value}'
            else:
                full_url += f'&{parameter_key}={parameter_value}'
        full_url += '&'
    else:
        full_url += '?'

    context['full_url'] = full_url
    context['paginator_page'] = paginator_page

    return context
