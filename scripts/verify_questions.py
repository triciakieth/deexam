"""Apply manually reviewed explanations; keep the source key unchanged.
Only entries below have been checked against the retrieved official documentation.
Run after import_questions.py. Never infer a verified answer from the source key.
"""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
sources=json.loads((ROOT/'research/sources.json').read_text())
reviews={}
def add(qid,correct,doc,section,concept,tip,*explanations):
 refs=[]
 for key in doc.split(','):
  s=sources[key];assert 'error' not in s,(qid,key)
  refs.append({'title':s['title'].split(' | ')[0],'url':s['url'],'section':section,'support':concept,'retrieved':s['retrieved']})
 reviews[qid]={'verifiedAnswer':correct.split(','),'verification':'verified','explanations':dict(zip('abcde',explanations)),'references':refs,'keyConcept':concept,'examTip':tip}
add('b1-q1','b','lakehouse','What is a data lakehouse used for?',
 'A lakehouse lets engineering and analytics use a shared source of truth instead of maintaining inconsistent silos.',
 'When reports disagree because teams use separate data stores, look for shared data rather than faster compute.',
 'Autoscaling changes compute capacity; it does not make the two teams read the same data.',
 'A shared source of truth directly addresses reports diverging because engineering and analytics maintain separate architectures.',
 'A lakehouse is a data architecture; reorganizing reporting lines is not its mechanism for consistency.',
 'Real-time collaboration can help teams work together, but does not itself reconcile separate copies of reporting data.',
 'Faster ad hoc responses concern responsiveness; the problem here is consistency between separate reporting sources.')
add('b1-q4','d','delta,lakehouse','What is Delta Lake in Databricks?',
 'Delta Lake supports batch and streaming operations on a single copy of data.',
 'Separate storage-layer capabilities from notebook and compute features.',
 'Multiple programming languages are a notebook/Spark interface capability; they are not the distinctive storage guarantee supplied by Delta Lake.',
 'Collaborative notebook editing is a workspace feature, rather than a Delta Lake storage feature.',
 'Query failure alerts belong to monitoring and orchestration, not the Delta Lake storage layer.',
 'The Delta Lake overview explicitly describes tight Structured Streaming integration and using a single copy for batch and streaming operations.',
 'Distributing execution across compute resources is Spark’s role; Delta Lake adds transactional storage and metadata.')
add('b1-q5','c','delta','What is Delta Lake in Databricks?',
 'Delta tables use Parquet data files plus a file-based transaction log, rather than one all-in-one file.',
 'Distinguish a table directory with data and transaction metadata from an individual data file.',
 'A Delta table is not a single file containing everything; it consists of data files plus a transaction log.',
 'Although metadata is separate from data files, the table’s data is not restricted to one data file.',
 'A collection of files containing data and transaction metadata matches Delta’s Parquet files plus transaction log.',
 'Data-only files omit the transaction log and metadata needed for table versions and ACID behavior.',
 'A single data-only file omits both the multi-file data layout and the transaction metadata.')
add('b1-q6','c','delete','Syntax; Parameters — WHERE',
 'DELETE FROM removes rows matching its WHERE predicate from a Delta table.',
 'Translate “remove rows greater than 25” into DELETE with age > 25.',
 'SELECT reads the rows where age > 25; it does not remove or persist changes to those rows.',
 'UPDATE is for changing column values, and this statement supplies no SET assignment or delete operation.',
 'DELETE FROM my_table WHERE age > 25 removes exactly the requested rows and commits the table change.',
 'UPDATE neither deletes rows nor supplies a SET clause; its age <= 25 predicate also targets the opposite group.',
 'This DELETE targets ages 25 and below, which is the complement of the requested age > 25 condition.')
add('b1-q29','a','medallion','Power analytics with the gold layer',
 'Gold typically contains business-oriented aggregates built from cleaned, detailed Silver data.',
 'Gold is about reporting shape and aggregation, not a claim that other layers are less truthful.',
 'Gold commonly contains aggregates tailored to reporting, whereas Silver retains validated detailed records.',
 '“More valuable” is subjective and is not the documented distinction between these layers.',
 'Gold is highly refined for downstream use, rather than a less refined form of Silver.',
 'Aggregation often reduces row counts; Gold is not defined by containing more data than Silver.',
 'Silver is also validated and cleaned. Truthfulness is not the distinguishing property; business-ready aggregation is.')
