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
        required=False,
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
        initial=True,
    )


class EditItemForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super(EditItemForm, self).__init__(*args)
        data = kwargs.get('data')
        if data:
            for idx, (key, value) in enumerate(data.items()):
                tmp_required = bool(value.get('required', False))
                tmp_placeholder = value.get('placeholder', '')
                if value['type'].lower() == 'int':
                    tmp_field = forms.IntegerField(
                        label=key,
                        required=tmp_required,
                        widget=forms.TextInput(
                            attrs={
                                'class': 'form-control',
                                'type': 'number',
                                'step': '1',
                                'placeholder': tmp_placeholder,
                            }),
                    )
                elif value['type'].lower() == 'float':
                    tmp_field = forms.FloatField(
                        label=key,
                        required=tmp_required,
                        widget=forms.TextInput(
                            attrs={
                                'class': 'form-control',
                                'type': 'number',
                                'placeholder': tmp_placeholder,
                            }),
                    )
                elif value['type'].lower() in ['bool', 'boolean']:
                    tmp_field = forms.BooleanField(
                        label=key,
                        widget=forms.CheckboxInput(
                            attrs={
                                'class': 'form-check-input position-static',
                            }),
                    )
                else:
                    tmp_field = forms.CharField(
                        label=key,
                        max_length=128,
                        required=tmp_required,
                        widget=forms.TextInput(
                            attrs={
                                'class': 'form-control',
                                'placeholder': tmp_placeholder,
                            }),
                    )
                self.fields[key.replace(' ', '_')] = tmp_field


class ChooseTemplateForm(forms.Form):
    template = forms.ChoiceField(
        label="类型",
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    def __init__(self, *args, **kwargs):
        super(ChooseTemplateForm, self).__init__(*args)
        self.fields["template"].choices = kwargs.get('choices', [(0, '--')])


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
