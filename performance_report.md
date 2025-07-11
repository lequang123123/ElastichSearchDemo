# Performance Test Report

## Test Summary
- **Test Date**: 2025-07-11 13:04:41
- **Total Requests**: 150
- **Test Duration**: 2.73 seconds
- **Success Rate**: 100.00%

## Overall Performance Metrics

### Response Time Statistics
- **Average**: 14.69 ms
- **Median**: 8.00 ms
- **Minimum**: 1.00 ms
- **Maximum**: 57.00 ms
- **Standard Deviation**: 14.85 ms

### Throughput
- **Requests per Second**: 54.97 req/s

## Per-Endpoint Analysis

### Health Check
- **Request Count**: 50
- **Success Rate**: 100.00%
- **Average Response Time**: 18.00 ms
- **Median Response Time**: 9.50 ms
- **Min Response Time**: 2.00 ms
- **Max Response Time**: 50.00 ms

### Get User by ID
- **Request Count**: 50
- **Success Rate**: 100.00%
- **Average Response Time**: 17.12 ms
- **Median Response Time**: 8.50 ms
- **Min Response Time**: 1.00 ms
- **Max Response Time**: 57.00 ms

### Get All Users
- **Request Count**: 50
- **Success Rate**: 100.00%
- **Average Response Time**: 8.96 ms
- **Median Response Time**: 6.50 ms
- **Min Response Time**: 1.00 ms
- **Max Response Time**: 48.00 ms

## JMeter Statistics

| Endpoint | Sample Count | Error Count | Error % | Mean Response Time | Throughput |
|----------|--------------|-------------|---------|-------------------|------------|
| Health Check | 50 | 0 | 0.00% | 18.00 ms | 18.35 req/s |
| Get All Users | 50 | 0 | 0.00% | 8.96 ms | 18.59 req/s |
| Get User by ID | 50 | 0 | 0.00% | 17.12 ms | 18.29 req/s |

## Performance Recommendations

### Based on the test results:

1. **Response Time Analysis**:
   - All endpoints show good response times under 100ms
   - Health check endpoint is the fastest
   - Get All Users endpoint handles larger data sets efficiently

2. **Throughput Analysis**:
   - System can handle approximately 55.0 requests per second
   - No errors detected during testing

3. **Recommendations**:
   - System performance is good for the current load
   - Consider monitoring under higher concurrent loads
   - Implement caching for frequently accessed data
   - Consider database optimization for larger datasets

## Test Configuration
- **Thread Count**: 5
- **Ramp-up Time**: 2 seconds
- **Loop Count**: 3
- **Total Virtual Users**: 15

## Charts and Visualizations
- Performance overview charts saved to `performance_charts/performance_overview.png`
- Detailed analysis charts saved to `performance_charts/detailed_analysis.png`

---
*Report generated on 2025-07-11 13:04:41*
