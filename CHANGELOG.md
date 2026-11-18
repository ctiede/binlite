# Changelog

Notable changes to `binlite` are documented here:

## v2.0.0

- [Accretion] Added an optional `normalize` parameter to `AccretionSeries` to normalize accretion series by the mean total accretion rate
- [Accretion] Updated periodic sampling to avoid repeated timestamps at the boundaries between orbits
- [Accretion] Cached the reconstructed primary, secondary, and total accretion series to avoid recomputing them on repeated access

- [Flux] Added a `mass_ratio` argument (currently fixed to `1.0`) to `BinaryAlphaDisk` and the high-level flux-series functions to accommodate future unequal-mass disk spectra
- [Flux] Updated the minidisk radii and temperatures to account for individual component masses and accretion rates
- [Flux] Corrected the normalized flux series so that each minidisk's accretion variability is normalized by its own mean
- [Flux] Added separate `lensing` and `boosting` options to the flux-series functions, so these effects to be selected independently

- [API] Replaced the `lens_boost` argument with separate `lensing` and `boosting` arguments in the flux-series functions
- [API] Renamed the circumbinary disk method `BinaryAlphaDisk.fnu_disk()` to `BinaryAlphaDisk.fnu_cbd()`
- [API] Replaced `BinaryAlphaDisk.rin_md` and `BinaryAlphaDisk.rout_md` with component-specific minidisk radii (`rin_md1`, `rin_md2`, `rout_md1`, and `rout_md2`)
- [API] Removed the redundant `retrograde` argument from `normalized_flux_series()` and `periodic_flux_series()`; the binary orientation is taken from the supplied `AccretionSeries` object

- [Packaging] Replaced deprecated `pkg_resources` with `importlib.resources` for loading Fourier coefficient data
- [Packaging] Removed the runtime dependency on `setuptools`