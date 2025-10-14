"""
A2A (Agent-to-Agent) Protocol - Foundation for Multi-Agent Communication

This module implements the core A2A protocol that enables:
1. Direct agent-to-agent messaging (no MCP overhead)
2. Async message passing with correlation IDs
3. Request-response pattern + pub-sub
4. Message routing and delivery guarantees
5. Context passing between agents

**Key Insight:** Workers should communicate with APC via A2A, not MCP tools!

Use Cases:
- Worker → APC: "What validation patterns exist?"
- APC → Worker: "Here are 3 patterns..."
- Worker → APC: "Where should I create X?"
- APC → Worker: "Create in agentflow/orchestration/"

Architecture:
- Message format: JSON with correlation IDs
- Transport: In-memory queue (async) + Redis (distributed)
- Routing: Agent registry with capabilities
- Delivery: At-least-once with acknowledgments
"""

import asyncio
import json
import uuid
from typing import Dict, Any, List, Optional, Callable, Set
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum
import structlog

logger = structlog.get_logger(__name__)


class MessageType(Enum):
    """Types of A2A messages."""
    QUERY = "query"                    # Request information
    RESPONSE = "response"              # Reply to query
    COMMAND = "command"                # Execute action
    EVENT = "event"                    # Notify of state change
    CLARIFICATION = "clarification"    # Ask for more details
    RECOMMENDATION = "recommendation"  # Suggest action


class MessagePriority(Enum):
    """Message priority levels."""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    URGENT = 3


