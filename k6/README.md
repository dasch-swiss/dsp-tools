# DSP-TOOLS Performance Testing

This directory contains performance tests for DSP-TOOLS.

To run the tests, you need to build [xk6](https://k6.io/docs/extensions/#xk6-makes-custom-binaries)
with the [xk6-exec](https://github.com/grafana/xk6-exec) extension which requires you to have
[just](#using-just) and [docker](https://www.docker.com/) installed:

```sh
just build-xk6
```

The binary is installed into `./bin/k6`.

## Running the tests

You can run the tests using the following command:

```sh
./bin/k6 run tests/<test_script.js>
```

### Using `just`

We provide a `justfile` to make it easier to run the tests.
If you don't have [`just`](https://just.systems/man/en/) installed, you can install it using brew:

```sh
brew install just
```

Listing all the available tests:

```sh
just list
```

You can run the tests locally using the following command:

```sh
just run <test_name>
```

You can run the tests locally and then upload the results to
[Grafana Cloud k6](https://grafana.com/docs/grafana-cloud/testing/k6/) using the following command:

```sh
K6_CLOUD_PROJECT_ID=<project_id> just run-and-upload <test_name>
```

For uploading the data to the cloud you [need to login](https://grafana.com/docs/k6/latest/results-output/real-time/cloud/#instructions).

## Documentation

- [k6: Types of Load Testing](https://grafana.com/load-testing/types-of-load-testing/)
- [k6: Official Tutorial](https://k6.io/docs/examples/tutorials/get-started-with-k6/)
- [k6: More resources](https://k6.io/docs/get-started/resources/)
- [k6: Create Custom Metrics](https://k6.io/docs/using-k6/metrics/create-custom-metrics/)
- [GitHub: k6-learn, a nice Tutorial](https://github.com/grafana/k6-learn/blob/main/Modules/II-k6-Foundations/01-Getting-started-with-k6-OSS.md)
