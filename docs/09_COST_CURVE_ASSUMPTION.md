# Working assumption: heterogeneous aggregator cost curves

**Status:** Synthetic assumption; **not empirically validated**.

For aggregator \(i\), let \(q_i=P_i^{nom}-P_i^{lim}\) and \(F_i=P_i^{nom}-P_i^{min}>0\). Proposed incremental CLS cost:

\[
C_i(q_i)=B_i\left(\frac{q_i}{F_i}\right)^{x_i},\quad 0\le q_i\le F_i.
\]

**Exponent assumption:** \(x_i\) is drawn once per aggregator from a truncated normal distribution with underlying \(\mu=2\), \(\sigma=0.5\), bounded to \([1,3]\). This choice is **ours**, not an empirical estimate; \(B_i\) is the EUR cost at full contractual tightening and still requires calibration.

**Literature basis:** Heinrich et al. (2021), *A Local Flexibility Market Mechanism with Capacity Limitation Services*, https://doi.org/10.1016/j.enpol.2021.112335. The paper motivates CLS cost curves, **not** this power-law exponent distribution.

**To validate:** compare the shape and scale against Heinrich's curves and suitable German EV-flexibility evidence; test fixed \(x=1,2,3\) and alternative distributions; handle \(F_i=0\) explicitly.

**Intended code:** `src/cls_market/curves.py` evaluates the curve; `src/cls_market/scenarios.py` draws and fixes per-aggregator parameters (reproducible random seed). Neither is implemented yet.
