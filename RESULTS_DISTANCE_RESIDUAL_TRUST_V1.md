# Results — E6 Distance × Data-Driven Trust v1

With calibrated correct-family priors fixed, neither residual architecture had
positive mean fixed-hybrid utility even at the nearest distance. NN ΔR fell
from −.0021 at d=.05 to −.0251 at d=1.0; spline fell from −.0060 to −.0735.
Spline catastrophic harm was 42.8% at d=.05 and about 42–50% across distance;
NN was about 23–27%.

Immediate failure (d*=.05) occurred for 67.0% spline and 61.4% NN tasks;
right-censoring beyond d=1.0 occurred for 16.6% and 20.6%. Pseudo-OOD near gain
did not predict far fixed-residual utility for NN (Spearman .003) and was weak
for spline (.157).

This is a valid negative result: under a calibrated family prior, the residual
mostly learns noise/estimation artifacts, so E6-v1 does not establish a useful
distance-decay regime. The next variant must predefine an *incomplete but
calibrated* prior, so a residual has genuine near-OOD signal to trade against
far-OOD risk; it must not introduce prior miscalibration, which belongs to E7.
