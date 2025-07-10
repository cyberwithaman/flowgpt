"""
Admin charts and analytics visualizations for the FlowGPT admin panel.
"""
import matplotlib
# Use non-interactive Agg backend to prevent warnings in web server
matplotlib.use('Agg')

import datetime
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from django.db.models.functions import TruncDay, TruncMonth, TruncWeek
from django.db.models import Count, Avg, Sum
from django.utils import timezone

from .models import Contact, Edge, ExecutionStep, Node, PipelineExecution, Pipeline


def get_contact_data():
    """Get data for Contact analytics."""
    # Contacts over time
    contacts_by_day = Contact.objects.annotate(
        day=TruncDay('created_at')
    ).values('day').annotate(count=Count('id')).order_by('day')
    
    # Read vs unread contacts
    read_status = Contact.objects.values('is_read').annotate(count=Count('id'))
    
    return {
        'contacts_by_day': list(contacts_by_day),
        'read_status': list(read_status)
    }


def get_node_data():
    """Get data for Node analytics."""
    # Nodes by type
    nodes_by_type = Node.objects.values('node_type').annotate(count=Count('id'))
    
    # Nodes used in pipelines
    nodes_usage = (Node.objects.annotate(
        pipeline_count=Count('outgoing_edges', distinct=True) + Count('incoming_edges', distinct=True)
    ).values('name', 'node_type', 'pipeline_count').order_by('-pipeline_count'))
    
    return {
        'nodes_by_type': list(nodes_by_type),
        'nodes_usage': list(nodes_usage)
    }


def get_pipeline_data():
    """Get data for Pipeline analytics."""
    # Pipelines by activity status
    pipelines_by_status = Pipeline.objects.values('is_active').annotate(count=Count('id'))
    
    # Pipelines by execution count
    pipeline_executions = (Pipeline.objects.annotate(
        execution_count=Count('executions')
    ).values('name', 'execution_count').order_by('-execution_count'))
    
    # Average pipeline length (number of edges)
    pipeline_lengths = (Pipeline.objects.annotate(
        edge_count=Count('edges')
    ).values('name', 'edge_count').order_by('-edge_count'))
    
    return {
        'pipelines_by_status': list(pipelines_by_status),
        'pipeline_executions': list(pipeline_executions),
        'pipeline_lengths': list(pipeline_lengths)
    }


def get_edge_data():
    """Get data for Edge analytics."""
    # Edges by pipeline
    edges_by_pipeline = (Pipeline.objects.annotate(
        edge_count=Count('edges')
    ).values('name', 'edge_count').order_by('-edge_count'))
    
    # Edge distribution by order
    edge_order_distribution = Edge.objects.values('order').annotate(count=Count('id')).order_by('order')
    
    return {
        'edges_by_pipeline': list(edges_by_pipeline),
        'edge_order_distribution': list(edge_order_distribution)
    }


def get_execution_data():
    """Get data for PipelineExecution analytics."""
    # Executions over time
    executions_by_day = PipelineExecution.objects.annotate(
        day=TruncDay('started_at')
    ).values('day').annotate(count=Count('id')).order_by('day')
    
    # Execution completion status
    execution_status = PipelineExecution.objects.values('is_complete').annotate(count=Count('id'))
    
    # Average execution duration
    execution_duration = (PipelineExecution.objects.filter(
        is_complete=True, completed_at__isnull=False
    ).annotate(
        duration=Sum(TruncDay('completed_at') - TruncDay('started_at'))
    ).values('pipeline__name', 'duration').order_by('pipeline__name'))
    
    return {
        'executions_by_day': list(executions_by_day),
        'execution_status': list(execution_status),
        'execution_duration': list(execution_duration)
    }


def get_execution_step_data():
    """Get data for ExecutionStep analytics."""
    # Execution steps by node type
    steps_by_node_type = ExecutionStep.objects.values(
        'node__node_type'
    ).annotate(count=Count('id')).order_by('-count')
    
    # Execution step completion status
    step_status = ExecutionStep.objects.values('is_complete').annotate(count=Count('id'))
    
    return {
        'steps_by_node_type': list(steps_by_node_type),
        'step_status': list(step_status)
    }


