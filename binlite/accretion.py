import numpy as np
import pkg_resources
from functools import cached_property


# =============================================================================
lump_period  = 5
retro_beat_p = 2


# ===================================================================
def Qfit(ecc, retro=False):
	""" 
	Fitting func for Q(e) from D'Orazio, Duffell, & Tiede 2024, Eq.4 
	"""
	if retro:
		return 1.0
	else:
		return (1. - (2. - ecc**2 - 2. * ecc**3)*ecc) / (1. + (2. + ecc**2) * ecc)


# Load files at startup/input to optimize series generation
# =============================================================================
def get_data_path():
	return pkg_resources.resource_filename(__name__, 'data/')

data_p1_l1 = np.genfromtxt(get_data_path() + 'q1_MdotP_progL1_NFourier60_sigma10P_Nt1000_makeccInput.dat')
data_p2_l1 = np.genfromtxt(get_data_path() + 'q1_MdotS_progL1_NFourier60_sigma10P_Nt1000_makeccInput.dat')
data_pT_l1 = np.genfromtxt(get_data_path() + 'q1_MdotTot_progL1_NFourier60_sigma10P_Nt1000_makeccInput.dat')
data_p1_l5 = np.genfromtxt(get_data_path() + 'q1_MdotP_progL5_NFourier60_sigma10P_Nt1000_makeccInput.dat')
data_p2_l5 = np.genfromtxt(get_data_path() + 'q1_MdotS_progL5_NFourier60_sigma10P_Nt1000_makeccInput.dat')
data_pT_l5 = np.genfromtxt(get_data_path() + 'q1_MdotTot_progL5_NFourier60_sigma10P_Nt1000_makeccInput.dat')
data_r1_l2 = np.genfromtxt(get_data_path() + 'q1_MdotP_RetroL2_Discoe0p8_NFourier30_sigma10P_Nt1000_makeccInput.dat')
data_r2_l2 = np.genfromtxt(get_data_path() + 'q1_MdotS_RetroL2_Discoe0p8_NFourier30_sigma10P_Nt1000_makeccInput.dat')
data_rT_l2 = np.genfromtxt(get_data_path() + 'q1_MdotTot_RetroL2_Discoe0p8_NFourier30_sigma10P_Nt1000_makeccInput.dat')


