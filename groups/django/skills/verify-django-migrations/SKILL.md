---
name: verify-django-migrations
description: Verify Django schema or data migrations against existing rows. Use when reviewing migration safety, diagnosing an upgrade failure, or checking compatibility across a rolling deploy.
---

# Verify Django migrations

Run checks with the project's Python and Django environment and a disposable database.

## Exercise the upgrade

1. Identify the migration targets and database aliases for the deployed starting point and the candidate. Inspect dependencies across apps and check the plan with `showmigrations --plan` or `migrate --plan` using isolated settings. Use the production database engine for claims about backend-specific SQL, locking, or transaction behavior.
2. Migrate a disposable database to the starting point. Seed representative rows with the historical app registry at that migration state. Include values that stress the change, such as nulls, duplicates after normalization, related rows, or multiple rows that would receive the same default. Apply the candidate through Django's migration executor.
3. Assert the resulting row identities and values with the target migration state. Check affected constraints and relationships. Use separate clean-install and model-state drift checks (`makemigrations --check --dry-run`) when changing the migration. Both can pass even when an upgrade fails.

If the project lacks a migration test helper, use `MigrationExecutor` with explicit target tuples and `executor.loader.project_state(targets).apps` for historical models. Recreate the executor after applying the starting targets so the forward plan sees the updated applied history. Use a disposable database or a transaction-aware migration test harness. If the harness changes a shared test schema, restore its normal migration targets during cleanup.

## Check ordering and rollout

- Review `RunPython` functions for historical models from `apps.get_model()`, dependencies on any referenced apps, and queries on `schema_editor.connection.alias`. When adding a required unique value, add the field in a compatible intermediate state, backfill per row, and then enforce the constraint. Prove that every preexisting row has the intended value before enforcing it.
- If old writers can run during the change, test their inserts and updates against each intermediate schema they will see. Decide how writes racing with the backfill are captured before enforcing constraints or removing old columns. For large tables, check transaction boundaries, lock duration, and what happens if the backfill stops partway.
- If rollback is part of the release plan, exercise it on the disposable database and check which data survives. For irreversible changes, identify the recovery point and evidence needed to validate recovery. Preserve migration history already applied in shared environments and account for those environments when choosing where to repair the graph.

Report the starting and target migrations, database engine, seeded cases, observed results, and any rollout assumptions still to verify.

For API and backend details, consult the [Django migrations guide](https://docs.djangoproject.com/en/stable/topics/migrations/) and [guide to writing migrations](https://docs.djangoproject.com/en/stable/howto/writing-migrations/) for the project's Django version.
