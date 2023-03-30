# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2023-03-29

- Add Makefile with, lint, build and publish targets

Added a authenication/configuration code path to publish to s3, using boto client
User should overwrite ship() and use method SHIPPING_AUTH_S3_USERPASS along with:
- _get_rh_bucket
- _get_rh_region
- _get_rh_user
- _get_rh_password

## [0.2.0] - 2022-08-22

Fix saving gathered timestamps

## [0.1.1] - 2022-04-29

Support mTLS for ingress upload of metrics data #7

## [0.1.0] - 2022-04-27

Data collection status CSV #5

## [0.0.3] - 2022-04-01

Fix update last_gathered_entries #3

## [0.0.2] - 2022-03-29

Fixing tests #2

## [0.0.1] - 2022-03-28

Initial release to pypi.org

[Unreleased]: https://github.com/RedHatInsights/insights-analytics-collector/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/RedHatInsights/insights-analytics-collector/releases/v0.2.0
[0.1.1]: https://github.com/RedHatInsights/insights-analytics-collector/releases/v0.1.1
[0.1.0]: https://github.com/RedHatInsights/insights-analytics-collector/releases/v0.1.0
[0.0.3]: https://github.com/RedHatInsights/insights-analytics-collector/releases/v0.0.3
