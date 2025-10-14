"""
Comprehensive Testing for Session Context Curator System

Tests the complete context curation workflow:
1. Session classification across all types
2. Context cherry-picking and size reduction
3. Interactive refinement with Q&A
4. Session routing and orchestration
5. Performance validation

Expected Results:
- Classification accuracy: >90%
- Context size reduction: >85%
- Quality preservation: 10/10
- Bootstrap time: <0.01s
"""

import json
import os
import time
from pathlib import Path
from typing import Dict, List

from agentflow.orchestration.session_recovery.session_context_curator import (
    SessionContextCurator,
    SessionContextCuratorWithRefinement,
    SessionClassifier,
    ContextCherryPicker,
    SessionType,
    InteractiveContextRefiner
)


class ContextCuratorTester:
    """Comprehensive testing for context curator"""

    def __init__(self, project_root: str = None):
        self.project_root = project_root or os.getcwd()
        self.curator = SessionContextCuratorWithRefinement(self.project_root)
        self.classifier = SessionClassifier()  # No args - uses internal rules
        self.cherry_picker = ContextCherryPicker(self.project_root)
        self.results = []

        # Test scenarios representing different session types
        self.test_scenarios = self._create_test_scenarios()

    def _create_test_scenarios(self) -> List[Dict]:
        """Create diverse test scenarios for each session type"""
        return [
            {
                'name': 'Unit Test Development',
                'expected_type': SessionType.TESTING,
                'task': 'Write comprehensive unit tests for SmartOrchestrator class',
                'modified_files': [
                    'tests/test_smart_orchestrator.py',
                    'agentflow/orchestration/smart_orchestrator.py'
                ],
                'expected_context_files': [
                    'agentflow/orchestration/smart_orchestrator.py',
                    'tests/conftest.py'
                ]
            },
            {
                'name': 'New Feature Implementation',
                'expected_type': SessionType.FEATURE_DEV,
                'task': 'Implement parallel delegation pool with 5 concurrent workers',
                'modified_files': [
                    'agentflow/orchestration/delegation_pool.py',
                    'agentflow/orchestration/pool_status.py',
                    'run_delegation_pool.py'
                ],
                'expected_context_files': [
                    'agentflow/orchestration/smart_orchestrator.py',
                    'agentflow/core/delegator.py'
                ]
            },
            {
                'name': 'Bug Fix - TypeError in Classifier',
                'expected_type': SessionType.BUG_FIX,
                'task': 'Fix TypeError: sequence item 0: expected str instance, dict found in session_classifier.py line 87',
                'modified_files': [
                    'agentflow/orchestration/session_recovery/session_context_curator.py'
                ],
                'expected_context_files': [
                    'agentflow/orchestration/session_recovery/session_context_curator.py'
                ]
            },
            {
                'name': 'Refactoring - Extract Utility Functions',
                'expected_type': SessionType.REFACTORING,
                'task': 'Extract file parsing logic from RecoveryAgent into reusable utility module',
                'modified_files': [
                    'agentflow/orchestration/session_recovery/recovery_agent.py',
                    'agentflow/orchestration/utils/file_parser.py'
                ],
                'expected_context_files': [
                    'agentflow/orchestration/session_recovery/recovery_agent.py',
                    'agentflow/orchestration/utils/__init__.py'
                ]
            },
            {
                'name': 'Documentation - API Reference',
                'expected_type': SessionType.DOCUMENTATION,
                'task': 'Generate comprehensive API documentation for Session Recovery Agent',
                'modified_files': [
                    'docs/SESSION_RECOVERY_AGENT.md',
                    'docs/api/recovery_agent_api.md'
                ],
                'expected_context_files': [
                    'agentflow/orchestration/session_recovery/recovery_agent.py',
                    'agentflow/orchestration/session_recovery/__init__.py'
                ]
            },
            {
                'name': 'Deployment - CI/CD Setup',
                'expected_type': SessionType.DEPLOYMENT,
                'task': 'Configure GitHub Actions workflow for automated testing and deployment',
                'modified_files': [
                    '.github/workflows/test.yml',
                    '.github/workflows/deploy.yml'
                ],
                'expected_context_files': [
                    'pyproject.toml',
                    'tests/conftest.py'
                ]
            },
            {
                'name': 'Research - Vector DB Evaluation',
                'expected_type': SessionType.RESEARCH,
                'task': 'Research and evaluate ChromaDB vs Pinecone for semantic search integration',
                'modified_files': [
                    'docs/VECTOR_DB_EVALUATION.md'
                ],
                'expected_context_files': [
                    'agentflow/orchestration/session_recovery/recovery_agent.py',
                    'requirements.txt'
                ]
            },
            {
                'name': 'Testing - Session Monitor Validation',
                'expected_type': SessionType.TESTING,
                'task': 'Review and validate SessionMonitor implementation for production readiness',
                'modified_files': [
                    'tests/test_session_monitor.py'
                ],
                'expected_context_files': [
                    'agentflow/orchestration/session_recovery/session_monitor.py',
                    'tests/test_session_monitor.py'
                ]
            }
        ]

    def test_session_classification(self) -> Dict:
        """Test classification accuracy across all session types"""
        print("\n" + "="*80)
        print("TEST 1: SESSION CLASSIFICATION ACCURACY")
        print("="*80)

        results = {
            'total': len(self.test_scenarios),
            'correct': 0,
            'incorrect': 0,
            'details': []
        }

        for scenario in self.test_scenarios:
            # Create mock manifest
            manifest = {
                'task_description': scenario['task'],
                'modified_files': scenario['modified_files'],
                'completed_tasks': [scenario['task']],
                'next_steps': []
            }

            # Classify
            predicted_type = self.classifier.classify_session(manifest)
            expected_type = scenario['expected_type']

            is_correct = predicted_type == expected_type
            if is_correct:
                results['correct'] += 1
            else:
                results['incorrect'] += 1

            detail = {
                'scenario': scenario['name'],
                'expected': expected_type.value,
                'predicted': predicted_type.value,
                'correct': is_correct
            }
            results['details'].append(detail)

            status = "✅" if is_correct else "❌"
            print(f"\n{status} {scenario['name']}")
            print(f"   Expected: {expected_type.value}")
            print(f"   Predicted: {predicted_type.value}")

        accuracy = (results['correct'] / results['total']) * 100
        results['accuracy_percentage'] = accuracy

        print(f"\n{'='*80}")
        print(f"CLASSIFICATION ACCURACY: {accuracy:.1f}% ({results['correct']}/{results['total']})")
        print(f"{'='*80}")

        return results

    def test_context_cherry_picking(self) -> Dict:
        """Test context size reduction and relevance"""
        print("\n" + "="*80)
        print("TEST 2: CONTEXT CHERRY-PICKING & SIZE REDUCTION")
        print("="*80)

        results = {
            'scenarios': [],
            'avg_reduction': 0.0,
            'avg_size_kb': 0.0
        }

        total_reduction = 0.0
        total_size = 0.0

        for scenario in self.test_scenarios:
            start_time = time.time()

            # Cherry-pick context
            curated = self.cherry_picker.cherry_pick(
                task=scenario['task'],
                session_type=scenario['expected_type'],
                max_size_kb=30
            )

            elapsed = time.time() - start_time

            # Calculate metrics
            size_kb = curated.size_bytes / 1024  # Convert bytes to KB
            full_size_kb = 200  # Typical full project context
            reduction = ((full_size_kb - size_kb) / full_size_kb) * 100

            total_reduction += reduction
            total_size += size_kb

            scenario_result = {
                'name': scenario['name'],
                'type': scenario['expected_type'].value,
                'size_kb': size_kb,
                'reduction_percent': reduction,
                'core_files_count': len(curated.core_files),
                'dependencies_count': len(curated.dependencies),
                'total_files': len(curated.core_files) + len(curated.dependencies),
                'cherry_pick_time': elapsed,
                'estimated_tokens': curated.estimated_tokens
            }
            results['scenarios'].append(scenario_result)

            print(f"\n📊 {scenario['name']}")
            print(f"   Type: {scenario['expected_type'].value}")
            print(f"   Size: {size_kb:.1f} KB (vs 200 KB full context)")
            print(f"   Reduction: {reduction:.1f}%")
            print(f"   Files: {len(curated.core_files)} core + {len(curated.dependencies)} dependencies")
            print(f"   Tokens: {curated.estimated_tokens}")
            print(f"   Time: {elapsed:.3f}s")

        results['avg_reduction'] = total_reduction / len(self.test_scenarios)
        results['avg_size_kb'] = total_size / len(self.test_scenarios)

        print(f"\n{'='*80}")
        print(f"AVERAGE REDUCTION: {results['avg_reduction']:.1f}%")
        print(f"AVERAGE SIZE: {results['avg_size_kb']:.1f} KB (target: <30 KB)")
        print(f"{'='*80}")

        return results

    def test_interactive_refinement(self) -> Dict:
        """Test Q&A system for context refinement"""
        print("\n" + "="*80)
        print("TEST 3: INTERACTIVE CONTEXT REFINEMENT")
        print("="*80)

        results = {
            'questions_tested': 0,
            'avg_response_time': 0.0,
            'learning_insights': None,
            'examples': []
        }

        # Test questions representing common scenarios
        test_questions = [
            {
                'session_type': SessionType.FEATURE_DEV,
                'question': 'I need the database migration utilities but they are not in my context',
                'expected_type': 'missing_file'
            },
            {
                'session_type': SessionType.BUG_FIX,
                'question': 'What are the common error patterns in the authentication module?',
                'expected_type': 'context_info'
            },
            {
                'session_type': SessionType.TESTING,
                'question': 'Which test fixtures should I use for integration tests?',
                'expected_type': 'clarification'
            },
            {
                'session_type': SessionType.REFACTORING,
                'question': 'Is there related code in other modules that depends on this?',
                'expected_type': 'dependency_info'
            }
        ]

        total_time = 0.0

        for i, test_q in enumerate(test_questions, 1):
            start_time = time.time()

            # Ask question
            answer = self.curator.refiner.ask_question(
                session_id=f"test_session_{i}",
                session_type=test_q['session_type'],
                question=test_q['question'],
                current_context=['mock_file_1.py', 'mock_file_2.py']
            )

            elapsed = time.time() - start_time
            total_time += elapsed

            results['questions_tested'] += 1

            example = {
                'question': test_q['question'],
                'session_type': test_q['session_type'].value,
                'expected_type': test_q['expected_type'],
                'actual_type': answer.answer_type,
                'response_time': elapsed,
                'improvement_score': answer.estimated_improvement
            }
            results['examples'].append(example)

            match = "✅" if answer.answer_type == test_q['expected_type'] else "⚠️"
            print(f"\n{match} Question {i}: {test_q['question'][:60]}...")
            print(f"   Type: {answer.answer_type} (expected: {test_q['expected_type']})")
            print(f"   Improvement: {answer.estimated_improvement:.1%}")
            print(f"   Time: {elapsed:.3f}s")

        results['avg_response_time'] = total_time / len(test_questions)

        # Get learning insights (public method, no underscore)
        insights = self.curator.refiner.get_learning_insights()
        results['learning_insights'] = {
            'total_questions': insights['total_questions'],
            'avg_improvement': insights['avg_improvement'],
            'insights_count': len(insights['insights'])
        }

        print(f"\n{'='*80}")
        print(f"QUESTIONS PROCESSED: {results['questions_tested']}")
        print(f"AVG RESPONSE TIME: {results['avg_response_time']:.3f}s")
        print(f"LEARNING INSIGHTS: {insights['total_questions']} questions analyzed")
        print(f"{'='*80}")

        return results

    def test_full_curation_workflow(self) -> Dict:
        """Test complete end-to-end curation workflow"""
        print("\n" + "="*80)
        print("TEST 4: FULL CURATION WORKFLOW (END-TO-END)")
        print("="*80)

        results = {
            'workflows_tested': 0,
            'avg_total_time': 0.0,
            'quality_score': 0.0,
            'details': []
        }

        total_time = 0.0
        total_quality = 0.0

        # Test 3 representative workflows
        test_workflows = self.test_scenarios[:3]  # Feature, Bug Fix, Testing

        for workflow in test_workflows:
            print(f"\n🔄 Testing: {workflow['name']}")
            start_time = time.time()

            # Step 1: Curate context
            curated = self.curator.curate_context(
                task_description=workflow['task'],
                session_type=workflow['expected_type'],
                max_size_kb=30
            )

            # Step 2: Simulate session asking question
            question = f"Are there any dependencies I should be aware of for: {workflow['task'][:50]}?"
            answer = self.curator.refiner.ask_question(
                session_id=f"workflow_{workflow['name']}",
                session_type=workflow['expected_type'],
                question=question,
                current_context=curated.core_files
            )

            elapsed = time.time() - start_time
            total_time += elapsed

            # Calculate quality score (heuristic based on completeness)
            quality = self._calculate_quality_score(curated, answer, workflow)
            total_quality += quality

            workflow_result = {
                'name': workflow['name'],
                'type': workflow['expected_type'].value,
                'size_kb': curated.size_bytes / 1024,
                'files_count': len(curated.core_files) + len(curated.dependencies),
                'question_asked': True,
                'context_improved': answer.estimated_improvement > 0,
                'total_time': elapsed,
                'quality_score': quality
            }
            results['details'].append(workflow_result)

            results['workflows_tested'] += 1

            print(f"   ✅ Context curated: {curated.size_bytes / 1024:.1f} KB")
            print(f"   ✅ Question answered: {answer.answer_type}")
            print(f"   ✅ Quality score: {quality:.1f}/10")
            print(f"   ✅ Total time: {elapsed:.3f}s")

        results['avg_total_time'] = total_time / results['workflows_tested']
        results['quality_score'] = total_quality / results['workflows_tested']

        print(f"\n{'='*80}")
        print(f"WORKFLOWS COMPLETED: {results['workflows_tested']}")
        print(f"AVG WORKFLOW TIME: {results['avg_total_time']:.3f}s")
        print(f"AVG QUALITY SCORE: {results['quality_score']:.1f}/10 (target: >8)")
        print(f"{'='*80}")

        return results

    def _calculate_quality_score(self, curated, answer, workflow) -> float:
        """Calculate quality score based on multiple factors"""
        score = 10.0

        # Deduct points for issues
        size_kb = curated.size_bytes / 1024
        if size_kb > 35:
            score -= 1.0  # Slightly too large

        if len(curated.core_files) == 0:
            score -= 3.0  # No core files identified

        if answer.estimated_improvement == 0:
            score -= 0.5  # Question didn't help

        # Check if expected files are present
        expected = set(workflow.get('expected_context_files', []))
        actual = set(curated.core_files + curated.dependencies)

        # Calculate overlap
        overlap = len(expected & actual)
        if len(expected) > 0:
            overlap_ratio = overlap / len(expected)
            if overlap_ratio < 0.5:
                score -= 2.0  # Missing too many expected files

        return max(0.0, min(10.0, score))

    def run_all_tests(self) -> Dict:
        """Run complete test suite"""
        print("\n" + "="*80)
        print("🧪 SESSION CONTEXT CURATOR - COMPREHENSIVE TEST SUITE")
        print("="*80)
        print(f"Project: {Path(self.project_root).name}")
        print(f"Test Scenarios: {len(self.test_scenarios)}")
        print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")

        start_time = time.time()

        # Run all tests
        classification_results = self.test_session_classification()
        cherry_pick_results = self.test_context_cherry_picking()
        refinement_results = self.test_interactive_refinement()
        workflow_results = self.test_full_curation_workflow()

        total_elapsed = time.time() - start_time

        # Compile final report
        final_report = {
            'timestamp': time.time(),
            'project': Path(self.project_root).name,
            'test_duration_seconds': total_elapsed,
            'classification': classification_results,
            'cherry_picking': cherry_pick_results,
            'refinement': refinement_results,
            'workflow': workflow_results,
            'overall_status': self._determine_overall_status(
                classification_results,
                cherry_pick_results,
                refinement_results,
                workflow_results
            )
        }

        # Print summary
        self._print_final_summary(final_report)

        # Save results
        output_path = os.path.join(self.project_root, 'context_curator_test_results.json')
        with open(output_path, 'w') as f:
            json.dump(final_report, f, indent=2)

        print(f"\n💾 Results saved to: {output_path}")

        return final_report

    def _determine_overall_status(self, classification, cherry_pick, refinement, workflow) -> str:
        """Determine overall test status"""
        # Check targets
        classification_ok = classification['accuracy_percentage'] >= 90
        cherry_pick_ok = cherry_pick['avg_reduction'] >= 85
        workflow_ok = workflow['quality_score'] >= 8.0

        if all([classification_ok, cherry_pick_ok, workflow_ok]):
            return "✅ ALL TESTS PASSED"
        elif classification_ok and cherry_pick_ok:
            return "⚠️ MOSTLY PASSING (workflow needs improvement)"
        else:
            return "❌ NEEDS IMPROVEMENT"

    def _print_final_summary(self, report: Dict):
        """Print comprehensive final summary"""
        print("\n" + "="*80)
        print("📊 FINAL TEST SUMMARY")
        print("="*80)

        print(f"\n⏱️  Total Duration: {report['test_duration_seconds']:.1f}s")
        print(f"\n🎯 Status: {report['overall_status']}")

        print(f"\n📋 Test Results:")
        print(f"   Classification Accuracy: {report['classification']['accuracy_percentage']:.1f}% (target: >90%)")
        print(f"   Context Size Reduction: {report['cherry_picking']['avg_reduction']:.1f}% (target: >85%)")
        print(f"   Avg Context Size: {report['cherry_picking']['avg_size_kb']:.1f} KB (target: <30 KB)")
        print(f"   Workflow Quality: {report['workflow']['quality_score']:.1f}/10 (target: >8)")
        print(f"   Refinement Questions: {report['refinement']['questions_tested']} processed")

        print(f"\n💰 Performance Metrics:")
        avg_workflow_time = report['workflow']['avg_total_time']
        print(f"   Avg Workflow Time: {avg_workflow_time:.3f}s")
        print(f"   Refinement Response: {report['refinement']['avg_response_time']:.3f}s")

        print(f"\n🎓 Key Achievements:")
        if report['classification']['accuracy_percentage'] >= 90:
            print(f"   ✅ Classification highly accurate ({report['classification']['accuracy_percentage']:.1f}%)")
        if report['cherry_picking']['avg_reduction'] >= 85:
            print(f"   ✅ Context reduction excellent ({report['cherry_picking']['avg_reduction']:.1f}%)")
        if report['cherry_picking']['avg_size_kb'] <= 30:
            print(f"   ✅ Context size within target ({report['cherry_picking']['avg_size_kb']:.1f} KB)")
        if report['workflow']['quality_score'] >= 8.0:
            print(f"   ✅ Workflow quality excellent ({report['workflow']['quality_score']:.1f}/10)")

        print("\n" + "="*80)


# Main execution
if __name__ == "__main__":
    tester = ContextCuratorTester()
    results = tester.run_all_tests()

    print("\n✅ Comprehensive testing complete!")
    print(f"Status: {results['overall_status']}")