def generate_contact_charts():
    """Generate charts for Contact model."""
    charts = []
    
    # Get data
    data = get_contact_data()
    
    # Contacts over time chart
    if data['contacts_by_day']:
        df = pd.DataFrame(data['contacts_by_day'])
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(df['day'], df['count'], color='skyblue')
        ax.set_title('Contact Submissions Over Time')
        ax.set_xlabel('Date')
        ax.set_ylabel('Number of Contacts')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Save to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        
        chart = {
            'title': 'Contact Submissions Over Time',
            'image': base64.b64encode(image_png).decode('utf-8')
        }
        charts.append(chart)
        plt.close()
    
    # Read vs unread pie chart
    if data['read_status']:
        df = pd.DataFrame(data['read_status'])
        fig, ax = plt.subplots(figsize=(8, 8))
        labels = ['Read' if status else 'Unread' for status in df['is_read']]
        ax.pie(df['count'], labels=labels, autopct='%1.1f%%', startangle=90, colors=['lightgreen', 'salmon'])
        ax.set_title('Contact Read Status')
        plt.tight_layout()
        
        # Save to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        
        chart = {
            'title': 'Contact Read Status',
            'image': base64.b64encode(image_png).decode('utf-8')
        }
        charts.append(chart)
        plt.close()
    
    return charts


def generate_node_charts():
    """Generate charts for Node model."""
    charts = []
    
    # Get data
    data = get_node_data()
    
    # Nodes by type pie chart
    if data['nodes_by_type']:
        df = pd.DataFrame(data['nodes_by_type'])
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(df['node_type'], df['count'], color='lightblue')
        ax.set_title('Node Types Distribution')
        ax.set_xlabel('Node Type')
        ax.set_ylabel('Number of Nodes')
        plt.tight_layout()
        
        # Save to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        
        chart = {
            'title': 'Node Types Distribution',
            'image': base64.b64encode(image_png).decode('utf-8')
        }
        charts.append(chart)
        plt.close()
    
    # Nodes usage chart
    if data['nodes_usage'] and len(data['nodes_usage']) > 0:
        # Limit to top 10 nodes for readability
        df = pd.DataFrame(data['nodes_usage'][:10])
        fig, ax = plt.subplots(figsize=(12, 6))
        bars = ax.bar(df['name'], df['pipeline_count'], color='lightgreen')
        ax.set_title('Most Used Nodes in Pipelines')
        ax.set_xlabel('Node Name')
        ax.set_ylabel('Number of Pipelines')
        plt.xticks(rotation=45, ha='right')
        
        # Add node type as text on top of bars
        for bar, node_type in zip(bars, df['node_type']):
            ax.text(
                bar.get_x() + bar.get_width()/2,
                bar.get_height() + 0.1,
                node_type,
                ha='center',
                rotation=45,
                fontsize=8
            )
            
        plt.tight_layout()
        
        # Save to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        
        chart = {
            'title': 'Most Used Nodes in Pipelines',
            'image': base64.b64encode(image_png).decode('utf-8')
        }
        charts.append(chart)
        plt.close()
    
    return charts


def generate_pipeline_charts():
    """Generate charts for Pipeline model."""
    charts = []
    
    # Get data
    data = get_pipeline_data()
    
    # Pipelines by status
    if data['pipelines_by_status']:
        df = pd.DataFrame(data['pipelines_by_status'])
        fig, ax = plt.subplots(figsize=(8, 8))
        labels = ['Active' if status else 'Inactive' for status in df['is_active']]
        ax.pie(df['count'], labels=labels, autopct='%1.1f%%', startangle=90, colors=['lightgreen', 'lightcoral'])
        ax.set_title('Pipeline Status')
        plt.tight_layout()
        
        # Save to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        
        chart = {
            'title': 'Pipeline Status',
            'image': base64.b64encode(image_png).decode('utf-8')
        }
        charts.append(chart)
        plt.close()
    
    # Pipeline execution count
    if data['pipeline_executions'] and len(data['pipeline_executions']) > 0:
        df = pd.DataFrame(data['pipeline_executions'])
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.bar(df['name'], df['execution_count'], color='skyblue')
        ax.set_title('Pipeline Execution Count')
        ax.set_xlabel('Pipeline')
        ax.set_ylabel('Number of Executions')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Save to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        
        chart = {
            'title': 'Pipeline Execution Count',
            'image': base64.b64encode(image_png).decode('utf-8')
        }
        charts.append(chart)
        plt.close()
    
    # Pipeline length (edge count)
    if data['pipeline_lengths'] and len(data['pipeline_lengths']) > 0:
        df = pd.DataFrame(data['pipeline_lengths'])
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.bar(df['name'], df['edge_count'], color='lightgreen')
        ax.set_title('Pipeline Length (Number of Edges)')
        ax.set_xlabel('Pipeline')
        ax.set_ylabel('Number of Edges')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Save to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        
        chart = {
            'title': 'Pipeline Length (Number of Edges)',
            'image': base64.b64encode(image_png).decode('utf-8')
        }
        charts.append(chart)
        plt.close()
    
    return charts


