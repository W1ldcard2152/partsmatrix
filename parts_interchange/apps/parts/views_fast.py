from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from apps.parts.models import Part, Manufacturer, PartCategory
from apps.vehicles.models import Vehicle, Make, Model
from apps.fitments.models import Fitment


@staff_member_required
def fast_parts_list(request):
    """Ultra-fast parts list for data entry"""
    search = request.GET.get('search', '')
    manufacturer_id = request.GET.get('manufacturer')
    category_id = request.GET.get('category')
    
    parts = Part.objects.select_related('manufacturer', 'category').filter(is_active=True)
    
    if search:
        parts = parts.filter(
            Q(part_number__icontains=search) | 
            Q(name__icontains=search)
        )
    
    if manufacturer_id:
        parts = parts.filter(manufacturer_id=manufacturer_id)
        
    if category_id:
        parts = parts.filter(category_id=category_id)
    
    paginator = Paginator(parts, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    manufacturers = Manufacturer.objects.all().order_by('abbreviation')
    categories = PartCategory.objects.filter(parent_category__isnull=True).order_by('name')
    
    context = {
        'parts': page_obj,
        'manufacturers': manufacturers,
        'categories': categories,
        'search': search,
        'selected_manufacturer': manufacturer_id,
        'selected_category': category_id,
        'total_count': parts.count() if search or manufacturer_id or category_id else None
    }
    
    return render(request, 'admin/fast_parts_list.html', context)


@staff_member_required
def fast_part_add(request):
    """Ultra-fast part entry form"""
    if request.method == 'POST':
        try:
            part = Part.objects.create(
                manufacturer_id=request.POST['manufacturer'],
                part_number=request.POST['part_number'],
                name=request.POST['name'],
                category_id=request.POST['category'],
                description=request.POST.get('description', ''),
                weight=request.POST.get('weight') or None,
                dimensions=request.POST.get('dimensions', ''),
                is_active=True
            )
            
            messages.success(request, f'Part {part.part_number} created successfully!')
            
            if 'save_and_add' in request.POST:
                return redirect('fast_part_add')
            else:
                return redirect('fast_parts_list')
                
        except Exception as e:
            messages.error(request, f'Error creating part: {e}')
    
    manufacturers = Manufacturer.objects.all().order_by('abbreviation')
    categories = PartCategory.objects.all().order_by('name')
    
    context = {
        'manufacturers': manufacturers,
        'categories': categories,
    }
    
    return render(request, 'admin/fast_part_add.html', context)


@staff_member_required
def fast_part_edit(request, part_id):
    """Ultra-fast part editing"""
    part = get_object_or_404(Part, id=part_id)
    
    if request.method == 'POST':
        try:
            part.manufacturer_id = request.POST['manufacturer']
            part.part_number = request.POST['part_number']
            part.name = request.POST['name']
            part.category_id = request.POST['category']
            part.description = request.POST.get('description', '')
            part.weight = request.POST.get('weight') or None
            part.dimensions = request.POST.get('dimensions', '')
            part.save()
            
            messages.success(request, f'Part {part.part_number} updated successfully!')
            return redirect('fast_parts_list')
            
        except Exception as e:
            messages.error(request, f'Error updating part: {e}')
    
    manufacturers = Manufacturer.objects.all().order_by('abbreviation')
    categories = PartCategory.objects.all().order_by('name')
    
    context = {
        'part': part,
        'manufacturers': manufacturers,
        'categories': categories,
    }
    
    return render(request, 'admin/fast_part_edit.html', context)


@staff_member_required
def autocomplete_manufacturers(request):
    """Fast manufacturer autocomplete"""
    term = request.GET.get('term', '')
    manufacturers = Manufacturer.objects.filter(
        Q(name__icontains=term) | Q(abbreviation__icontains=term)
    )[:10]
    
    results = [{
        'id': m.id,
        'text': f"{m.abbreviation} - {m.name}"
    } for m in manufacturers]
    
    return JsonResponse({'results': results})


@staff_member_required
def autocomplete_categories(request):
    """Fast category autocomplete"""
    term = request.GET.get('term', '')
    categories = PartCategory.objects.filter(name__icontains=term)[:10]
    
    results = [{
        'id': c.id,
        'text': c.name
    } for c in categories]
    
    return JsonResponse({'results': results})


@staff_member_required
def fast_dashboard(request):
    """Fast admin dashboard with key stats"""
    stats = {
        'total_parts': Part.objects.filter(is_active=True).count(),
        'total_vehicles': Vehicle.objects.filter(is_active=True).count(),
        'total_fitments': Fitment.objects.count(),
        'recent_parts': Part.objects.select_related('manufacturer').filter(is_active=True).order_by('-created_at')[:5]
    }
    
    return render(request, 'admin/fast_dashboard.html', stats)
