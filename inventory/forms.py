from django import forms


class AddForm(forms.Form):
    name = forms.CharField(
        label="名称",
        max_length=128,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    location = forms.CharField(
        label="位置(用空格隔开)",
        max_length=256,
        widget=forms.TextInput(attrs={'class': 'form-control'}))
    quantity = forms.DecimalField(
        label="数量",
        widget=forms.TextInput(attrs={'class': 'form-control'}))