def generate_edge_charts():
    """Generate charts for Edge model."""
    charts = []
    
    # Get data
    data = get_edge_data()
    
    # Edges by pipeline
    if data['edges_by_pipeline'] and len(data['edges_by_pipeline']) > 0:
        df = pd.DataFrame(data['edges_by_pipeline'])
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.bar(df['name'], df['edge_count'], color='coral')
        ax.set_title('Number of Edges by Pipeline')
        ax.set_xlabel('Pipeline')
        ax.set_ylabel('Number of Edges')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        
        # Save to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        
        chart = {
            'title': 'Number of Edges by Pipeline',
            'image': base64.b64encode(image_png).decode('utf-8')
        }
        charts.append(chart)
        plt.close()
    
    # Edge order distribution
    if data['edge_order_distribution'] and len(data['edge_order_distribution']) > 0:
        df = pd.DataFrame(data['edge_order_distribution'])
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.bar(df['order'], df['count'], color='lightblue')
        ax.set_title('Edge Order Distribution')
        ax.set_xlabel('Edge Order')
        ax.set_ylabel('Number of Edges')
        plt.tight_layout()
        
        # Save to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        
        chart = {
            'title': 'Edge Order Distribution',
            'image': base64.b64encode(image_png).decode('utf-8')
        }
        charts.append(chart)
        plt.close()
    
    return charts


def generate_execution_charts():
    """Generate charts for PipelineExecution model."""
    charts = []
    
    # Get data
    data = get_execution_data()
    
    # Executions by day
    if data['executions_by_day'] and len(data['executions_by_day']) > 0:
        df = pd.DataFrame(data['executions_by_day'])
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.bar(df['day'], df['count'], color='skyblue')
        ax.set_title('Pipeline Executions Over Time')
        ax.set_xlabel('Date')
        ax.set_ylabel('Number of Executions')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        # Save to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        
        chart = {
            'title': 'Pipeline Executions Over Time',
            'image': base64.b64encode(image_png).decode('utf-8')
        }
        charts.append(chart)
        plt.close()
    
    # Execution status
    if data['execution_status'] and len(data['execution_status']) > 0:
        df = pd.DataFrame(data['execution_status'])
        fig, ax = plt.subplots(figsize=(8, 8))
        labels = ['Complete' if status else 'Incomplete' for status in df['is_complete']]
        ax.pie(df['count'], labels=labels, autopct='%1.1f%%', startangle=90, colors=['lightgreen', 'lightcoral'])
        ax.set_title('Pipeline Execution Status')
        plt.tight_layout()
        
        # Save to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        
        chart = {
            'title': 'Pipeline Execution Status',
            'image': base64.b64encode(image_png).decode('utf-8')
        }
        charts.append(chart)
        plt.close()
    
    return charts


def generate_execution_step_charts():
    """Generate charts for ExecutionStep model."""
    charts = []
    
    # Get data
    data = get_execution_step_data()
    
    # Steps by node type
    if data['steps_by_node_type'] and len(data['steps_by_node_type']) > 0:
        df = pd.DataFrame(data['steps_by_node_type'])
        if 'node__node_type' in df.columns:  # Verify column exists
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.bar(df['node__node_type'], df['count'], color='lightblue')
            ax.set_title('Execution Steps by Node Type')
            ax.set_xlabel('Node Type')
            ax.set_ylabel('Number of Execution Steps')
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            # Save to base64
            buffer = BytesIO()
            plt.savefig(buffer, format='png')
            buffer.seek(0)
            image_png = buffer.getvalue()
            buffer.close()
            
            chart = {
                'title': 'Execution Steps by Node Type',
                'image': base64.b64encode(image_png).decode('utf-8')
            }
            charts.append(chart)
            plt.close()
    
    # Step completion status
    if data['step_status'] and len(data['step_status']) > 0:
        df = pd.DataFrame(data['step_status'])
        fig, ax = plt.subplots(figsize=(8, 8))
        labels = ['Complete' if status else 'Incomplete' for status in df['is_complete']]
        ax.pie(df['count'], labels=labels, autopct='%1.1f%%', startangle=90, colors=['lightgreen', 'lightcoral'])
        ax.set_title('Execution Step Completion Status')
        plt.tight_layout()
        
        # Save to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()
        
        chart = {
            'title': 'Execution Step Completion Status',
            'image': base64.b64encode(image_png).decode('utf-8')
        }
        charts.append(chart)
        plt.close()
    
    return charts 