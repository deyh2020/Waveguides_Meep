import meep as mp
import meep.materials as mt
import matplotlib.pyplot as plt
import numpy as np
import utilities as util
import h5py
import clipboard_and_style_sheet

clipboard_and_style_sheet.style_sheet()

# %% Set up the geometry of the problem. One waveguide laid out in the x direction
wl_wvgd = 3.5
n_center_wvl = mt.LiNbO3.epsilon(1 / wl_wvgd)[2, 2]  # z polarization
w_wvgd = 0.5 * wl_wvgd / n_center_wvl  # width of the waveguide is half a wavelength wide

dpml = 1  # PML thickness

center_wvgd = mp.Vector3(0, 0, 0)  # where the waveguide is centered
sx = 6  # size of the cell in the x direction
sy = 6  # size of the cell in y direction

# %% create the geometric objects from the above
blk = mp.Block(size=mp.Vector3(mp.inf, w_wvgd, mp.inf),
               center=center_wvgd
               )
cell = mp.Vector3(sx, sy, 0)
PML = mp.PML(dpml, direction=mp.Y)

# %% set the appropriate media for the geometric objects
blk.material = mt.LiNbO3

# %% create the geometry and boundary layers list
geometry = [blk]
boundary_layers = [PML]

# %% Done with geometry, moving on to sources, initialize an empty list for sources and append sources as you go
Sources = []

# %% create a gaussian source instance and place it at the front of the waveguide
wl_src = 1.5
df_src = 1.5
src = mp.GaussianSource(wavelength=wl_src,
                        fwidth=df_src
                        )
pt_src = center_wvgd + mp.Vector3(0.0, 0.0 * w_wvgd)

source = mp.Source(
    src=src,
    component=mp.Ez,
    center=pt_src,
)

Sources.append(source)

# %% Done with sources, initialize the simulation instance
sim = mp.Simulation(cell_size=cell,
                    geometry=geometry,
                    sources=Sources,
                    boundary_layers=boundary_layers,
                    resolution=35,
                    )
sim.use_output_directory('sim_output')

# %% Exploit symmetries (if there are any)
symm1 = mp.Symmetry(
    direction=mp.Y,
    phase=1
)
symm2 = mp.Symmetry(
    direction=mp.X,
    phase=1
)

sim.symmetries = [
    symm1,
    symm2
]

# %%
# run to visualize the fields
# sim.run(
#     mp.to_appended("ez", mp.at_every(0.6, mp.output_efield_z)),
#     # mp.at_beginning(mp.output_epsilon()),
#     # until_after_sources=mp.stop_when_fields_decayed(50, mp.Ez, mon_pt, 1e-3),
#     until_after_sources=300,
# )

# set periodic boundary conditions for a given k_point, run the sim, then anlayze result with Harmin repeatedly
# at multile k_points
kmin, kmax = blk.material.valid_freq_range
kpts = mp.interpolate(5, [mp.Vector3(kmin), mp.Vector3(kmax)])
kx = np.array([i.x for i in kpts])
freq = sim.run_k_points(500, kpts)

# %%
plt.figure()
plt.plot([kx.min(), kx.max()], [kx.min(), kx.max()], 'k')
for n in range(len(freq)):
    if len(freq[n]) > 0:
        [plt.plot(kx[n], i.real, marker='o', color='C0') for i in freq[n]]

# %% get data for gif / video
# with h5py.File('sim_output/2-scratch-ez.h5', 'r') as f:
#     data = np.array(f[util.get_key(f)])
#
# with h5py.File('sim_output/2-scratch-eps-000000.00.h5', 'r') as f:
#     eps = np.array(f[util.get_key(f)])
#
# save = False
#
# fig, ax = plt.subplots(1, 1)
# for n in range(0, data.shape[2], 1):
#     ax.clear()
#     ax.imshow(data[:, ::-1, n].T, cmap='jet', vmax=np.max(data), vmin=data.min())
#     if save:
#         plt.savefig(f'../fig/{n}.png')
#     else:
#         plt.pause(.01)
