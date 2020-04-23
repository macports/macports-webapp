from django.shortcuts import render
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

from variant.models import Variant


def variant(request, variant):
    all_objects = Variant.objects.filter(variant=variant, port__active=True).select_related('port').order_by(Lower('port__name'))
    all_objects_count = all_objects.count()
    paginated_objects = Paginator(all_objects, 100)
    page = request.GET.get('page', 1)
    try:
        objects = paginated_objects.get_page(page)
    except PageNotAnInteger:
        objects = paginated_objects.get_page(1)
    except EmptyPage:
        objects = paginated_objects.get_page(paginated_objects.num_pages)
    return render(request, 'variant/variant.html', {
        'objects': objects,
        'variant': variant,
        'all_objects_count': all_objects_count
    })


def search_ports_in_variant(request):
    query = request.GET.get('name', '')
    search_in = request.GET.get('variant', '')

    filtered_ports = Variant.objects.filter(variant=search_in, port__name__icontains=query, port__active=True)
    return render(request, 'filtered_table.html', {
        'ports': filtered_ports,
        'query': query,
        'search_in': search_in,
        'content': "Variant"
    })
