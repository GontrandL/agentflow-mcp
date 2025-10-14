#!/usr/bin/env python3
import os
import sys
import json
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from pathlib import Path

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from agentflow.core.smart_orchestrator import SmartOrchestrator, generate_delegated_task
from agentflow.orchestration.delegation_pool import DelegationPool
from agentflow.integration.agentflow_delegation_system import AgentFlowDelegationSystem
from agentflow.core.project_scanner import ProjectScanner, scan_and_save

from agentflow.integration.agentflow_a2a_adapter import AgentFlowA2AAdapter
from agentflow.integration.a2a_protocol import get_message_queue

import structlog

logger = structlog.get_logger(__name__)


class AgentFlowMCPServer:
    def __init__(self):
        self.smart_orchestrator = SmartOrchestrator()
        self.delegation_pool = DelegationPool()
        self.system = AgentFlowDelegationSystem()
        self.project_scanner = None
        self.project_index = None

        self.a2a_adapter = AgentFlowA2AAdapter(self)
        self.a2a_adapter.register()
        self.a2a_enabled = True

        logger.info(
            "agentflow_mcp_server_initialized",
            a2a_enabled=True,
            a2a_agent_id="agentflow",
            capabilities=["TASK_DELEGATION", "PARALLEL_EXECUTION", "VALIDATION"],
            message="AgentFlow registered in A2A message queue"
        )

        self.server_info = {
            "name": "agentflow-mcp-server",
            "version": "1.0.0",
            "description": "AgentFlow - Task delegation and parallel execution",
            "tools": [
                {
                    "name": "delegate_task",
                    "description": "Delegate single task to cost-effective model",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "task_description": {
                                "type": "string",
                                "description": "Task to delegate"
                            },
                            "context": {
                                "type": "array",
                                "description": "Array of context objects",
                                "items": {
                                    "type": "object"
                                }
                            },
                            "target_model": {
                                "type": "string",
                                "description": "Target model for delegation",
                                "default": "cost-effective"
                            }
                        },
                        "required": ["task_description"]
                    }
                },
                {
                    "name": "delegate_parallel",
                    "description": "Spawn parallel workers for complex tasks",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "task_description": {
                                "type": "string",
                                "description": "Task to parallelize"
                            },
                            "context": {
                                "type": "array",
                                "description": "Context for workers",
                                "items": {
                                    "type": "object"
                                }
                            },
                            "worker_count": {
                                "type": "number",
                                "description": "Number of workers (3-8)",
                                "default": 5
                            }
                        },
                        "required": ["task_description"]
                    }
                },
                {
                    "name": "check_delegation_status",
                    "description": "Monitor task progress and results",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "task_id": {
                                "type": "string",
                                "description": "Task ID to check"
                            }
                        },
                        "required": ["task_id"]
                    }
                },
                {
                    "name": "list_models",
                    "description": "Show available models and pricing",
                    "inputSchema": {
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                }
            ]
        }

        logger.info("agentflow_mcp_server_initialized", tools=len(self.server_info['tools']))

    async def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        method = request.get('method')
        params = request.get('params', {})

        try:
            if method == 'delegate_task':
                result = await self._delegate_task(params)
            elif method == 'delegate_parallel':
                result = await self._delegate_parallel(params)
            elif method == 'check_delegation_status':
                result = await self._check_delegation_status(params)
            elif method == 'list_models':
                result = await self._list_models(params)
            elif method == 'initialize':
                result = self.server_info
            elif method == 'list_tools':
                result = {"tools": self.server_info['tools']}
            else:
                raise ValueError(f"Unknown method: {method}")

            return {
                "jsonrpc": "2.0",
                "id": request.get('id'),
                "result": result
            }

        except Exception as e:
            logger.error("request_error", method=method, error=str(e))
            return {
                "jsonrpc": "2.0",
                "id": request.get('id'),
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }

    async def _delegate_task(self, params: Dict[str, Any]) -> Dict[str, Any]:
        task_description = params['task_description']
        context = params.get('context', [])
        target_model = params.get('target_model', 'cost-effective')

        delegated = generate_delegated_task(
            task_description,
            context,
            target_model=target_model
        )

        logger.info(
            "task_delegated",
            task=task_description,
            model=target_model,
            tokens=delegated.total_tokens
        )

        return {
            "task_id": delegated.task_id,
            "model": delegated.model,
            "status": delegated.status,
            "estimated_cost": delegated.estimated_cost,
            "timeout": delegated.timeout
        }

    async def _delegate_parallel(self, params: Dict[str, Any]) -> Dict[str, Any]:
        task_description = params['task_description']
        context = params.get('context', [])
        worker_count = min(max(params.get('worker_count', 5), 3), 8)

        parallel = self.delegation_pool.create_parallel(
            task_description,
            context,
            worker_count=worker_count
        )

        logger.info(
            "parallel_delegation",
            task=task_description,
            workers=worker_count,
            batch_id=parallel.batch_id
        )

        return {
            "batch_id": parallel.batch_id,
            "worker_count": parallel.worker_count,
            "status": parallel.status,
            "tasks": [t.task_id for t in parallel.tasks]
        }

    async def _check_delegation_status(self, params: Dict[str, Any]) -> Dict[str, Any]:
        task_id = params['task_id']
        status = self.system.check_status(task_id)

        logger.info(
            "status_checked",
            task_id=task_id,
            status=status['status']
        )

        return status

    async def _list_models(self, params: Dict[str, Any]) -> Dict[str, Any]:
        models = self.system.list_models()

        logger.info(
            "models_listed",
            count=len(models)
        )

        return {
            "models": models,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    async def run(self):
        logger.info("agentflow_mcp_server_started", mode="stdio")

        while True:
            try:
                line = await asyncio.get_event_loop().run_in_executor(
                    None, sys.stdin.readline
                )

                if not line:
                    break

                request = json.loads(line.strip())
                response = await self.handle_request(request)
                print(json.dumps(response), flush=True)

            except json.JSONDecodeError as e:
                logger.error("json_decode_error", error=str(e))
                continue
            except KeyboardInterrupt:
                logger.info("server_shutdown")
                break
            except Exception as e:
                logger.error("server_error", error=str(e))
                continue


async def test_mcp_server():
    print("\n" + "="*70)
    print("🧪 AgentFlow MCP Server - Local Test")
    print("="*70)

    server = AgentFlowMCPServer()

    print("\n📋 Test 1: Delegate Task")
    request1 = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "delegate_task",
        "params": {
            "task_description": "Process customer data",
            "target_model": "cost-effective"
        }
    }

    response1 = await server.handle_request(request1)
    print(f"✅ Task ID: {response1['result']['task_id']}")

    print("\n🔍 Test 2: Delegate Parallel")
    request2 = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "delegate_parallel",
        "params": {
            "task_description": "Analyze large dataset",
            "worker_count": 5
        }
    }

    response2 = await server.handle_request(request2)
    print(f"✅ Batch ID: {response2['result']['batch_id']}")

    print("\n📊 Test 3: List Models")
    request3 = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "list_models",
        "params": {}
    }

    response3 = await server.handle_request(request3)
    print(f"✅ Models: {len(response3['result']['models'])} available")

    print("\n" + "="*70)
    print("🎉 All tests passed!")
    print("="*70)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        asyncio.run(test_mcp_server())
    else:
        server = AgentFlowMCPServer()
        asyncio.run(server.run())


if __name__ == '__main__':
    main()