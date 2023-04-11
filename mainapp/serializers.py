from rest_framework import serializers
from .models import NotionalGreeks, ZDTEDates

class DynamicFieldsModelSerializer(serializers.ModelSerializer):
    """
    A ModelSerializer that takes an additional `fields` argument that
    controls which fields should be displayed.
    """

    def __init__(self, *args, **kwargs):
        # Don't pass the 'fields' arg up to the superclass
        fields = kwargs.pop('fields', None)

        # Instantiate the superclass normally
        super().__init__(*args, **kwargs)

        if fields is not None:
            # Drop any fields that are not specified in the `fields` argument.
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)

class NotionalGreekSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = NotionalGreeks
        fields = '__all__'

class ZDTEDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ZDTEDates
        fields = '__all__'
        # fields = ('quote_datetime')