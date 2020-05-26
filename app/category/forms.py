from haystack.forms import SearchForm
from haystack.query import EmptySearchQuerySet, SearchQuerySet

from category.models import Category


class CategoryAutocompleteForm(SearchForm):
    def no_query_found(self):
        return EmptySearchQuerySet()

    def search(self):
        if not self.is_valid():
            return self.no_query_found()

        sqs = SearchQuerySet().models(Category)

        if self.cleaned_data['q']:
            sqs = sqs.autocomplete(name=self.cleaned_data['q'])
        return sqs
