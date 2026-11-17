## binlite
`binlite` is a Python package for rapidly generating accretion templates and inferred flux timeseries from eccentric binaries.

### Modules

`accretion` : generate periodic templates of accretion onto the 'primary', 'secondary', or 'total' of an eccentric binary  
`flux` : calculate periodic flux templates associated with a periodic accretion template

### Intended Use

Users can generate a periodic accretion template in two separate ways:

1. Generate an instance of an `AccretionSeries` object and access the data via the associated `time`, `primary`, `secondary`, and `total` attributes; e.g.

    ```python
    import binlite as blt
    ts = blt.AccretionSeries(0.3, n_orbits=5, n_modes=29)
    orbits = ts.time
    mdot_primary = ts.primary
    mdot_secondary = ts.secondary
    mdot_total = ts.total
    ```

2. Directly call the functions `accretion.primary`, `accretion.secondary`, `accretion.total`, `accretion.orbits` with the same signature as `AccretionSeries` objects (which generate an `AccretionSeries` object as an intermediary); e.g.

    ```python
    from binlite.accretion import orbits, primary, secondary, total
    time_orbits = orbits(0.5, n_orbits=5, n_modes=29, retrograde=True)
    mdot_primary = primary(0.5, n_orbits=5, n_modes=29, retrograde=True)
    mdot_secondary = secondary(0.5, n_orbits=5, n_modes=29, retrograde=True)
    mdot_total = total(0.5, n_orbits=5, n_modes=29, retrograde=True)
    ```

The accretion templates are based on simulations of equal-mass (`q=1`) binaries, with prograde and retrograde prescriptions described in D'Orazio, Duffell & Tiede (2024).

Similarly, users have access to two means of creating an associated flux timeseries, both of which first require the creation of an `AccretionSeries` object from which to compute the flux variability:

1. Directly call the functions `periodic_flux_series` and `normalized_flux_series` for a flux series or a series normalized against the baseline total flux, respectively. These functions require the user to supply the observing frequency in hertz, an `AccretionSeries` object, the orbital period of the binary in years, the total mass of the binary in solar masses, and the luminosity distance to the binary in parsecs. They also optionally accept specifications for the Eddington accretion fraction, accretion efficiency, binary mass ratio (`q=M_2/M_1`, with `0 < q <= 1`), observer inclination angle in degrees, and the inner and outer disk boundaries for integrating the blackbody spectra; e.g.

    ```python
    from binlite import AccretionSeries
    from binlite.flux import periodic_flux_series, normalized_flux_series
    acc = AccretionSeries(0.4)
    fnu_series = periodic_flux_series(frequency, acc, period_yr, total_mass_msun, luminosity_distance_pc, eddington_ratio=0.1)
    fnu_normal = normalized_flux_series(frequency, acc, period_yr, total_mass_msun, luminosity_distance_pc, eddington_ratio=0.1)
    ```

    The flux model supports unequal binary mass ratios through the optional `mass_ratio` argument (default `1.0`). Note, however, that the current accretion variability templates are calibrated to equal-mass simulations. The normalized flux series is dimensionless, with each minidisk's accretion variability normalized by its own mean accretion rate.

    The `time` routine is for plotting and generates an array of observation times in years from the associated `AccretionSeries` object and the binary orbital period.

    ```python
    import binlite as blt
    time = blt.flux.time(acc, period_yr)
    ```

2. The above routines, as an intermediary, generate an instance of a `BinaryAlphaDisk` object which contains all the information about the system eccentricity, period, mass, mass ratio, distance, accretion rate, efficiency, and disk sizes. If preferred, one can instead generate a `BinaryAlphaDisk` object directly and calculate flux series from this and an associated `AccretionSeries` object via the `periodic_flux_series_from_bad`, `normalized_flux_series_from_bad`, and `time_from_bad` functions; e.g.

    ```python
    import binlite as blt
    acc = blt.AccretionSeries(eccentricity)
    bad = blt.BinaryAlphaDisk(acc.ecc, period_yr, total_mass_msun, luminosity_distance_pc, accretion_efficiency=0.01, retrograde=acc.is_retro)
    time = blt.flux.time_from_bad(acc, bad)
    fnu_series = blt.flux.periodic_flux_series_from_bad(frequency, acc, bad)
    fnu_normal = blt.flux.normalized_flux_series_from_bad(frequency, acc, bad)
    ```

`BinaryAlphaDisk` objects also contain information on the system barycenter velocity, orbital orientation, and emission spectral slope for superimposing gravitational lensing and Doppler boosting onto a given flux series. Each flux-series function accepts separate optional arguments `lensing` and `boosting` (both default to `False`), allowing either or both effects to be included; e.g.

```python
fnu_series = blt.flux.periodic_flux_series_from_bad(frequency, acc, bad, lensing=True, boosting=True)
```

The `BinaryAlphaDisk` class also provides methods `fnu_primary`, `fnu_secondary`, `fnu_cbd`, and `fnu_total` for calculating the specific flux contributions from the individual minidisks, circumbinary disk, and full system, respectively.

The flux module also contains a convenience function `magnitude_from_flux` which converts a flux timeseries into a timeseries of apparent magnitudes. The function takes as input any flux series at some frequency and the associated zero-point flux for that observing band: `blt.flux.magnitude_from_flux(fnu_series, zero_point_flux)`.

The calculations for generating flux timeseries assume that the circumbinary disk and each minidisk are described by independent Shakura-Sunyaev alpha-disk solutions. See the associated paper D'Orazio, Duffell & Tiede (2024) for more detail.

Each module can also be run directly by running `python -m binlite.accretion` or `python -m binlite.flux`. For each module this will run a small example script (that additionally requires a `matplotlib` installation; not specified as a dependency). The `accretion` example will generate figures like Figs. 2, 3 & 4 in D'Orazio, Duffell & Tiede (2024), and the `flux` example will create figures like Fig. 7 (without the lensed or boosted components).

### Changelog

See [CHANGELOG.md](CHANGELOG.md) for a summary of new features, scientific corrections, and API changes.