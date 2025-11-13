import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)

def load_golf_data():
    """Load golf round data from CSV files."""
    csv_file = DATA_DIR / "golf_rounds.csv"
    
    if csv_file.exists():
        return pd.read_csv(csv_file)
    return pd.DataFrame()

def save_golf_data(df):
    """Save golf round data to CSV."""
    csv_file = DATA_DIR / "golf_rounds.csv"
    df.to_csv(csv_file, index=False)

def create_sample_data():
    """Create sample golf data for demonstration."""
    sample_data = {
        'date': pd.date_range('2024-01-01', periods=10),
        'course': ['Pinehurst', 'Torrey Pines', 'Augusta', 'Pebble Beach'] * 3,
        'score': [78, 82, 75, 88, 76, 81, 79, 84, 77, 83],
        'handicap': [5, 6, 4, 8, 5, 6, 5, 7, 5, 6]
    }
    return pd.DataFrame(sample_data)
