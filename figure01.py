# -*- coding: utf-8 -*-
"""
Figure 1 demonstrates the grid cell model with phase precession and the
shuffling feature.
"""

import matplotlib.pyplot as plt
import numpy as np
import grid_model
import matplotlib.gridspec as gridspec
from neo.core import AnalogSignal
import quantities as pq
from elephant import spike_train_generation as stg
from scipy import ndimage
import seaborn as sns


colors = plt.rcParams['axes.prop_cycle'].by_key()['color']

spacing = 50
orientation = 30
pos_peak = [20, 20]
arr_size = 200
dur_ms = 2000
dt_s = 0.002

trajectories = [75.0]
simulation_result = grid_model.grid_simulate(
    trajectories,
    dur_ms=dur_ms,
    grid_seed=1,
    poiss_seeds=[1],
    shuffle='non-shuffled',
    n_grid=200,
    speed_cm=20,
    rate_scale=5,
    arr_size=arr_size,
    f=10,
    shift_deg=180,
<<<<<<< HEAD
    dt_s=0.001,
=======
    dt_s=dt_s,
>>>>>>> 5887f8a0c0c1aebf6c85bad742693598fed6cba3
    large_output=True
)

grid_length_cm = 100
grid_axes_ticks = np.arange(0,grid_length_cm,grid_length_cm/arr_size)

trajectories_y = 100 - np.array(trajectories)
trajectories_xstart = 0
trajectories_xend= 40

fig = plt.figure(constrained_layout=True)
gs = fig.add_gridspec(6,2)
ax1 = fig.add_subplot(gs[:3,0])
ax1.imshow(simulation_result[3][:,:,1], extent=[0,100,0,100]) # TODO UNITS
for trajectory in trajectories_y:
    ax1.plot([trajectories_xstart, trajectories_xend], [trajectory]*2,
             linewidth=3)
ax2 = fig.add_subplot(gs[0:2,1])
x = np.arange(0,dur_ms,dt_s*1000)
ax2.plot(x,simulation_result[4][1,:,0])
ax2.plot(x,simulation_result[4][1,:,1])
ax2.plot(x,simulation_result[4][1,:,2])
ax2.set_xlabel("Time (ms)")
ax2.set_ylabel("Frequency (Hz)")
ax2.legend(("Traj1", "Traj2", "Traj3"))
ax3 = fig.add_subplot(gs[2:3,1])
ax3.eventplot(simulation_result[0][trajectories[0]][1][1], lineoffsets=3, color=colors[0])
ax3.eventplot(simulation_result[0][trajectories[1]][1][1], lineoffsets=2, color=colors[1])
ax3.eventplot(simulation_result[0][trajectories[2]][1][1], lineoffsets=1, color=colors[2])
ax3.set_ylabel("Trajectory")
ax3.set_xlabel("Time (ms)")
ax3.get_yaxis().set_visible(False)
xlim=[-10, 2010]
ax2.set_xlim((xlim))
ax3.set_xlim((xlim))


# =============================================================================
# =============================================================================
# # Figure 01 C
# =============================================================================
# =============================================================================
# =============================================================================
# grid fields
# =============================================================================

spacing = 50
pos_peak = [80, 100]
x1 = int(pos_peak[0]/2)
y1 = int(pos_peak[1]/2)
orientation = 40

grid_rate = grid_model._grid_maker(spacing,
                             orientation, pos_peak).reshape(200, 200)


f1, ax1 = plt.subplots(figsize=(7, 9))

cmap2 = sns.color_palette('RdYlBu_r', as_cmap=True)
im1 = ax1.imshow(grid_rate, cmap=cmap2)

ax1.set_xticks(np.arange(0, 240, 40))
ax1.set_xticklabels(np.arange(0, 120, 20))
ax1.set_yticks(np.arange(0, 240, 40))
ax1.set_yticklabels(np.arange(0, 120, 20))

ax1.set_xlabel('Position (cm)')
ax1.set_ylabel('Position (cm)')

ax1.set_title(f'spacing= {spacing} cm    ' +
              f'origin = [{y1} cm, {x1} cm]     ' +
              f'orientation={orientation} degree', loc='center')

