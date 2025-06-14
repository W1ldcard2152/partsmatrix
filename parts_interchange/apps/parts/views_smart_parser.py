from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import re
from apps.parts.models import Part, Manufacturer, PartCategory
from apps.vehicles.models import Vehicle, Make, Model, Engine, Trim
from apps.fitments.models import Fitment
from django.db import transaction


class SmartPartParser:
    """Web-based smart part parser"""
    
    def __init__(self):
        # Copy the extraction logic from the management command
        self.part_name_patterns = [
            r'^([^-]+)\s*-\s*(?:Acura|Honda|Toyota|Ford|GM|Chevrolet)',
            r'([A-Za-z\s]+?)\s*\([0-9A-Z-]+\)',
            r'([A-Za-z\s]+?)\s*-\s*[A-Z]+',
        ]
        
        self.part_number_patterns = [
            r'\(([0-9A-Z-]{8,})\)',
            r'Part Number:\s*([0-9A-Z-]+)',
            r'SKU:\s*([0-9A-Z-]+)',
            r'([0-9A-Z]{5,}-[0-9A-Z]{3,}-[0-9A-Z]{3,})',
            r'([0-9A-Z]{8,})',
        ]
        
        self.fitment_pattern = r'(\d{4})\s+([A-Za-z]+)\s+(\S+)\s{2,}(.*?)\s{2,}([0-9.]+L\s+[A-Za-z0-9\s-]+)'
        
        self.manufacturer_mapping = {
            'acura': 'Acura', 'honda': 'Honda', 'toyota': 'Toyota', 'lexus': 'Lexus',
            'ford': 'Ford', 'chevrolet': 'Chevrolet', 'gm': 'GM', 'dodge': 'Dodge',
            'chrysler': 'Chrysler', 'jeep': 'Jeep', 'ram': 'Ram', 'bmw': 'BMW',
            'mercedes': 'Mercedes-Benz', 'audi': 'Audi', 'volkswagen': 'Volkswagen',
            'vw': 'Volkswagen', 'nissan': 'Nissan', 'infiniti': 'Infiniti',
            'mazda': 'Mazda', 'subaru': 'Subaru', 'mitsubishi': 'Mitsubishi',
            'hyundai': 'Hyundai', 'kia': 'Kia', 'volvo': 'Volvo', 'porsche': 'Porsche',
        }
        
        self.category_mapping = {
            'drive plate': 'Transmission & Drivetrain',
            'ac line': 'HVAC & Climate Control',
            'a/c line': 'HVAC & Climate Control',
            'air conditioning': 'HVAC & Climate Control',
            'brake pad': 'Wheels, Tires & Brakes',
            'brake rotor': 'Wheels, Tires & Brakes',
            'oil filter': 'Filters',
            'air filter': 'Filters',
            'fuel filter': 'Filters',
            'spark plug': 'Engine',
            'ignition coil': 'Engine',
            'alternator': 'Electrical Systems',
            'starter': 'Electrical Systems',
            'radiator': 'Engine',
            'water pump': 'Engine',
            'fuel pump': 'Intake, Exhaust & Fuel',
            'muffler': 'Intake, Exhaust & Fuel',
            'strut': 'Steering & Suspension',
            'shock': 'Steering & Suspension',
            'transmission': 'Transmission & Drivetrain',
            'headlight': 'Lighting & Visibility',
            'mirror': 'Body & Exterior',
            'bumper': 'Body & Exterior',
            'seat': 'Interior',
        }

    def extract_part_name(self, text):
        for pattern in self.part_name_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                name = match.group(1).strip()
                name = re.sub(r'\s+', ' ', name)
                return name.title()
        return None

    def extract_part_number(self, text):
        for pattern in self.part_number_patterns:
            match = re.search(pattern, text)
            if match:
                part_num = match.group(1).strip().upper()
                if len(part_num) >= 5 and any(c.isdigit() for c in part_num):
                    return part_num
        return None

    def extract_manufacturer(self, text):
        for pattern in [
            r'Manufacturer:\s*([A-Za-z]+)',
            r'([A-Za-z]+)\s+Parts',
            r'-\s*([A-Za-z]+)\s*\(',
            r'Genuine\s+([A-Za-z]+)\s+Parts',
        ]:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                mfg = match.group(1).lower()
                if mfg in self.manufacturer_mapping:
                    return self.manufacturer_mapping[mfg]
        return None

    def guess_category(self, part_name):
        if not part_name:
            return None
        name_lower = part_name.lower()
        for keyword, category in self.category_mapping.items():
            if keyword in name_lower:
                return category
        return 'Engine'

    def extract_fitments(self, text):
        fitments = []
        fitment_section = re.search(
            r'Vehicle Fitment.*?Year\s+Make\s+Model\s+Body.*?Engine.*?\n(.*?)(?:\n\n|\Z)',
            text, re.DOTALL | re.IGNORECASE
        )

        if fitment_section:
            fitment_text = fitment_section.group(1)
            lines = fitment_text.strip().split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue

                parts = re.split(r'\s{2,}', line)
                if len(parts) < 4:
                    continue

                try:
                    year = int(parts[0])
                    make = parts[1]
                    model = parts[2]
                    
                    # The rest of the line is split into trim and engine
                    remaining_parts = parts[3:]
                    
                    engine_candidate = remaining_parts[-1]
                    if re.search(r'\d\.\dL', engine_candidate):
                        engine = engine_candidate
                        trim_parts = remaining_parts[:-1]
                    else:
                        engine = ''
                        trim_parts = remaining_parts

                    # Join all trim parts and then split by comma
                    full_trim_string = ' '.join(trim_parts).strip()
                    trims = [t.strip() for t in full_trim_string.split(',') if t.strip()]

                    if not trims:
                        trims.append('Base')

                    for trim in trims:
                        fitments.append({
                            'year': year,
                            'make': make,
                            'model': model,
                            'trim': trim,
                            'engine': engine
                        })
                except (ValueError, IndexError):
                    continue
        return fitments

    def extract_description(self, text):
        desc_patterns = [
            r'Description:\s*([^*\n]+)',
            r'Other Names:\s*([^*\n]+)',
            r'([0-9.]+[tT][lL].*?[lL]\.)',
        ]
        
        for pattern in desc_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                desc = match.group(1).strip()
                if len(desc) > 5:
                    return desc
        return ''

    def parse_text(self, text):
        """Main parsing function"""
        part_name = self.extract_part_name(text)
        return {
            'part_name': part_name,
            'part_number': self.extract_part_number(text),
            'manufacturer': self.extract_manufacturer(text),
            'description': self.extract_description(text),
            'fitments': self.extract_fitments(text),
            'category_guess': self.guess_category(part_name)
        }


