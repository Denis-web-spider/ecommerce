from django.views.generic import View

from .models import Category

class LeftSideBarMixin(View):

    def get_context_data(self, *args, **kwargs):
        try:
            context = super().get_context_data(*args, **kwargs)
        except:
            context = {}
        categories = Category.objects.all()
        context['categories'] = categories
        return context

