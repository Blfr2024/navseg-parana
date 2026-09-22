import pandas as pd

def evaluate_vts_safety(active_points, umbral_ukc_critico=0.60):
    df = pd.DataFrame(active_points)
    
    # Under Keel Clearance (Margen bajo quilla: profundidad de solera - calado)
    df["ukc"] = (df["channel_depth"] - df["draught"]).round(2)
    df["ukc_alert"] = df["ukc"] < umbral_ukc_critico
    
    return df