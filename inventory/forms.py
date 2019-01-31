from django import forms


class AddItemForm(forms.Form):
    name = forms.CharField(
        label="名称",
        max_length=128,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    quantity = forms.FloatField(
        label="数量",
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'type': 'number',
                'min': '1e-12',
                'step': '1e-12',
                'value': '1',
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
                        required=tmp_required,
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
    quantity = forms.FloatField(
        label="使用数量",
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'type': 'number',
                'min': '1e-12',
                'step': '1e-12',
                'value': '0.5',
            }),
    )


class ApplyLocationForm(forms.Form):
    note = forms.CharField(
        label="备注",
        max_length=256,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