add('b1-q31','b','auto-loader','How does Auto Loader work?',
 'Auto Loader exposes the cloudFiles source for Spark Structured Streaming.',
 'A checkpoint stores progress; Structured Streaming is the processing engine.',
 'Checkpointing tracks discovered files and recovery state, but is not the processing engine named by the Auto Loader documentation.',
 'Auto Loader provides a Structured Streaming source called cloudFiles, making Structured Streaming the incremental processing mechanism.',
 'Data Explorer is a catalog browsing interface, not an incremental file processing engine.',
 'Unity Catalog governs access to data; it does not implement Auto Loader’s streaming execution.',
 'Databricks SQL is a SQL analytics interface; the engine used by Auto Loader’s cloudFiles source is Structured Streaming.')
add('b1-q32','b','streaming','AvailableNow: Incremental batch processing',
 'AvailableNow processes the records available at the start of a run, using multiple micro-batches when needed.',
 '“All available data, as many batches as required” points to availableNow=True.',
 'processingTime(1) is neither the shown DataStreamWriter trigger syntax nor a bounded catch-up request.',
 'trigger(availableNow=True) performs bounded incremental processing of available data and supports batch sizing.',
 'parallelBatch is not a documented trigger option and cannot request AvailableNow processing.',
 'processingTime expects a time interval, not the string once, and describes periodic processing rather than a bounded catch-up.',
 'continuous="once" is not the supported bounded trigger. The documentation lists Continuous as unsupported on Databricks.')
add('b1-q34','d','medallion','Power analytics with the gold layer',
 'Gold tables are refined and often aggregated to serve dashboards and business analytics.',
 'Match the layer to what the consumer needs: raw ingestion, cleansing, or reporting.',
 'Parsing timestamps is a refinement operation, normally upstream of a report-ready Gold dataset.',
 'Aggregating uncleaned inputs bypasses the validated Silver stage; it is not a reason to read a Gold source.',
 'Removing malformed records is a cleansing operation associated with Silver, not consumption of Gold aggregates.',
 'A dashboard query over aggregated data is the documented downstream use of Gold tables.',
 'Raw streaming ingestion lands in Bronze, rather than using a business-ready Gold table as its source.')
add('b1-q35','b','expectations','Action on invalid record — Fail on invalid records',
 'ON VIOLATION FAIL UPDATE fails the affected flow update rather than silently retaining or dropping invalid rows.',
 'Read the violation action literally: fail, drop, and retain have different outcomes.',
 'Dropping invalid rows is the DROP ROW action, not the FAIL UPDATE action used here.',
 'FAIL UPDATE stops the affected flow when the expectation is violated. In this question’s update context, the processing fails; unrelated parallel flows need not stop.',
 'Quarantine requires a separately implemented routing pattern; FAIL UPDATE does not create a quarantine table.',
 'Keeping invalid rows and recording metrics corresponds to retaining invalid records, not FAIL UPDATE.',
 'This expectation does not add a per-row flag column; its configured violation action is to fail the update.')
add('b1-q36','d','medallion','Validate and deduplicate data in the silver layer',
 'Silver contains validated and cleaned data derived from raw Bronze inputs.',
 'Layer definitions describe data quality, not a guaranteed increase or decrease in row count.',
 'Silver improves data quality; it is not defined as less refined than Bronze.',
 'Some Silver aggregates are possible, but aggregation is not always present; Gold is the typical reporting aggregate layer.',
 'Joins, deduplication, filtering, and transformations can change row counts in either direction; more data is not guaranteed.',
 'A cleaner and more refined representation is the documented quality distinction between Silver and Bronze.',
 'Cleaning may reduce rows, but Silver is not guaranteed to have fewer rows; row count is not the layer’s definition.')
add('b1-q39','e','auto-loader','How does Auto Loader track ingestion progress?',
 'Auto Loader records file discovery progress in checkpoint state so subsequent runs can identify unprocessed files.',
 'When source files accumulate and only new ones should be ingested, look for incremental file discovery and checkpointing.',
 'Unity Catalog supplies governance, rather than tracking which input files this ingestion stream has processed.',
 'Delta Lake supplies transactional target storage, but by itself is not the file discovery ingestion tool requested here.',
 'Databricks SQL is a broad SQL service; this option does not specify an incremental discovery mechanism.',
 'Data Explorer browses data objects and metadata; it does not perform checkpointed file ingestion.',
 'Auto Loader discovers new cloud files and persists discovery state at its checkpoint, fitting repeated ingestion without deleting source files.')
