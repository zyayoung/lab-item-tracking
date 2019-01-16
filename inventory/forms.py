from django import forms


class AddItemForm(forms.Form):
    name = forms.CharField(
        label="名称",
        max_length=128,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    quantity = forms.DecimalField(
        label="数量",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'type': 'number',
            'step': '1',
            'value': '0',
        }))
    unit = forms.CharField(
        label="单位",
        max_length=32,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}))


class UseItemForm(forms.Form):
    quantity = forms.DecimalField(
        label="使用数量",
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'type': 'number',
                'step': '1',
                'min': '0',
                'value': '0',
            }))
