# Profiling the order formsets

Use a Python environment with Django installed. The fixture settings module is
`settings`. The two request factories are `scenarios:repeated` and
`scenarios:bulky`. From this directory run the following command for each
factory, substituting its name after `--scenarios`.

```sh
python .agents/skills/diagnose-django-performance/scripts/compare_request_profiles.py --settings settings --scenarios scenarios:repeated
```
