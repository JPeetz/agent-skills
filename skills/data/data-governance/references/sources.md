# Sources

Authoritative references for the `data-governance` skill. Prefer primary sources (specs, vendor docs, regulation text) over blog summaries; vendor marketing pages drift fastest.

## Frameworks and bodies of knowledge

| Source | Why it matters |
|---|---|
| [DAMA-DMBOK (DAMA International)](https://www.dama.org/cpages/body-of-knowledge) | Canonical governance knowledge areas: metadata, quality, master/reference data, stewardship |
| [NIST Privacy Framework](https://www.nist.gov/privacy-framework) | Risk-based privacy engineering; useful for DPIA structure |
| [EDPB guidelines & recommendations](https://www.edpb.europa.eu/our-work-tools/general-guidance/guidelines-recommendations-best-practices_en) | Authoritative EU interpretation of GDPR obligations |
| [OpenLineage spec](https://openlineage.io/docs/) | Vendor-neutral lineage event model; the interchange format to standardise on |
| [Data Governance: The Definitive Guide (O'Reilly)](https://www.oreilly.com/library/view/data-governance-the/9781492063483/) | Operating-model patterns, roles, and program rollout |

## Catalogs and metadata platforms

| Source | Why it matters |
|---|---|
| [DataHub docs](https://docs.datahub.com/docs/) | Ingestion recipes, GraphQL API, lineage queries, tags/glossary/domains model |
| [Atlan docs](https://docs.atlan.com/) | Bulk entity API, glossary and tag propagation, auto-classification |
| [Amundsen](https://www.amundsen.io/) | Databuilder extraction jobs, Neo4j/Elasticsearch backend model |
| [OpenMetadata docs](https://docs.open-metadata.org/) | Alternative catalog with strong column-lineage and data-quality integration |
| [dbt `meta` reference](https://docs.getdbt.com/reference/resource-properties/meta) | Where owner/tier/classification/retention metadata should live |
| [dbt exposures](https://docs.getdbt.com/docs/build/exposures) | Declaring dashboards/ML consumers so lineage reaches the BI layer |

## Data quality

| Source | Why it matters |
|---|---|
| [Great Expectations docs](https://docs.greatexpectations.io/docs/) | Expectation suites, 1.x data-source/asset/batch API, checkpoints |
| [Soda docs](https://docs.soda.io/) | SodaCL check syntax, freshness and schema-evolution checks |
| [dbt data tests](https://docs.getdbt.com/docs/build/data-tests) | Generic/singular tests, severity thresholds, `store_failures` |
| [Elementary](https://docs.elementary-data.com/) | dbt-native anomaly monitoring and quality reporting |
| [Monte Carlo — data quality dimensions](https://www.montecarlodata.com/blog-data-quality-dimensions/) | Practical definitions of completeness, accuracy, timeliness, etc. |

## Classification, masking, access

| Source | Why it matters |
|---|---|
| [Microsoft Presidio](https://microsoft.github.io/presidio/) | Open-source PII detection and anonymisation for the detect step |
| [Snowflake masking policies](https://docs.snowflake.com/en/sql-reference/sql/create-masking-policy) | Tag-based dynamic masking syntax used in §5.1 |
| [BigQuery column-level access control](https://cloud.google.com/bigquery/docs/column-level-security-intro) | Policy tags as the enforcement mechanism |
| [Databricks Unity Catalog](https://docs.databricks.com/en/data-governance/unity-catalog/index.html) | Column masks, row filters, tag-driven governance |
| [Snowflake object tagging](https://docs.snowflake.com/en/user-guide/object-tagging) | How classification tags propagate to columns and drive policy |

## Regulation and audit criteria

| Source | Why it matters |
|---|---|
| [GDPR full text (EUR-Lex)](https://eur-lex.europa.eu/eli/reg/2016/679/oj) | Primary text for Arts. 5, 6, 15–17, 28, 30, 32, 33/34, 35, 44+ |
| [ICO Guide to the GDPR](https://ico.org.uk/for-organisations/uk-gdpr-guidance-and-resources/) | Plain-language regulator guidance; retention and DSR practice |
| [CCPA / CPRA (California AG)](https://oag.ca.gov/privacy/ccpa) | Statutory text and consumer-rights scope |
| [AICPA & CIMA — SOC 2](https://www.aicpa-cima.com/topic/audit-assurance/audit-and-assurance-greater-than-soc-2) | Trust Services Criteria (CC6, CC7, P-series) and Type II evidence expectations |
| [NIST SP 800-53 (Privacy & Access Control families)](https://csrc.nist.gov/pubs/sp/800/53/r5/upd1/final) | Control catalogue when mapping beyond SOC 2 |

## Retention and deletion

| Source | Why it matters |
|---|---|
| [EDPB — storage limitation](https://www.edpb.europa.eu/our-work-tools/our-documents/guidelines/guidelines-032019-processing-personal-data-through-video_en) | Example of regulator reasoning on storage limitation and deletion triggers |
| [BigQuery partitioning & DML](https://cloud.google.com/bigquery/docs/managing-partitioned-tables) | Partition-drop purge pattern from §7.3 |
| [Snowflake Time Travel & fail-safe](https://docs.snowflake.com/en/user-guide/data-time-travel) | Why purge is not immediate, and the backup-window lag to document |

## Notes on currency

Regulation text and vendor APIs change; `evals/` and code samples are written against versions noted where relevant (GX 1.x, dbt 1.8+ `data_tests` key). When a link 404s, search the vendor docs site rather than trusting a mirror — catalogue APIs in particular rename endpoints between minor releases.
