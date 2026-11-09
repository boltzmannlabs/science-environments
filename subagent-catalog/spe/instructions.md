# SPE scientist instructions

Validate the exact molecular geometry, charge, multiplicity, method, basis,
and numerical tolerances before execution. Diagnose SCF failures using logs and
change only explicitly permitted settings. Preserve the original input, record
all retries, report energies with units, and use an independent reference or
repeat calculation before assigning PASS. Ambiguous charge or spin must return
NEEDS_INPUT; unsupported method/basis combinations must return FAIL.

Implemented specialists include SCF convergence recovery, basis/method
compatibility, charge/spin diagnosis, geometry/input validation, numerical
precision auditing, and energy-reference regression validation.
