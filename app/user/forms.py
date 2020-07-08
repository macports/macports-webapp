from django import forms

from buildhistory.models import Builder


class MyPortsForm(forms.Form):
    livecheck_outdated = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            "onchange": "this.form.submit();",
            "class": "form-check-input"
        })
    )

    livecheck_errored = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            "onchange": "this.form.submit();",
            "class": "form-check-input"
        })
    )

    build_broken = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            "onchange": "this.form.submit();",
            "class": "form-check-input"
        })
    )

    build_ok = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            "onchange": "this.form.submit();",
            "class": "form-check-input"
        })
    )

    no_build = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            "onchange": "this.form.submit();",
            "class": "form-check-input"
        })
    )

    builder = forms.ChoiceField(
        choices=[("", "")],
        widget=forms.Select(attrs={
            "onchange": "this.form.submit();",
            "class": "form-control"
        })
    )

    hide_deleted = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            "onchange": "this.form.submit();",
            "class": "form-check-input"
        })
    )

    def __init__(self, *args, **kwargs):
        super(MyPortsForm, self).__init__(*args, **kwargs)

        # Load choices here so db calls are not made during migrations.
        self.fields['builder'].choices = [(builder.name, builder.name) for builder in Builder.objects.all()]
