import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from scipy.optimize import fsolve
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Ellipse

# Constants
g_earth = 9.81  # m/s²
g_mars = 3.71   # m/s²
g_moon = 1.62   # m/s²
rho_earth = 1.225     # kg/m³
rho_mars_actual = 0.020  # kg/m³, actual Mars
rho_moon_actual = 0.0   # kg/m³, negligible on Moon
L = 250         # m, track length
m = 70          # kg, rider mass
m_suit = 80     # kg, with spacesuit
CdA = 0.3       # m², drag area
Cr = 0.005      # rolling resistance coefficient
v_earth_kph = 50  # kph
v_earth = v_earth_kph / 3.6  # m/s

# Power on Earth
P_earth = 0.5 * CdA * rho_earth * v_earth**3 + m * g_earth * Cr * v_earth
print(f"Power on Earth at {v_earth_kph} kph: {P_earth:.2f} W")

# Function to solve for velocity given power, gravity, rho, mass
def power_eq(v, P, g, rho, mass):
    return 0.5 * CdA * rho * v**3 + mass * g * Cr * v - P

# Hypothetical: Earth air density
v_mars_hyp = fsolve(power_eq, v_earth, args=(P_earth, g_mars, rho_earth, m))[0]
v_mars_hyp_kph = v_mars_hyp * 3.6
v_moon_hyp = fsolve(power_eq, v_earth, args=(P_earth, g_moon, rho_earth, m))[0]
v_moon_hyp_kph = v_moon_hyp * 3.6

# Actual: Real air densities, with spacesuit
v_mars_real = fsolve(power_eq, v_earth, args=(P_earth, g_mars, rho_mars_actual, m_suit))[0]
v_mars_real_kph = v_mars_real * 3.6
v_moon_real = fsolve(power_eq, v_earth, args=(P_earth, g_moon, rho_moon_actual, m_suit))[0]
v_moon_real_kph = v_moon_real * 3.6

print(f"Hypothetical (Earth air) - Mars: {v_mars_hyp_kph:.2f} kph, Moon: {v_moon_hyp_kph:.2f} kph")
print(f"Actual (real air) - Mars: {v_mars_real_kph:.2f} kph, Moon: {v_moon_real_kph:.2f} kph")

# Time for 10 laps on Earth
t_earth = 10 * L / v_earth

# Laps in that time
laps_mars_hyp = (v_mars_hyp * t_earth) / L
laps_moon_hyp = (v_moon_hyp * t_earth) / L
laps_mars_real = (v_mars_real * t_earth) / L
laps_moon_real = (v_moon_real * t_earth) / L

# Simulate acceleration from rest
def simulate_race(P, g, rho, mass, L, total_time=180):
    dt = 0.1  # s
    t = 0
    v = 0
    distance = 0
    times = []
    velocities = []
    distances = []
    laps = []
    while t < total_time and distance < 10 * L:  # up to 10 laps
        drag = 0.5 * CdA * rho * v**2
        rolling = mass * g * Cr
        if v > 0:
            a = (P / v - drag - rolling) / mass
        else:
            a = (P / 0.1 - drag - rolling) / mass  # small v to avoid div0
        v += a * dt
        if v < 0: v = 0
        distance += v * dt
        t += dt
        times.append(t)
        velocities.append(v * 3.6)  # kph
        distances.append(distance)
        laps.append(distance / L)
    return np.array(times), np.array(velocities), np.array(laps), np.array(distances)

# Simulate for each scenario
t_hyp_earth, v_hyp_earth, laps_hyp_earth, dist_hyp_earth = simulate_race(P_earth, g_earth, rho_earth, m, L)
t_hyp_mars, v_hyp_mars, laps_hyp_mars, dist_hyp_mars = simulate_race(P_earth, g_mars, rho_earth, m, L)
t_hyp_moon, v_hyp_moon, laps_hyp_moon, dist_hyp_moon = simulate_race(P_earth, g_moon, rho_earth, m, L)

t_real_earth, v_real_earth, laps_real_earth, dist_real_earth = simulate_race(P_earth, g_earth, rho_earth, m, L)
t_real_mars, v_real_mars, laps_real_mars, dist_real_mars = simulate_race(P_earth, g_mars, rho_mars_actual, m_suit, L)
t_real_moon, v_real_moon, laps_real_moon, dist_real_moon = simulate_race(P_earth, g_moon, rho_moon_actual, m_suit, L)

# 3D Plots side by side
fig = plt.figure(figsize=(14, 10))