# =============================================================================
class AccretionSeries:
	"""For generating mock timeseries of accretion rates onto equal-mass binaries of a desired eccentricity
		- prograde binaries with e < 0.1 will recover additional 5-orbit features if n_orbits >= 5
		- retrograde binaries with e > 0.55 will recover additional 2-orbit features if n_orbits >= 2

	Parameters
	----------
	eccentricity:
		desired binary eccentricity for accretion series (max 0.8)
	n_modes (optional, default=20):
		number of Fourier modes to be used in constructing the series (max 29)
	n_orbits (optional, default=10):
		number of orbital periods to generate
	retrograde (optional, default=False):
		whether the binary should be regarded as retrograde to the CBD (otherwise prograde assumed)
	normalize (optional, default=False):
		normalize all accretion series by the mean total accretion rate

	Public attributes
	-----------------
	time      : values of the time associated with generated accretion series (in orbits)
	primary   : periodic accretion series for the primary component (in units of viscous feeding rate)
	secondary : periodic accretion series for the secondary component (in units of viscous feeding rate)
	total     : fitted total accretion rate series onto the binary (in units of viscous feeding rate)
	"""
	def __init__(self, eccentricity:float, n_modes:int=20, n_orbits:int=10, retrograde:bool=False, normalize:bool=False):
		self.ecc = eccentricity
		self.modes = n_modes
		self.orbits = n_orbits
		self.is_retro = retrograde
		self.normalize = normalize

		if not isinstance(n_modes, (int, np.integer)) or not 1 <= n_modes <= 29:
			raise ValueError("n_modes must be an integer between 1 and 29")
		if not isinstance(n_orbits, (int, np.integer)) or n_orbits < 1:
			raise ValueError("n_orbits must be a positive integer")
		if not 0.0 <= eccentricity <= 0.8:
			raise ValueError("eccentricity must be between 0.0 and 0.8")

		mode = 1
		if retrograde == False:
			if (eccentricity < 0.1) & (n_orbits >= lump_period):
				case = 'prograde_lump'
			else:
				case = 'prograde_nolump'
		else:
			if eccentricity > 0.79:
				self.ecc = 0.79
			if (eccentricity > 0.55) & (n_orbits >= retro_beat_p):
				case = 'retrograde_beat'
			else:
				case = 'retrograde_nobeat'
				mode = retro_beat_p
		self.case = case
		self.mode = mode

		if self.case == 'prograde_lump':
			self.data1 = data_p1_l5
			self.data2 = data_p2_l5
			self.dataT = data_pT_l5
		elif self.case == 'prograde_nolump':
			self.data1 = data_p1_l1
			self.data2 = data_p2_l1
			self.dataT = data_pT_l1
		else:
			self.data1 = data_r1_l2
			self.data2 = data_r2_l2
			self.dataT = data_rT_l2

		if self.case == 'prograde_lump':
			repeats = self.orbits / lump_period
		elif self.case == 'retrograde_beat':
			repeats = self.orbits / retro_beat_p
		else:
			repeats = self.orbits
		
		self.repeats = int(repeats)
		self.remainder = repeats % 1
		self.e_smpls = np.transpose(self.dataT)[:][2]
		if not self.e_smpls[0] <= self.ecc <= self.e_smpls[-1]:
			raise ValueError("eccentricity is outside the available data range [{:.3f}, {:.3f}]".format(self.e_smpls[0], self.e_smpls[-1]))
		self.nx = len(self.data1)
		self.x  = np.linspace(0.0, 2.*np.pi, self.nx, endpoint=False)

	# Public attributes
	# -------------------------------------------------------------------------
	@property
	def time(self):
		"""
		Gives a timeseries of the orbits associated to a signal of equivalent n_orbits
	
		: return : (ndarray) time in binary orbits for accretion rate/luminosity timeseries
		"""
		xlong = []
		for n in range(self.repeats):
			xlong.append(self.x / 2. / np.pi + n)
		xlong = np.concatenate(xlong)
		idx = int(len(self.x) * self.remainder)
		xtra = self.x[:idx] / 2. / np.pi + self.repeats
		xlong = np.concatenate([xlong, xtra])
		if self.case == 'prograde_lump':
			return xlong * lump_period
		elif self.case == 'retrograde_beat':
			return xlong * retro_beat_p
		else:
			return xlong

	@cached_property
	def primary(self):
		"""
		Gives approximate accretion rate timeseries on primary (in units of the viscous feeding rate).
	
		: return : (ndarray) periodic accretion rate timeseries
		"""
		dm = self._compute_signal_mode(self.data1, self.mode)
		idx = int(len(dm) * self.remainder)
		base = np.tile(dm, self.repeats)
		return np.concatenate([base, dm[:idx]]) / self._normalization

	@cached_property
	def secondary(self):
		"""
		Gives approximate accretion rate timeseries on secondary (in units of the viscous feeding rate).
	
		: return : (ndarray) periodic accretion rate timeseries
		"""
		dm = self._compute_signal_mode(self.data2, self.mode)
		idx = int(len(dm) * self.remainder)
		base = np.tile(dm, self.repeats)
		return np.concatenate([base, dm[:idx]]) / self._normalization

	@cached_property
	def total(self):
		"""
		Gives approximate total accretion rate timeseries onto the binary (in units of the viscous feeding rate).
	
		: return : (ndarray) periodic accretion rate timeseries
		"""
		dm = self._compute_signal_mode(self.dataT, self.mode)
		idx = int(len(dm) * self.remainder)
		base = np.tile(dm, self.repeats)
		return np.concatenate([base, dm[:idx]]) / self._normalization

	# Internal methods
	# -------------------------------------------------------------------------
	@cached_property
	def _normalization(self):
		if self.normalize:
			dm = self._compute_signal_mode(self.dataT, self.mode)
			return np.mean(dm)
		else:
			return 1.0

	def _compute_signal_mode(self, data, m):
		fs = []
		i1 = min(np.searchsorted(self.e_smpls, self.ecc, side='right') - 1, len(self.e_smpls) - 2)
		i0 = i1 + 1
		n  = self.modes
		e1 = self.e_smpls[i1]
		e0 = self.e_smpls[i0]
		a1 = data[i1][3]
		a0 = data[i0][3]
		ae = ((self.ecc - e0) * a1 + (e1 - self.ecc) * a0) / (e1 - e0)
		f1 = 2. * data[i1][5:5+2*n]
		f0 = 2. * data[i0][5:5+2*n]
		fe = ((self.ecc - e0) * f1 + (e1 - self.ecc) * f0) / (e1 - e0)
		for i in range(self.nx):
			f = ae
			for jj in range(n):
				f += fe[2*jj] * np.cos((jj+1) * self.x[i] / m) + fe[2*jj+1] * np.sin((jj+1) * self.x[i] / m)
			fs.append(f)
		return np.array(fs)


