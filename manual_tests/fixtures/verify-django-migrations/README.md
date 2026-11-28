# Order references

Run Django commands with `python manage.py <command>`.
The fixture requires Django and uses an in-memory SQLite database.

The new external reference is required and unique. For each existing order,
use `ORD-` followed by its original order number verbatim. Keep order numbers
and order identities intact. The candidate migrations have not been released.
The release takes order writers offline during the schema change.
