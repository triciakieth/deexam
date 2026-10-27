"""Add concrete usage/comparison detail to the original individually reviewed set."""
from reviewlib import reviews,save
extra={
'b1-q1':[
 'Autoscaling is appropriate when workload demand grows or shrinks. Report consistency still depends on reading the same governed source.',
 'The scenario’s clue is disagreement caused by architecture silos. Reusing shared governed data removes that separate-copy cause rather than only making each report faster.',
 'Reporting-line changes are an organizational intervention. They do not establish a shared table version or consistent source values.',
 'Collaborative editing is useful when coauthoring notebooks or queries. It is not equivalent to replacing inconsistent reporting datasets with one source of truth.',
 'Ad hoc responsiveness is useful for analysis turnaround. A fast report can still disagree with another report that reads a different copy.'],
'b1-q3':[
 'Workers execute tasks and process workload data. Classic workers reside in the customer compute plane rather than the central web-application service.',
 'JDBC is a connectivity interface to a data system. An external database does not move into the control plane merely because Databricks queries it.',
 'The architecture reference explicitly identifies the web application as control-plane hosted. This distinguishes user-facing management from Spark execution.',
 'Storage access and the workspace storage bucket are distinct from hosting the web UI. Do not classify a filesystem namespace as the control-plane application.',
 'The driver coordinates a Spark application on compute. It is not the management web application hosted by the control plane.'],
'b1-q4':[
 'Notebook language selection and Spark APIs let developers choose Python, SQL, Scala, or R where supported. That interface choice is not the Delta storage layer’s distinctive benefit here.',
 'Coauthoring improves team development workflows. It is separate from the guarantees of transaction-log-backed table storage.',
 'Alerts monitor query outcomes or result conditions. They belong to workflow/SQL services rather than being supplied by a Delta data file.',
 'The scenario asks which platform benefit is attributable specifically to Delta Lake. Its single-table batch/streaming integration is expressly documented.',
 'Spark distributes execution across tasks and workers. Delta complements that engine with transactional tables, not with the engine’s general distribution mechanism.'],
'b1-q5':[
 'A table directory may contain many Parquet files and log/checkpoint metadata. One file is not the unit that stores the entire table history.',
 'A growing table can have multiple active data files. Separating metadata from data does not imply that only one data file holds all rows.',
 'The transaction log records table state and actions while Parquet files hold rows. Together they form the file collection described by this option.',
 'Without transaction metadata, a directory of data files is not sufficient to supply Delta versions and ACID semantics. Data-only layout omits the feature being tested.',
 'A single file can be part of a tiny snapshot but is not the Delta table storage model. The question asks about the model, not an accidental small-table file count.'],
'b1-q6':[
 'SELECT is suitable for inspecting which records match before deletion. It does not commit a DELETE to the target table.',
 'Use UPDATE ... SET when values in existing records need changing. Removing records instead calls for DELETE FROM with the requested predicate.',
 'The condition is strictly greater than 25, so age 25 is retained. The committed delete removes matching rows from the current logical table state.',
 'Even a syntactically complete UPDATE would change values rather than delete records. This predicate also selects the wrong side of the age boundary.',
 'This would remove the records that should remain. Checking the predicate direction is as important as selecting the correct DML verb.'],
'b1-q29':[
 'Gold is tailored to business questions such as weekly sales or customer spending. Silver normally retains validated detailed records that those aggregates use.',
 'Both layers can be valuable to different consumers. Value judgments are not a technical definition that determines layer placement.',
 'Gold adds a business-serving shape on top of cleaned data. It does not deliberately degrade the data quality of Silver.',
 'A summary can have fewer rows than its inputs, while modeling can change shapes in other ways. No universal row-count ordering defines the layers.',
 'Silver and Gold should both be trustworthy under their quality contracts. Aggregation and consumer-oriented modeling, not relative truthfulness, distinguish them.'],
'b1-q31':[
 'Checkpointing is essential for progress and recovery state. It works with Structured Streaming rather than replacing the processing framework.',
 'cloudFiles integrates file discovery into the streaming read API. The source can run continuously or in a bounded AvailableNow catch-up.',
 'The explorer is appropriate for inspecting catalog tables and metadata. It is not the runtime source that notices and ingests arriving files.',
 'Catalog privileges can authorize the ingestion workload. Authorization does not perform its file-by-file discovery and incremental execution.',
 'SQL can consume the resulting tables or define supported managed ingestion. The named cloudFiles source still operates with streaming semantics.'],
'b1-q32':[
 'A fixed processing interval would use the named processingTime argument. It does not express terminating after the starting backlog has been processed.',
 'The multi-batch wording is the key clue. AvailableNow can respect input-rate limits while eventually finishing the bounded backlog.',
 'Trigger names must come from the documented API, not plausible English descriptions. No such parallelBatch option is established in the reference.',
 'The string once is not a valid processing-time duration. A bounded trigger and a periodic micro-batch interval are different configurations.',
 'The documented overview distinguishes AvailableNow from Continuous. A made-up combination of the two names does not create bounded catch-up behavior.'],
'b1-q34':[
 'Timestamp cleanup/enrichment normally produces a cleaner detailed representation. It is upstream refinement rather than a reason to consume Gold summaries.',
 'Raw invalid data should first pass the appropriate validation stages. Directly summarizing dirty inputs does not make the source a Gold serving dataset.',
 'Removing malformed records is a quality step. Silver is the documented layer for that refinement, while Gold serves the resulting business metrics.',
 'Gold is optimized for consumers such as dashboards and reports. Querying its stored aggregates avoids rebuilding the same business result for every reader.',
 'Bronze preserves raw source fidelity and historical landing data. The ingestion job does not need a Gold aggregate as its raw source.'],
'b1-q35':[
 'DROP ROW is the rule to discard bad rows while continuing a supported update. The source explicitly chooses a different violation action.',
 'The action applies to the affected flow/update and rolls back the failed table update. Do not generalize it to an unconditional stop of every unrelated parallel flow.',
 'Quarantine requires defining where valid and invalid records are routed. It is not a side effect automatically added by this expectation.',
 'Retaining bad rows with metrics is warning/retain behavior. FAIL UPDATE instead prevents the affected update from committing successfully.',
 'A per-row flag requires an explicit derived field or other application logic. The declared rule only defines validation and its failure action.'],
'b1-q36':[
 'Bronze preserves raw fidelity; Silver applies validation and cleaning. Reversing that direction contradicts the documented design.',
 'Some aggregates can be useful in Silver, but they are not mandatory for every Silver table. An always-true answer must describe the quality role instead.',
 'Joins can increase row counts while filtering/deduplication can reduce them. Layer names do not impose a guaranteed cardinality relation.',
 'Validated, cleaned representations are Silver’s documented role. That quality distinction holds independently of a particular table’s row count.',
 'Fewer records can be a consequence of cleanup, not a defining law. A valid Silver model might join or enrich data without a smaller cardinality.'],
'b1-q39':[
 'Unity Catalog helps govern which source and target objects the workload may use. It does not itself persist Auto Loader’s discovered-file progress.',
 'A Delta sink supplies reliable commits and table history. File discovery and replay state still need the ingestion source/checkpoint mechanism.',
 'SQL analytics is not a single checkpointed file-discovery tool. The question asks for the specific feature that tracks new cloud files.',
 'Browsing metadata can help inspect the output after ingestion. It is not the incremental reader described by the scenario.',
 'Checkpoint state lets repeated runs distinguish newly discovered files from already processed ones. Source deletion is not necessary to achieve that incremental behavior.'],
'b1-q68':[
 'Merge is appropriate when combining branch histories. It is not by itself the remote update operation asked for here.',
 'Push is appropriate after creating local commits that should be published. The colleague’s changes are already remote, so the direction is opposite.',
 'The remote-to-local direction is the decisive clue. Resolve conflicts if local edits overlap incoming changes.',
 'Commit saves a chosen local change set in branch history. It does not retrieve another user’s new remote work.',
 'Clone initializes a new working copy. Updating this existing working copy should not require making another clone.'],
'b1-q76':[
 'A lake alone does not automatically supply the warehouse-style management and transactional serving model described. The question asks for the combined architectural pattern.',
 'A warehouse may serve SQL analytics well but is not itself the whole combined lakehouse pattern. The requested scope includes varied data/analysis workloads.',
 'Choosing All of these would treat distinct architectures as interchangeable. The documentation names the combined model specifically.',
 'A supported combined architectural option is present. None of these would ignore the lakehouse description in the reference.',
 'A single-source approach lets multiple workloads share governed data rather than maintain separate specialty copies. That directly addresses the silo-unification requirement.'],
'b1-q80':[
 'INTO appends rather than replacing the table. Column ordering and compatible types must still match the target definition when no column list is given.',
 'UNION is a query-result set operation, not a persistence command by itself. A complete INSERT could consume a query, but that is not the printed fragment.',
 'The target must be specified before the inserted query/VALUES clause. SQL keyword order is part of validating the complete DML statement.',
 'UPDATE uses SET and a predicate to change existing records. Adding a new literal record requires INSERT rather than this malformed UPDATE.',
 'Both the verb and clause ordering are wrong for appending a record. Correct literal values do not make an invalid DML statement executable.'],
'b1-q81':[
 'The operation name must be the supported Delta command. A plausible synonym is not a SQL keyword for table compaction.',
 'Compaction changes physical layout without changing the logical records returned. It is different from deleting unreferenced historical files.',
 'Use the documented OPTIMIZE spelling rather than a descriptive noun. The distinction matters when executing table maintenance SQL.',
 'A repartitioned DataFrame would still need a deliberate write strategy to affect table files. It is not the single maintenance keyword requested.',
 'VACUUM is appropriate for reclaiming eligible stale files after retention. It is not a rewrite that consolidates current small data files.'],
'b1-q82':[
 'A format name can refer to a table protocol rather than its physical row-file encoding. Delta’s protocol adds transaction semantics around Parquet data.',
 'CSV is a supported ingestion format but is not the physical row-file representation described by the Delta reference. Ingested text may be converted into Delta storage.',
 'The file-based transaction log complements Parquet rather than replacing it with a proprietary encoding. That is why the primary data-file answer is Parquet.',
 'JSON log records describe transaction actions and metadata. They should not be confused with the main files storing table rows.',
 'Open format/protocol interoperability is a documented Delta property. A proprietary-only answer contradicts that storage model.'],
'b1-q83':[
 'A notebook can mix supported languages across cells. The default language is only the starting interpreter for an unqualified cell.',
 'The requested task is selecting SQL interpretation of this cell. Changing the notebook’s compute attachment is not a substitute for that language selection.',
 'A Python interpreter does not parse bare SQL as Python code. A magic cell or an explicit spark.sql call supplies the correct interface.',
 'Only that cell’s language is overridden. Other Python cells can continue using their existing default without conversion.',
 'Changing the entire default is broader than necessary. The cell magic directly satisfies the requirement to leave other cells alone.'],
'b1-q86':[
 'That aggregate is useful for the number of present member_id values. It excludes the very NULL inputs the scenario asks to count.',
 'A supported predicate count avoids inventing an extra null-count function and subtracting unrelated quantities. Expressing the desired set directly is clearer.',
 'The predicate defines the exact population to count. COUNT_IF increments for true Boolean results rather than counting every non-null original identifier.',
 'A value-returning null expression is not a row-count aggregate. The requirement needs a count across the whole input population.',
 'Use the documented count_if predicate API or COUNT(*) over a WHERE member_id IS NULL filter. The printed function name is not that documented aggregate.'],
'b2-q4':[
 'Bronze retains raw historical data for auditing/reprocessing. Lineage is a governance capability spanning layers rather than a unique Gold shape.',
 'Gold is already refined for business consumers. Sending raw data directly there skips the intended quality/modeling stages.',
 'Silver commonly retains normalized detailed data. Gold’s serving model is designed around business access patterns rather than normalization as its defining property.',
 'A domain-aligned serving model can reduce repeated expensive BI joins. Denormalization is an intended Gold characteristic here, not a rule that every Gold object must use one schema pattern.',
 'The documentation explicitly emphasizes query/dashboard performance for Gold. Read optimization is the other requested serving characteristic.'],
'b2-q5':[
 'Raw application records are suitable Bronze inputs. Calling them Silver before cleaning conflicts with the documented quality progression.',
 'Country/city totals are already an aggregate business representation. They are not the fidelity-preserving raw landing form expected in Bronze.',
 'Validated master records retain detailed information for subsequent joins and analytics. That is the Silver role rather than a Gold summary or Bronze raw landing.',
 'Deduplicated detailed transaction records fit the Silver quality stage. A later Gold dataset may build business measures from those records.'],
'b2-q8':[
 'Logs are useful for messages and failures already emitted by the process. They do not pause on a source line and expose the current local variables.',
 'Run status and duration belong to operational job monitoring. The requested interactive source-level inspection needs a debugger.',
 'Breakpoints stop execution before the line runs and allow inspection/stepping. That matches both the unexpected output and live-variable clues.',
 'The code is Python, and the requested action is stepping rather than running SQL analysis. A SQL interface does not replace Python debugging.'],
'b2-q10':[
 'CDC concerns how source inserts/updates/deletes are propagated. It does not express the sensor-validity Boolean rule described here.',
 'A general error-handling label is not the documented row-quality feature. The required action is specifically an expectation with a drop policy.',
 'Observing metrics can reveal bad values but does not automatically remove them. Enforcement needs the configured expectation action.',
 'Configure the rule and select DROP ROW rather than FAIL UPDATE. This discards violating sensor records without intentionally failing the affected update.'],
'b3-q3':[
 'Branches control source versions, not merely deployment-time values. The scenario explicitly wants the same codebase promoted with configuration-only differences.',
 'Resource references use ${var.name}, while the selected target supplies its overrides. This is deployment-time configuration rather than a notebook code edit.',
 'Job parameters supply runtime values to an execution. They do not automatically replace bundle-level deployment settings for resources.',
 'Manual edits create drift between the reviewed source configuration and deployed workspace objects. Reproducible promotion should flow through target configuration.'],
'b3-q4':[
 'External sequential scheduling discards both the single-job DAG and the requested parallel middle stage. It also adds another orchestration layer.',
 'The dashboard is the fan-in consumer of all three parallel outputs. Set All done only if running after failures is actually intended; otherwise the default requires success.',
 'Sequential edges serialize otherwise independent tasks. They can increase runtime and are not the stated parallel dependency pattern.',
 'A missing edge means the dashboard is not constrained by the other two tasks. It could start while those outputs are still incomplete.'],
'b3-q5':[
 'File-arrival detection belongs to job orchestration, while discovery mode belongs to the ingestion reader. They are separate supported configuration choices.',
 'AvailableNow then gives the ingestion run a bounded backlog to process. The checkpoint still defines what the reader has already committed, independently of why the job started.',
 'The job starts the configured notebook/task rather than rewriting its input path. The reader still needs its source configuration and progress state.',
 'Checkpoint state is what makes repeated runs and failures recoverable. Turning it off would not be a supported way to prevent duplicate processing.'],
'b3-q64':[
 'show or collect returns materialized results through the client connection. Manual copying is not the normal DataFrame result path.',
 'Local Python business logic can run on the client, but distributed Spark transformations are sent to the target. The distinction is explicit in the Connect architecture.',
 'The API constructs plans locally and submits them for remote execution. Actions then return their results to the local program as appropriate.',
 'The client is intentionally thin and relies on remote runtime services. Recreating the entire cluster on the laptop would be a different architecture.'],
'b3-q65':[
 'Preserving raw fidelity belongs in Bronze rather than a dashboard-serving Gold model. Raw landing does not eliminate the need for a business representation.',
 'The source asks for named business metrics and avoiding repeated analyst joins. Precomputed domain-oriented outputs directly address those query and usability requirements.',
 'Light cleansing does not by itself supply the shared business measures described. Keeping all logic elsewhere can push unnecessary work into every dashboard query.',
 'Normalization can be valuable in detailed models but is not the stated dashboard simplification goal. Relying on each BI query to reconstruct the business model misses that requirement.'],
'b3-q67':[
 'A reporting schema is not a substitute for retaining original events and catalog records. It can remove detail needed for auditing and replay.',
 'Batch versus streaming delivery does not determine whether raw history should be preserved. Both source types can land in Bronze.',
 'The retained Bronze history lets the team rebuild downstream stages after correcting quality logic. Silver and Gold can then refine the same raw evidence.',
 'Direct validation/deduplication before raw retention can hide the original source state. That conflicts with the explicitly requested auditability and reprocessing.'],
'b3-q69':[
 'Some Silver aggregates can exist, but the question explicitly describes a separate business-serving stage. The documented example places detailed conformed data and executive summaries in different roles.',
 'A cleaned joined customer dataset is not raw Bronze. Putting the later executive aggregates only in Silver also reverses the stated downstream serving progression.',
 'This swaps the model’s detailed refinement and business-summary roles. Gold is not the prerequisite raw input from which Silver executive summaries are defined.',
 'The official example uses customer_transactions in Silver and customer spending/executive summaries in Gold. That closely matches the exact scenario, not just a generic layer mnemonic.'],
'b3-q73':[
 'Raw historical fidelity and replay are Bronze goals. Silver may support auditing but is not defined as an audit-only archive.',
 'Reporting-oriented aggregates are a typical Gold responsibility. Silver primarily improves the quality and structure of detailed records.',
 'The reference lists null handling, type casting, quality checks, and deduplication in Silver. Those operations make records ready for downstream modeling.',
 'Bronze is the landing stage that preserves raw source state. Moving that definition to Silver would skip the quality distinction being tested.'],
'b3-q74':[
 'Minimal provenance fields or robust landing types can still be added to support ingestion. Raw fidelity does not require keeping a source CSV file’s physical encoding as the target table format.',
 'Removing null records changes the retained source evidence. Silver is where those cleaning rules should be applied explicitly.',
 'Segmentation labels encode business meaning beyond raw landing. They belong in downstream enrichment or serving definitions.',
 'A daily total no longer preserves each original transaction. Raw landing should retain records before aggregate reporting reduces their detail.'],
'b3-q76':[
 'Spark stage diagnostics are not the notebook’s Python variable explorer. Use them for distributed execution rather than expecting a generic Debug tab of function arguments.',
 'Validation code raises type errors when a rule is evaluated; a breakpoint itself only pauses execution. That documented distinction is why the original B key is corrected.',
 'Inspect the paused function’s argument values in the variable explorer and step to the failing operation. This helps identify the unexpected input without claiming breakpoints enforce types.',
 'Print statements can show a value but require changing or rerunning instrumented code. The question asks for the dedicated interactive inspection feature.'],
'b3-q80':[
 'The requested source path is external data already present in ADLS. A managed-table declaration is not the source’s documented CREATE TABLE ... LOCATION approach.',
 'An unsupported keyword does not become a table type merely because it sounds like the opposite of managed. A valid table definition also needs the intended source location.',
 'The catalog definition references the external data path under the configured authorization model. It does not copy the data into a managed storage root just by being registered.',
 'An external table still needs its data location established. The missing path prevents the statement from identifying the ADLS dataset in the scenario.'],
'b3-q81':[
 'Logs can report exceptions and messages but cannot interactively inspect every current Python variable. They are useful supporting evidence rather than the debugger replacement.',
 'The paused source line and variable explorer expose the intermediate state the scenario asks for. Continue stepping to locate the operation that diverges or fails.',
 'Hardware resource monitoring can reveal CPU/memory pressure. It does not show the live Python argument values at a breakpoint.',
 'Spark UI is useful for stages, plans, shuffles, and task failures. The requested notebook variable inspection is a different diagnostic granularity.'],
'b3-q85':[
 'Supported language cells are dispatched to their own execution contexts. There is no general special exception making mixed Scala/SQL source one interpreter.',
 'Notebook-level multilingual support is broader than cell-level execution. Separate cells can use different supported languages.',
 'A %sql cell executes as SQL rather than making arbitrary Python statements part of SQL syntax. Explicit interfaces such as spark.sql handle SQL strings from Python instead.',
 'A magic selects a language context; it is not an unrestricted variable-sharing bridge. Data can be exchanged through supported external/table/result mechanisms.'],
'b3-q86':[
 'The transaction log tracks committed table state and enables versioned operations. This is the storage layer named by the required reliability guarantees.',
 'Governance controls who can access objects and tracks catalog metadata/lineage. It complements rather than replaces the table transaction protocol.',
 'Raw files in object storage do not by themselves define an atomic multi-file table transaction or schema contract. A table layer must supply those semantics.',
 'A lake can contain many types of files and tables. The specific optimized transactional format in the options is Delta Lake.'],
'b3-q89':[
 'CSV can be an input format that is ingested into Delta. It does not become the primary Delta row-file encoding.',
 'The transaction protocol and log add table state around those data files. Naming Parquet does not imply that a plain Parquet folder alone supplies Delta semantics.',
 'JSON log files record actions/metadata rather than the primary table rows. The question asks about data storage, not every file in the table directory.',
 'Delta names the transactional table format. Parquet is the more precise physical data-file answer among the choices.'],
'b3-q90':[
 'A new clone is appropriate for creating another working copy, not for updating this existing one. The engineer already has the central repository configured.',
 'Pull transfers the latest remote changes into the current working copy. Local conflicts may need resolution before the combined branch can be used.',
 'Merging is useful for combining branch histories, but it is not alone the remote fetch/update operation requested. Pull addresses the stated remote-to-local direction.',
 'Push is the local-to-remote publication operation. It does not retrieve the colleague’s already published changes.']}
for qid,paragraphs in extra.items():
 r=reviews[qid];assert len(paragraphs)==len(r['explanations']),qid
 r['explanations']={letter:text.split('\n\nAdditional context:\n')[0]+'\n\nAdditional context:\n'+paragraphs[i] for i,(letter,text) in enumerate(r['explanations'].items())}
 r['reviewedAt']='2026-10-28';r['reviewStatus']='verified';r['analysis']=r['keyConcept']
save()
