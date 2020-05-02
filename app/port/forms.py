from django import forms
from django.utils.translation import gettext as _
from haystack.forms import SearchForm
from haystack.query import EmptySearchQuerySet, SearchQuerySet

from port.models import Port


class AdvancedSearch(SearchForm):
    show_deleted_ports = forms.BooleanField(required=False)
    q = forms.CharField(
        required=False,
        label=_("Search"),
        widget=forms.TextInput(attrs={
            "type": "search",
            "placeholder": "Search for ports",
            "class": "form-control rounded-pill",
            "autofocus": "autofocus",
        }),
    )

    name = forms.BooleanField(required=False, initial=True)
    maintainers = forms.BooleanField(required=False)
    variants = forms.BooleanField(required=False)
    description = forms.BooleanField(required=False, initial=True)

    def no_query_found(self):
        return EmptySearchQuerySet()

    def search(self):
        if not self.is_valid():
            return self.no_query_found()

        if not self.cleaned_data.get("q"):
            return self.no_query_found()

        sqs = SearchQuerySet().models(Port).all()

        if self.cleaned_data['maintainers']:
            sqs = sqs.filter_or(maintainers__contains=self.cleaned_data['q'])

        if self.cleaned_data['name']:
            sqs = sqs.filter_or(name__contains=self.cleaned_data["q"])

        if self.cleaned_data['variants']:
            sqs = sqs.filter_or(variants__contains=self.cleaned_data['q'])

        if self.cleaned_data['description']:
            sqs = sqs.filter_or(description__contains=self.cleaned_data['q'])

        return sqs