add('b1-q68','c','git','Pull changes',
 'Pull updates a local Databricks Git folder with changes from the remote repository.',
 'Remote-to-local synchronization is Pull; local-to-remote publication is Push.',
 'Merge combines branches but does not itself fetch the latest remote changes into this checkout.',
 'Push sends local commits to the remote, the opposite direction from the requested synchronization.',
 'The documented Pull operation updates notebooks and files from the central remote repository.',
 'Commit records local changes and does not retrieve a colleague’s remote commits.',
 'Clone creates a new working copy; the engineer already has a repo that needs updating.')
add('b1-q76','e','lakehouse','What is a data lakehouse?',
 'A lakehouse combines the benefits of lakes and warehouses in one architecture for multiple workloads.',
 'A question about unifying specialist data silos points to a lakehouse architecture.',
 'A standalone data lake provides storage but does not by itself provide the combined warehouse and lake capabilities described.',
 'A warehouse serves structured analytics but alone does not unify the broader lake and warehouse workloads described.',
 'The alternatives do not all provide the combined architecture; a lakehouse is the specific pattern documented for this need.',
 'Databricks documents the lakehouse pattern specifically to avoid isolated workload systems, so a matching option exists.',
 'The lakehouse combines data lake and data warehouse benefits and establishes a shared architecture for varied workloads.')
add('b1-q80','a','insert','Syntax; Parameters — INTO',
 'INSERT INTO appends rows, with VALUES supplying a new literal row.',
 'Distinguish appending a new record from updating existing rows.',
 'INSERT INTO my_table VALUES supplies the target table followed by the literal row, appending the requested record.',
 'A UNION combines query results; this fragment is not an INSERT and does not persist a new row to my_table.',
 'The documented syntax places INTO and the target table before the VALUES query, not after the values.',
 'UPDATE modifies existing rows and uses SET assignments; UPDATE ... VALUES is not the append syntax.',
 'This reverses the required target and assignment structure and is not a supported INSERT statement.')
add('b1-q81','b','optimize,vacuum','Optimize data file layout — Syntax examples',
 'OPTIMIZE compacts small data files while preserving logical table contents.',
 'Compaction rewrites layout; VACUUM removes stale files after retention.',
 'REDUCE is not the documented Delta SQL command for compaction.',
 'OPTIMIZE performs file compaction, combining small data files to improve the table’s physical layout.',
 'Compaction describes the operation, but COMPACTION is not the documented SQL command to invoke it.',
 'Repartitioning a DataFrame is not the Delta table maintenance command requested, and by itself does not rewrite the existing table files.',
 'VACUUM removes unreferenced files older than retention; it does not combine active small files into larger ones.')
add('b1-q82','c','delta','What is Delta Lake in Databricks?',
 'Delta Lake extends Parquet data files with a transaction log.',
 'Differentiate the Delta table format from the physical format of its primary data files.',
 'Delta names the table protocol and transaction layer; its primary data files are Parquet.',
 'CSV is not the primary data-file format used by Delta tables.',
 'The Delta Lake overview explicitly describes Parquet data files extended with a file-based transaction log.',
 'JSON is used in parts of transaction metadata, not as the primary table data-file format.',
 'Delta Lake is open source and uses Parquet; its table data is not a proprietary Databricks-only file format.')
add('b1-q83','d','notebooks','Code languages in notebooks — Mix languages',
 'A %sql magic at the beginning of a cell overrides the Python notebook’s default language for that cell.',
 'Use a cell-level magic when only one cell needs another language.',
 'Databricks explicitly supports SQL cells within a Python-default notebook.',
 'The requested control is cell language, not assigning separate compute to a single cell; a Python-default cluster notebook can use %sql.',
 'Without a language override, this cell is interpreted according to its Python default, so bare SQL is not the requested solution.',
 'Adding %sql as the first line overrides that cell’s language without requiring other Python cells to change.',
 'Changing the notebook default is unnecessary when only one cell needs SQL; a cell magic is the targeted option.')
