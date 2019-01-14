from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.views import generic
from . import forms

from inventory.models import Material
from login.models import User as myUser


class IndexView(generic.View):
    def get(self, request):
        return render(request, 'inventory/index.html')


class MaterialsView(generic.ListView):
    template_name = 'inventory/materials.html'
    context_object_name = 'material_list'
    user_id = 0

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('is_login', None):
            return redirect("/")
        else:
            self.user_id = request.session.get('user_id', None)
            return super(MaterialsView, self).dispatch(request, *args,
                                                       **kwargs)

    def get_queryset(self):
        return Material.objects.filter(user=self.user_id).order_by('-name')


class AddView(generic.View):
    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('is_login', None):
            return redirect("/")
        else:
            return super(AddView, self).dispatch(request, *args, **kwargs)

    def get(self, request):
        add_form = forms.AddForm()
        return render(request, 'inventory/add.html', locals())

    # TODO:add materials properly
    def post(self, request):
        add_form = forms.AddForm(request.POST)
        message = "请检查填写的内容！"
        if add_form.is_valid():  # 获取数据
            name = add_form.cleaned_data['name']
            quantity = add_form.cleaned_data['quantity']
            new_material = Material.objects.create(
                name=name,
                quantity=quantity,
            )
            new_material.user.add(myUser.objects.get(id=request.session['user_id']))
            new_material.save()
            message = "添加成功！"
            return redirect('/add/')
        else:
            return self.get(request)
