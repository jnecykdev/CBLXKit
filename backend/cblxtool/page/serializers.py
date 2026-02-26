#page/serializers.py
from .models import *
from rest_framework import serializers
from drf_base64.fields import Base64ImageField, Base64FileField

class PageSerializer(serializers.ModelSerializer):
    title = serializers.SerializerMethodField()
    type = serializers.SerializerMethodField()
    content = serializers.SerializerMethodField()

    class Meta:
        model = Page
        fields = ['id', 'order', 'phase_name', 'project_id', 'title', 'type', 'dynamic_data', 'blocks', 'content']

    def get_title(self, obj):
        # Gera o título dinâmico baseado no order
        return f"Página {obj.order}"
    
    def get_type(self, obj):
        return 'steps' if obj.order == 1 else 'content'

    def get_content(self, obj):
        # páginas steps não usam content
        return ""
    
class PageHtmlUpdateSerializer(serializers.ModelSerializer):
    # O frontend manda "dynamic", mas o model tem "dynamic_data"
    dynamic = serializers.JSONField(
        source='dynamic_data',
        required=False,
        allow_null=True
    )

    # Vamos permitir title vindo do frontend
    title = serializers.CharField(
        required=False,
        allow_blank=True,
        allow_null=True
    )

    # order e phase vêm no payload, mas não queremos complicar a validação
    order = serializers.IntegerField(required=False)
    # phase = serializers.CharField(required=False)

    blocks = serializers.JSONField(required=False)

    class Meta:
        model = Page
        fields = ['id', 'html', 'title', 'order', 'phase_name', 'dynamic', 'blocks']

    def update(self, instance, validated_data):
        # html é obrigatório para esse endpoint
        html = validated_data.get('html', None)
        if html is not None:
            instance.html = html

        title = validated_data.get('title', None)
        if title is not None:
            instance.title = title

        # Se o frontend mandar dynamic → dynamic_data
        if 'dynamic_data' in validated_data:
            instance.dynamic_data = validated_data['dynamic_data']

        blocks = validated_data.get('blocks', None)
        if blocks is not None:
            instance.blocks = blocks

        # order e phase são opcionais
        order = validated_data.get('order', None)
        if order is not None:
            instance.order = order

        instance.save()
        return instance