add('b1-q86','c','countif','count_if aggregate function — Syntax',
 'count_if counts rows for which its Boolean predicate is true, including member_id IS NULL.',
 'COUNT(column) counts non-null values; count_if(column IS NULL) counts nulls.',
 'COUNT(member_id) counts non-null values, which is the opposite population from the null values requested.',
 'This uses count_null, which is not the documented count_if predicate approach, and subtraction would not directly count the desired null population.',
 'member_id IS NULL is true exactly for missing values, so count_if returns their count.',
 'null(member_id) is not a documented aggregate for counting null-valued rows.',
 'count_null is not the documented Databricks SQL aggregate here; the supported predicate-based count is count_if.')
add('b2-q4','d,e','medallion','Power analytics with the gold layer; Align with business logic and requirements',
 'Gold shapes domain-specific, often denormalized datasets for efficient reporting and dashboard queries.',
 'For Gold characteristics, look for query-friendly shape and read performance, rather than raw ingestion.',
 'Historical source fidelity and reprocessing are Bronze concerns; historical lineage does not distinguish the Gold layer.',
 'Raw unvalidated data belongs in Bronze, not the business-ready Gold layer.',
 'Normalized detailed data is more characteristic of Silver than of dashboard-oriented Gold models.',
 'Denormalized, business-aligned data reduces repeated reporting joins and matches Gold’s dimensional modeling purpose.',
 'Optimizing queries and dashboards is an explicit Gold-layer goal in the medallion documentation.')
add('b2-q5','c','medallion','Ingest raw data to the bronze layer; Validate and deduplicate data in the silver layer',
 'Silver stores cleaned validated records; Bronze preserves raw data; Gold serves business aggregates.',
 'Match cleansed master data with Silver, not raw landing or summary reporting.',
 'Raw deposit application data should first land in Bronze; Silver is validated and cleaned.',
 'Country/city cash deposit summaries are business aggregates, more appropriate for Gold than raw Bronze.',
 'Cleansed master customer records fit the validated detailed representation required in Silver.',
 'Deduplication of detailed transfers is a Silver cleansing step; Gold is intended for business-ready modeling and aggregates.')
add('b2-q8','c','debugger','Debugging actions',
 'The Python notebook debugger supports breakpoints, stepping, and inspecting variables during execution.',
 'A requirement to step through Python and inspect live variables points to an interactive debugger.',
 'Cluster logs contain recorded diagnostic output, but do not supply interactive Python stepping and variable inspection.',
 'A job dashboard tracks job runs and outcomes rather than offering live source-level Python debugging.',
 'The Python Notebook Interactive Debugger provides breakpoints, step execution, and variable values, directly matching this request.',
 'SQL Analytics is for SQL workloads and does not provide the requested interactive debugging of a Python notebook.')
add('b2-q10','d','expectations','Action on invalid record — Drop invalid records',
 'A pipeline expectation configured with ON VIOLATION DROP ROW discards invalid rows while allowing processing to continue.',
 'Expectations are the feature; DROP ROW is the required violation action.',
 'Change Data Capture processes data changes, not a configured data quality rule for dropping invalid sensor values.',
 'Generic error handling does not identify the documented declarative row-level quality feature.',
 'Monitoring observes behavior; it does not itself enforce dropping invalid rows.',
 'Expectations evaluate Boolean constraints; the DROP ROW action removes violations without failing the stream update.')
add('b3-q3','b','bundles','Set a variable’s value; Reference a variable',
 'Bundle variables can be referenced in resources and overridden under targets for each deployment environment.',
 'Use targets for environment configuration and variables for substitution; runtime job parameters are different.',
 'Separate branches change the codebase during promotion and do not meet the requirement for configuration-only environment behavior.',
 'Referencing ${var.name} and overriding variables under bundle targets supplies environment-specific values at deployment without editing resource definitions.',
 'Notebook job parameters are runtime inputs; the requirement is deployment-time environment behavior through bundle configuration.',
 'Manual workspace edits bypass the versioned bundle configuration and do not make environment behavior reproducible through configuration alone.')
