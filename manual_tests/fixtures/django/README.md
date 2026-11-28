# Profiling the order formsets

Use a Python environment with Django installed. The fixture settings module is
`settings`. The two request factories are `scenarios:repeated` and
`scenarios:bulky`. Each context manager yields a small and a large request.
Measure each response, including rendering, with these same settings.
