"""
LangGraph-based pipeline executor for FlowGPT.
This module creates and executes LangGraph workflows based on the pipeline configurations.
"""
from typing import Dict, Any, List, Callable, Optional, Union, TypedDict
import datetime
import json
from langgraph.graph import StateGraph, END
from .node_functions import NODE_FUNCTIONS
from ..models import Pipeline, Node, Edge, PipelineExecution, ExecutionStep


# Define state schema type for LangGraph
class FlowGPTState(TypedDict, total=False):
    text: str
    config: Dict[str, Any]
    summary: Optional[str]
    translated_text: Optional[str]
    email_result: Optional[Dict[str, Any]]
    metadata: Dict[str, Any]
    error: Optional[str]


def get_node_config(node_id: int) -> Dict[str, Any]:
    """
    Get node configuration from database.
    """
    try:
        node = Node.objects.get(id=node_id)
        return node.config or {}
    except Node.DoesNotExist:
        return {}


def create_pipeline_graph(pipeline_id: int) -> StateGraph:
    """
    Create a LangGraph StateGraph based on a pipeline configuration.
    """
    try:
        pipeline = Pipeline.objects.get(id=pipeline_id)
    except Pipeline.DoesNotExist:
        raise ValueError(f"Pipeline with id {pipeline_id} does not exist")
    
    # Get all nodes and edges for this pipeline
    edges = Edge.objects.filter(pipeline=pipeline).order_by('order')
    
    if not edges.exists():
        raise ValueError(f"Pipeline {pipeline.name} has no edges defined")
    
    # Create a new state graph with the defined schema
    graph = StateGraph(state_schema=FlowGPTState)
    
    # Track all nodes we've seen to add them to the graph
    nodes_in_graph = set()
    
    # Add all nodes and edges to the graph
    for edge in edges:
        source_node = edge.source
        target_node = edge.target
        
        # Add source node if not already in graph
        if source_node.id not in nodes_in_graph:
            node_function = NODE_FUNCTIONS.get(source_node.node_type)
            if not node_function:
                raise ValueError(f"Unknown node type: {source_node.node_type}")
            
            graph.add_node(str(source_node.id), node_function)
            nodes_in_graph.add(source_node.id)
            
        # Add target node if not already in graph
        if target_node.id not in nodes_in_graph:
            node_function = NODE_FUNCTIONS.get(target_node.node_type)
            if not node_function:
                raise ValueError(f"Unknown node type: {target_node.node_type}")
                
            graph.add_node(str(target_node.id), node_function)
            nodes_in_graph.add(target_node.id)
        
        # Add edge
        # We use the node IDs as string keys in the graph
        graph.add_edge(str(source_node.id), str(target_node.id))
    
    # Find the first node (no incoming edges or lowest order)
    first_node = None
    all_targets = set(edges.values_list('target_id', flat=True))
    
    for edge in edges:
        if edge.source.id not in all_targets:
            first_node = edge.source
            break
    
    if not first_node:
        # If no clear first node, use the source of the first edge
        first_node = edges.first().source
    
    # Find the last node (no outgoing edges)
    last_node = None
    all_sources = set(edges.values_list('source_id', flat=True))
    
    for edge in edges:
        if edge.target.id not in all_sources:
            last_node = edge.target
            break
            
    if not last_node:
        # If no clear last node, use the target of the last edge
        last_node = edges.last().target
    
    # Set the entry point
    graph.set_entry_point(str(first_node.id))
    
    # Connect the last node to END
    graph.add_edge(str(last_node.id), END)
    
    return graph


def update_execution_state(execution_id: int, state: Dict[str, Any], node_id: Optional[str] = None,
                          is_complete: bool = False) -> None:
    """
    Update the execution state in the database.
    """
    try:
        execution = PipelineExecution.objects.get(id=execution_id)
        
        # Update current node if provided
        if node_id and node_id != 'END':
            try:
                node = Node.objects.get(id=int(node_id))
                execution.current_node = node
            except (Node.DoesNotExist, ValueError):
                # If node doesn't exist or isn't a valid ID, ignore
                pass
        
        # Update completion status
        if is_complete:
            execution.is_complete = True
            execution.completed_at = datetime.datetime.now()
            execution.output_data = json.dumps(state)
            
        execution.save()
        
    except PipelineExecution.DoesNotExist:
        # Log error but don't crash
        print(f"Error: PipelineExecution with id {execution_id} not found")