# =============================================================================
# =============================================================================
# # Figure 01 C
# =============================================================================
# =============================================================================


# =============================================================================
# =============================================================================
# # Figure 01 D and E
# =============================================================================
# =============================================================================

# function to produce samples with phase precession from overall firing
def precession_spikes(overall, dur_s=5, n_sim=1000, T=0.1,
                      dt_s=0.002, bins_size_deg=7.2, shuffle=False):
    dur_ms = dur_s*1000
    asig = AnalogSignal(overall,
                        units=1*pq.Hz,
                        t_start=0*pq.s,
                        t_stop=dur_s*pq.s,
                        sampling_period=dt_s*pq.s,
                        sampling_interval=dt_s*pq.s)
    
    times = np.arange(0, dur_s+T, T)
    n_time_bins = int(dur_s/T)
    phase_norm_fact = 360/bins_size_deg
    n_phase_bins = int(720/bins_size_deg)
    phases = [[] for _ in range(n_time_bins)]
    phases_doubled = [[] for _ in range(n_time_bins)]
    trains = []
    for i in range(n_sim):
        train = stg.inhomogeneous_poisson_process(asig,
                                                  refractory_period=(0.001 *
                                                                     pq.s),
                                                  as_array=True)*1000
        if shuffle is True:
            train = grid_model._randomize_grid_spikes(train, 100,
                                                      time_ms=dur_ms)/1000
        else:
            train = train/1000
        trains.append(train)
        for j, time in enumerate(times):
            if j == times.shape[0]-1:
                break
            curr_train = train[np.logical_and(train > time,
                                              train < times[j+1])]
            if curr_train.size > 0:
                phases[j] += list(curr_train % (T)/(T)*360)
                phases_doubled[j] += list(curr_train % (T)/(T)*360)
                phases_doubled[j] += list(curr_train % (T)/(T)*360+360)
    counts = np.empty((n_phase_bins, n_time_bins))
    for i in range(n_phase_bins):
        for j, phases_in_time in enumerate(phases_doubled):
            phases_in_time = np.array(phases_in_time)
            counts[i][j] = ((bins_size_deg*(i) < phases_in_time) &
                            (phases_in_time < bins_size_deg*(i+1))).sum()
    f = int(1/T)
    phase_loc = counts*phase_norm_fact*f/n_sim
    phase_loc = ndimage.gaussian_filter(phase_loc, sigma=[1, 1])
    return trains, phases, phase_loc


# =============================================================================
# 1D
# =============================================================================

spacing = 20
pos_peak = [100,100]
orientation = 30
dur_s = 2
dur_ms = dur_s*1000
n_sim = 20

grid_rate = grid_model._grid_maker(spacing,
                             orientation, pos_peak).reshape(200, 200, 1)
grid_rates = np.append(grid_rate, grid_rate, axis=2)
spacings = [spacing, spacing]
grid_dist = grid_model._rate2dist(grid_rates, spacings)[:, :, 0].reshape(200,
                                                                         200,
                                                                         1)
trajs = np.array([50])
dist_trajs = grid_model._draw_traj(grid_dist, 1, trajs, dur_ms=dur_ms)
rate_trajs = grid_model._draw_traj(grid_rate, 1, trajs, dur_ms=dur_ms)
rate_trajs, rate_t_arr = grid_model._interp(rate_trajs, dur_s, new_dt_s=0.002)

grid_overall = grid_model._overall(dist_trajs,
                                   rate_trajs, 240, 0.1,
                                   1, 1, 5, 20, dur_s)[0, :, 0]

trains, phases, phase_loc = precession_spikes(grid_overall,
                                               dur_s=2,
                                               shuffle=False,
                                               n_sim=5)

means = [np.mean(i) for i in phases]
repeated = np.repeat(means, 100)

# plotting

plt.close('all')
sns.reset_orig()
sns.set(style='dark', palette='deep', font='Arial',
        font_scale=1, color_codes=True)
cmap = sns.color_palette('RdYlBu_r', as_cmap=True)
f1, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, sharex=True,
                                        gridspec_kw={'height_ratios':[1.8,1,1,1]},
                                        figsize=(6, 8))

