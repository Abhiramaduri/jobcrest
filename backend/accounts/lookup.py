import uuid
from django.shortcuts import get_object_or_404
from django.http import Http404
from rest_framework import serializers


def get_object_by_uuid_or_id(model_or_qs, identifier, **kwargs):
    """
    Looks up a model instance by UUID (preferred and secure) with integer fallback.
    """
    id_str = str(identifier).strip()
    try:
        val = uuid.UUID(id_str)
        return get_object_or_404(model_or_qs, uuid=val, **kwargs)
    except (ValueError, AttributeError):
        if id_str.isdigit():
            return get_object_or_404(model_or_qs, id=int(id_str), **kwargs)
        raise Http404("Item not found.")


class FlexibleUUIDRelatedField(serializers.RelatedField):
    """
    A serializer field that resolves a related model instance by UUID, ID, or slug.
    Outputs UUID as representation.
    """
    def __init__(self, model, slug_field=None, **kwargs):
        self.target_model = model
        self.slug_field = slug_field
        super().__init__(queryset=model.objects.all(), **kwargs)

    def to_representation(self, value):
        return str(getattr(value, 'uuid', getattr(value, 'id', value)))

    def to_internal_value(self, data):
        data_str = str(data).strip()
        # 1. UUID lookup
        try:
            val_uuid = uuid.UUID(data_str)
            obj = self.target_model.objects.filter(uuid=val_uuid).first()
            if obj:
                return obj
        except (ValueError, AttributeError):
            pass

        # 2. Integer ID fallback
        if data_str.isdigit():
            obj = self.target_model.objects.filter(id=int(data_str)).first()
            if obj:
                return obj

        # 3. Slug lookup if supported
        if self.slug_field and hasattr(self.target_model, self.slug_field):
            obj = self.target_model.objects.filter(**{self.slug_field: data_str}).first()
            if obj:
                return obj

        raise serializers.ValidationError(f"Invalid {self.target_model.__name__} identifier: '{data}'.")