add('b3-q4','b','jobs','Example job with task dependencies; Run if condition options',
 'A fan-in task depends on every parallel upstream task; the default All succeeded condition waits for them to succeed.',
 'Read dependency diagrams from prerequisites to consumers. A dashboard consuming three outputs needs all three dependencies.',
 'Separate externally sequenced jobs do not implement the requested dependency graph inside this Lakeflow Job.',
 'Adding all three tasks as dashboard dependencies creates the fan-in graph. Use All succeeded by default, or All done if completion regardless of success is explicitly intended.',
 'Chaining tasks sequentially discards the requested parallel execution pattern.',
 'Depending only on the SQL task leaves the dashboard free to run before the notebook and pipeline outputs are ready.')
add('b3-q5','b','file-arrival,auto-loader,streaming','How file arrival triggers work; How does Auto Loader track ingestion progress?',
 'A file-arrival trigger schedules the job; Auto Loader’s checkpoint separately determines which files the ingestion run processes.',
 'Distinguish when a job starts from the ingestion state that makes reprocessing incremental.',
 'File-arrival triggering and Auto Loader discovery modes are separate mechanisms; the job trigger does not require selecting Auto Loader File Notification mode.',
 'The job trigger detects arrivals and starts the run; Auto Loader then uses its own persisted state to process unprocessed files with AvailableNow.',
 'The trigger starts a job run; it does not let ingestion code omit its source path by automatically wiring an arriving file path into Auto Loader.',
 'Disabling checkpointing removes the state Auto Loader uses for recovery and tracking processed files. A file-arrival trigger does not replace that checkpoint or require disabling it.')
add('b3-q64','c','connect','How does it work?',
 'Databricks Connect runs Spark operations on remote Databricks compute while allowing client-side development.',
 'Local development does not imply local execution of distributed Spark transformations.',
 'The client API returns results to the local program; manually synchronizing output is not the normal interaction described.',
 'The heavy Spark computation runs on Databricks compute, rather than entirely on the developer’s laptop.',
 'Submitting Spark operations from the local client to remote compute explains why transformations execute remotely and results return to the local console.',
 'Connect is a remote client interface; it does not replicate the entire cluster environment onto the local machine.')
add('b3-q65','b','medallion','Align with business logic and requirements; Create aggregates tailored for analytics and reporting',
 'Gold builds business-domain tables and reusable aggregates on top of cleaned Silver data to support BI.',
 'Look for business concepts and dashboard-friendly preaggregation when designing Gold.',
 'Raw append-only source fidelity is the Bronze role, not the dashboard-optimized Gold design requested.',
 'Denormalized domain-aligned tables and materialized aggregates directly match the documented Gold modeling and query-performance goals.',
 'Light cleansing without a business-serving model does not meet the stated need to avoid complex analyst joins.',
 'Keeping everything heavily normalized and forcing BI to repeatedly join does not meet this scenario’s dashboard latency and simplicity requirements.')
add('b3-q67','c','medallion','Ingest raw data to the bronze layer; Limit data cleanup or validation',
 'Bronze retains append-only source data for audit and reprocessing; Silver and Gold perform quality refinement and business modeling.',
 'Batch versus streaming does not change the raw landing layer in a medallion design.',
 'Gold’s business-serving schema is downstream of raw landing and would skip the intended fidelity-preserving Bronze stage.',
 'Sending each source directly to a different refined layer bypasses a consistent raw history for auditing and replay.',
 'Landing both sources in Bronze with minimal validation preserves the source state; downstream Silver and Gold can apply cleansing and analytics.',
 'Direct-to-Silver deduplication and validation remove the raw landing stage that this scenario explicitly needs for source fidelity and reprocessing.')
add('b3-q69','d','medallion','Example medallion architecture; Power analytics with the gold layer',
 'The medallion example puts cleaned customer/transaction joins in Silver and business spending aggregates in Gold.',
 'Cleaned detailed conformed data is Silver; executive summaries are Gold.',
 'Silver can contain some aggregates, but putting all report-ready outputs there does not follow the scenario’s explicit downstream Gold business-serving design.',
 'Bronze holds raw unvalidated data, not a cleaned conformed customer dataset; report aggregates are normally Gold.',
 'This reverses the usual roles: conformed detailed data belongs in Silver, while report aggregates belong in Gold.',
 'The documentation’s example specifically joins cleaned customer and transaction data in Silver, then creates spending and executive aggregates in Gold.')
