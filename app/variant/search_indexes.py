from haystack import indexes
from variant.models import Variant

added = {}


class CategoryIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    variant = indexes.NgramField(model_attr='variant')

    def get_model(self):
        return Variant

    def prepare_variant(self, obj):
        # This is done to maintain only unique entries in the index
        # I could not find a nicer way to do this using haystack itself
        if added.get(obj.variant) is None:
            added[obj.variant] = True
            return obj.variant
        return None
