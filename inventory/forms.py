from django import forms
from login.models import User as myUser


class AddItemForm(forms.Form):
    name = forms.CharField(
        label="名称",
        max_length=128,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    quantity = forms.DecimalField(
        label="数量",
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'type': 'number',
                'step': '0.01',
                'value': '1',
                'min': '0.01',
            }),
        min_value=0.01,
    )
    unit = forms.CharField(
        label="单位",
        max_length=32,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    public = forms.BooleanField(
        label="公开",
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    )


class UseItemForm(forms.Form):
    quantity = forms.DecimalField(
        label="使用数量",
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'type': 'number',
                'step': '0.01',
                'min': '0.01',
                'value': '1',
            }),
    )


class ApplyLocationForm(forms.Form):
    note = forms.CharField(
        label="备注",
        max_length=256,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )

class SelectUserForm(forms.Form):
    values = [(user.id, user.name) for user in myUser.objects.all()]
    share = forms.CharField(widget=forms.widgets.Select(choices=values))

