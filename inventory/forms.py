from django import forms
from .models import Item, ItemTemplate
from .utils import get_my_list, get_my_template_queryset
from django.template.loader import render_to_string
import re
from django.utils.translation import gettext_lazy as _


class AddItemForm(forms.Form):
    name = forms.CharField(
        label=_("名称"),
        max_length=128,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    custom_id = forms.CharField(
        label=_("自定编号"),
        max_length=128,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    public = forms.BooleanField(
        label=_("公开"),
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        initial=True,
    )


class SelectWithAdd(forms.Select):
    def __init__(self, *args, **kwargs):
        self.template = kwargs.get('template')
        self.user = kwargs.get('user')
        kwargs.pop('template')
        kwargs.pop('user')
        super(SelectWithAdd, self).__init__(*args, **kwargs)

    def render(self, name, *args, **kwargs):
        select = super(SelectWithAdd, self).render(name, *args, **kwargs)
        _template = ItemTemplate.objects.get(name=self.template)
        if _template in get_my_template_queryset(self.user,
                                                 ItemTemplate.objects.all()):
            select_with_add = render_to_string(
                "inventory/select_with_add.html", {
                    'select': select,
                    'name': name,
                    'template_name': self.template,
                })
        else:
            select_with_add = select
        return select_with_add


class EditItemForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(EditItemForm, self).__init__(*args)
        data = kwargs.get('data')
        user = kwargs.get('user')
        if data:
            for idx, value in enumerate(data):
                tmp_type = value.get('type', 'text').lower()
                tmp_label = value.get('name', '属性{}'.format(idx + 1))
                tmp_required = bool(value.get('required', False))
                tmp_placeholder = value.get('placeholder', '')
                if tmp_type == 'int':
                    tmp_field = forms.IntegerField(
                        label=tmp_label,
                        required=tmp_required,
                        widget=forms.TextInput(
                            attrs={
                                'class': 'form-control',
                                'type': 'number',
                                'step': '1',
                                'placeholder': tmp_placeholder,
                            }),
                    )
                elif tmp_type == 'float':
                    tmp_field = forms.FloatField(
                        label=tmp_label,
                        required=tmp_required,
                        widget=forms.TextInput(
                            attrs={
                                'class': 'form-control',
                                'type': 'number',
                                'step': '1e-12',
                                'placeholder': tmp_placeholder,
                            }),
                    )
                elif tmp_type == 'bool':
                    tmp_field = forms.BooleanField(
                        label=tmp_label,
                        required=False,
                        widget=forms.CheckboxInput(
                            attrs={
                                'class': 'form-check-input position-static',
                            }),
                    )
                elif tmp_type == 'text':
                    tmp_field = forms.CharField(
                        label=tmp_label,
                        required=tmp_required,
                        max_length=128,
                        widget=forms.TextInput(
                            attrs={
                                'class': 'form-control',
                                'placeholder': tmp_placeholder,
                                'autocomplete': tmp_label,
                            }),
                    )
                elif tmp_type == 'date':
                    tmp_field = forms.DateField(
                        label=tmp_label,
                        required=tmp_required,
                        widget=forms.TextInput(
                            attrs={'class': 'form_datetime form-control','autocomplete': 'off'}),
                    )
                else:
                    objects = Item.objects.filter(template__name=tmp_type)
                    attrs = {
                        'class':
                        'form-control selectpicker select_' + tmp_type,
                        'data-live-search': 'true'
                    }
                    if tmp_required:
                        attrs['required'] = ''
                    tmp_field = forms.ChoiceField(
                        label=tmp_label,
                        required=tmp_required,
                        choices=get_my_list(user, objects).values_list(
                            'id', 'name'),
                        widget=SelectWithAdd(
                            attrs=attrs, template=tmp_type, user=user),
                    )
                    if not tmp_required:
                        tmp_field.choices.insert(0, [0, '--'])
                self.fields[tmp_label.replace(' ', '_')] = tmp_field


class AddTemplateForm(forms.Form):
    name = forms.CharField(
        label=_("名称"),
        max_length=64,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )


class EditTemplateForm(forms.Form):
    name = forms.CharField(
        max_length=128,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    var_type = forms.CharField(
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    required = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(),
    )
    placeholder = forms.CharField(
        max_length=128,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )


class ChooseTemplateForm(forms.Form):
    template = forms.ChoiceField(
        label=_("类型"),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    def __init__(self, *args, **kwargs):
        super(ChooseTemplateForm, self).__init__(*args)
        template_queryset = kwargs.get('template_queryset')
        if 'is_property' in kwargs.keys():
            choices = template_queryset.filter(
                is_property=kwargs.get('is_property')).values_list(
                    'id', 'name')
        else:
            choices = template_queryset.all().values_list('id', 'name')
        self.fields["template"].choices = choices


class AddLocationForm(forms.Form):
    name = forms.CharField(
        label=_("名称"),
        max_length=128,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    public = forms.BooleanField(
        label=_("公开"),
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        initial=True,
    )


class ApplyLocationForm(forms.Form):
    note = forms.CharField(
        label=_("备注"),
        max_length=256,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