add('b3-q73','c','medallion','Validate and deduplicate data in the silver layer',
 'Silver turns raw data into validated, cleaned, deduplicated representations for downstream processing.',
 'Associate Silver with data quality, rather than raw retention or dashboard aggregates.',
 'Preserving raw history for audit is a Bronze responsibility, and Silver is not restricted solely to auditing.',
 'Business-oriented aggregation for analytics describes Gold’s primary serving role.',
 'Validation, cleansing, and deduplication are explicitly listed Silver-layer operations.',
 'Ingesting source data in its original state is the Bronze layer’s primary role.')
add('b3-q74','a','medallion,delta','Ingest raw data to the bronze layer; Limit data cleanup or validation',
 'Bronze preserves source fidelity with minimal validation; Delta can store those raw records with transaction guarantees.',
 '“Raw” means minimally transformed, not necessarily storing the original file encoding unchanged.',
 'Landing raw records with minimal transformation in Delta preserves source fidelity for future processing. Original schemas means retaining source fields, not a guarantee of inferred native JSON/CSV field types.',
 'Dropping nulls and standardizing records are Silver quality operations, which would alter the raw landing representation.',
 'Customer segmentation is business enrichment downstream of raw ingestion, rather than a Bronze landing operation.',
 'Daily sales metrics are business aggregates typically materialized in Gold, not raw Bronze inputs.')
add('b3-q76','c','debugger','Debugging actions',
 'A debugger pauses at breakpoints so a developer can inspect variable values; breakpoints do not enforce data types.',
 'Do not confuse a breakpoint with validation code that raises an error.',
 'The Spark UI focuses on distributed execution rather than the Python debugger’s variable explorer described by this need.',
 'A breakpoint pauses execution before a line; it does not automatically raise an error for a wrong argument type. This is why the supplied B key is not accepted.',
 'The debugger’s variable explorer displays variable values at a breakpoint, helping identify an incorrect argument during the function call.',
 'Print statements can add diagnostics, but do not provide the dedicated live variable inspection offered by the notebook debugger.')
add('b3-q80','c','create-table','Parameters — LOCATION',
 'CREATE TABLE with a LOCATION references external data at that location rather than moving it into managed table storage.',
 'An external table requires a declared data location and appropriate storage permissions.',
 'CREATE MANAGED TABLE is not the documented syntax for this external-location table, and managed storage is contrary to the scenario.',
 'CREATE UNMANAGED TABLE without a location is not the documented external table syntax and does not identify the ADLS data.',
 'CREATE TABLE with LOCATION declares the external storage path; required external-location permissions and credentials must also be in place.',
 'An external table definition must identify the data location; omitting LOCATION does not point Databricks to the specified ADLS data.')
add('b3-q81','b','debugger','Start debugging; Debugging actions',
 'The Python notebook debugger lets you pause at breakpoints and inspect variables while stepping through code.',
 'Execution plans explain Spark work; a Python debugger reveals program state at a line.',
 'Downloaded logs can explain recorded failures but do not provide live breakpoint-based inspection of Python variables.',
 'The interactive debugger explicitly supports breakpoints, stepping, and viewing variable values, matching the requested inspection workflow.',
 'Cluster resource monitoring diagnoses utilization, rather than exposing the notebook’s current Python variable state.',
 'Spark UI stages and query plans help diagnose distributed execution, but are not the requested source-level variable inspection tool.')
add('b3-q85','c','notebooks','Code languages in notebooks — Mix languages',
 'A cell executes in one language REPL; a language magic selects the interpreter rather than mixing Python and SQL statements in one cell.',
 'Different languages can share external data resources, but not arbitrary variables across REPLs.',
 'The documentation does not grant special same-cell interoperability only to Scala and SQL; language execution contexts remain separate.',
 'A notebook can contain multiple languages in separate cells, so the restriction is not one language for the entire notebook.',
 'A cell has a single language context; mixing bare Python and SQL in the same cell does not create a shared interpreter.',
 'A language magic chooses that cell’s language; it does not generally make mixed Python/SQL statements and variables interoperable in the same cell.')
add('b3-q86','a','delta','What is Delta Lake in Databricks?',
 'Delta Lake is the optimized storage layer providing ACID transactions and schema enforcement.',
 'Separate transactional storage (Delta Lake) from governance (Unity Catalog).',
 'Delta Lake extends Parquet files with a transaction log and provides ACID transactions and schema enforcement.',
 'Unity Catalog is the governance layer, not the transaction/storage format that supplies the requested capabilities.',
 'Cloud object storage alone does not add Delta’s table-level ACID protocol or schema enforcement.',
 'A data lake describes a broader storage architecture; Delta Lake is the specific transactional storage technology named in the question.')
