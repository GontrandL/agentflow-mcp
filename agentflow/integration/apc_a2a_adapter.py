"""
APC A2A Adapter - Connects APC to A2A Protocol

This adapter enables APC to communicate via A2A protocol, allowing
worker agents to query APC directly without MCP overhead.

Architecture:
- APC registers in A2A system with PROJECT_QUERY capability
- Workers send A2A messages to "apc" agent
- APC processes queries and responds via A2A
- No MCP invocation needed for inter-agent communication

Benefits:
- Faster (no MCP protocol overhead)
- Direct agent-to-agent communication
- Contextual queries (worker can send current task)
- Bidirectional (APC can ask clarifications)
"""

import asyncio
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
import structlog

from agentflow.integration.a2a_protocol import (
    A2AMessage,
    A2AMessageQueue,
    MessageType,
    AgentCapability,
    get_message_queue
)

logger = structlog.get_logger(__name__)


class APCA2AAdapter:
    """
    Adapter to connect APC to A2A protocol.

    This allows APC to:
    1. Register as an agent in A2A system
    2. Receive queries from workers
    3. Process queries using existing APC capabilities
    4. Respond via A2A
    """

    def __init__(self, apc_mcp_server):
        """
        Initialize APC A2A Adapter.

        Args:
            apc_mcp_server: APCMCPServer instance to wrap
        """
        self.apc_server = apc_mcp_server
        self.message_queue = get_message_queue()
        self.agent_id = "apc"
        self.is_running = False

        logger.info("apc_a2a_adapter_initialized")

    def register(self) -> None:
        """Register APC in A2A system."""
        self.message_queue.register_agent(
            agent_id=self.agent_id,
            agent_type="apc",
            capabilities=[
                AgentCapability.PROJECT_QUERY,
                AgentCapability.CONTEXT_COMPRESSION,
                AgentCapability.VALIDATION
            ],
            message_handler=self.handle_message
        )

        logger.info(
            "apc_registered_in_a2a",
            agent_id=self.agent_id,
            capabilities=["project_query", "context_compression", "validation"]
        )

    async def handle_message(self, message: A2AMessage) -> None:
        """
        Handle incoming A2A message.

        Args:
            message: Incoming A2AMessage
        """
        logger.info(
            "apc_received_message",
            from_agent=message.from_agent,
            message_type=message.message_type.value,
            payload_keys=list(message.payload.keys())
        )

        try:
            if message.message_type == MessageType.QUERY:
                await self._handle_query(message)
            elif message.message_type == MessageType.COMMAND:
                await self._handle_command(message)
            else:
                logger.warning(
                    "unsupported_message_type",
                    message_type=message.message_type.value
                )

        except Exception as e:
            logger.error(
                "message_handling_error",
                error=str(e),
                from_agent=message.from_agent
            )

            # Send error response
            await self.message_queue.send_response(
                message,
                {"error": str(e), "status": "failed"}
            )

    async def _handle_query(self, message: A2AMessage) -> None:
        """
        Handle query message (worker asking APC something).

        Supported queries:
        - project_query: Query project structure
        - prepare_context: Compress conversation context
        - validate_output: Validate generated code
        """
        payload = message.payload
        query_subtype = payload.get('query_subtype', 'project_query')

        if query_subtype == 'project_query':
            result = await self._handle_project_query(payload, message.context)
        elif query_subtype == 'prepare_context':
            result = await self._handle_prepare_context(payload, message.context)
        elif query_subtype == 'validate_output':
            result = await self._handle_validate_output(payload, message.context)
        else:
            result = {"error": f"Unknown query subtype: {query_subtype}"}

        # Send response
        await self.message_queue.send_response(message, result)

    async def _handle_project_query(
        self,
        payload: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Handle project query (worker asking about project structure).

        Args:
            payload: {query_type, query, file_type?, limit?}
            context: Worker context (current task, namespace, etc.)

        Returns:
            Query results
        """
        query_type = payload.get('query_type', 'ask')
        query = payload.get('query', '')
        file_type = payload.get('file_type', 'all')
        limit = payload.get('limit', 20)

        logger.info(
            "handling_project_query",
            query_type=query_type,
            query=query,
            context=context
        )

        # Use APC's existing query_project implementation
        params = {
            "query_type": query_type,
            "query": query,
            "file_type": file_type,
            "limit": limit
        }

        result = await self.apc_server._query_project(params)

        # Add context-aware recommendations if available
        if context and context.get('task'):
            result['recommendations'] = self._generate_recommendations(
                result,
                context['task']
            )

        return result

    async def _handle_prepare_context(
        self,
        payload: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Handle context preparation (worker asking to compress context).

        Args:
            payload: {conversation_history, current_task, target_tokens?}
            context: Worker context

        Returns:
            Compressed context
        """
        logger.info("handling_prepare_context", context=context)

        result = await self.apc_server._prepare_context(payload)
        return result

    async def _handle_validate_output(
        self,
        payload: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Handle output validation (worker asking to validate generated code).

        Args:
            payload: {task, output, threshold?}
            context: Worker context

        Returns:
            Validation results
        """
        logger.info("handling_validate_output", context=context)

        result = await self.apc_server._validate_output(payload)
        return result

    async def _handle_command(self, message: A2AMessage) -> None:
        """
        Handle command message (worker instructing APC to do something).

        Supported commands:
        - scan_project: Scan and index project
        """
        payload = message.payload
        command = payload.get('command')

        if command == 'scan_project':
            result = await self._handle_scan_project(payload)
        else:
            result = {"error": f"Unknown command: {command}"}

        await self.message_queue.send_response(message, result)

    async def _handle_scan_project(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle scan_project command."""
        logger.info("handling_scan_project", payload=payload)

        result = await self.apc_server._scan_project(payload)
        return result

    def _generate_recommendations(
        self,
        query_result: Dict[str, Any],
        current_task: str
    ) -> List[str]:
        """
        Generate context-aware recommendations based on query and task.

        Args:
            query_result: Query results from APC
            current_task: Worker's current task

        Returns:
            List of recommendation strings
        """
        recommendations = []

        # Extract keywords from task
        task_lower = current_task.lower()

        # Recommend based on results
        results = query_result.get('results', [])
        if not results:
            recommendations.append("Consider checking similar files in project structure")
            return recommendations

        # Pattern-specific recommendations
        if 'validation' in task_lower or 'validator' in task_lower:
            recommendations.append(
                "Follow pattern: class {Name}Validator with _validate_output method"
            )
            recommendations.append(
                "Location: agentflow/orchestration/ (see existing validators)"
            )

        if 'orchestrat' in task_lower:
            recommendations.append(
                "Follow pattern: class {Name}Orchestrator with orchestrate method"
            )
            recommendations.append(
                "Location: agentflow/orchestration/ (see smart_orchestrator.py)"
            )

        if 'test' in task_lower:
            recommendations.append(
                "Create test file: tests/test_{module_name}.py"
            )
            recommendations.append(
                "Use pytest framework (see existing tests for patterns)"
            )

        return recommendations

    async def start_listener(self) -> None:
        """Start listening for A2A messages (background task)."""
        self.is_running = True
        logger.info("apc_a2a_listener_started")

        await self.message_queue.start_agent_listener(self.agent_id)

    def stop_listener(self) -> None:
        """Stop listening for A2A messages."""
        self.is_running = False
        logger.info("apc_a2a_listener_stopped")


# ==============================================================================
# Convenience Functions for Workers
# ==============================================================================

async def ask_apc(
    worker_id: str,
    question: str,
    context: Optional[Dict[str, Any]] = None,
    timeout: float = 30.0
) -> Dict[str, Any]:
    """
    Convenience function for workers to ask APC a question.

    Args:
        worker_id: Worker agent ID
        question: Natural language question
        context: Worker context (current task, namespace, etc.)
        timeout: Response timeout

    Returns:
        APC response with results

    Example:
        # Worker asks APC
        response = await ask_apc(
            worker_id="worker-123",
            question="What validation patterns exist?",
            context={"task": "Creating validator module"}
        )

        for result in response['results']:
            print(result)
    """
    queue = get_message_queue()

    message = A2AMessage(
        from_agent=worker_id,
        to_agent="apc",
        message_type=MessageType.QUERY,
        payload={
            "query_subtype": "project_query",
            "query_type": "ask",
            "query": question
        },
        context=context
    )

    response = await queue.send_message(message, wait_for_response=True, timeout=timeout)

    return response.payload if response else {"error": "No response"}


async def find_files_in_project(
    worker_id: str,
    pattern: str,
    file_type: str = "all",
    limit: int = 20,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Find files matching pattern.

    Args:
        worker_id: Worker agent ID
        pattern: File name pattern
        file_type: Filter by type (code, test, doc, etc.)
        limit: Max results
        context: Worker context

    Returns:
        File matches
    """
    queue = get_message_queue()

    message = A2AMessage(
        from_agent=worker_id,
        to_agent="apc",
        message_type=MessageType.QUERY,
        payload={
            "query_subtype": "project_query",
            "query_type": "find_files",
            "query": pattern,
            "file_type": file_type,
            "limit": limit
        },
        context=context
    )

    response = await queue.send_message(message, wait_for_response=True, timeout=30.0)

    return response.payload if response else {"error": "No response"}
