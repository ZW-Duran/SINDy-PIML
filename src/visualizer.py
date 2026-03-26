import matplotlib.pyplot as plt
import numpy as np

def plot_corner_dynamics(df_corner, X_simulated, title_prefix="GT4"):
    """
    Graph specific corner dynamics to verify SINDy model performance.
    
    Parameters:
    df_corner: pandas DataFrame, sliced corner data
    X_simulated: numpy array, predicted states from SINDy simulate()
    title_prefix: str, vehicle model prefix
    """
    # Extract time axis (relative to slice start)
    t = df_corner['Time'].values
    t = t - t[0]
    
    # Extract true data
    r_true = df_corner['ROTY'].values     # True yaw rate
    ay_true = df_corner['G_LAT'].values   # True lateral G-force
    
    # Extract simulated data (assuming index 3 is ROTY, index 1 is G_LAT)
    r_sim = X_simulated[:, 3]
    ay_sim = X_simulated[:, 1]
    
    # Driver inputs
    steer = df_corner['STEERANGLE'].values
    brake = df_corner['BRAKE'].values
    throttle = df_corner['THROTTLE'].values
    
    # Start plotting (two subplots: top for dynamics, bottom for inputs)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
    
    ax1.plot(t, r_true, 'k-', linewidth=2, label='Telemetry (True Yaw Rate)')
    ax1.plot(t, r_sim, 'r--', linewidth=2, label='SINDy ODE (Predicted Yaw Rate)')
    
    ax1.set_title(f"{title_prefix} - Cornering Dynamics Verification", fontsize=14, fontweight='bold')
    ax1.set_ylabel("Yaw Rate (rad/s)", fontsize=12)
    ax1.grid(True, linestyle=':', alpha=0.7)
    ax1.legend(loc='upper right')
    
    ax2.plot(t, steer, 'b-', label='Steer Angle (rad)')
    
    # different y-axis for throttle and brake
    ax2_twin = ax2.twinx()
    ax2_twin.plot(t, throttle, 'g-', alpha=0.6, label='Throttle (%)')
    ax2_twin.plot(t, brake, 'r-', alpha=0.6, label='Brake (%)')
    
    ax2.set_xlabel("Time (s) from Corner Entry", fontsize=12)
    ax2.set_ylabel("Steering", color='b', fontsize=12)
    ax2_twin.set_ylabel("Pedals (%)", color='k', fontsize=12)
    
    # merge
    lines_1, labels_1 = ax2.get_legend_handles_labels()
    lines_2, labels_2 = ax2_twin.get_legend_handles_labels()
    ax2.legend(lines_1 + lines_2, labels_1 + labels_2, loc='upper right')
    
    plt.tight_layout()
    plt.show()