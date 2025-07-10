from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
import json
import traceback

from .models import Pipeline, PipelineExecution, ExecutionStep, Contact
from .graph.pipeline_executor import execute_pipeline


def home(request):
    """
    Home page view showing available pipelines and execution form.
    """
    pipelines = Pipeline.objects.filter(is_active=True).order_by('name')
    
    context = {
        'pipelines': pipelines,
    }
    
    return render(request, 'flowgptapp/home.html', context)


def pipeline_detail(request, pipeline_id):
    """
    View for detailed information about a specific pipeline.
    """
    pipeline = get_object_or_404(Pipeline, id=pipeline_id)
    edges = pipeline.edges.all().order_by('order')
    
    context = {
        'pipeline': pipeline,
        'edges': edges,
    }
    
    return render(request, 'flowgptapp/pipeline_detail.html', context)


def execution_history(request):
    """
    View to list execution history of pipelines.
    """
    executions = PipelineExecution.objects.all().order_by('-started_at')[:50]
    
    context = {
        'executions': executions,
    }
    
    return render(request, 'flowgptapp/execution_history.html', context)


def execution_detail(request, execution_id):
    """
    View for detailed information about a specific execution.
    """
    execution = get_object_or_404(PipelineExecution, id=execution_id)
    steps = execution.steps.all().order_by('started_at')
    
    try:
        # Parse output data if available
        output_data = json.loads(execution.output_data) if execution.output_data else {}
    except json.JSONDecodeError:
        output_data = {"error": "Invalid JSON data"}
    
    context = {
        'execution': execution,
        'steps': steps,
        'output_data': output_data,
    }
    
    return render(request, 'flowgptapp/execution_detail.html', context)


def contact(request):
    """
    View for the contact page and form handling.
    """
    if request.method == 'POST':
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone', '')
        message_text = request.POST.get('message', '')
        
        # Basic validation
        if not name or not email or not message_text:
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'flowgptapp/contact.html')
        
        # Create new contact message
        contact = Contact.objects.create(
            name=name,
            email=email,
            phone=phone,
            message=message_text
        )
        
        messages.success(request, 'Thank you for your message! We will get back to you soon.')
        return redirect('contact')
    
    return render(request, 'flowgptapp/contact.html')


@csrf_exempt
def execute_pipeline_view(request):
    """
    View to execute a pipeline with input text.
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)
    
    try:
        # Parse request data
        pipeline_id = request.POST.get('pipeline_id')
        input_text = request.POST.get('input_text', '')
        
        if not pipeline_id:
            return JsonResponse({'error': 'Pipeline ID is required'}, status=400)
        
        # Execute the pipeline
        result = execute_pipeline(int(pipeline_id), input_text)
        
        # Get the execution ID from metadata
        execution_id = result.get('metadata', {}).get('execution_id')
        
        return JsonResponse({
            'success': True,
            'execution_id': execution_id,
            'result': result
        })
        
    except Exception as e:
        error_msg = str(e)
        traceback.print_exc()
        return JsonResponse({'error': error_msg}, status=500)


def get_execution_status(request, execution_id):
    """
    API view to get the current status of an execution.
    """
    try:
        execution = get_object_or_404(PipelineExecution, id=execution_id)
        steps = execution.steps.all().order_by('started_at')
        
        steps_data = []
        for step in steps:
            try:
                output = json.loads(step.output_data) if step.output_data else {}
            except json.JSONDecodeError:
                output = {"error": "Invalid output data"}
                
            steps_data.append({
                'node_name': step.node.name,
                'node_type': step.node.node_type,
                'is_complete': step.is_complete,
                'started_at': step.started_at.isoformat(),
                'completed_at': step.completed_at.isoformat() if step.completed_at else None,
                'output': output,
            })
        
        return JsonResponse({
            'execution_id': execution.id,
            'pipeline_name': execution.pipeline.name,
            'is_complete': execution.is_complete,
            'started_at': execution.started_at.isoformat(),
            'completed_at': execution.completed_at.isoformat() if execution.completed_at else None,
            'current_node': execution.current_node.name if execution.current_node else None,
            'steps': steps_data,
        })
        
    except Exception as e:
        error_msg = str(e)
        traceback.print_exc()
        return JsonResponse({'error': error_msg}, status=500)
