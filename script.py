import meep as mp
import meep.materials as mt
import numpy as np
import copy
import clipboard_and_style_sheet
from meep import mpb
import matplotlib.pyplot as plt
import utilities as util
import h5py
import time
import waveguide_dispersion as wg
import materials as mtp

wl_wvgd = 3.5  # um
n_cntr_wl = mt.LiNbO3.epsilon((1 / wl_wvgd))[2, 2]  # ne polarization
wdth_wvgd = 0.5 * wl_wvgd / n_cntr_wl

ridge = wg.RidgeWaveguide(
    # width=wdth_wvgd,
    width=0.5,
    height=0.7,
    substrate_medium=mtp.Al2O3,  # dispersive
    waveguide_medium=mt.LiNbO3,  # dispersive
    # substrate_medium=mp.Medium(index=1.45),  # non-dispersive
    # waveguide_medium=mp.Medium(index=3.45),  # non-dispersive
    resolution=40,
    num_bands=1,
    cell_width=7,
    cell_height=7
)

# widths = np.linspace(.4, 2, 100)
# RES = []
# E = []
# for h, wdth in enumerate(widths[7:]):
#     ridge.width = wdth
#     res = ridge.calc_dispersion(.4, 5, 19)
#     RES.append(res)
#     E.append(ridge.E)
#
#     print(f'__________________{len(widths) - h}________________________________')

ridge.width = 10
ridge.height = .7
ridge.cell_width = 20
ridge.cell_height = 5
ridge.num_bands = 8

ridge.wvgd_mdm = mp.Medium(epsilon_diag=mt.LiNbO3.epsilon(1 / 1.55).diagonal())
ridge.sbstrt_mdm = mp.Medium(epsilon_diag=mtp.Al2O3.epsilon(1 / 1.55).diagonal())
res = ridge.calc_w_from_k(.4, 5, 20)
res.plot_dispersion()

bands = [ridge.get_sm_band_at_k_index(i) for i in range(len(res.kx))]
for n in range(len(res.kx)):
    ridge.plot_mode(bands[n], n)

# for n, i in enumerate(range(len(res.kx))):
#     band = np.argmin(np.sum(abs(ridge.index_rank_sm(i)), 1))
#     print(band, n)
#     ridge.plot_mode(band, i)

# res = ridge.calc_dispersion(.8, 5, 7)
# res.plot_dispersion()
# [ridge.plot_mode(0, n) for n in range(len(res.kx))]

# %%____________________________________________________________________________________________________________________
# omega = 1 / 1
# n = ridge.wvgd_mdm.epsilon(1 / 1.55)[2, 2]
# kmag_guess = n * omega
#
# eps_wvgd = ridge.wvgd_mdm.epsilon(omega)
# eps_sbstrt = ridge.sbstrt_mdm.epsilon(omega)
# ridge.wvgd_mdm = mp.Medium(epsilon_diag=eps_wvgd.diagonal())
# ridge.sbstrt_mdm = mp.Medium(epsilon_diag=eps_sbstrt.diagonal())
#
# k = ridge.find_k(
#     p=mp.EVEN_Y,
#     omega=1,
#     band_min=1,
#     band_max=4,
#     korig_and_kdir=mp.Vector3(1),
#     tol=1e-6,
#     kmag_guess=kmag_guess,
#     kmag_min=kmag_guess * .1,
#     kmag_max=kmag_guess * 10
# )

# # As you can see, the light line for free space isn't the constraint,
# # it's the light line for the oxide!
# E = ridge.ms.get_efield(4, False)
# eps = ridge.ms.get_epsilon()
# for n, title in enumerate(['Ex', 'Ey', 'Ez']):
#     plt.figure()
#     x = E[:, :, 0, n].__abs__() ** 2
#     plt.imshow(eps[::-1, ::-1].T, interpolation='spline36', cmap='binary')
#     plt.imshow(x[::-1, ::-1].T, cmap='RdBu', alpha=0.9)
#     plt.axis(False)
#     plt.title(title)
