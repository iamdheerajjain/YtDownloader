# Test Plan and Validation Procedures

This document outlines the test cases and validation procedures for ensuring the correctness and reliability of the CI/CD pipeline and application.

## Test Environment Setup

### Prerequisites

1. Python 3.6 or higher
2. Docker
3. Kubernetes cluster (for integration tests)
4. Jenkins server (for pipeline tests)

### Environment Variables

Set the following environment variables for testing:

```bash
export PYTHONPATH="${PYTHONPATH}:/path/to/project/app"
export FLASK_APP=main.py
```

## Unit Tests

### Running Unit Tests

```bash
# Install dependencies
pip install -r app/requirements.txt

# Run all tests
python -m pytest tests/ -v

# Run specific test
python -m pytest tests/test_basic.py::test_home_endpoint -v
```

### Test Cases

#### 1. Application Import Test

- **Test**: Verify that the main application module can be imported
- **File**: [test_basic.py](file:///home/prakuljain/yt/tests/test_basic.py)
- **Function**: `test_import_main`
- **Expected Result**: Module imports without errors

#### 2. Home Endpoint Test

- **Test**: Verify the home endpoint returns correct information
- **File**: [test_basic.py](file:///home/prakuljain/yt/tests/test_basic.py)
- **Function**: `test_home_endpoint`
- **Expected Result**: HTTP 200 with JSON containing app information

#### 3. Health Endpoint Test

- **Test**: Verify the health endpoint returns correct status
- **File**: [test_basic.py](file:///home/prakuljain/yt/tests/test_basic.py)
- **Function**: `test_health_endpoint`
- **Expected Result**: HTTP 200 with JSON containing "UP" status

#### 4. Readiness Endpoint Test

- **Test**: Verify the readiness endpoint checks dependencies
- **File**: [test_basic.py](file:///home/prakuljain/yt/tests/test_basic.py)
- **Function**: `test_ready_endpoint`
- **Expected Result**: HTTP 200 with JSON containing readiness status

#### 5. Video Info Endpoint Test

- **Test**: Verify the video info endpoint processes requests correctly
- **File**: [test_basic.py](file:///home/prakuljain/yt/tests/test_basic.py)
- **Function**: `test_info_endpoint`
- **Expected Result**:
  - HTTP 200 with video information for valid requests
  - HTTP 400 for missing URL

#### 6. Download Endpoint Test

- **Test**: Verify the download endpoint processes requests correctly
- **File**: [test_basic.py](file:///home/prakuljain/yt/tests/test_basic.py)
- **Function**: `test_download_endpoint`
- **Expected Result**:
  - HTTP 200 with download information for valid requests
  - HTTP 400 for missing URL

## Integration Tests

### Docker Build Test

```bash
# Build the Docker image
docker build -t yt-downloader:test .

# Run the container
docker run -d -p 8080:8080 --name yt-test yt-downloader:test

# Test the endpoints
curl http://localhost:8080/
curl http://localhost:8080/health
curl http://localhost:8080/ready

# Clean up
docker stop yt-test
docker rm yt-test
```

### Kubernetes Deployment Test

```bash
# Apply manifests
kubectl apply -f k8s/

# Check deployment status
kubectl rollout status deployment/youtube-api

# Check pods
kubectl get pods -l app=youtube-api

# Check services
kubectl get svc youtube-api

# Test endpoints
kubectl port-forward svc/youtube-api 8080:80 &
curl http://localhost:8080/
curl http://localhost:8080/health
curl http://localhost:8080/ready

# Clean up
kill %1  # Kill port-forward process
kubectl delete -f k8s/
```

## Pipeline Validation

### Jenkins Pipeline Test

1. **Checkout Stage**

   - Verify code is properly checked out from repository
   - Check Git information is displayed correctly

2. **Code Quality Stage**

   - Verify flake8 runs without errors
   - Verify bandit security scan completes

3. **Unit Test Stage**

   - Verify all unit tests pass
   - Check test results are properly reported

4. **Docker Build Stage**

   - Verify Docker image builds successfully
   - Check image is tagged correctly

5. **Security Scan Stage**

   - Verify dependency scanning tools run
   - Check Docker image scanning (if Trivy is available)

6. **Push Image Stage**

   - Verify image is pushed to registry
   - Check credentials are properly handled

7. **Deploy to Kubernetes Stage**

   - Verify Kubernetes manifests are applied
   - Check deployment rollout status
   - Verify HPA is applied

8. **Health Check Stage**
   - Verify pods are running
   - Check service endpoints are available

### Parameter Testing

Test pipeline with different parameter combinations:

1. **Default Parameters**

   - DEPLOY_ENVIRONMENT: development
   - RUN_TESTS: true
   - SKIP_DEPLOYMENT: false

2. **Skip Tests**

   - DEPLOY_ENVIRONMENT: development
   - RUN_TESTS: false
   - SKIP_DEPLOYMENT: false

3. **Skip Deployment**

   - DEPLOY_ENVIRONMENT: development
   - RUN_TESTS: true
   - SKIP_DEPLOYMENT: true

4. **Production Environment**
   - DEPLOY_ENVIRONMENT: production
   - RUN_TESTS: true
   - SKIP_DEPLOYMENT: false

## Performance Tests

### Load Testing

Use a tool like Apache Bench or Locust to test performance:

```bash
# Example with Apache Bench
ab -n 1000 -c 10 http://localhost:8080/health
```

### Resource Usage Monitoring

Monitor resource usage during load:

- CPU and memory usage
- Response times
- Error rates

## Security Tests

### Dependency Scanning

```bash
# Run safety check
safety check -r app/requirements.txt

# Run pip-audit
pip-audit -r app/requirements.txt
```

### Container Scanning

If Trivy is available:

```bash
trivy image --exit-code 0 --severity HIGH,CRITICAL yt-downloader:test
```

## Monitoring and Logging Tests

### Prometheus Metrics

Verify metrics are exposed correctly:

```bash
curl http://localhost:8080/metrics
```

Check for specific metrics:

- `download_requests_total`
- `download_duration_seconds`
- `health_check_requests_total`
- `active_requests`
- `app_info`

### Log Validation

Check application logs for:

- Proper log levels (INFO, ERROR, DEBUG)
- Request logging
- Error logging
- Startup messages

## Test Reporting

### Test Results Collection

Jenkins will automatically collect and display test results:

- Unit test results
- Code quality reports
- Security scan results
- Deployment status

### Test Metrics

Track the following metrics over time:

- Test pass/fail rates
- Code coverage (when implemented)
- Security vulnerabilities
- Deployment success rates
- Performance metrics

## Continuous Improvement

### Test Coverage Expansion

Planned future test additions:

1. Integration tests with actual YouTube API
2. End-to-end tests with real video downloads
3. Chaos engineering tests
4. Load and stress tests
5. Security penetration tests

### Test Automation

Ensure all tests are automated and run:

1. On every commit (unit tests)
2. On pull requests (integration tests)
3. Periodically (security scans, performance tests)
4. Before production deployments (full suite)
