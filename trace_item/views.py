from django.shortcuts import render
from django.views import generic

from trace_item.models import ItemLog
from inventory.utils import get_my_item
from login.models import User as myUser


class TraceItemView(generic.View):
    item = None
    tmp_user = None

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('is_login', None):
            return render(request, 'reace_item/reace_item.html')
        else:
            user_id = request.session.get('user_id')
            self.tmp_user = myUser.objects.get(id=user_id)
            self.item = get_my_item(self.tmp_user, kwargs.get('id'))
            return super(TraceItemView, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        logs = ItemLog.objects.filter(item=self.item)
        return render(request, 'reace_item/reace_item.html', locals())
