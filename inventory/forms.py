from django import forms
from .models import Item, ItemTemplate
from .utils import get_my_list


class AddItemForm(forms.Form):
    name = forms.CharField(
        label="名称",
        max_length=128,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    public = forms.BooleanField(
        label="公开",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        initial=True,
    )


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
                            }),
                    )
                else:
                    objects = Item.objects.filter(template__name=tmp_type)
                    attrs = {'class': 'form-control'}
                    if tmp_required:
                        attrs['required'] = ''
                    tmp_field = forms.ChoiceField(
                        label=tmp_label,
                        required=tmp_required,
                        choices=get_my_list(user, objects).values_list(
                            'id', 'name'),
                        widget=forms.Select(attrs=attrs),
                    )
                    if not tmp_required:
                        tmp_field.choices.insert(0, [0, '--'])
                self.fields[tmp_label.replace(' ', '_')] = tmp_field


class AddTemplateForm(forms.Form):
    name = forms.CharField(
        label="名称",
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
        label="类型",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    def __init__(self, *args, **kwargs):
        super(ChooseTemplateForm, self).__init__(*args)
        if 'is_property' in kwargs.keys():
            choices = ItemTemplate.objects.filter(
                is_property=kwargs.get('is_property')).values_list(
                    'id', 'name')
        else:
            choices = ItemTemplate.objects.all().values_list('id', 'name')
        self.fields["template"].choices = choices


class AddLocationForm(forms.Form):
    name = forms.CharField(
        label="名称",
        max_length=128,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    public = forms.BooleanField(
        label="公开",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        initial=True,
    )


class ApplyLocationForm(forms.Form):
    note = forms.CharField(
        label="备注",
        max_length=256,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
