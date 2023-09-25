from google.colab import drive
drive.mount('/content/drive')

#Menginstall modul yang diperlukan
!pip install astropy>5.1
!pip install pyspeckit
!pip install specutils

import glob
import os
import pyspeckit
import pandas as pd
import numpy as np
from astropy.io import fits
from astropy import units as u
from specutils import Spectrum1D
from specutils import SpectralRegion
from specutils.fitting import fit_generic_continuum

#Membuka satu persatu file dalam sebuah folder
names=[]
for item in glob.glob("/content/drive/MyDrive/tugas_anas/ta/Woods/spek_woods/*.fits"):
  names.append((os.path.basename(item)))

df=pd.DataFrame()
df['filename']=names

df2=pd.DataFrame()
for item in glob.glob("/content/drive/MyDrive/tugas_anas/ta/Woods/spek_woods/*.fits"):
  hdul=fits.open(item)
  dataspek1=hdul[1].data
  fluks=dataspek1['flux']*u.Unit('10e-17 erg cm-2 s-1 AA-1')
  lamda=(10**dataspek1['loglam'])*u.AA
  dataspek2=hdul[2].data
  z1=dataspek2['Z']
  newlamda=lamda/(1+z1)

#Nilai tengah panjang gelombang yang akan dihitung
  NIIa = 6549
  NIIb = 6585
  Halpha = 6564
  SIIa = 6718.29
  SIIb = 6732.68
#   Hbeta=4862
#   OIII = 5008

# Menginisialisasi spektrum dan membuat plot sekitar daerah Halpha-[NII]
  spectrum = Spectrum1D(flux=fluks, spectral_axis=newlamda)
  g1_fit = fit_generic_continuum(spectrum)
  spec1=spectrum-g1_fit(newlamda) #mengurangi spektrum dengan spektrum kontinum sebelum menghitung fluks 
#   spec1=spectrum/g1_fit(newlamda) #menormalisasi spektrum dengan spektrum kontinum sebelum menghitung lebar ekuivalen
  spec = pyspeckit.Spectrum(xarr=spec1.spectral_axis,data=spec1.flux)
  spec.plotter(xmin = 6450, xmax = 6650, title=os.path.basename(item))

# Menginisialisasi spektrum dan membuat plot sekitar daerah H beta
#   spec = pyspeckit.Spectrum(xarr=newlamda,data=fluks)
#   spec.baseline() #mengurangi spektrum dengan spektrum kontinum sebelum menghitung fluks 
#   spec.plotter(xmin = 4820, xmax = 4900)

# Menginisialisasi spektrum dan membuat plot sekitar daerah [O III]
#   spec = pyspeckit.Spectrum(xarr=newlamda,data=fluks)
#   spec.baseline() #mengurangi spektrum dengan spektrum kontinum sebelum menghitung fluks 
#   spec.plotter(xmin = 4980, xmax = 5040)
    
   #initial guesses untuk H alpha + [N II]
  guesses = [50, NIIa, 5, 100, Halpha, 5, 50, Halpha, 50, 50, NIIb, 5, 20, SIIa, 5, 20, SIIb, 5]
  tied = ['', '', 'p[17]','', '', 'p[17]', '', 'p[4]', '', '3 * p[0]', '','p[17]', '', '', 'p[17]', '', '', '']

  #initial guesses untuk H beta
#   guesses = [100, Hbeta, 5]

  #initial guesses untuk H [O III]
#   guesses = [50, OIII, 5]

# Proses fitting dan pengukuran
  spec.specfit(guesses = guesses, tied=tied, annotate=False)
  spec.plotter.refresh()
  spec.measure()

# Membuat label sumbu
  spec.plotter.axis.set_xlabel(r'Wavelength $(\AA)$')
  spec.plotter.axis.set_ylabel(r'Flux $(10^{-17} \mathrm{erg/s/cm^2/\AA})$')
  spec.plotter.refresh()

# Menyimpan hasil perhitungan ke dalam dataframe
  fluksNIIa=[]
  fluksHalpha=[]
  fluksNIIb=[]

  for i, line in enumerate(spec.measurements.lines.keys()):
    if i==0:
      fluksNIIa.append(spec.measurements.lines[line]['flux'])
    if i==1:
      fluksHalpha.append(spec.measurements.lines[line]['flux'])
    if i==3:
      fluksNIIb.append(spec.measurements.lines[line]['flux'])
    
#   eqwNIIa=[]
#   eqwHalpha=[]
#   eqwNIIb=[]

#   for i, line in enumerate(spec.measurements.lines.keys()):
#     if i==0:
#       eqwNIIa.append(spec.measurements.lines[line]['flux'])
#     if i==1:
#       eqwHalpha.append(spec.measurements.lines[line]['flux'])
#     if i==3:
#       eqwNIIb.append(spec.measurements.lines[line]['flux'])

#   fluksHbeta=[]

#   for ii, line in enumerate(spec.measurements.lines.keys()):
#     if ii==0:
#       fluksHbeta.append(spec.measurements.lines[line]['flux'])

#   fluksOIII=[]
#   for line in spec.measurements.lines.keys():
#     if line=='OIIIb':
#       fluksOIII.append(spec.measurements.lines[line]['flux'])
#     if line=='unknown_1':
#       fluksOIII.append(spec.measurements.lines[line]['flux'])

  df1=pd.DataFrame()
  df1['filename']=names
  df1['fluks_NIIa']=fluksNIIa
  df1['fluks_Halpha']=fluksHalpha
  df1['fluks_NIIb']=fluksNIIb
#   df1['eqw_NIIa']=eqwNIIa
#   df1['eqw_Halpha']=eqwHalpha
#   df1['eqw_NIIb']=eqwNIIb
#   df1['fluks_Hbeta']=fluksHbeta
#   df1['fluks_OIII']=fluksOIII
  df2=pd.concat([df2,df1])
    

df2=df2.reset_index(drop=True)
df3=pd.concat([df,df2],axis=1)

#Mengunduh dataframe dalam format csv
# df3.to_csv(f'/content/drive/MyDrive/tugas_anas/ta/hasil_ew.csv')