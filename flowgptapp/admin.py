from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from .models import Node, Pipeline, Edge, PipelineExecution, ExecutionStep, Contact


class EdgeInline(admin.TabularInline):
    model = Edge
    extra = 0
    fk_name = 'pipeline'


class ExecutionStepInline(admin.TabularInline):
    model = ExecutionStep
    extra = 0
    fields = ('node', 'is_complete', 'started_at', 'completed_at')
    readonly_fields = ('started_at', 'completed_at')
    can_delete = False
    max_num = 0
    show_change_link = True


@admin.register(Node)
class NodeAdmin(admin.ModelAdmin):
    list_display = ('name', 'node_type', 'description')
    list_filter = ('node_type',)
    search_fields = ('name', 'description')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        request.nodes_count = qs.count()
        return qs
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['dashboard_url'] = reverse('admin_dashboard')
        return super().changelist_view(request, extra_context=extra_context)
    

@admin.register(Pipeline)
class PipelineAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'is_active', 'edge_count')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    inlines = [EdgeInline]
    
    def edge_count(self, obj):
        return obj.edge_set.count()
    edge_count.short_description = 'Edges'
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['dashboard_url'] = reverse('admin_dashboard')
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(Edge)
class EdgeAdmin(admin.ModelAdmin):
    list_display = ('id', 'pipeline', 'source', 'target', 'order')
    list_filter = ('pipeline', 'source', 'target')
    search_fields = ('pipeline__name', 'source__name', 'target__name')
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['dashboard_url'] = reverse('admin_dashboard')
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(PipelineExecution)
class PipelineExecutionAdmin(admin.ModelAdmin):
    list_display = ('id', 'pipeline', 'started_at', 'completed_at', 'is_complete', 'step_count')
    list_filter = ('pipeline', 'is_complete', 'started_at')
    search_fields = ('pipeline__name',)
    inlines = [ExecutionStepInline]
    readonly_fields = ('started_at', 'completed_at', 'formatted_output')
    
    def step_count(self, obj):
        return obj.executionstep_set.count()
    step_count.short_description = 'Steps'
    
    def formatted_output(self, obj):
        if not obj.output_data:
            return '-'
        try:
            import json
            data = json.loads(obj.output_data)
            formatted = json.dumps(data, indent=2)
            return mark_safe(f'<pre>{formatted}</pre>')
        except:
            return obj.output_data
    formatted_output.short_description = 'Output Data'
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['dashboard_url'] = reverse('admin_dashboard')
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(ExecutionStep)
class ExecutionStepAdmin(admin.ModelAdmin):
    list_display = ('id', 'execution', 'node', 'is_complete', 'started_at', 'completed_at')
    list_filter = ('is_complete', 'node', 'execution__pipeline')
    search_fields = ('node__name', 'execution__pipeline__name')
    readonly_fields = ('started_at', 'completed_at', 'formatted_input', 'formatted_output')
    
    def formatted_input(self, obj):
        if not obj.input_data:
            return '-'
        try:
            import json
            data = json.loads(obj.input_data)
            formatted = json.dumps(data, indent=2)
            return mark_safe(f'<pre>{formatted}</pre>')
        except:
            return obj.input_data
    formatted_input.short_description = 'Input Data'
    
    def formatted_output(self, obj):
        if not obj.output_data:
            return '-'
        try:
            import json
            data = json.loads(obj.output_data)
            formatted = json.dumps(data, indent=2)
            return mark_safe(f'<pre>{formatted}</pre>')
        except:
            return obj.output_data
    formatted_output.short_description = 'Output Data'
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['dashboard_url'] = reverse('admin_dashboard')
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'created_at', 'is_read')
    list_filter = ('is_read', 'created_at')
    search_fields = ('name', 'email', 'phone', 'message')
    readonly_fields = ('created_at',)
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['dashboard_url'] = reverse('admin_dashboard')
        return super().changelist_view(request, extra_context=extra_context)
