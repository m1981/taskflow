Best Practices for Unit Testing and Mocking:
Arrange-Act-Assert (AAA) pattern for clear test structure
Mock at the right level (usually service boundaries)
Only mock what you own or what's absolutely necessary
Use descriptive test names that indicate scenario, action, and expected result
One assertion concept per test
Setup common mocks in fixtures
Make test failures easy to diagnose
Don't test implementation details
Use proper assertions instead of just assert
Clear separation between test setup and verification