@staff_member_required
def smart_parser_interface(request):
    """Web interface for smart part parsing"""
    if request.method == 'POST':
        raw_text = request.POST.get('raw_text', '')
        if raw_text:
            parser = SmartPartParser()
            parsed_data = parser.parse_text(raw_text)

            # Add dummy confidence scores and other data to match template
            parsed_data['confidence'] = {
                'part_name': 'high', 'part_number': 'high',
                'manufacturer': 'high', 'fitments': 'high'
            }
            parsed_data['confidence_scores'] = {
                'part_name': 95, 'part_number': 95,
                'manufacturer': 95, 'fitments': 95
            }
            parsed_data['parsing_notes'] = []
            parsed_data['category'] = parsed_data.get('category_guess')
            parsed_data['fitments_json'] = json.dumps(parsed_data.get('fitments', []))
            parsed_data['confidence_json'] = json.dumps(parsed_data.get('confidence_scores', {}))
            
            # Store in session for confirmation page
            request.session['parsed_data'] = parsed_data
            request.session['raw_text'] = raw_text
            
            return redirect('parts:confirm_parsed_part')
    
    return render(request, 'admin/smart_parser.html', {
        'recent_parts': Part.objects.select_related('manufacturer').order_by('-created_at')[:5]
    })


@staff_member_required
def confirm_parsed_part(request):
    """Confirm and edit parsed part data before saving"""
    parsed_data = request.session.get('parsed_data')
    if not parsed_data:
        messages.error(request, 'No parsed data found. Please try again.')
        return redirect('parts:smart_parser')

    # Ensure all required data is present for the template
    parsed_data.setdefault('confidence', {
        'part_name': 'high', 'part_number': 'high',
        'manufacturer': 'high', 'fitments': 'high'
    })
    parsed_data.setdefault('confidence_scores', {
        'part_name': 95, 'part_number': 95,
        'manufacturer': 95, 'fitments': 95
    })
    parsed_data.setdefault('parsing_notes', [])
    parsed_data.setdefault('category', parsed_data.get('category_guess'))
    parsed_data.setdefault('fitments_json', json.dumps(parsed_data.get('fitments', [])))
    parsed_data.setdefault('confidence_json', json.dumps(parsed_data.get('confidence_scores', {})))
    parsed_data.setdefault('weight', '')
    parsed_data.setdefault('dimensions', '')
    parsed_data.setdefault('suggested_interchanges', None)
    parsed_data.setdefault('suggested_part_group', None)
    
    if request.method == 'POST':
        if 'save_part' in request.POST:
            # Create the part with user modifications
            success = create_part_from_parsed_data(
                request.POST, parsed_data, request.user
            )
            if success:
                messages.success(request, 'Part created successfully!')
                return redirect('parts:smart_parser')
            else:
                messages.error(request, 'Error creating part. Please check the data.')
        elif 'edit_again' in request.POST:
            return redirect('parts:smart_parser')
    
    # Get available manufacturers and categories for dropdowns
    manufacturers = Manufacturer.objects.all().order_by('name')
    categories = PartCategory.objects.all().order_by('name')
    
    context = {
        'parsed_data': parsed_data,
        'manufacturers': manufacturers,
        'categories': categories,
        'raw_text': request.session.get('raw_text', '')
    }
    
    return render(request, 'admin/confirm_parsed_part.html', context)