def update_execution_step(execution_id: int, node_id: str, 
                        input_data: Dict[str, Any], 
                        output_data: Dict[str, Any]) -> None:
    """
    Create or update an execution step in the database.
    """
    try:
        execution = PipelineExecution.objects.get(id=execution_id)
        
        # Skip if this is the END node
        if node_id == 'END':
            return
            
        try:
            node = Node.objects.get(id=int(node_id))
            
            # Create execution step
            ExecutionStep.objects.create(
                execution=execution,
                node=node,
                input_data=json.dumps(input_data),
                output_data=json.dumps(output_data),
                is_complete=True,
                completed_at=datetime.datetime.now()
            )
            
        except Node.DoesNotExist:
            # Log error but don't crash
            print(f"Error: Node with id {node_id} not found")
            
    except PipelineExecution.DoesNotExist:
        # Log error but don't crash
        print(f"Error: PipelineExecution with id {execution_id} not found")


def execute_pipeline(pipeline_id: int, input_text: str) -> Dict[str, Any]:
    """
    Execute a pipeline with the given input text.
    """
    # Create pipeline graph
    graph = create_pipeline_graph(pipeline_id)
    
    # Create pipeline execution record
    pipeline = Pipeline.objects.get(id=pipeline_id)
    execution = PipelineExecution.objects.create(
        pipeline=pipeline,
        input_data=input_text,
        is_complete=False
    )
    execution_id = execution.id
    
    # Prepare initial state with config
    state = {
        "text": input_text,
        "config": {},
        "metadata": {
            "pipeline_id": pipeline_id,
            "execution_id": execution_id,
            "started_at": str(datetime.datetime.now())
        }
    }
    
    # Create a custom event handler to track node execution
    class NodeExecutionHandler:
        """Event handler to track execution progress"""
        
        def on_chain_start(self, node_name: str, inputs: Dict[str, Any]) -> None:
            """Called at node start"""
            try:
                # Don't update DB for END node
                if node_name != 'END':
                    # Add node configuration to state
                    inputs["config"] = get_node_config(int(node_name))
                    
                    # Update execution record with current node
                    update_execution_state(execution_id, inputs, node_name)
            except Exception as e:
                print(f"Error in on_chain_start: {str(e)}")
        
        def on_chain_end(self, node_name: str, inputs: Dict[str, Any], outputs: Dict[str, Any]) -> None:
            """Called at node completion"""
            try:
                # Record step completion
                update_execution_step(execution_id, node_name, inputs, outputs)
            except Exception as e:
                print(f"Error in on_chain_end: {str(e)}")
                
        def on_chain_error(self, node_name: str, inputs: Dict[str, Any], error: Exception) -> None:
            """Called on node error"""
            try:
                print(f"Error executing node {node_name}: {str(error)}")
            except Exception as e:
                print(f"Error in on_chain_error: {str(e)}")
    
    # Create event handler instance
    handler = NodeExecutionHandler()
    
    # Compile the graph with event tracking
    compiled_graph = graph.compile()
    
    # Run the graph with our initial state
    try:
        # Configure the execution - note the API has likely changed
        # Using just the callbacks parameter and removing recursion_limit
        config = {
            "callbacks": [handler]
        }
        
        # Run the graph with the updated API
        result = compiled_graph.invoke(state, **config)
        
        # Mark execution as complete
        update_execution_state(execution_id, result, is_complete=True)
        
        return result
    except Exception as e:
        # Record error in execution
        state["error"] = str(e)
        update_execution_state(execution_id, state, is_complete=True)
        
        print(f"Error executing pipeline: {str(e)}")
        raise 