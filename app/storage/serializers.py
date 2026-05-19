from .models import Storage
from rest_framework import serializers


class StorageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Storage
        fields = '__all__'
        read_only_fields = ('company',)

    def validate_address(self, value):
        if len(value) < 5:
            raise serializers.ValidationError('Адрес должен быть не менее 5 символов')
        return value