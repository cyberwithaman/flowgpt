from django.db import models
from django.core.validators import MinValueValidator

class Node(models.Model):
    """
    Represents a node in a LangGraph pipeline.
    Each node represents a specific operation/function in the workflow.
    """
    TYPE_CHOICES = [
        ('clean_text', 'Clean Text'),
        ('uppercase', 'Convert to Uppercase'),
        ('summary', 'Basic Summary'),
        ('translate', 'Translate'),
        ('email', 'Send Email'),
    ]

    name = models.CharField(max_length=100)
    node_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    description = models.TextField(blank=True, null=True)
    config = models.JSONField(default=dict, blank=True, null=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_node_type_display()})"

class Pipeline(models.Model):
    """
    Represents a complete workflow pipeline consisting of nodes connected by edges.
    """
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Edge(models.Model):
    """
    Represents a directed connection between two nodes in a pipeline.
    """
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE, related_name='edges')
    source = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='outgoing_edges')
    target = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='incoming_edges')
    order = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    condition = models.CharField(max_length=255, blank=True, null=True,
                               help_text="Optional condition to determine if this edge should be followed")

    class Meta:
        unique_together = [['pipeline', 'source', 'target']]
        ordering = ['pipeline', 'order']

    def __str__(self):
        return f"{self.pipeline.name}: {self.source.name} → {self.target.name}"

class PipelineExecution(models.Model):
    """
    Represents a specific execution of a pipeline with input and results.
    """
    pipeline = models.ForeignKey(Pipeline, on_delete=models.CASCADE, related_name='executions')
    input_data = models.TextField()
    output_data = models.TextField(blank=True, null=True)
    is_complete = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    current_node = models.ForeignKey(Node, on_delete=models.SET_NULL, null=True, blank=True, related_name='executions')
    
    def __str__(self):
        return f"Execution of {self.pipeline.name} ({self.started_at.strftime('%Y-%m-%d %H:%M')})"

class ExecutionStep(models.Model):
    """
    Represents a single step in a pipeline execution.
    """
    execution = models.ForeignKey(PipelineExecution, on_delete=models.CASCADE, related_name='steps')
    node = models.ForeignKey(Node, on_delete=models.CASCADE)
    input_data = models.TextField()
    output_data = models.TextField(blank=True, null=True)
    is_complete = models.BooleanField(default=False)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['started_at']
    
    def __str__(self):
        return f"Step {self.node.name} of {self.execution}"

class Contact(models.Model):
    """
    Stores contact form submissions from users.
    """
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Message from {self.name} ({self.created_at.strftime('%Y-%m-%d')})"
