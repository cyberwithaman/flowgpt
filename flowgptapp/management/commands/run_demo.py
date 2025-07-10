from django.core.management.base import BaseCommand
import json
from pprint import pformat

from flowgptapp.models import Pipeline, Node, Edge


class Command(BaseCommand):
    help = 'Shows FlowGPT pipeline configuration details without execution'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('FlowGPT Pipeline Configuration Demo'))
        self.stdout.write('=' * 50)
        
        # Get all available pipelines
        pipelines = Pipeline.objects.filter(is_active=True).order_by('name')
        
        if not pipelines.exists():
            self.stdout.write(self.style.WARNING(
                "No pipelines found. Please run 'python manage.py load_sample_data' first."
            ))
            return
        
        # Display available pipelines
        self.stdout.write(self.style.SUCCESS('Available Pipelines:'))
        for i, pipeline in enumerate(pipelines):
            self.stdout.write(f"{i+1}. {pipeline.name} - {pipeline.description}")
        
        # Sample text for demonstration
        sample_text = (
            "LangGraph is a powerful framework for building stateful, multi-step applications "
            "using language models. It provides tools for creating reliable flows and handling "
            "complex application states. This is a demo of FlowGPT, which uses LangGraph for "
            "pipeline execution without any actual LLMs."
        )
        
        self.stdout.write("\nSample Text:")
        self.stdout.write(sample_text)
        self.stdout.write('=' * 50)
        
        # Show pipeline configurations
        for pipeline in pipelines:
            self.stdout.write("")
            self.stdout.write(self.style.SUCCESS(f"Pipeline: {pipeline.name}"))
            self.stdout.write('-' * 50)
            
            edges = Edge.objects.filter(pipeline=pipeline).order_by('order')
            
            if not edges.exists():
                self.stdout.write("No edges defined for this pipeline.")
                continue
                
            # Show pipeline structure
            self.stdout.write(self.style.SUCCESS("Pipeline Structure:"))
            
            # Get all unique nodes in this pipeline
            nodes = set()
            for edge in edges:
                nodes.add(edge.source)
                nodes.add(edge.target)
            
            # Find start and end nodes
            all_targets = set(edges.values_list('target_id', flat=True))
            all_sources = set(edges.values_list('source_id', flat=True))
            
            start_nodes = [node for node in nodes if node.id not in all_targets]
            end_nodes = [node for node in nodes if node.id not in all_sources]
            
            if not start_nodes:
                start_nodes = [edges.first().source]
                
            if not end_nodes:
                end_nodes = [edges.last().target]
                
            # Show start nodes
            self.stdout.write("\nStart Node(s):")
            for node in start_nodes:
                self.stdout.write(f"  - {node.name} ({node.get_node_type_display()})")
            
            # Show pipeline flow
            self.stdout.write("\nFlow:")
            for edge in edges:
                self.stdout.write(f"  {edge.source.name} → {edge.target.name}")
                
            # Show end nodes
            self.stdout.write("\nEnd Node(s):")
            for node in end_nodes:
                self.stdout.write(f"  - {node.name} ({node.get_node_type_display()})")
                
            # Show node details
            self.stdout.write("\nNode Details:")
            for node in sorted(nodes, key=lambda n: n.name):
                self.stdout.write(f"\n  {node.name} ({node.get_node_type_display()}):")
                if node.description:
                    self.stdout.write(f"    Description: {node.description}")
                    
                if node.config:
                    self.stdout.write("    Configuration:")
                    try:
                        for key, value in node.config.items():
                            self.stdout.write(f"      - {key}: {value}")
                    except (AttributeError, TypeError):
                        self.stdout.write(f"      {node.config}")
            
            self.stdout.write('=' * 50)
            
        self.stdout.write(self.style.SUCCESS("\nDemo completed.")) 