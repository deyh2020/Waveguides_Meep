# -*- coding: utf-8 -*-

import meep as mp
import matplotlib.pyplot as plt
import numpy as np

resolution = 25  # pixels/μm

w1 = 1.0  # width of waveguide 1
w2 = 2.0  # width of waveguide 2
Lw = 10.0  # length of waveguides 1 and 2

Lt = 2

dair = 3.0  # length of air region
dpml_x = 6.0  # length of PML in x direction
dpml_y = 2.0  # length of PML in y direction

sy = dpml_y + dair + w2 + dair + dpml_y

Si = mp.Medium(epsilon=12.0)

boundary_layers = [mp.PML(dpml_x, direction=mp.X),
                   mp.PML(dpml_y, direction=mp.Y)]

lcen = 6.67  # mode wavelength
fcen = 1 / lcen  # mode frequency

symmetries = [mp.Mirror(mp.Y)]

R_coeffs = []
R_flux = []

sx = dpml_x + Lw + Lt + Lw + dpml_x
cell_size = mp.Vector3(sx, sy, 0)

df = 0.2
src_pt = mp.Vector3(-0.5 * sx + dpml_x + 0.2 * Lw)
sources = [mp.EigenModeSource(src=mp.GaussianSource(fcen, fwidth=df * fcen),
                              center=src_pt,
                              size=mp.Vector3(y=sy - 2 * dpml_y),
                              eig_match_freq=True,
                              eig_parity=mp.ODD_Z + mp.EVEN_Y)]

# straight waveguide
vertices = [mp.Vector3(-0.5 * sx - 1, 0.5 * w1),
            mp.Vector3(0.5 * sx + 1, 0.5 * w1),
            mp.Vector3(0.5 * sx + 1, -0.5 * w1),
            mp.Vector3(-0.5 * sx - 1, -0.5 * w1)]

sim = mp.Simulation(resolution=resolution,
                    cell_size=cell_size,
                    boundary_layers=boundary_layers,
                    geometry=[mp.Prism(vertices, height=mp.inf, material=Si)],
                    sources=sources,
                    symmetries=symmetries
                    )

mon_pt = mp.Vector3(-0.5 * sx + dpml_x + 0.7 * Lw)
# `add_flux(fcen, df, nfreq, freq, FluxRegions, decimation_factor=0)`  ##sig
nfreq = 10
flux = sim.add_mode_monitor(fcen,
                            df,
                            nfreq,
                            mp.ModeRegion(center=mon_pt, size=mp.Vector3(y=sy - 2 * dpml_y)))

sim.run(until_after_sources=mp.stop_when_fields_decayed(50, mp.Ez, mon_pt, 1e-9))

res = sim.get_eigenmode_coefficients(flux, [1], eig_parity=mp.NO_PARITY)
incident_coeffs = res.alpha
incident_flux = mp.get_fluxes(flux)
incident_flux_data = sim.get_flux_data(flux)

sim.reset_meep()

# linear taper
vertices = [mp.Vector3(-0.5 * sx - 1, 0.5 * w1),
            mp.Vector3(-0.5 * Lt, 0.5 * w1),
            mp.Vector3(0.5 * Lt, 0.5 * w2),
            mp.Vector3(0.5 * sx + 1, 0.5 * w2),
            mp.Vector3(0.5 * sx + 1, -0.5 * w2),
            mp.Vector3(0.5 * Lt, -0.5 * w2),
            mp.Vector3(-0.5 * Lt, -0.5 * w1),
            mp.Vector3(-0.5 * sx - 1, -0.5 * w1)]

sim = mp.Simulation(resolution=resolution,
                    cell_size=cell_size,
                    boundary_layers=boundary_layers,
                    geometry=[mp.Prism(vertices, height=mp.inf, material=Si)],
                    sources=sources,
                    symmetries=symmetries)

flux = sim.add_mode_monitor(fcen,
                            df,
                            nfreq,
                            mp.FluxRegion(center=mon_pt, size=mp.Vector3(y=sy - 2 * dpml_y)))

sim.load_minus_flux_data(flux, incident_flux_data)

sim.run(until_after_sources=mp.stop_when_fields_decayed(50, mp.Ez, mon_pt, 1e-9))

res2 = sim.get_eigenmode_coefficients(flux, [1], eig_parity=mp.NO_PARITY)
taper_coeffs = res2.alpha
taper_flux = mp.get_fluxes(flux)

R_coeffs.append(abs(taper_coeffs[0, 0, 1]) ** 2 / abs(incident_coeffs[0, 0, 0]) ** 2)
R_flux.append(-taper_flux[0] / incident_flux[0])