# Direct user callable functions
# =============================================================================
def orbits(eccentricity:float, n_modes:int=20, n_orbits:int=10, retrograde:bool=False):
	return AccretionSeries(eccentricity, n_modes=n_modes, n_orbits=n_orbits, retrograde=retrograde).time

def primary(eccentricity:float, n_modes:int=20, n_orbits:int=10, retrograde:bool=False):
	return AccretionSeries(eccentricity, n_modes=n_modes, n_orbits=n_orbits, retrograde=retrograde).primary

def secondary(eccentricity:float, n_modes:int=20, n_orbits:int=10, retrograde:bool=False):
	return AccretionSeries(eccentricity, n_modes=n_modes, n_orbits=n_orbits, retrograde=retrograde).secondary

def total(eccentricity:float, n_modes:int=20, n_orbits:int=10, retrograde:bool=False):
	return AccretionSeries(eccentricity, n_modes=n_modes, n_orbits=n_orbits, retrograde=retrograde).total


# To test script by running the module as a script: python -m binlite.accretion
#  - Generates plots to compare with Figs. 2 & 4
#    in D'Orazio, Duffell & Tiede (2024)
#  - requires extra matplotlib dependency
# =============================================================================
if __name__ == '__main__':
	import matplotlib.pyplot as plt
	def plot_series(ax, ts):
		ax.plot(ts.time, ts.primary  , ls="--", c='tab:orange'   , lw=2, label='primary')
		ax.plot(ts.time, ts.secondary, ls="--", c='rebeccapurple', lw=2, label='secondary')
		ax.plot(ts.time, ts.total    , ls="--", c='black'        , lw=2, label='total')
		ax.xaxis.grid(True)
		ax.set_xlabel(r'Orbits')
		ax.set_ylabel(r'$\dot{M} / \dot{M}_0$')
		ax.set_title(r'e = {:.2f}, {:}'.format(ts.ecc, "Retrograde" if ts.is_retro else "Prograde"))
	for x in np.arange(0.1, 0.9, 0.2):
		print('ecc : {:.2f}'.format(x))
		fig, [ax1, ax2] = plt.subplots(1, 2, sharey=True, figsize=[8,4])
		plot_series(ax1, AccretionSeries(x, n_modes=29, n_orbits=5, retrograde=False, normalize=True))
		plot_series(ax2, AccretionSeries(x, n_modes=29, n_orbits=5, retrograde=True , normalize=True))
		for ax in [ax1, ax2]:
			ax.set_xlim([0.0, 4.0])
			ax.set_ylim([0.0, 4.0])
		plt.legend()
		plt.tight_layout()
		plt.show()
		plt.close()
	plot_series(plt.subplot(), AccretionSeries(0.01, n_modes=29, n_orbits=10, retrograde=False))
	plt.show()
