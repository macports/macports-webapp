from django import forms

from buildhistory.models import Builder

STATUS_CHOICES = [
    ("build successful", "Successful Builds"),
    ("failed install-port", "Failed install-port"),
    ("failed install-dependencies", "Failed install-dependencies"),
]


class BuildHistoryForm(forms.Form):
    builder_name__name = forms.MultipleChoiceField(
        choices=[("", "")],
        widget=forms.SelectMultiple(attrs={
            "class": "selectpicker",
            "multiple": "multiple",
            "data-size": 8,
            "data-deselect-all-text": "Reset",
            "data-select-all-text": "Select All",
            "data-actions-box": "true",
            "data-width": "300px",
            "data-none-selected-text": "All"
        }),
        required=False
    )

    status = forms.MultipleChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.SelectMultiple(attrs={
            "class": "selectpicker",
            "multiple": "multiple",
            "data-size": 8,
            "data-deselect-all-text": "Reset",
            "data-select-all-text": "Select All",
            "data-actions-box": "true",
            "data-width": "300px",
            "data-none-selected-text": "All"
        }),
        required=False
    )

    port_name = forms.CharField(
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Port name"
        }),
        required=False
    )

    unresolved = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            "onchange": "this.form.submit();"
        })
    )

    def __init__(self, *args, **kwargs):
        super(BuildHistoryForm, self).__init__(*args, **kwargs)

        # Load choices here so db calls are not made during migrations.
        self.fields['builder_name__name'].choices = [(builder.name, builder.name) for builder in Builder.objects.all()]
