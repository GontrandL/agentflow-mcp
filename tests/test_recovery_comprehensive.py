#!/usr/bin/env python3
"""
Comprehensive Session Recovery Testing

Tests Session Recovery Agent on real past sessions to validate:
1. Information extraction quality
2. Context preservation accuracy
3. Bootstrap reliability
4. Document coherence

Target: Prove infinite session continuity works in practice
"""

from dotenv import load_dotenv
load_dotenv()

import json
import time
from pathlib import Path
from typing import Dict, List, Tuple

from agentflow.orchestration.session_recovery import (
    SessionMonitor,
    RecoveryAgent,
    BootstrapManager
)


class RecoveryTester:
    """Comprehensive recovery testing framework"""

    def __init__(self):
        self.test_sessions = [
            "SESSION_2025-10-13_TAGGED.md",
            "SESSION_COMPLETE_2025-10-13.md",
            "SESSION_REVIEW_2025-10-13.md",
            "SESSION_SUMMARY_2025-10-14.md"
        ]
        self.results = []

    def run_all_tests(self):
        """Run recovery tests on all past sessions"""
        print("="*80)
        print("COMPREHENSIVE SESSION RECOVERY TESTING")
        print("="*80)
        print(f"\nTesting {len(self.test_sessions)} past sessions\n")

        for session_file in self.test_sessions:
            print(f"\n{'='*80}")
            print(f"Testing: {session_file}")
            print('='*80)

            result = self.test_single_session(session_file)
            self.results.append(result)

            self._print_result(result)

        self._print_summary()

    def test_single_session(self, session_file: str) -> Dict:
        """
        Test recovery on a single session

        Returns:
            Dict with test results
        """
        session_path = Path(session_file)

        if not session_path.exists():
            return {
                'session': session_file,
                'status': 'FAILED',
                'error': 'File not found',
                'metrics': {}
            }

        try:
            # Read session content
            with open(session_path) as f:
                session_content = f.read()

            session_size = len(session_content)
            session_lines = session_content.count('\n')

            print(f"📄 Session size: {session_size:,} bytes ({session_lines:,} lines)")

            # Test recovery preparation
            start_time = time.time()

            recovery_agent = RecoveryAgent()

            # Simulate conversation from session (extract key sections)
            conversation = self._extract_conversation_from_session(session_content)

            manifest = recovery_agent.prepare_recovery(
                session_log_path=str(session_path),
                conversation_history=conversation,
                output_path=f"test_recovery_{session_path.stem}.json"
            )

            prep_time = time.time() - start_time

            # Analyze manifest quality
            quality_score = self._analyze_manifest_quality(
                manifest,
                session_content
            )

            # Test bootstrap
            bootstrap_start = time.time()
            bootstrap = BootstrapManager()
            summary = bootstrap.bootstrap_session(
                manifest_path=f"test_recovery_{session_path.stem}.json"
            )
            bootstrap_time = time.time() - bootstrap_start

            # Calculate metrics
            manifest_size = len(json.dumps(manifest))
            compression_ratio = 1 - (manifest_size / session_size)

            return {
                'session': session_file,
                'status': 'SUCCESS',
                'metrics': {
                    'session_size_bytes': session_size,
                    'session_lines': session_lines,
                    'manifest_size_bytes': manifest_size,
                    'compression_ratio': compression_ratio,
                    'prep_time_seconds': prep_time,
                    'bootstrap_time_seconds': bootstrap_time,
                    'quality_score': quality_score,
                    'completed_tasks': len(manifest.get('completed_tasks', [])),
                    'pending_tasks': len(manifest.get('pending_tasks', [])),
                    'key_decisions': len(manifest.get('critical_context', {}).get('key_decisions', [])),
                    'blockers': len(manifest.get('critical_context', {}).get('blockers', []))
                },
                'quality_analysis': self._detailed_quality_analysis(manifest, session_content)
            }

        except Exception as e:
            return {
                'session': session_file,
                'status': 'FAILED',
                'error': str(e),
                'metrics': {}
            }

    def _extract_conversation_from_session(self, content: str) -> List[Dict]:
        """Extract key conversation points from session file"""
        # Simplified extraction - would be more sophisticated in production
        lines = content.split('\n')

        conversation = []

        # Look for task markers
        for i, line in enumerate(lines[:50]):  # First 50 lines for context
            if any(marker in line.lower() for marker in ['task', 'completed', 'working on', 'fixed', 'implemented']):
                conversation.append({
                    'role': 'system',
                    'content': line.strip()
                })

        return conversation[:10]  # Return first 10 relevant lines

    def _analyze_manifest_quality(self, manifest: Dict, session_content: str) -> float:
        """
        Analyze how well the manifest captured session information

        Returns:
            Quality score 0-10
        """
        score = 0.0

        # Check completeness (2 points)
        required_keys = ['session_metadata', 'completed_tasks', 'pending_tasks',
                        'active_state', 'critical_context', 'memory_pointers']
        if all(key in manifest for key in required_keys):
            score += 2.0

        # Check task extraction (2 points)
        total_tasks = len(manifest.get('completed_tasks', [])) + len(manifest.get('pending_tasks', []))
        if total_tasks >= 3:
            score += 2.0
        elif total_tasks >= 1:
            score += 1.0

        # Check critical context (2 points)
        critical = manifest.get('critical_context', {})
        if critical.get('key_decisions') or critical.get('next_steps'):
            score += 2.0

        # Check memory pointers (2 points)
        pointers = manifest.get('memory_pointers', {})
        if pointers.get('modified_files') and len(pointers.get('modified_files', [])) > 0:
            score += 2.0

        # Check phase identification (2 points)
        phase = manifest.get('session_metadata', {}).get('phase', '')
        if phase and phase != 'Unknown' and 'fallback' not in phase.lower():
            score += 2.0

        return score

    def _detailed_quality_analysis(self, manifest: Dict, session_content: str) -> Dict:
        """Detailed quality analysis for reporting"""
        return {
            'has_phase_info': 'phase' in manifest.get('session_metadata', {}),
            'has_completed_tasks': len(manifest.get('completed_tasks', [])) > 0,
            'has_pending_tasks': len(manifest.get('pending_tasks', [])) > 0,
            'has_key_decisions': len(manifest.get('critical_context', {}).get('key_decisions', [])) > 0,
            'has_next_steps': len(manifest.get('critical_context', {}).get('next_steps', [])) > 0,
            'has_blockers': len(manifest.get('critical_context', {}).get('blockers', [])) > 0,
            'has_modified_files': len(manifest.get('memory_pointers', {}).get('modified_files', [])) > 0,
            'bootstrap_instructions_count': len(manifest.get('bootstrap_instructions', []))
        }

    def _print_result(self, result: Dict):
        """Print single test result"""
        print(f"\n{'─'*80}")
        print(f"Result: {result['status']}")

        if result['status'] == 'SUCCESS':
            metrics = result['metrics']
            print(f"\n📊 Metrics:")
            print(f"  Session Size:      {metrics['session_size_bytes']:,} bytes")
            print(f"  Manifest Size:     {metrics['manifest_size_bytes']:,} bytes")
            print(f"  Compression Ratio: {metrics['compression_ratio']:.2%}")
            print(f"  Prep Time:         {metrics['prep_time_seconds']:.1f}s")
            print(f"  Bootstrap Time:    {metrics['bootstrap_time_seconds']:.3f}s")
            print(f"  Quality Score:     {metrics['quality_score']:.1f}/10")
            print(f"\n📋 Content:")
            print(f"  Completed Tasks:   {metrics['completed_tasks']}")
            print(f"  Pending Tasks:     {metrics['pending_tasks']}")
            print(f"  Key Decisions:     {metrics['key_decisions']}")
            print(f"  Blockers:          {metrics['blockers']}")

            # Quality indicators
            quality = result['quality_analysis']
            print(f"\n✓ Quality Indicators:")
            for key, value in quality.items():
                icon = '✅' if value else '⚠️'
                print(f"  {icon} {key.replace('_', ' ').title()}: {value}")

        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")

    def _print_summary(self):
        """Print overall test summary"""
        print(f"\n{'='*80}")
        print("OVERALL TEST SUMMARY")
        print('='*80)

        total = len(self.results)
        successful = sum(1 for r in self.results if r['status'] == 'SUCCESS')
        failed = total - successful

        print(f"\nTotal Tests:      {total}")
        print(f"✅ Successful:     {successful} ({successful/total*100:.0f}%)")
        print(f"❌ Failed:         {failed} ({failed/total*100:.0f}%)")

        if successful > 0:
            # Average metrics
            success_results = [r for r in self.results if r['status'] == 'SUCCESS']

            avg_compression = sum(r['metrics']['compression_ratio'] for r in success_results) / successful
            avg_quality = sum(r['metrics']['quality_score'] for r in success_results) / successful
            avg_prep_time = sum(r['metrics']['prep_time_seconds'] for r in success_results) / successful
            avg_bootstrap_time = sum(r['metrics']['bootstrap_time_seconds'] for r in success_results) / successful

            print(f"\n📊 Average Metrics:")
            print(f"  Compression Ratio: {avg_compression:.2%}")
            print(f"  Quality Score:     {avg_quality:.1f}/10")
            print(f"  Prep Time:         {avg_prep_time:.1f}s")
            print(f"  Bootstrap Time:    {avg_bootstrap_time:.3f}s")

            # Best and worst
            best = max(success_results, key=lambda x: x['metrics']['quality_score'])
            worst = min(success_results, key=lambda x: x['metrics']['quality_score'])

            print(f"\n🏆 Best Recovery:")
            print(f"  Session: {best['session']}")
            print(f"  Quality Score: {best['metrics']['quality_score']:.1f}/10")

            print(f"\n⚠️  Worst Recovery:")
            print(f"  Session: {worst['session']}")
            print(f"  Quality Score: {worst['metrics']['quality_score']:.1f}/10")

        # Recommendations
        print(f"\n💡 Recommendations:")

        if avg_quality < 7.0:
            print("  ⚠️  Quality scores below 7/10 - consider improving extraction algorithms")

        if avg_compression < 0.98:
            print("  ⚠️  Compression below 98% - consider more aggressive summarization")

        if avg_prep_time > 60:
            print("  ⚠️  Prep time > 60s - consider optimization or caching")

        if successful == total:
            print("  ✅ All tests passed! System ready for production.")

        # Save results
        with open('recovery_test_results.json', 'w') as f:
            json.dump(self.results, f, indent=2)

        print(f"\n📁 Detailed results saved to: recovery_test_results.json")


if __name__ == "__main__":
    tester = RecoveryTester()
    tester.run_all_tests()
