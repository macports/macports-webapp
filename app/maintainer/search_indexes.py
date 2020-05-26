from haystack import indexes
from maintainer.models import Maintainer


class MaintainerIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    github = indexes.NgramField(model_attr='github')

    def get_model(self):
        return Maintainer
