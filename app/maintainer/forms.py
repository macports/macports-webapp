from haystack.forms import SearchForm
from haystack.query import EmptySearchQuerySet, SearchQuerySet

from maintainer.models import Maintainer


class MaintainerAutocompleteForm(SearchForm):
    def no_query_found(self):
        return EmptySearchQuerySet()

    def search(self):
        if not self.is_valid():
            return self.no_query_found()

        sqs = SearchQuerySet().models(Maintainer)

        if self.cleaned_data['q']:
            sqs = sqs.autocomplete(github=self.cleaned_data['q'])
        return sqs