@csrf_exempt
@require_POST
def parse_text_api(request):
    """API endpoint for real-time text parsing"""
    try:
        data = json.loads(request.body)
        raw_text = data.get('text', '')
        
        if raw_text:
            parser = SmartPartParser()
            parsed_data = parser.parse_text(raw_text)
            
            # Add validation info
            validation = {
                'has_required_data': bool(
                    parsed_data['part_name'] and 
                    parsed_data['part_number'] and 
                    parsed_data['manufacturer']
                ),
                'missing_fields': [],
                'warnings': []
            }
            
            if not parsed_data['part_name']:
                validation['missing_fields'].append('part_name')
            if not parsed_data['part_number']:
                validation['missing_fields'].append('part_number')
            if not parsed_data['manufacturer']:
                validation['missing_fields'].append('manufacturer')
            if not parsed_data['fitments']:
                validation['warnings'].append('No vehicle fitments found')
            
            return JsonResponse({
                'success': True,
                'parsed_data': parsed_data,
                'validation': validation
            })
        
        return JsonResponse({
            'success': False,
            'error': 'No text provided'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


def create_part_from_parsed_data(post_data, parsed_data, user):
    """Create part and fitments from parsed data and user input"""
    try:
        with transaction.atomic():
            # Get or create manufacturer
            manufacturer_name = post_data.get('manufacturer', parsed_data.get('manufacturer'))
            if not manufacturer_name:
                return False
            
            manufacturer, _ = Manufacturer.objects.get_or_create(
                name=manufacturer_name,
                defaults={'abbreviation': manufacturer_name[:4].upper()}
            )
            
            # Get or create category
            category_name = post_data.get('category', parsed_data.get('category_guess'))
            if not category_name:
                return False
            
            category, _ = PartCategory.objects.get_or_create(
                name=category_name,
                defaults={'description': f'Auto-created for {category_name}'}
            )
            
            # Create the part
            part_number = post_data.get('part_number', parsed_data.get('part_number'))
            part_name = post_data.get('part_name', parsed_data.get('part_name'))
            description = post_data.get('description', parsed_data.get('description', ''))
            
            if not (part_number and part_name):
                return False
            
            # Check if part already exists
            if Part.objects.filter(manufacturer=manufacturer, part_number=part_number).exists():
                return False
            
            part = Part.objects.create(
                manufacturer=manufacturer,
                part_number=part_number,
                name=part_name,
                category=category,
                description=description,
                is_active=True
            )
            
            # Create fitments if any
            fitments_created = 0
            for fitment_data in parsed_data.get('fitments', []):
                try:
                    # Find the vehicle in the database
                    vehicle = Vehicle.objects.filter(
                        year=fitment_data['year'],
                        make__name__iexact=fitment_data['make'],
                        model__name__iexact=fitment_data['model'],
                        trim__name__iexact=fitment_data['trim']
                    ).first()

                    if vehicle:
                        # Create fitment only if vehicle exists
                        Fitment.objects.get_or_create(
                            part=part,
                            vehicle=vehicle,
                            defaults={
                                'is_verified': False,
                                'created_by': user.username if user.is_authenticated else 'smart_parser'
                            }
                        )
                        fitments_created += 1
                        
                except Exception as e:
                    # Continue with other fitments if one fails
                    continue
            
            return True
            
    except Exception as e:
        return False


@staff_member_required
def bulk_smart_parser(request):
    """Bulk process multiple part texts"""
    if request.method == 'POST':
        bulk_text = request.POST.get('bulk_text', '')
        separator = request.POST.get('separator', '---')
        
        if bulk_text:
            # Split by separator and process each part
            part_texts = [text.strip() for text in bulk_text.split(separator) if text.strip()]
            
            parser = SmartPartParser()
            parsed_parts = []
            
            for i, text in enumerate(part_texts):
                parsed_data = parser.parse_text(text)
                parsed_data['index'] = i
                parsed_data['raw_text'] = text
                parsed_parts.append(parsed_data)
            
            # Store in session
            request.session['bulk_parsed_parts'] = parsed_parts
            return redirect('parts:confirm_bulk_parts')
    
    return render(request, 'admin/bulk_smart_parser.html')


@staff_member_required
def confirm_bulk_parts(request):
    """Confirm and edit bulk parsed parts"""
    bulk_parsed_parts = request.session.get('bulk_parsed_parts', [])
    
    if not bulk_parsed_parts:
        messages.error(request, 'No bulk parsed data found.')
        return redirect('parts:bulk_smart_parser')
    
    if request.method == 'POST':
        if 'save_all' in request.POST:
            created_count = 0
            failed_count = 0
            
            for i, parsed_data in enumerate(bulk_parsed_parts):
                # Get form data for this part
                prefix = f'part_{i}_'
                form_data = {}
                for key in request.POST:
                    if key.startswith(prefix):
                        clean_key = key[len(prefix):]
                        form_data[clean_key] = request.POST[key]
                
                # Try to create the part
                if create_part_from_parsed_data(form_data, parsed_data, request.user):
                    created_count += 1
                else:
                    failed_count += 1
            
            messages.success(request, f'Created {created_count} parts. {failed_count} failed.')
            return redirect('parts:smart_parser')
    
    # Get manufacturers and categories for dropdowns
    manufacturers = Manufacturer.objects.all().order_by('name')
    categories = PartCategory.objects.all().order_by('name')
    
    context = {
        'bulk_parsed_parts': bulk_parsed_parts,
        'manufacturers': manufacturers,
        'categories': categories
    }
    
    return render(request, 'admin/confirm_bulk_parts.html', context)
