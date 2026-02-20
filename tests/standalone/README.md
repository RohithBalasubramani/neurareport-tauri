# Standalone AI Testing Suite

These standalone test files allow you to test AI capabilities on any device for accuracy and speed. They are designed to be easily copied, pasted, and run without complex setup.

## Test Files

### 1. `ai_accuracy_test.py` - AI Accuracy Tests
Tests the accuracy of various AI capabilities:
- LLM Basic Reasoning
- Text-to-SQL Generation Accuracy
- Data Analysis Accuracy
- Sentiment Analysis Accuracy
- RAG Document Retrieval Accuracy
- Content Generation Quality
- Multi-Agent Coordination

### 2. `ai_speed_test.py` - AI Speed & Performance Tests
Tests the speed and performance of AI operations:
- LLM Response Time
- Text-to-SQL Generation Speed
- Document Processing Speed
- Batch Processing Throughput
- Concurrent Request Handling
- Memory Usage Under Load
- RAG Query Response Time

## Prerequisites

### Required Python Packages
```bash
pip install psutil
```

That's it! Both test files are designed to run with minimal dependencies.

## How to Run

### Run Accuracy Tests
```bash
python ai_accuracy_test.py
```

### Run Speed Tests
```bash
python ai_speed_test.py
```

### Run Both Tests
```bash
python ai_accuracy_test.py && python ai_speed_test.py
```

## Output

Both tests will:
1. Display real-time progress in the terminal
2. Show a summary of results at the end
3. Generate a detailed JSON report file with timestamp

### Accuracy Test Output
- `ai_accuracy_report_YYYYMMDD_HHMMSS.json` - Detailed accuracy metrics

### Speed Test Output
- `ai_speed_report_YYYYMMDD_HHMMSS.json` - Detailed performance metrics

## Understanding Results

### Accuracy Test Results
- **Passed/Failed**: Whether the test met the accuracy threshold
- **Accuracy Score**: 0.0 to 1.0 (0% to 100%)
- **Expected vs Actual**: What was expected and what was actually produced
- **Average Accuracy**: Overall accuracy across all tests

### Speed Test Results
- **Avg Time**: Average response time in milliseconds
- **Median Time**: Median response time
- **Min/Max Time**: Fastest and slowest response times
- **Throughput**: Operations per second
- **P95/P99**: 95th and 99th percentile response times
- **Memory Usage**: Memory consumed during operations

## Customizing Tests

You can modify the test parameters by editing the source files:

### Accuracy Tests
```python
# Modify iterations or test data
tester = AIAccuracyTester(base_url="http://your-api-url:8000")
```

### Speed Tests
```python
# Modify iterations, batch size, concurrency
await tester.test_llm_response_time(iterations=100)  # Default: 50
await tester.test_concurrent_requests(concurrent=20)  # Default: 10
```

## Pass/Fail Criteria

### Accuracy Tests
- **LLM Reasoning**: Must produce correct answer
- **Text-to-SQL**: Must include 80%+ expected keywords
- **Data Analysis**: Must be within 1% margin of error
- **Sentiment Analysis**: Must achieve 80%+ accuracy
- **RAG Retrieval**: Must retrieve 50%+ relevant documents
- **Content Generation**: Must include 60%+ expected elements
- **Multi-Agent**: Must execute all steps

### Speed Tests
- **LLM Response**: < 500ms average
- **Text-to-SQL**: < 300ms average
- **Document Processing**: < 500ms average
- **Batch Processing**: > 100 items/sec
- **Concurrent Requests**: > 50 requests/sec
- **Memory Usage**: < 100MB for 1000 operations
- **RAG Query**: < 200ms average

## Integration with Real AI Services

To integrate these tests with your actual AI service:

1. Replace the simulated API calls with real API calls
2. Update the `base_url` parameter
3. Add authentication if needed

### Example: Replace Simulated LLM Call
```python
# Before (simulated)
await asyncio.sleep(0.1)
response = "The answer is 4"

# After (real API call)
import httpx
async with httpx.AsyncClient() as client:
    response = await client.post(
        f"{self.base_url}/api/llm/generate",
        json={"prompt": prompt}
    )
    result = response.json()
```

## Running on Different Devices

### Copy Files to Another Device
1. Copy both `.py` files to the target device
2. Ensure Python 3.8+ is installed
3. Install required packages: `pip install psutil`
4. Run the tests

### Comparing Results Across Devices
The JSON report files include device information:
- Platform and version
- Processor
- CPU cores
- Total memory
- Python version

You can compare these reports to see how AI performance varies across different hardware.

## Continuous Testing

You can run these tests periodically to monitor AI performance over time:

### Linux/Mac (Cron)
```bash
# Run tests daily at 2 AM
0 2 * * * cd /path/to/tests && python ai_accuracy_test.py && python ai_speed_test.py
```

### Windows (Task Scheduler)
Create a batch file `run_ai_tests.bat`:
```batch
@echo off
cd C:\path\to\tests
python ai_accuracy_test.py
python ai_speed_test.py
```

Schedule it to run at your desired frequency.

## Troubleshooting

### Import Error: No module named 'psutil'
```bash
pip install psutil
```

### Tests Run Too Slowly
Reduce the number of iterations:
```python
# In the source file
await tester.test_llm_response_time(iterations=10)  # Reduced from 50
```

### Memory Test Fails
Increase the memory threshold:
```python
# In ai_speed_test.py
passed = mem_used < 200  # Increased from 100MB
```

## Advanced Usage

### Running Specific Tests Only
Modify the `run_all_tests()` method to comment out tests you don't want to run:

```python
tests = [
    self.test_llm_response_time(),
    # self.test_text_to_sql_speed(),  # Commented out
    self.test_document_processing_speed(),
]
```

### Custom Reporting
The JSON reports can be parsed and analyzed with custom scripts:

```python
import json

with open('ai_accuracy_report_20260203_120000.json') as f:
    report = json.load(f)

print(f"Average Accuracy: {report['average_accuracy'] * 100:.1f}%")
for result in report['results']:
    print(f"{result['test_name']}: {result['accuracy_score'] * 100:.1f}%")
```

## Support

For issues or questions:
1. Check the error message in the terminal output
2. Review the JSON report files for detailed diagnostics
3. Ensure your Python version is 3.8 or higher
4. Verify all required packages are installed

## License

These test files are part of the NeuraReport project and follow the same license.
