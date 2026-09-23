# E16-A Virkler Delta-K Operational Contract v1

## Status

This contract resolves only the public physics operationalization for the
E16-A Paris-type mechanism.  It does not resolve dataset-specific use terms,
authorize a specimen split, or freeze a Paris parameter grid, residual family,
prefix geometry, quota, or model policy.

## Frozen variables and units

The dataset field `CrackLength` is interpreted as the half-crack length
\(a\).  Convert it before all physics calculations:

\[
a_{\rm m}=a_{\rm mm}/1000.
\]

The full panel width is fixed as

\[
w=152.4\;{\rm mm}=0.1524\;{\rm m},
\qquad
\Delta\sigma=48.28\;{\rm MPa}.
\]

The Feddersen finite-width correction is

\[
F(a)=\left[\cos\left(\pi\frac{a}{w}\right)\right]^{-1/2},
\qquad
\Delta K(a)=48.28\,F(a)\sqrt{\pi a_{\rm m}}.
\]

Accordingly, \(\Delta K\) is represented in \({\rm MPa}\sqrt{\rm m}\).
The dataset's observed crack-length range is \(9.0\) through \(49.8\) mm;
therefore

\[
\frac{a_{\max}}{w}=\frac{49.8}{152.4}=0.3268<0.7,
\]

which lies within the stated \(a/w<0.7\) applicability condition for this
correction.

The public experimental metadata \(R=0.2\), thickness \(2.54\) mm, and
loading frequency 20 Hz are frozen as provenance metadata.  They are not
arguments to the above \(\Delta K\) expression because \(\Delta\sigma\) is
already the stress range.

## Paris inverse form

All later mechanism policies must use the observation-aligned inverse form:

\[
\frac{dN}{da}=\frac{1}{C[\Delta K(a)]^m},
\qquad
N(a)-N(a_0)=\int_{a_0}^{a}\frac{ds}{C[\Delta K(s)]^m},
\]

with integration variable \(s\) measured in meters.  Under this convention,
\(C\) has units

\[
\frac{{\rm m/cycle}}{({\rm MPa}\sqrt{\rm m})^m}.
\]

No later population \((C,m)\) construction may mix a millimetre-based crack
coordinate with this metre-based Paris coefficient convention.

## Physics sanity values

These are public-geometry checks, not fitted outcomes:

\[
\Delta K(9.0\;{\rm mm})\approx 8.19\;{\rm MPa}\sqrt{\rm m},
\qquad
\Delta K(49.8\;{\rm mm})\approx 26.54\;{\rm MPa}\sqrt{\rm m}.
\]

## Provenance

The constants, Feddersen correction, and stated domain are taken from the
published Virkler application documentation cited in the source manifest:

- https://c3.ndc.nasa.gov/dashlink/static/media/publication/2010_IJPHM_fatigue.pdf
- https://oaktrust.library.tamu.edu/server/api/core/bitstreams/0d20556e-daff-4f39-be68-d2d53f096f0a/content

This resolves the physics-provenance subgate only.  It does not supply a
dataset-specific license grant or alter the overall E16-A source disposition.
