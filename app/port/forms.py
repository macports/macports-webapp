from django import forms
from django.utils.translation import gettext as _
from haystack.forms import SearchForm
from haystack.query import SearchQuerySet, SQ

from port.models import Port


class AdvancedSearchForm(SearchForm):
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
    livecheck_broken = forms.BooleanField(required=False, initial=False)
    livecheck_outdated = forms.BooleanField(required=False, initial=False)
    active = forms.BooleanField(required=False, initial=False)


    def no_query_found(self):
        return SearchQuerySet().models(Port)

    def search(self):
        if not self.is_valid():
            return self.no_query_found()

        if not self.cleaned_data.get('active'):
            sqs = SearchQuerySet().models(Port).all().narrow('active=True')
        else:
            sqs = SearchQuerySet().models(Port).all()
        do_sort = False

        # If a search query is present, only then perform the search operations
        if self.cleaned_data.get('q'):
            if self.cleaned_data['maintainers']:
                sqs = sqs.filter_or(maintainers=self.cleaned_data['q'])

            if self.cleaned_data['name']:
                sqs = sqs.filter_or(name=self.cleaned_data['q'])
                do_sort = True

            if self.cleaned_data['variants']:
                sqs = sqs.filter_or(variants__contains=self.cleaned_data['q'])

            if self.cleaned_data['description']:
                sqs = sqs.filter_or(description=self.cleaned_data['q'])
                do_sort = False

            if do_sort:
                sqs = sqs.order_by('name_l')

        # Filter operations, perform even if a search query is absent
        # This is done to allow viewing all "outdated ports", "all ports with broken livecheck" etc.
        f = SQ()
        if self.cleaned_data['livecheck_broken']:
            f = SQ(livecheck_broken=True)

        if self.cleaned_data['livecheck_outdated']:
            f = f | SQ(livecheck_outdated=True)

        sqs = sqs.filter(f)

        return sqs
