"""
Demo script for testing FlowGPT pipelines directly.

This script demonstrates how to execute pipelines using the LangGraph integration
without going through the web interface.

Run this script with:
python manage.py shell < flowgptapp/demo_script.py
"""

import os
import sys
import django
import json
from pprint import pprint

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flowgpt.settings')
django.setup()

# Import models and pipeline executor
from flowgptapp.models import Pipeline
from flowgptapp.graph.pipeline_executor import execute_pipeline


def demo_pipeline_execution():
    """Demonstrate pipeline execution with the LangGraph integration."""
    print("FlowGPT Pipeline Execution Demo")
    print("-" * 50)
    
    # Get all available pipelines
    pipelines = Pipeline.objects.filter(is_active=True).order_by('name')
    
    if not pipelines.exists():
        print("No pipelines found. Please run 'python manage.py load_sample_data' first.")
        return
    
    # Display available pipelines
    print("Available Pipelines:")
    for i, pipeline in enumerate(pipelines):
        print(f"{i+1}. {pipeline.name} - {pipeline.description}")
    
    # Sample text for demonstration
    sample_text = (
        "LangGraph is a powerful framework for building stateful, multi-step applications "
        "using language models. It provides tools for creating reliable flows and handling "
        "complex application states. This is a demo of FlowGPT, which uses LangGraph for "
        "pipeline execution without any actual LLMs."
    )
    
    print("\nSample Text:")
    print(sample_text)
    print("-" * 50)
    
    # Execute each pipeline and show results
    for pipeline in pipelines:
        print(f"\nExecuting: {pipeline.name}")
        print("-" * 30)
        
        try:
            # Execute the pipeline with the sample text
            result = execute_pipeline(pipeline.id, sample_text)
            
            # Display the result in a readable format
            print("Result:")
            if "text" in result:
                print("\nProcessed Text:")
                print(result["text"])
                
            if "summary" in result:
                print("\nSummary:")
                print(result["summary"])
                
            if "translated_text" in result:
                print("\nTranslated Text:")
                print(result["translated_text"])
                
            if "email_result" in result:
                print("\nEmail Result:")
                print(f"Recipient: {result['email_result']['recipient']}")
                print(f"Subject: {result['email_result']['subject']}")
                print(f"Status: {'Sent' if result['email_result']['success'] else 'Failed'}")
                
            # Show the entire state for debugging
            print("\nFull State:")
            pprint(result)
            
        except Exception as e:
            print(f"Error executing pipeline: {str(e)}")
        
        print("-" * 50)
        
    print("\nDemo completed.")


if __name__ == "__main__":
    demo_pipeline_execution() 