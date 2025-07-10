"""
Sample data generation script for FlowGPT.

This script creates sample nodes, pipelines, edges, and example executions.
Run this script using: python manage.py shell < flowgptapp/sample_data.py
"""

import os
import sys
import django
import datetime
import json
import random

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'flowgpt.settings')
django.setup()

# Now you can import Django models
from flowgptapp.models import Node, Pipeline, Edge, PipelineExecution, ExecutionStep, Contact
from django.contrib.auth.models import User
from django.utils import timezone


def create_sample_data():
    """Create sample data for the FlowGPT application."""
    print("Creating sample data for FlowGPT...")
    
    # Check if data already exists
    if Node.objects.count() > 0:
        print("Sample data already exists. Skipping creation.")
        return
        
    # Create sample nodes
    print("Creating sample nodes...")
    clean_node = Node.objects.create(
        name="Text Cleaner",
        node_type="clean_text",
        description="Removes extra whitespace, special characters, and URLs.",
        config={
            "remove_special_chars": True,
            "remove_urls": True
        }
    )
    
    uppercase_node = Node.objects.create(
        name="Uppercase Converter",
        node_type="uppercase",
        description="Converts all text to uppercase.",
        config={}
    )
    
    summary_node = Node.objects.create(
        name="Basic Summarizer",
        node_type="summary",
        description="Creates a summary by taking the first few sentences.",
        config={
            "num_sentences": 2,
            "max_chars": 150
        }
    )
    
    translate_node = Node.objects.create(
        name="Spanish Translator",
        node_type="translate",
        description="Translates text from English to Spanish.",
        config={
            "target_language": "spanish"
        }
    )
    
    french_translate_node = Node.objects.create(
        name="French Translator",
        node_type="translate",
        description="Translates text from English to French.",
        config={
            "target_language": "french"
        }
    )
    
    email_node = Node.objects.create(
        name="Email Sender",
        node_type="email",
        description="Sends the processed text via email.",
        config={
            "recipient": "user@example.com",
            "subject": "Processed Text from FlowGPT"
        }
    )
    
    # Create sample pipelines
    print("Creating sample pipelines...")
    text_cleanup_pipeline = Pipeline.objects.create(
        name="Text Cleanup Pipeline",
        description="Cleans and converts text to uppercase.",
        is_active=True
    )
    
    summary_pipeline = Pipeline.objects.create(
        name="Text Summary Pipeline",
        description="Cleans text and generates a summary.",
        is_active=True
    )
    
    translation_pipeline = Pipeline.objects.create(
        name="Spanish Translation Pipeline",
        description="Cleans text, generates a summary, and translates to Spanish.",
        is_active=True
    )
    
    full_pipeline = Pipeline.objects.create(
        name="Full Text Processing Pipeline",
        description="Complete pipeline that cleans, summarizes, translates, and emails the text.",
        is_active=True
    )
    
    # Create edges for pipelines
    print("Creating pipeline edges...")
    # Text cleanup pipeline edges
    Edge.objects.create(
        pipeline=text_cleanup_pipeline,
        source=clean_node,
        target=uppercase_node,
        order=0
    )
    
    # Summary pipeline edges
    Edge.objects.create(
        pipeline=summary_pipeline,
        source=clean_node,
        target=summary_node,
        order=0
    )
    
    # Translation pipeline edges
    Edge.objects.create(
        pipeline=translation_pipeline,
        source=clean_node,
        target=summary_node,
        order=0
    )
    Edge.objects.create(
        pipeline=translation_pipeline,
        source=summary_node,
        target=translate_node,
        order=1
    )
    
    # Full pipeline edges
    Edge.objects.create(
        pipeline=full_pipeline,
        source=clean_node,
        target=summary_node,
        order=0
    )
    Edge.objects.create(
        pipeline=full_pipeline,
        source=summary_node,
        target=translate_node,
        order=1
    )
    Edge.objects.create(
        pipeline=full_pipeline,
        source=translate_node,
        target=email_node,
        order=2
    )
    
    # Create sample executions
    print("Creating sample executions...")
    sample_texts = [
        "Hello world! This is a sample text for testing. It contains multiple sentences. We'll use this to demonstrate the pipeline functionality.",
        "Welcome to FlowGPT. This is an automation tool for creating task pipelines. It uses LangGraph for node-based flows. Let's see how it works!",
        "Machine learning is a method of data analysis that automates analytical model building. It is a branch of artificial intelligence based on the idea that systems can learn from data, identify patterns and make decisions with minimal human intervention.",
    ]
    
    # Create sample executions for each pipeline
    for pipeline in Pipeline.objects.all():
        for text in sample_texts:
            # Create execution
            execution = PipelineExecution.objects.create(
                pipeline=pipeline,
                input_data=text,
                is_complete=True,
                started_at=timezone.now() - datetime.timedelta(days=random.randint(0, 5), hours=random.randint(0, 12)),
                completed_at=timezone.now() - datetime.timedelta(hours=random.randint(0, 3)),
                output_data=json.dumps({
                    "text": text.upper() if pipeline.name == "Text Cleanup Pipeline" else text,
                    "summary": text.split('.')[0] + '.' if '.' in text else text,
                    "translated_text": f"[TRANSLATED: {text.split('.')[0]}...]" if "Translation" in pipeline.name else None,
                    "metadata": {
                        "pipeline_id": pipeline.id,
                        "execution_id": random.randint(1000, 9999),
                        "started_at": str(timezone.now() - datetime.timedelta(days=1))
                    }
                })
            )
            
            # Create execution steps
            edges = Edge.objects.filter(pipeline=pipeline).order_by('order')
            for i, edge in enumerate(edges):
                # First step uses source node
                if i == 0:
                    ExecutionStep.objects.create(
                        execution=execution,
                        node=edge.source,
                        input_data=json.dumps({"text": text}),
                        output_data=json.dumps({"text": text, "metadata": {"clean_text_applied": True}}),
                        is_complete=True,
                        started_at=execution.started_at,
                        completed_at=execution.started_at + datetime.timedelta(seconds=2)
                    )
                
                # Create step for target node
                input_data = {"text": text}
                output_data = {"text": text}
                
                if edge.target.node_type == "uppercase":
                    output_data["text"] = text.upper()
                elif edge.target.node_type == "summary":
                    output_data["summary"] = text.split('.')[0] + '.' if '.' in text else text
                elif edge.target.node_type == "translate":
                    output_data["translated_text"] = f"[TRANSLATED: {text.split('.')[0]}...]"
                elif edge.target.node_type == "email":
                    output_data["email_result"] = {
                        "success": True,
                        "recipient": "user@example.com",
                        "subject": "Processed Text from FlowGPT",
                        "sent_at": str(execution.completed_at - datetime.timedelta(seconds=1))
                    }
                
                ExecutionStep.objects.create(
                    execution=execution,
                    node=edge.target,
                    input_data=json.dumps(input_data),
                    output_data=json.dumps(output_data),
                    is_complete=True,
                    started_at=execution.started_at + datetime.timedelta(seconds=2 + i*3),
                    completed_at=execution.started_at + datetime.timedelta(seconds=4 + i*3)
                )
    
    # Create sample contact messages
    print("Creating sample contact messages...")
    sample_contacts = [
        {
            "name": "John Smith",
            "email": "john.smith@example.com",
            "phone": "(555) 123-4567",
            "message": "I'm interested in learning more about FlowGPT. Can you provide more information about pricing and features?",
            "days_ago": 7,
            "is_read": True
        },
        {
            "name": "Emma Johnson",
            "email": "emma.j@example.com",
            "phone": "(555) 987-6543",
            "message": "Hello, I'm experiencing an issue with the text cleanup pipeline. It's not removing URLs as expected. Can you help?",
            "days_ago": 3,
            "is_read": True
        },
        {
            "name": "Michael Brown",
            "email": "m.brown@example.com",
            "phone": "",
            "message": "I'd like to request a new feature: the ability to save and reuse configurations for nodes. This would make creating new pipelines much faster.",
            "days_ago": 1,
            "is_read": False
        },
    ]
    
    for contact_data in sample_contacts:
        Contact.objects.create(
            name=contact_data["name"],
            email=contact_data["email"],
            phone=contact_data["phone"],
            message=contact_data["message"],
            created_at=timezone.now() - datetime.timedelta(days=contact_data["days_ago"]),
            is_read=contact_data["is_read"]
        )
    
    print("Sample data creation completed successfully!")


if __name__ == "__main__":
    create_sample_data() 