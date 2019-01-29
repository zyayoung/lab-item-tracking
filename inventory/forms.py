from django import forms


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
                'min': '0.00',
            }),
        min_value=0,
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


class ChooseTemplateForm(forms.Form):
    template = forms.ChoiceField(
        label="类型",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    def __init__(self, *args, **kwargs):
        super(ChooseTemplateForm, self).__init__(*args)
        self.fields["template"].choices = kwargs.get('choices', [('', '--')])


class AddLocationForm(forms.Form):
    name = forms.CharField(
        label="名称",
        max_length=128,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
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
