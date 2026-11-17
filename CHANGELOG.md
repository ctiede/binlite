# Changelog

### Accretion templates

- Updated the periodic sampling to avoid repeated timestamps at the boundaries between orbits.
- Cached the reconstructed primary, secondary, and total accretion series to avoid recomputing them on repeated access.

### Flux calculations

- Added a `mass_ratio` argument (default `1.0`) to `BinaryAlphaDisk` and the high-level flux-series functions, to accomodate future unequal-mass disk spectra (the current templates are based only on equal-mass binaries).
- Updated the minidisk radii and temperatures to account for the individual component masses and accretion rates.
- Corrected the normalized flux series so that each minidisk's accretion variability is normalized by its own mean, rather than by the mean total accretion rate.
- Added separate `lensing` and `boosting` options to the flux-series functions, allowing these effects to be selected independently.

### API changes

- Replaced the `lens_boost` argument with separate `lensing` and `boosting` arguments in the flux-series functions.
- Renamed the circumbinary disk method `BinaryAlphaDisk.fnu_disk()` to `BinaryAlphaDisk.fnu_cbd()`
- Replaced `BinaryAlphaDisk.rin_md` and `BinaryAlphaDisk.rout_md` with component-specific minidisk radii (`rin_md1`, `rin_md2`, `rout_md1`, and `rout_md2`).
- Removed the redundant `retrograde` argument from `normalized_flux_series()` and `periodic_flux_series()`; the binary orientation is taken from the supplied `AccretionSeries` object.

