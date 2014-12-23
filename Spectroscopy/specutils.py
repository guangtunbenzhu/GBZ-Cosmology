
""" 
Useful small tools for spectroscopic analysis
"""

from __future__ import print_function, division
import numpy as np
from scipy.interpolate import UnivariateSpline, interp1d

# Create a center wavelength grid with constant width in log (i.e., velocity) space:
# Input is in Angstrom, output is log10(lambda/Angstrom)
def get_loglam(minwave=448., maxwave=10402., dloglam=1.E-4):
    """Return a central wavelength grid uniform in velocity space
    """
    if minwave>maxwave:
       raise ValueError("Your maximum wavelength is smaller than the minimum wavelength.")
    return np.arange(np.log10(minwave), np.log10(maxwave), dloglam)+0.5*dloglam

def resample_spec(inloglam, influx, inivar, newloglam):
    """
    resample a spectrum/many spectra: convolution then interpolation?
    given f(lambda)dlambda
    """
    pass

# Need to vectorize this
def interpol_spec(inloglam, influx, inivar, newloglam):
    """interpolate the spectra onto a desired wavelength grid
    a simpler, faster and not worse version of combine1fiber
    works if the binning of newloglam is similar to that of loglam
    to resample a spectrum, use resample_spec which does convolution properly
    fine-tuned for logarithmic binning 
    hardcoded parameters: bkptbin; maxsep; 1 pixel around ivar==0
    inloglam: sorted
    newloglam: sorted
    """

    if (inloglam.size != influx.size) or (inloglam.size != inivar.size):
       raise ValueError("The shapes of inputs don't match")

    # Initialization
    newflux = np.zeros(newloglam.size)
    newivar = np.zeros(newloglam.size)

    if inivar[inivar>0].size<5:
       print("input spectrum invalid, no interpolation is performed.")
       return (newflux, newivar)

    # choosing break point binning
    # in_inbetween_out = (np.where(np.logical_and(inloglam>=np.min(newloglam), inloglam<=np.max(newloglam))))[0]
    # this shouldn't matter if binning is in logarithmic scale
    # binsize = np.median(inloglam[in_inbetween_out[1:]]-inloglam[in_inbetween_out[:-1]]) 
    # bkptbin = 1.2*binsize
    # Break the inputs into groups based on maxsep
    # maxsep = 2.0*binsize

    # Check boundary
    inbetween = (np.where(np.logical_and(newloglam>=np.min(inloglam), newloglam<=np.max(inloglam))))[0]
    if inbetween.size == 0:
       print("newloglam not in range, no interpolation is necessary.")
       return (newflux, newivar)
    
    # print(inbetween[0],inbetween[1])

    # Spline
    # s is determined by difference between input and output wavelength, minimum==2
    # desired_nknots = np.ceil(np.median(newloglam[1:]-newloglam[:-1])/np.median(inloglam[1:]-inloglam[:-1]))
    #if desired_nknots<3: # No smoothing in this case
    #   s = 0
    #else: 
    #   s = int(np.floor(inivar.size/desired_nknots))
    #s = 1000
    #print(s)

    # Smoothing does not working properly, forced interpolation
    #s = 0

    # See combine1fiber
    # 1. Break the inputs into groups based on maxsep
    # 2. Choose knots ourselves

    # try except needed here
    # Let's choose the knots ourselves
    # f = LSQUnivariateSpline(inloglam, influx, knots, w=inivar)

    # No smoothing
    #f = UnivariateSpline(inloglam[inivar>0], influx[inivar>0], w=inivar[inivar>0], k=3, s=0)
    f = interp1d(inloglam[inivar>0], influx[inivar>0], kind='cubic')
    newflux[inbetween] = f(newloglam[inbetween])

    # Linear
    g = interp1d(inloglam, inivar, kind='linear')
    newivar[inbetween] = g(newloglam[inbetween])
    #  

    # set newivar=0 where inivar=0
    izero_inivar = (np.where(inivar==0))[0]
    if izero_inivar.size>0:
       # find those pixels that use inivar==0
       index = np.searchsorted(inloglam, newloglam[inbetween])
       newivar[inbetween[np.in1d(index, izero_inivar)]] = 0.
       newivar[inbetween[np.in1d(index-1, izero_inivar)]] = 0.

    newflux[newivar==0] = 0.

    return (newflux, newivar)