ax1.imshow(grid_rate[80:120,:80],cmap=cmap, extent=[0,2,1,0], aspect='auto')
ax1.set_xticklabels([])
ax1.set_yticklabels([])
ax1.set_ylabel('Grid field')

ax2.plot(rate_t_arr, grid_overall)
ax2.set_ylabel('Frequency (Hz)')
    
ax3.eventplot(np.array(trains[:5]), linewidth=0.7, linelengths=0.5)
ax3.set_yticklabels([])
ax3.set_ylabel('Spike trains')

ax4.plot(np.arange(0, 2, 2/2000), repeated/180)
ax4.set_ylim([0, 2])
ax4.set_xlabel('Time (s)')
ax4.set_ylabel('Phases (\u03C0)')

xpos = np.arange(0, dur_s+0.1, 0.1)
for xc in xpos:
    ax2.axvline(xc, color='0.5', linestyle='-.', linewidth=0.5)
    ax3.axvline(xc, color="0.5", linestyle='-.', linewidth=0.5)

f1.tight_layout()

# save_dir = '/home/baris/paper/figures/'
# f1.savefig(save_dir+'figure01_D.eps', dpi=200)
# f1.savefig(save_dir+'figure01_D.png', dpi=200)


# =============================================================================
# 1E
# =============================================================================

spacing = 40
pos_peak = [100, 100]
orientation = 30
dur = 5
shuffle = True

grid_rate = grid_model._grid_maker(spacing,
                             orientation, pos_peak).reshape(200, 200, 1)

grid_rates = np.append(grid_rate, grid_rate, axis=2)
spacings = [spacing, spacing]
grid_dist = grid_model._rate2dist(grid_rates,
                                  spacings)[:, :, 0].reshape(200, 200, 1)
trajs = np.array([50])
dist_trajs = grid_model._draw_traj(grid_dist, 1, trajs, dur_ms=5000)
rate_trajs = grid_model._draw_traj(grid_rate, 1, trajs, dur_ms=5000)
rate_trajs, rate_t_arr = grid_model._interp(rate_trajs, 5, new_dt_s=0.002)

grid_overall = grid_model._overall(dist_trajs,
                             rate_trajs, 180, 0.1, 1, 1, 5, 20, 5)[0, :, 0]
trains, phases, phase_loc = precession_spikes(grid_overall, shuffle=shuffle)


# plotting
rate = grid_rate.reshape(200, 200)
cmap = sns.color_palette('RdYlBu_r', as_cmap=True)
cmap2 = sns.color_palette('RdYlBu_r', as_cmap=True)
f2, (ax1, ax2) = plt.subplots(2, 1, sharex=False,
                              gridspec_kw={'height_ratios': [1, 2]},
                              figsize=(7, 9))
# f2.tight_layout(pad=0.1)
im2 = ax2.imshow(phase_loc, aspect=1/7, cmap=cmap, extent=[0, 100, 720, 0])
ax2.set_ylim((0, 720))
im1 = ax1.imshow(rate[50:150, :], cmap=cmap2)
ax1.set_xticklabels([])
ax1.set_yticklabels([])
ax1.set_title(f'\u0394= {spacing} cm    ' +
              f'[$x_{0}$ $y_{0}$]={(100-np.array(pos_peak))}     ' +
              f'\u03A8={orientation} degree', loc='center')
ax2.set_xlabel('Position (cm)')
ax2.set_ylabel('Theta phase (deg)')
f2.subplots_adjust(right=0.8)
# cax = f2.add_axes([0.60,0.16,0.015,0.35])
cax = f2.add_axes([0.80, 0.16, 0.025, 0.35])
cbar = f2.colorbar(im2, cax=cax)
cbar.set_label('Hz', labelpad=15, rotation=270)

# save_dir = '/home/baris/paper/figures/'
# f2.savefig(save_dir+'figure01_E.eps', dpi=200)
# f2.savefig(save_dir+'figure01_E.png', dpi=200)

# =============================================================================
# =============================================================================
# # Figure 01 D and E
# =============================================================================
# =============================================================================
