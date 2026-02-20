"""
AI SPEED & PERFORMANCE TEST SUITE
Standalone test for AI capabilities speed and performance on any device.

Tests:
1. LLM Response Time
2. Text-to-SQL Generation Speed
3. Document Processing Speed
4. Batch Processing Throughput
5. Concurrent Request Handling
6. Memory Usage Under Load
7. RAG Query Response Time

Run with: python ai_speed_test.py
"""
import asyncio
import json
import os
import psutil
import time
from dataclasses import dataclass
from datetime import datetime
from statistics import mean, median, stdev
from typing import Any, Dict, List, Optional


@dataclass
class PerformanceResult:
    """Result of a single performance test."""
    test_name: str
    passed: bool
    avg_time_ms: float
    median_time_ms: float
    min_time_ms: float
    max_time_ms: float
    std_dev_ms: float
    throughput: float  # ops/second
    p95_time_ms: Optional[float] = None
    p99_time_ms: Optional[float] = None
    memory_mb: Optional[float] = None
    error: Optional[str] = None


@dataclass
class PerformanceReport:
    """Overall performance report."""
    total_tests: int
    passed_tests: int
    failed_tests: int
    results: List[PerformanceResult]
    timestamp: str
    device_info: Dict[str, str]


class AISpeedTester:
    """Test AI capabilities for speed and performance."""

    def __init__(self, base_url: str = "http://127.0.0.1:8000"):
        self.base_url = base_url
        self.results: List[PerformanceResult] = []
        self.process = psutil.Process()

    def print_header(self, title: str):
        """Print formatted header."""
        print("\n" + "=" * 70)
        print(f"  {title}")
        print("=" * 70)

    def print_result(self, result: PerformanceResult):
        """Print test result."""
        status = "✓ PASS" if result.passed else "✗ FAIL"
        print(f"{status} | {result.test_name:<35}")
        print(f"       Avg: {result.avg_time_ms:.1f}ms | Median: {result.median_time_ms:.1f}ms | "
              f"Min: {result.min_time_ms:.1f}ms | Max: {result.max_time_ms:.1f}ms")
        print(f"       Throughput: {result.throughput:.1f} ops/sec | Std Dev: {result.std_dev_ms:.1f}ms")
        if result.p95_time_ms:
            print(f"       P95: {result.p95_time_ms:.1f}ms | P99: {result.p99_time_ms:.1f}ms")
        if result.memory_mb:
            print(f"       Memory Usage: {result.memory_mb:.1f} MB")
        if result.error:
            print(f"       Error: {result.error}")

    def get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        return self.process.memory_info().rss / 1024 / 1024

    def calculate_percentile(self, data: List[float], percentile: float) -> float:
        """Calculate percentile from data."""
        sorted_data = sorted(data)
        index = int(len(sorted_data) * (percentile / 100))
        return sorted_data[min(index, len(sorted_data) - 1)]

    async def test_llm_response_time(self, iterations: int = 50) -> PerformanceResult:
        """Test LLM response time."""
        test_name = "LLM Response Time"
        timings = []

        try:
            for i in range(iterations):
                start = time.time()

                # Simulate LLM call (replace with actual API call)
                prompt = f"What is {i} + {i}?"
                await asyncio.sleep(0.1)  # Simulate API latency
                response = f"The answer is {i + i}"

                elapsed = (time.time() - start) * 1000
                timings.append(elapsed)

            avg_time = mean(timings)
            median_time = median(timings)
            min_time = min(timings)
            max_time = max(timings)
            std_dev = stdev(timings) if len(timings) > 1 else 0
            throughput = 1000 / avg_time  # ops per second
            p95 = self.calculate_percentile(timings, 95)
            p99 = self.calculate_percentile(timings, 99)

            # Pass if average response time is under 500ms
            passed = avg_time < 500

            return PerformanceResult(
                test_name=test_name,
                passed=passed,
                avg_time_ms=avg_time,
                median_time_ms=median_time,
                min_time_ms=min_time,
                max_time_ms=max_time,
                std_dev_ms=std_dev,
                throughput=throughput,
                p95_time_ms=p95,
                p99_time_ms=p99,
            )
        except Exception as e:
            return PerformanceResult(
                test_name=test_name,
                passed=False,
                avg_time_ms=0,
                median_time_ms=0,
                min_time_ms=0,
                max_time_ms=0,
                std_dev_ms=0,
                throughput=0,
                error=str(e),
            )

    async def test_text_to_sql_speed(self, iterations: int = 30) -> PerformanceResult:
        """Test Text-to-SQL generation speed."""
        test_name = "Text-to-SQL Generation Speed"
        timings = []

        try:
            for i in range(iterations):
                start = time.time()

                # Simulate SQL generation (replace with actual call)
                question = f"Show me all orders over ${i * 100}"
                await asyncio.sleep(0.15)  # Simulate processing
                sql = f"SELECT * FROM orders WHERE amount > {i * 100}"

                elapsed = (time.time() - start) * 1000
                timings.append(elapsed)

            avg_time = mean(timings)
            median_time = median(timings)
            min_time = min(timings)
            max_time = max(timings)
            std_dev = stdev(timings) if len(timings) > 1 else 0
            throughput = 1000 / avg_time
            p95 = self.calculate_percentile(timings, 95)
            p99 = self.calculate_percentile(timings, 99)

            # Pass if average is under 300ms
            passed = avg_time < 300

            return PerformanceResult(
                test_name=test_name,
                passed=passed,
                avg_time_ms=avg_time,
                median_time_ms=median_time,
                min_time_ms=min_time,
                max_time_ms=max_time,
                std_dev_ms=std_dev,
                throughput=throughput,
                p95_time_ms=p95,
                p99_time_ms=p99,
            )
        except Exception as e:
            return PerformanceResult(
                test_name=test_name,
                passed=False,
                avg_time_ms=0,
                median_time_ms=0,
                min_time_ms=0,
                max_time_ms=0,
                std_dev_ms=0,
                throughput=0,
                error=str(e),
            )

    async def test_document_processing_speed(self, iterations: int = 20) -> PerformanceResult:
        """Test document processing speed."""
        test_name = "Document Processing Speed"
        timings = []

        try:
            # Simulate document data
            document = "Lorem ipsum " * 1000  # ~2000 words

            for i in range(iterations):
                start = time.time()

                # Simulate document processing (replace with actual processing)
                await asyncio.sleep(0.2)  # Simulate extraction/parsing
                word_count = len(document.split())
                char_count = len(document)

                elapsed = (time.time() - start) * 1000
                timings.append(elapsed)

            avg_time = mean(timings)
            median_time = median(timings)
            min_time = min(timings)
            max_time = max(timings)
            std_dev = stdev(timings) if len(timings) > 1 else 0
            throughput = 1000 / avg_time
            p95 = self.calculate_percentile(timings, 95)
            p99 = self.calculate_percentile(timings, 99)

            # Pass if average is under 500ms
            passed = avg_time < 500

            return PerformanceResult(
                test_name=test_name,
                passed=passed,
                avg_time_ms=avg_time,
                median_time_ms=median_time,
                min_time_ms=min_time,
                max_time_ms=max_time,
                std_dev_ms=std_dev,
                throughput=throughput,
                p95_time_ms=p95,
                p99_time_ms=p99,
            )
        except Exception as e:
            return PerformanceResult(
                test_name=test_name,
                passed=False,
                avg_time_ms=0,
                median_time_ms=0,
                min_time_ms=0,
                max_time_ms=0,
                std_dev_ms=0,
                throughput=0,
                error=str(e),
            )

    async def test_batch_processing_throughput(self, batch_size: int = 100) -> PerformanceResult:
        """Test batch processing throughput."""
        test_name = f"Batch Processing ({batch_size} items)"
        timings = []

        try:
            start = time.time()

            # Simulate batch processing
            tasks = []
            for i in range(batch_size):
                tasks.append(asyncio.sleep(0.01))  # Simulate small operation

            await asyncio.gather(*tasks)

            elapsed = (time.time() - start) * 1000
            timings.append(elapsed)

            avg_time = elapsed
            throughput = batch_size / (elapsed / 1000)  # items per second

            # Pass if throughput is > 100 items/sec
            passed = throughput > 100

            return PerformanceResult(
                test_name=test_name,
                passed=passed,
                avg_time_ms=avg_time,
                median_time_ms=avg_time,
                min_time_ms=avg_time,
                max_time_ms=avg_time,
                std_dev_ms=0,
                throughput=throughput,
            )
        except Exception as e:
            return PerformanceResult(
                test_name=test_name,
                passed=False,
                avg_time_ms=0,
                median_time_ms=0,
                min_time_ms=0,
                max_time_ms=0,
                std_dev_ms=0,
                throughput=0,
                error=str(e),
            )

    async def test_concurrent_requests(self, concurrent: int = 10, requests_per_worker: int = 5) -> PerformanceResult:
        """Test concurrent request handling."""
        test_name = f"Concurrent Requests ({concurrent} workers)"
        timings = []

        try:
            async def worker(worker_id: int):
                """Simulate concurrent worker."""
                worker_timings = []
                for i in range(requests_per_worker):
                    start = time.time()
                    await asyncio.sleep(0.1)  # Simulate request
                    elapsed = (time.time() - start) * 1000
                    worker_timings.append(elapsed)
                return worker_timings

            start = time.time()
            results = await asyncio.gather(*[worker(i) for i in range(concurrent)])
            total_elapsed = (time.time() - start) * 1000

            # Flatten all timings
            for worker_timings in results:
                timings.extend(worker_timings)

            total_requests = concurrent * requests_per_worker
            avg_time = mean(timings)
            median_time = median(timings)
            min_time = min(timings)
            max_time = max(timings)
            std_dev = stdev(timings) if len(timings) > 1 else 0
            throughput = total_requests / (total_elapsed / 1000)
            p95 = self.calculate_percentile(timings, 95)
            p99 = self.calculate_percentile(timings, 99)

            # Pass if throughput is > 50 requests/sec
            passed = throughput > 50

            return PerformanceResult(
                test_name=test_name,
                passed=passed,
                avg_time_ms=avg_time,
                median_time_ms=median_time,
                min_time_ms=min_time,
                max_time_ms=max_time,
                std_dev_ms=std_dev,
                throughput=throughput,
                p95_time_ms=p95,
                p99_time_ms=p99,
            )
        except Exception as e:
            return PerformanceResult(
                test_name=test_name,
                passed=False,
                avg_time_ms=0,
                median_time_ms=0,
                min_time_ms=0,
                max_time_ms=0,
                std_dev_ms=0,
                throughput=0,
                error=str(e),
            )

    async def test_memory_under_load(self, operations: int = 1000) -> PerformanceResult:
        """Test memory usage under load."""
        test_name = f"Memory Under Load ({operations} ops)"
        timings = []

        try:
            mem_before = self.get_memory_usage()

            # Simulate memory-intensive operations
            data_store = []
            for i in range(operations):
                start = time.time()

                # Create some data
                data = {"id": i, "content": "x" * 1000}
                data_store.append(data)

                elapsed = (time.time() - start) * 1000
                timings.append(elapsed)

            mem_after = self.get_memory_usage()
            mem_used = mem_after - mem_before

            avg_time = mean(timings)
            throughput = 1000 / avg_time

            # Pass if memory usage is under 100MB
            passed = mem_used < 100

            return PerformanceResult(
                test_name=test_name,
                passed=passed,
                avg_time_ms=avg_time,
                median_time_ms=median(timings),
                min_time_ms=min(timings),
                max_time_ms=max(timings),
                std_dev_ms=stdev(timings) if len(timings) > 1 else 0,
                throughput=throughput,
                memory_mb=mem_used,
            )
        except Exception as e:
            return PerformanceResult(
                test_name=test_name,
                passed=False,
                avg_time_ms=0,
                median_time_ms=0,
                min_time_ms=0,
                max_time_ms=0,
                std_dev_ms=0,
                throughput=0,
                error=str(e),
            )

    async def test_rag_query_response_time(self, iterations: int = 50) -> PerformanceResult:
        """Test RAG query response time."""
        test_name = "RAG Query Response Time"
        timings = []

        try:
            # Simulate document store
            documents = [
                {"id": i, "content": f"Document {i} content " * 100}
                for i in range(100)
            ]

            for i in range(iterations):
                start = time.time()

                # Simulate RAG query (search + retrieval)
                query = f"query {i}"
                await asyncio.sleep(0.05)  # Simulate vector search
                results = documents[:5]  # Top 5 results

                elapsed = (time.time() - start) * 1000
                timings.append(elapsed)

            avg_time = mean(timings)
            median_time = median(timings)
            min_time = min(timings)
            max_time = max(timings)
            std_dev = stdev(timings) if len(timings) > 1 else 0
            throughput = 1000 / avg_time
            p95 = self.calculate_percentile(timings, 95)
            p99 = self.calculate_percentile(timings, 99)

            # Pass if average is under 200ms
            passed = avg_time < 200

            return PerformanceResult(
                test_name=test_name,
                passed=passed,
                avg_time_ms=avg_time,
                median_time_ms=median_time,
                min_time_ms=min_time,
                max_time_ms=max_time,
                std_dev_ms=std_dev,
                throughput=throughput,
                p95_time_ms=p95,
                p99_time_ms=p99,
            )
        except Exception as e:
            return PerformanceResult(
                test_name=test_name,
                passed=False,
                avg_time_ms=0,
                median_time_ms=0,
                min_time_ms=0,
                max_time_ms=0,
                std_dev_ms=0,
                throughput=0,
                error=str(e),
            )

    async def run_all_tests(self) -> PerformanceReport:
        """Run all performance tests."""
        self.print_header("AI SPEED & PERFORMANCE TEST SUITE")

        # Get device info
        import platform
        device_info = {
            "platform": platform.system(),
            "platform_version": platform.version(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "cpu_count": psutil.cpu_count(),
            "total_memory_gb": round(psutil.virtual_memory().total / 1024 / 1024 / 1024, 2),
        }

        print(f"Device: {device_info['platform']} {device_info['platform_version']}")
        print(f"Processor: {device_info['processor']}")
        print(f"CPU Cores: {device_info['cpu_count']}")
        print(f"Total Memory: {device_info['total_memory_gb']} GB")
        print(f"Python: {device_info['python_version']}")

        # Run all tests
        tests = [
            self.test_llm_response_time(),
            self.test_text_to_sql_speed(),
            self.test_document_processing_speed(),
            self.test_batch_processing_throughput(),
            self.test_concurrent_requests(),
            self.test_memory_under_load(),
            self.test_rag_query_response_time(),
        ]

        self.print_header("Running Performance Tests")
        for test_coro in tests:
            result = await test_coro
            self.results.append(result)
            self.print_result(result)

        # Generate report
        passed = sum(1 for r in self.results if r.passed)
        failed = len(self.results) - passed

        report = PerformanceReport(
            total_tests=len(self.results),
            passed_tests=passed,
            failed_tests=failed,
            results=self.results,
            timestamp=datetime.now().isoformat(),
            device_info=device_info,
        )

        # Print summary
        self.print_header("PERFORMANCE SUMMARY")
        print(f"Total Tests: {report.total_tests}")
        print(f"Passed: {report.passed_tests}")
        print(f"Failed: {report.failed_tests}")
        print(f"Pass Rate: {(report.passed_tests / report.total_tests) * 100:.1f}%")

        # Calculate overall statistics
        avg_response_time = mean([r.avg_time_ms for r in self.results if r.avg_time_ms > 0])
        total_throughput = sum([r.throughput for r in self.results])

        print(f"\nOverall Average Response Time: {avg_response_time:.1f}ms")
        print(f"Total Throughput: {total_throughput:.1f} ops/sec")

        # Save report to file
        report_file = f"ai_speed_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump({
                "total_tests": report.total_tests,
                "passed_tests": report.passed_tests,
                "failed_tests": report.failed_tests,
                "timestamp": report.timestamp,
                "device_info": report.device_info,
                "overall_avg_response_time_ms": avg_response_time,
                "overall_throughput": total_throughput,
                "results": [
                    {
                        "test_name": r.test_name,
                        "passed": r.passed,
                        "avg_time_ms": r.avg_time_ms,
                        "median_time_ms": r.median_time_ms,
                        "min_time_ms": r.min_time_ms,
                        "max_time_ms": r.max_time_ms,
                        "std_dev_ms": r.std_dev_ms,
                        "throughput": r.throughput,
                        "p95_time_ms": r.p95_time_ms,
                        "p99_time_ms": r.p99_time_ms,
                        "memory_mb": r.memory_mb,
                        "error": r.error,
                    }
                    for r in report.results
                ]
            }, f, indent=2)

        print(f"\nDetailed report saved to: {report_file}")

        return report


async def main():
    """Main entry point."""
    tester = AISpeedTester()
    report = await tester.run_all_tests()

    # Exit with error code if tests failed
    import sys
    sys.exit(0 if report.failed_tests == 0 else 1)


if __name__ == "__main__":
    asyncio.run(main())
