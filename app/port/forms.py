from django import forms
from django.utils.translation import gettext as _
from haystack.forms import FacetedSearchForm
from haystack.query import SearchQuerySet, SQ

from port.models import Port


class AdvancedSearchForm(FacetedSearchForm):
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

    name = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            "form": "super-form",
            "onchange": "this.form.submit();"
        })
    )
    livecheck_broken = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            "form": "super-form",
            "onchange": "this.form.submit();"
        })
    )
    livecheck_outdated = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            "form": "super-form",
            "onchange": "this.form.submit();"
        })
    )
    nomaintainer = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            "form": "super-form",
            "onchange": "this.form.submit();"
        })
    )
    show_deleted_ports = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            "form": "super-form",
            "onchange": "this.form.submit();"
        })
    )

    def no_query_found(self):
        return SearchQuerySet().models(Port)

    def search(self):
        if not self.is_valid():
            return self.no_query_found()

        sqs = SearchQuerySet().models(Port).facet('maintainers').facet('categories').facet('variants')

        # Performing narrowing based on facets
        for facet in self.selected_facets:
            if ":" not in facet:
                continue

            field, value = facet.split(":", 1)

            if value:
                sqs = sqs.narrow('%s:"%s"' % (field, sqs.query.clean(value)))

        do_sort = False

        # Filter out deleted ports, based on query
        if not self.cleaned_data.get('show_deleted_ports'):
            sqs = sqs.filter(active=True)

        # If a search query is present, only then perform the search operations
        if self.cleaned_data.get('q'):
            if self.cleaned_data['name']:
                sqs = sqs.filter(name=self.cleaned_data['q'])
                do_sort = True
            else:
                sqs = sqs.filter(SQ(name=self.cleaned_data['q']) | SQ(description=self.cleaned_data['q']))

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