add('b3-q89','b','delta','What is Delta Lake in Databricks?',
 'Delta table data is primarily stored in Parquet files, with transaction metadata alongside it.',
 'The table format is Delta; the underlying data-file format is Parquet.',
 'CSV is not the primary physical data-file format of a Delta table.',
 'The official overview states that Delta Lake extends Parquet data files with a file-based transaction log.',
 'JSON can appear in transaction log metadata, but does not describe the primary table data-file format.',
 'Delta is the transaction-aware table protocol, rather than the physical encoding of its main data files.')
add('b3-q90','b','git','Pull changes',
 'Pull retrieves and applies central repository changes to an existing Databricks Git folder.',
 'Use Pull for central-to-local updates; Push moves changes in the other direction.',
 'Clone creates a new copy; this engineer already has a working checkout that needs updating.',
 'Pull is the documented action to update notebooks and files from the remote repository.',
 'Merge combines branches but does not alone retrieve the colleague’s remote commits into this checkout.',
 'Push publishes local changes to the central remote, opposite to the required update direction.')
add('b1-q3','c','architecture','Workspace architecture',
 'The Databricks web application is in the Databricks-managed control plane; classic compute nodes run in the customer compute plane.',
 'For classic architecture, distinguish the workspace UI from the driver and workers that execute workloads.',
 'A worker executes distributed processing in the classic compute plane, rather than being hosted entirely in the control plane.',
 'A JDBC data source is an external system being queried; using a connector does not make the source a control-plane application.',
 'The architecture documentation explicitly locates the Databricks web application in the control plane.',
 'The filesystem represents data storage access, rather than the control-plane web application; classic workspace storage is associated with the customer cloud account.',
 'The driver is part of classic compute execution in the compute plane, not the control-plane web application.')
questions=json.loads((ROOT/'src/data/questions.json').read_text())
for q in questions:
 if q['id'] in reviews:
  review=reviews[q['id']]
  assert set(review['explanations'])=={c['id'] for c in q['choices']},(q['id'],'options mismatch')
  assert set(review['verifiedAnswer'])<={c['id'] for c in q['choices']}
  q.update(review)
  if q['verifiedAnswer']!=q['originalAnswer']:q['issues'].append('Official documentation conflicts with the source key; grading uses the verified answer. Original key retained for audit.')
# Source defects are flagged, not silently rewritten.
flags={
'b1-q7':'Ambiguous retention assumption: VACUUM can remove history files, but its default retention is 7 days, not 3. The question does not specify a shortened retention policy.',
'b1-q8':'Outdated premise: current Databricks Git folders documentation supports merging in the UI. Do not rely on the provided Merge key.',
'b1-q33':'Source options do not accurately explain the default: Auto Loader infers JSON/CSV fields as STRING unless cloudFiles.inferColumnTypes is enabled.',
'b2-q3':'Ambiguous distractor: Bronze is commonly called the raw layer, so both source options refer to the same conceptual landing stage.',
'b3-q70':'Network requirements are underspecified; serverless access to customer-defined networks needs appropriate supported connectivity. Do not assume the supplied key is universally valid.',
'b3-q83':'Imprecise wording: Databricks Connect is a remote Spark client; it does not mirror the entire Databricks Runtime locally.',
'b3-q87':'Ambiguous question: commit, pull, merge, and clone can all be performed with external Git tools. The source Clone key is not uniquely supported.'}
for q in questions:
 if q['id'] in flags:q['issues'].append(flags[q['id']])
for q in questions:q['issues']=list(dict.fromkeys(q['issues']))
(ROOT/'src/data/questions.json').write_text(json.dumps(questions,ensure_ascii=False,indent=2))
report=json.loads((ROOT/'src/data/import-report.json').read_text());report['verified']=len(reviews);report['unverified']=len(questions)-len(reviews);report['issues']=[{'id':q['id'],'issues':q['issues']} for q in questions if q['issues']]
(ROOT/'src/data/import-report.json').write_text(json.dumps(report,indent=2));print('Verified',len(reviews),'Unverified',report['unverified'])
