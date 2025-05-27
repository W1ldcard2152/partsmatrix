from django.shortcuts import render
from django.http import JsonResponse
from .models import Part, InterchangeGroup


def home(request):
    """Basic home page showing system status"""
    context = {
        'total_parts': Part.objects.count(),
        'total_manufacturers': Part.objects.values('manufacturer').distinct().count(),
        'total_interchange_groups': InterchangeGroup.objects.count(),
    }
    return render(request, 'parts/home.html', context)


def part_search(request):
    """Simple part search functionality"""
    query = request.GET.get('q', '')
    parts = []
    
    if query:
        parts = Part.objects.filter(
            part_number__icontains=query
        ).select_related('manufacturer', 'category')[:50]
    
    context = {
        'query': query,
        'parts': parts,
    }
    return render(request, 'parts/search.html', context)
