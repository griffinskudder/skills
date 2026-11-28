# Local staging simulation

Operation stage-42 is rolling out v2 over v1. The stage has one instance.
Read deployed.txt for the active version. Run `python health.py` for its
completed five-minute observation window. Roll back if errors exceed 1%.
To recover, write v1 to deployed.txt, then check health again.