# Hypothetical plot
ax1 = fig.add_subplot(221, projection='3d')
ax1.plot(t_hyp_earth, laps_hyp_earth, v_hyp_earth, label='Earth', color='blue')
ax1.plot(t_hyp_mars, laps_hyp_mars, v_hyp_mars, label='Mars', color='red')
ax1.plot(t_hyp_moon, laps_hyp_moon, v_hyp_moon, label='Moon', color='gray')
ax1.set_xlabel('Time (s)')
ax1.set_ylabel('Laps')
ax1.set_zlabel('Speed (kph)')
ax1.set_title('Hypothetical: Earth Air Density\n(Acceleration from Rest)')
ax1.legend()

# Actual plot
ax2 = fig.add_subplot(222, projection='3d')
ax2.plot(t_real_earth, laps_real_earth, v_real_earth, label='Earth', color='blue')
ax2.plot(t_real_mars, laps_real_mars, v_real_mars, label='Mars', color='red')
ax2.plot(t_real_moon, laps_real_moon, v_real_moon, label='Moon', color='gray')
ax2.set_xlabel('Time (s)')
ax2.set_ylabel('Laps')
ax2.set_zlabel('Speed (kph)')
ax2.set_title('Actual: Real Air Densities\n(Spacesuit Cyclists, Acceleration)')
ax2.legend()

# Velodrome plots
a = 50  # semi-major axis
b = 25  # semi-minor axis
width = 2 * a
height = 2 * b

# Hypothetical velodrome
ax3 = fig.add_subplot(223)
ax3.add_patch(Ellipse((0, 0), width, height, edgecolor='k', facecolor='none', linewidth=2))
ax3.axis('equal')
ax3.set_xlim(-60, 60)
ax3.set_ylim(-35, 35)
ax3.set_title('Earth-Pressured Velodrome')
ax3.text(0, 0, 'Air drag dominates\nSimilar speeds\non all planets', ha='center', va='center', fontsize=10, bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
scatters_hyp = [ax3.scatter([], [], color=c, s=100) for c in ['blue', 'red', 'gray']]

# Actual velodrome
ax4 = fig.add_subplot(224)
ax4.add_patch(Ellipse((0, 0), width, height, edgecolor='k', facecolor='none', linewidth=2))
ax4.axis('equal')
ax4.set_xlim(-60, 60)
ax4.set_ylim(-35, 35)
ax4.set_title('Spacesuit Velodrome')
ax4.text(0, 0, 'Lower air density\nEnabled higher speeds\nMoon: extreme speeds!', ha='center', va='center', fontsize=10, bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
scatters_real = [ax4.scatter([], [], color=c, s=100) for c in ['blue', 'red', 'gray']]

# Animation update function
def update(frame):
    dists_hyp = [dist_hyp_earth, dist_hyp_mars, dist_hyp_moon]
    dists_real = [dist_real_earth, dist_real_mars, dist_real_moon]
    for i, (dist, scatter) in enumerate(zip(dists_hyp, scatters_hyp)):
        if frame < len(dist):
            d = dist[frame]
        else:
            d = dist[-1]
        theta = (d % L) / L * 2 * np.pi
        x = a * np.cos(theta)
        y = b * np.sin(theta)
        scatter.set_offsets([[x, y]])
    for i, (dist, scatter) in enumerate(zip(dists_real, scatters_real)):
        if frame < len(dist):
            d = dist[frame]
        else:
            d = dist[-1]
        theta = (d % L) / L * 2 * np.pi
        x = a * np.cos(theta)
        y = b * np.sin(theta)
        scatter.set_offsets([[x, y]])
    return scatters_hyp + scatters_real

# Create animation
ani = FuncAnimation(fig, update, frames=len(t_hyp_earth), interval=50, blit=True)

# Constants legend - centered in middle of screen
constants_text = f"""Constants Legend:
g_earth = {g_earth} m/s², g_mars = {g_mars} m/s², g_moon = {g_moon} m/s²
rho_earth = {rho_earth} kg/m³, rho_mars = {rho_mars_actual} kg/m³, rho_moon = {rho_moon_actual} kg/m³
L = {L} m, m = {m} kg, m_suit = {m_suit} kg
CdA = {CdA} m², Cr = {Cr}, v_earth = {v_earth_kph} kph, Power on Earth: {P_earth:.2f} W
Equation: Power = 0.5 * CdA * ρ * v³ + m * g * Cr * v + m * a * v"""
fig.text(0.5, 0.5, constants_text, ha='center', va='center', fontsize=9, transform=fig.transFigure, bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.9, edgecolor='black', linewidth=2))

plt.tight_layout()
plt.show()