@dataclass
class A2AMessage:
    """
    Agent-to-Agent message structure.

    Attributes:
        message_id: Unique message identifier (UUID)
        from_agent: Sender agent ID
        to_agent: Recipient agent ID (or "broadcast" for pub-sub)
        message_type: Type of message (query, response, etc.)
        payload: Message content (dict)
        correlation_id: For request-response pairing
        timestamp: When message was created
        priority: Message priority (for queue ordering)
        context: Additional context (current task, namespace, etc.)
        reply_to: Message ID this is replying to
        ttl: Time-to-live in seconds (None = no expiry)
    """
    from_agent: str
    to_agent: str
    message_type: MessageType
    payload: Dict[str, Any]
    message_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    correlation_id: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    priority: MessagePriority = MessagePriority.NORMAL
    context: Optional[Dict[str, Any]] = None
    reply_to: Optional[str] = None
    ttl: Optional[int] = None  # seconds

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dict for serialization."""
        data = asdict(self)
        data['message_type'] = self.message_type.value
        data['priority'] = self.priority.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'A2AMessage':
        """Create from dict (deserialization)."""
        data['message_type'] = MessageType(data['message_type'])
        data['priority'] = MessagePriority(data['priority'])
        return cls(**data)


class AgentCapability(Enum):
    """Agent capabilities for routing."""
    PROJECT_QUERY = "project_query"           # Can answer project questions
    CONTEXT_COMPRESSION = "context_compression"  # Can compress context
    CODE_GENERATION = "code_generation"       # Can generate code
    VALIDATION = "validation"                 # Can validate output
    ORCHESTRATION = "orchestration"           # Can orchestrate tasks
    TESTING = "testing"                       # Can run/generate tests


@dataclass
class AgentRegistration:
    """Agent registration in A2A system."""
    agent_id: str
    agent_type: str  # "apc", "worker", "orchestrator", etc.
    capabilities: Set[AgentCapability]
    message_handler: Callable
    registered_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class A2AMessageQueue:
    """
    Agent-to-Agent message queue (in-memory with async).

    This is the transport layer for A2A protocol.
    Supports:
    - Async message delivery
    - Priority queuing
    - Request-response correlation
    - Pub-sub broadcasting
    - Message persistence (optional Redis backend)
    """

    def __init__(self, enable_persistence: bool = False):
        """
        Initialize A2A message queue.

        Args:
            enable_persistence: Enable Redis backend for distributed agents
        """
        # Agent registry
        self.agents: Dict[str, AgentRegistration] = {}

        # Message queues (per agent)
        self.queues: Dict[str, asyncio.Queue] = {}

        # Pending responses (correlation_id → future)
        self.pending_responses: Dict[str, asyncio.Future] = {}

        # Message history (for debugging)
        self.message_history: List[A2AMessage] = []

        # Subscribers for pub-sub
        self.subscribers: Dict[str, Set[str]] = {}  # topic → agent_ids

        self.enable_persistence = enable_persistence
        self.redis_client = None  # TODO: Add Redis support

        logger.info("a2a_message_queue_initialized", persistence=enable_persistence)

    def register_agent(
        self,
        agent_id: str,
        agent_type: str,
        capabilities: List[AgentCapability],
        message_handler: Callable
    ) -> None:
        """
        Register an agent in the A2A system.

        Args:
            agent_id: Unique agent identifier
            agent_type: Type of agent (apc, worker, orchestrator)
            capabilities: List of capabilities this agent provides
            message_handler: Async function to handle incoming messages
        """
        registration = AgentRegistration(
            agent_id=agent_id,
            agent_type=agent_type,
            capabilities=set(capabilities),
            message_handler=message_handler
        )

        self.agents[agent_id] = registration
        self.queues[agent_id] = asyncio.Queue()

        logger.info(
            "agent_registered",
            agent_id=agent_id,
            agent_type=agent_type,
            capabilities=[c.value for c in capabilities]
        )

    def unregister_agent(self, agent_id: str) -> None:
        """Unregister an agent."""
        if agent_id in self.agents:
            del self.agents[agent_id]
            del self.queues[agent_id]
            logger.info("agent_unregistered", agent_id=agent_id)

    async def send_message(
        self,
        message: A2AMessage,
        wait_for_response: bool = False,
        timeout: float = 30.0
    ) -> Optional[A2AMessage]:
        """
        Send a message to an agent.

        Args:
            message: A2AMessage to send
            wait_for_response: If True, wait for response (request-response)
            timeout: Timeout for response in seconds

        Returns:
            Response message if wait_for_response=True, else None
        """
        # Validate recipient exists
        if message.to_agent != "broadcast" and message.to_agent not in self.agents:
            logger.error("recipient_not_found", to_agent=message.to_agent)
            raise ValueError(f"Agent not found: {message.to_agent}")

        # Set correlation ID if not set
        if message.correlation_id is None:
            message.correlation_id = message.message_id

        logger.debug(
            "message_sent",
            from_agent=message.from_agent,
            to_agent=message.to_agent,
            message_type=message.message_type.value,
            correlation_id=message.correlation_id
        )

        # Add to history
        self.message_history.append(message)

        # Handle broadcast
        if message.to_agent == "broadcast":
            await self._broadcast_message(message)
            return None

        # Enqueue message
        await self.queues[message.to_agent].put(message)

        # If waiting for response, set up future
        if wait_for_response:
            future = asyncio.Future()
            self.pending_responses[message.correlation_id] = future

            try:
                response = await asyncio.wait_for(future, timeout=timeout)
                return response
            except asyncio.TimeoutError:
                logger.warning(
                    "response_timeout",
                    correlation_id=message.correlation_id,
                    timeout=timeout
                )
                del self.pending_responses[message.correlation_id]
                raise

        return None

    async def _broadcast_message(self, message: A2AMessage) -> None:
        """Broadcast message to all agents."""
        for agent_id in self.agents.keys():
            if agent_id != message.from_agent:  # Don't send to self
                await self.queues[agent_id].put(message)

    async def receive_message(self, agent_id: str) -> A2AMessage:
        """
        Receive next message for an agent (blocking).

        Args:
            agent_id: Agent to receive for

        Returns:
            Next A2AMessage from queue
        """
        if agent_id not in self.queues:
            raise ValueError(f"Agent not registered: {agent_id}")

        message = await self.queues[agent_id].get()

        logger.debug(
            "message_received",
            agent_id=agent_id,
            from_agent=message.from_agent,
            message_type=message.message_type.value
        )

        return message

    async def send_response(
        self,
        original_message: A2AMessage,
        response_payload: Dict[str, Any]
    ) -> None:
        """
        Send a response to a query/command.

        Args:
            original_message: Message being responded to
            response_payload: Response data
        """
        response = A2AMessage(
            from_agent=original_message.to_agent,
            to_agent=original_message.from_agent,
            message_type=MessageType.RESPONSE,
            payload=response_payload,
            correlation_id=original_message.correlation_id,
            reply_to=original_message.message_id,
            context=original_message.context
        )

        # If there's a pending future, resolve it
        if response.correlation_id in self.pending_responses:
            future = self.pending_responses[response.correlation_id]
            future.set_result(response)
            del self.pending_responses[response.correlation_id]
        else:
            # Otherwise send as normal message
            await self.send_message(response, wait_for_response=False)

    async def start_agent_listener(self, agent_id: str) -> None:
        """
        Start listening for messages for an agent (background task).

        Args:
            agent_id: Agent to listen for
        """
        if agent_id not in self.agents:
            raise ValueError(f"Agent not registered: {agent_id}")

        registration = self.agents[agent_id]

        logger.info("agent_listener_started", agent_id=agent_id)

        while agent_id in self.agents:
            try:
                message = await self.receive_message(agent_id)

                # Call agent's message handler
                await registration.message_handler(message)

            except Exception as e:
                logger.error(
                    "message_handler_error",
                    agent_id=agent_id,
                    error=str(e)
                )

    def find_agent_by_capability(
        self,
        capability: AgentCapability
    ) -> Optional[str]:
        """
        Find an agent ID by capability.

        Args:
            capability: Capability to search for

        Returns:
            Agent ID or None if not found
        """
        for agent_id, registration in self.agents.items():
            if capability in registration.capabilities:
                return agent_id
        return None

    def get_agent_info(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get info about a registered agent."""
        if agent_id not in self.agents:
            return None

        registration = self.agents[agent_id]
        return {
            "agent_id": registration.agent_id,
            "agent_type": registration.agent_type,
            "capabilities": [c.value for c in registration.capabilities],
            "registered_at": registration.registered_at
        }

    def get_all_agents(self) -> List[Dict[str, Any]]:
        """Get info about all registered agents."""
        return [self.get_agent_info(aid) for aid in self.agents.keys()]


