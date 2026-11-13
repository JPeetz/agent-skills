# Sources — Data Pipeline Engineering

Authoritative references for the claims, defaults, and configuration snippets in `SKILL.md`.
Version-sensitive claims were written against the 2026 releases of each tool; upstream docs
win if they conflict.

## Orchestration

| Topic | Source |
|---|---|
| Airflow DAG authoring, decorators, scheduling | https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dags.html |
| Airflow datasets / asset scheduling (`outlets`, `inlets`) | https://airflow.apache.org/docs/apache-airflow/stable/authoring-and-scheduling/datasets.html |
| Airflow backfill and clearing task instances | https://airflow.apache.org/docs/apache-airflow/stable/core-concepts/dag-run.html |
| Airflow best practices (idempotency, `max_active_runs`, retries) | https://airflow.apache.org/docs/apache-airflow/stable/best-practices.html |
| Dagster assets and partitions | https://docs.dagster.io/guides/build/partitions-and-backfills/partitioning-assets |
| Dagster backfills (partition-based, lineage-aware) | https://docs.dagster.io/guides/build/partitions-and-backfills/backfilling-data |
| Dagster vs Airflow (official comparison) | https://dagster.io/vs/dagster-vs-airflow |
| Prefect flows, tasks, retries | https://docs.prefect.io/v3/develop/write-flows |
| Prefect deployments and scheduling | https://docs.prefect.io/v3/deploy/ |

## Streaming

| Topic | Source |
|---|---|
| Kafka producer idempotence and `enable.idempotence` | https://kafka.apache.org/documentation/#producerconfigs_enable.idempotence |
| Kafka exactly-once semantics (transactions, `isolation.level`) | https://kafka.apache.org/documentation/#semantics |
| Kafka consumer group rebalancing and offset commits | https://kafka.apache.org/documentation/#consumerconfigs |
| Log compaction (key-based retention for re-readable state) | https://kafka.apache.org/documentation/#compaction |
| Spark Structured Streaming exactly-once / checkpointing | https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html#fault-tolerance-semantics |
| Spark `trigger(availableNow=True)` (micro-batch over backlog) | https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html#triggers |
| Confluent Schema Registry compatibility modes | https://docs.confluent.io/platform/current/schema-registry/fundamentals/schema-evolution.html |
| Debezium change event envelope (`op`, `before`, `after`) | https://debezium.io/documentation/reference/stable/connectors/postgresql.html#postgresql-change-events |

## Warehouses

| Topic | Source |
|---|---|
| BigQuery partitioned tables, partition filter requirement | https://cloud.google.com/bigquery/docs/partitioned-tables |
| BigQuery clustered tables (limits: 4 clustering columns) | https://cloud.google.com/bigquery/docs/clustered-tables |
| BigQuery `MERGE` semantics | https://cloud.google.com/bigquery/docs/reference/standard-sql/dml-syntax#merge_statement |
| BigQuery `maximum_bytes_billed` cost control | https://cloud.google.com/bigquery/docs/reference/standard-sql/query-syntax#maximum_bytes_billed |
| BigQuery `INFORMATION_SCHEMA.JOBS` (cost attribution) | https://cloud.google.com/bigquery/docs/information-schema-jobs |
| Snowflake clustering keys and clustering depth | https://docs.snowflake.com/en/user-guide/tables-clustering-keys |
| Snowflake `SYSTEM$CLUSTERING_INFORMATION` | https://docs.snowflake.com/en/sql-reference/functions/system_clustering_information |
| Snowflake `COPY INTO` error handling (`ON_ERROR`, `VALIDATION_MODE`) | https://docs.snowflake.com/en/sql-reference/sql/copy-into-table |
| Snowflake `ALTER TABLE ... SWAP WITH` (atomic replace) | https://docs.snowflake.com/en/sql-reference/sql/alter-table |
| Snowflake resource monitors | https://docs.snowflake.com/en/user-guide/resource-monitors |
| Redshift distribution styles | https://docs.aws.amazon.com/redshift/latest/dg/c_choosing_dist_sort.html |
| Redshift sort keys (compound vs interleaved) | https://docs.aws.amazon.com/redshift/latest/dg/c_best-practices-sort-key.html |
| Redshift VACUUM and `SVV_TABLE_INFO` | https://docs.aws.amazon.com/redshift/latest/dg/r_SVV_TABLE_INFO.html |
| Redshift `STL_ALERT_EVENT_LOG` (query alerts) | https://docs.aws.amazon.com/redshift/latest/dg/r_STL_ALERT_EVENT_LOG.html |

## Modeling, Quality, and Contracts

| Topic | Source |
|---|---|
| dbt incremental models and `is_incremental()` | https://docs.getdbt.com/docs/build/incremental-models |
| dbt `unique` / `not_null` tests and severity | https://docs.getdbt.com/docs/build/data-tests |
| dbt model contracts | https://docs.getdbt.com/docs/collaborate/govern/model-contracts |
| Great Expectations checkpoints and expectations | https://docs.greatexpectations.io/docs/core/introduction/try_gx |
| Soda checks (freshness, volume, schema) | https://docs.soda.io/soda-core/overview-main.html |
| OpenLineage spec (run/Job/Dataset events) | https://openlineage.io/docs/spec/object-model |
| Data Contract CLI / spec | https://datacontract.com/ |
| Medallion (bronze/silver/gold) architecture | https://docs.databricks.com/aws/en/lakehouse/medallion |

## Design and Theory

| Topic | Source |
|---|---|
| Kappa vs Lambda architecture | Jay Kreps, "Questioning the Lambda Architecture" — https://www.oreilly.com/radar/questioning-the-lambda-architecture/ |
| Idempotency in distributed data processing | https://en.wikipedia.org/wiki/Idempotence#Computer_science |
| Slowly changing dimensions (Type 1/2/3) | Kimball Group, https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/ |
| The Data Engineering Cookbook (pipeline patterns) | https://github.com/andkret/Cookbook |
| Awesome Data Engineering (tool index) | https://github.com/igorbarinov/awesome-data-engineering |

## Debugging Aids

| Topic | Source |
|---|---|
| Airflow task failure / scheduler health | https://airflow.apache.org/docs/apache-airflow/stable/administration-and-deployment/logging-monitoring/check-health.html |
| Snowflake `QUERY_HISTORY` | https://docs.snowflake.com/en/sql-reference/account-usage/query_history |
| Redshift `STL_WLM_QUERY` (queue time) | https://docs.aws.amazon.com/redshift/latest/dg/r_STL_WLM_QUERY.html |
| Spark UI / streaming query progress metrics | https://spark.apache.org/docs/latest/web-ui.html |
