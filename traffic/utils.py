import re
import django.urls.resolvers
from django.shortcuts import resolve_url
from inventory.models import Item, Location
from inventory.utils import get_my_list
from login.utils import check_admin

ban_list = ['app_list']


def show_urls(url_list, depth=0):
    ret = {}
    for entry in url_list:
        if type(entry) == django.urls.resolvers.URLPattern:
            if str(entry.pattern) and str(
                    entry.pattern
            )[0] == r'^' and entry.name and entry.name not in ban_list:
                ret.update({str(entry.name): str(entry.pattern)})
        if hasattr(entry, 'url_patterns'):
            if entry.app_name in [
                    'inventory', 'login', 'trace_item', 'personal', 'traffic'
            ]:
                ret.update(show_urls(entry.url_patterns, depth + 1))
    return ret


def wash_regex(r):
    return re.sub(r'\?P<.+?>', '', r)

# def display(locations, tot_count, user=None, cnt=True):
#     res_list = []
#     for loc in locations:
#         count = Item.objects.filter(location=loc).count() if cnt else 1
#         tmp_dict = {
#             "name": loc.path,
#             "value": count,
#         }
#         tmp_count = 0
#         children = loc.location_children.all()
#         if user:
#             children = get_my_list(user, children)
#         if len(children) > 0:
#             tmp_dict["children"], tmp_count = display(
#                 loc.location_children.all(),
#                 tot_count,
#                 user,
#                 cnt,
#             )
#         tmp_dict["symbolSize"] = int(
#             ((count + tmp_count) / tot_count)**0.5 * 60) + 10
#         res_list.append(tmp_dict)
#     return res_list, count + tmp_count


def build_loc_tree(location=None, count=False, user=None, depth=1000, link=False):
    ret = {'name': location.path if location else 'root'}
    tot_count = Item.objects.filter(location=location).count() if location and count else 0
    children = []
    if depth:
        _children = location.location_children.all() if location else Location.objects.filter(parent=None)
        for child in get_my_list(user, _children) if user else _children:
            sub_tree, sub_tree_count = build_loc_tree(child, count, user, depth - 1, link)
            tot_count += sub_tree_count
            children.append(sub_tree)
    ret['children'] = children
    if link and location:
        ret['link'] = resolve_url('inventory:location', location.id)
    ret['value'] = tot_count
    return ret, tot_count
