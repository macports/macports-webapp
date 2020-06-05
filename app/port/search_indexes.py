from haystack import indexes

from port.models import Port
from buildhistory.models import BuildHistory


class PortIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    name = indexes.NgramField(model_attr='name', boost=2.0)
    name_l = indexes.IntegerField()
    maintainers = indexes.MultiValueField(boost=1.2, faceted=True)
    description = indexes.CharField(model_attr='description', boost=1.5)
    variants = indexes.MultiValueField(faceted=True)
    livecheck_broken = indexes.BooleanField()
    livecheck_outdated = indexes.BooleanField()
    nomaintainer = indexes.BooleanField()
    active = indexes.BooleanField(model_attr='active')
    categories = indexes.MultiValueField(faceted=True)
    version = indexes.CharField(model_attr='version', indexed=False)
    files = indexes.MultiValueField()

    def get_model(self):
        return Port

    def prepare_name_l(self, obj):
        return len(obj.name)

    def prepare_maintainers(self, obj):
        return [m.github for m in obj.maintainers.all()]

    def prepare_nomaintainer(self, obj):
        return False if obj.maintainers.all().count() > 0 else True

    def prepare_variants(self, obj):
        return [v.variant for v in obj.variants.all()]

    def prepare_livecheck_broken(self, obj):
        if hasattr(obj, 'livecheck'):
            return False if obj.livecheck.error is None else True
        else:
            return False

    def prepare_livecheck_outdated(self, obj):
        if hasattr(obj, 'livecheck'):
            return obj.livecheck.has_updates
        else:
            return False

    def prepare_categories(self, obj):
        return [c.name for c in obj.categories.all()]

    def prepare_files(self, obj):
        port_name = obj.name
        latest_build = BuildHistory.objects.filter(port_name__iexact=port_name, status="build successful").order_by('-time_start').prefetch_related('files').first()
        if latest_build:
            return [f.file for f in latest_build.files.all()]
        else:
            return []
