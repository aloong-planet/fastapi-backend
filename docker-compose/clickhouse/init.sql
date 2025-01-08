CREATE DATABASE IF NOT EXISTS otel ON CLUSTER '{cluster}';

CREATE TABLE IF NOT EXISTS  otel.customers ON CLUSTER '{cluster}'(
    `customer_id` String CODEC(ZSTD(1)),
    `customer_name` String CODEC(ZSTD(1)),
    `region` LowCardinality(String) CODEC(ZSTD(1)),
    `level` LowCardinality(String) CODEC(ZSTD(1))
) ENGINE = ReplicatedMergeTree('/clickhouse/clusters/{cluster}/databases/{database}/tables/{table}/{shard}', '{replica}')
PARTITION BY region ORDER BY (region, level, customer_id)
SETTINGS index_granularity = 8192;

CREATE TABLE IF NOT EXISTS otel.dist_customers ON CLUSTER '{cluster}'
ENGINE = Distributed('{cluster}', 'otel', 'customers', rand());
