from django import forms
from django.utils.translation import gettext as _
from haystack.forms import FacetedSearchForm
from haystack.query import SearchQuerySet, SQ

from port.models import Port


class AdvancedSearchForm(FacetedSearchForm):
    show_deleted_ports = forms.BooleanField(required=False)
    q = forms.CharField(
        required=False,
        label=_("Search"),
        widget=forms.TextInput(attrs={
            "type": "search",
            "placeholder": "Search for ports",
            "class": "form-control",
            "autofocus": "autofocus",
        }),
    )

    name = forms.BooleanField(required=False, initial=False)
    livecheck_broken = forms.BooleanField(required=False, initial=False)
    livecheck_outdated = forms.BooleanField(required=False, initial=False)
    nomaintainer = forms.BooleanField(required=False, initial=False)
    active = forms.BooleanField(required=False, initial=False)

    def no_query_found(self):
        return SearchQuerySet().models(Port)

    def search(self):
        if not self.is_valid():
            return self.no_query_found()

        sqs = super(AdvancedSearchForm, self).search()
        do_sort = False

        # Filter out deleted ports, based on query
        if not self.cleaned_data.get('show_deleted_ports'):
            sqs = sqs.filter(active=True)

        # If a search query is present, only then perform the search operations
        if self.cleaned_data.get('q'):
            if self.cleaned_data['name']:
                sqs = sqs.filter(name=self.cleaned_data['q'])
                do_sort = True

            if do_sort:
                sqs = sqs.order_by('name_l')

        # Filter operations, perform even if a search query is absent
        # This is done to allow viewing all "outdated ports", "all ports with broken livecheck" etc.
        f = SQ()
        if self.cleaned_data['livecheck_broken']:
            f = SQ(livecheck_broken=True)

        if self.cleaned_data['livecheck_outdated']:
            f = f | SQ(livecheck_outdated=True)

        if self.cleaned_data['nomaintainer']:
            f = f & SQ(nomaintainer=True)

        if f != SQ():
            sqs = sqs.filter(f)

        return sqs
