from django.conf import settings


def college_info(request):
    return {
        'college_name': settings.COLLEGE_NAME,
        'college_address': settings.COLLEGE_ADDRESS,
        'college_contact': settings.COLLEGE_CONTACT,
        'college_email': settings.COLLEGE_EMAIL,
        'academic_year': settings.ACADEMIC_YEAR,
    }
