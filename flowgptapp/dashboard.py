"""
Admin dashboard for FlowGPT with data visualizations.
"""
from django.views.generic import TemplateView
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.db.models import Count
from .models import Node, Pipeline, Edge, PipelineExecution, ExecutionStep, Contact
from .admin_charts import (
    generate_contact_charts,
    generate_node_charts,
    generate_pipeline_charts,
    generate_edge_charts,
    generate_execution_charts,
    generate_execution_step_charts
)


@method_decorator(staff_member_required, name='dispatch')
class AdminDashboardView(TemplateView):
    """Admin dashboard view with data analytics."""
    template_name = 'admin/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add summary counts
        context['pipeline_count'] = Pipeline.objects.count()
        context['active_pipeline_count'] = Pipeline.objects.filter(is_active=True).count()
        context['node_count'] = Node.objects.count()
        context['edge_count'] = Edge.objects.count()
        context['execution_count'] = PipelineExecution.objects.count()
        context['completed_execution_count'] = PipelineExecution.objects.filter(is_complete=True).count()
        context['execution_step_count'] = ExecutionStep.objects.count()
        context['contact_count'] = Contact.objects.count()
        context['unread_contact_count'] = Contact.objects.filter(is_read=False).count()
        
        # Get model distributions
        context['node_type_distribution'] = (Node.objects.values('node_type')
                                             .annotate(count=Count('id'))
                                             .order_by('-count'))
        
        # Generate charts
        context['contact_charts'] = generate_contact_charts()
        context['node_charts'] = generate_node_charts()
        context['pipeline_charts'] = generate_pipeline_charts()
        context['edge_charts'] = generate_edge_charts()
        context['execution_charts'] = generate_execution_charts()
        context['execution_step_charts'] = generate_execution_step_charts()
        
        return context 