from rest_framework import serializers
from page.models import Page
from phase.models.phase import Phase
from project.models import Project

class PageExportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Page
        fields = ("id", "order", "title", "dynamic_data", "blocks", "html")

class PhaseExportSerializer(serializers.ModelSerializer):
    pages = serializers.SerializerMethodField()

    class Meta:
        model = Phase
        fields = ("id", "name", "index", "pages")

    def get_pages(self, obj):
        pages = obj.page_set.all().order_by("order", "id")
        return PageExportSerializer(pages, many=True).data

class ProjectExportSerializer(serializers.ModelSerializer):
    phases = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ("id", "name", "description", "created_at", "phases")

    def get_phases(self, obj):
        phases = Phase.objects.filter(project=obj).order_by("index", "id")
        return PhaseExportSerializer(phases, many=True).data