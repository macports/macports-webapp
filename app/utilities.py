from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


def paginate(request, items, paginate_by=100):
    paginated_items = Paginator(items, paginate_by)
    page = request.GET.get('page', 1)
    try:
        page_items = paginated_items.get_page(page)
    except PageNotAnInteger:
        page_items = paginated_items.get_page(1)
    except EmptyPage:
        page_items = paginated_items.get_page(paginated_items.num_pages)

    return page_items
