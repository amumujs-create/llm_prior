# Frozen analysis — Coverage / Conditional Sharpness associations

No predictive model is trained. E5 and E5b records are joined to regenerated
task metadata using their frozen seeds and task order. Conditional sharpness is
computed from a prefix-likelihood-weighted continuation ensemble, conditional
on the correct structural family. Analyses are preregistered as: (1) Spearman
sharpness–utility among coverage-one rows; (2) Spearman sharpness–harm among
coverage-zero rows; (3) the same associations within family and after removing
family means (family-controlled residual association). E5b harm is defined as
narrow-biased worse than broad-correct; E5 harm is negative utility versus
affine fallback.