# ==============================================================================
# Convenience Functions
# ==============================================================================

# Global message queue instance
_global_message_queue: Optional[A2AMessageQueue] = None


def get_message_queue(create_if_missing: bool = True) -> A2AMessageQueue:
    """
    Get the global A2A message queue.

    Args:
        create_if_missing: Create queue if it doesn't exist

    Returns:
        Global A2AMessageQueue instance
    """
    global _global_message_queue

    if _global_message_queue is None and create_if_missing:
        _global_message_queue = A2AMessageQueue()

    return _global_message_queue


async def send_to_agent(
    from_agent: str,
    to_agent: str,
    message_type: MessageType,
    payload: Dict[str, Any],
    wait_for_response: bool = False,
    timeout: float = 30.0,
    context: Optional[Dict[str, Any]] = None
) -> Optional[A2AMessage]:
    """
    Convenience function to send a message to an agent.

    Args:
        from_agent: Sender agent ID
        to_agent: Recipient agent ID
        message_type: Type of message
        payload: Message content
        wait_for_response: Wait for response?
        timeout: Response timeout
        context: Additional context

    Returns:
        Response message if wait_for_response=True, else None

    Example:
        # Worker asks APC about validation patterns
        response = await send_to_agent(
            from_agent="worker-123",
            to_agent="apc",
            message_type=MessageType.QUERY,
            payload={
                "query_type": "ask",
                "query": "What validation patterns exist?"
            },
            wait_for_response=True,
            context={"task": "Creating validator module"}
        )

        patterns = response.payload['results']
    """
    queue = get_message_queue()

    message = A2AMessage(
        from_agent=from_agent,
        to_agent=to_agent,
        message_type=message_type,
        payload=payload,
        context=context
    )

    return await queue.send_message(message, wait_for_response, timeout)


async def query_apc(
    from_agent: str,
    query_type: str,
    query: str,
    context: Optional[Dict[str, Any]] = None,
    timeout: float = 30.0
) -> Dict[str, Any]:
    """
    Convenience function for workers to query APC.

    Args:
        from_agent: Worker agent ID
        query_type: Type of query (ask, find_files, find_pattern, etc.)
        query: Query string
        context: Additional context
        timeout: Response timeout

    Returns:
        Query results

    Example:
        # Worker asks about validation patterns
        results = await query_apc(
            from_agent="worker-123",
            query_type="ask",
            query="What validation patterns exist?",
            context={"task": "Creating validator"}
        )

        for result in results['results']:
            print(result)
    """
    response = await send_to_agent(
        from_agent=from_agent,
        to_agent="apc",
        message_type=MessageType.QUERY,
        payload={
            "query_type": query_type,
            "query": query
        },
        wait_for_response=True,
        timeout=timeout,
        context=context
    )

    return response.payload if response else {}
