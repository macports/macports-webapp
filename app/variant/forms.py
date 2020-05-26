from haystack.forms import SearchForm
from haystack.query import EmptySearchQuerySet, SearchQuerySet

from variant.models import Variant


class VariantAutocompleteForm(SearchForm):
    def no_query_found(self):
        return EmptySearchQuerySet()

    def search(self):
        if not self.is_valid():
            return self.no_query_found()

        sqs = SearchQuerySet().models(Variant)

        if self.cleaned_data['q']:
            sqs = sqs.autocomplete(variant=self.cleaned_data['q'])
        return sqs
