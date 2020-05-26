from haystack import indexes
from category.models import Category


class CategoryIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.NgramField(model_attr='name')

    def get_model(self):
        return Category
