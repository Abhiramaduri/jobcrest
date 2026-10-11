import django_filters
from .models import Job

class JobFilter(django_filters.FilterSet):
    location=django_filters.CharFilter(field_name='location',lookup_expr='icotains')
    salary_min=django_filters.NumberFilter(field_name='salary_min',lookup_expr='gte')
    salary_max=django_filters.NumberFilter(field_name='salary_max',lookup_expr='lte')
    experience_min=django_filters.NumberFilter(field_name='experience_min',lookup_expr='gte')
    skills=django_filters.CharFilter(method='filter_skills')

    class Meta:
        model=Job
        fields=['category','job_type','is_remote','location','salary_min','salary_max','experience_min']

    def filter_skills(self,queryset,name,value):
        skill_names=[s.strip() for s in value.split(',')]
        return queryset.filter(skills_required_name_in=skill_names).distinct()