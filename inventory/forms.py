from django import forms


class AddItemForm(forms.Form):
    name = forms.CharField(
        label="名称",
        max_length=128,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    quantity = forms.DecimalField(
        label="数量", widget=forms.TextInput(attrs={'class': 'form-control'}))
    unit = forms.CharField(
        label="单位",
        max_length=32,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
