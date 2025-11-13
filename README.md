# Electric Phactory Winter Sim League

A data visualization application for tracking and analyzing league golf statistics using Python, Pandas, Plotly, and Streamlit.

## Features

- Track golf round statistics
- Visualize performance metrics with interactive charts
- Analyze trends and patterns in your game
- Compare rounds and courses

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment:
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the Streamlit application:
```bash
streamlit run app.py
```

The application will open in your default web browser at `http://localhost:8501`

## Project Structure

```
golf-stat-tracker/
├── app.py              # Main Streamlit application
├── data/               # Data storage directory
├── modules/            # Python modules for core functionality
│   ├── __init__.py
│   ├── data_loader.py
│   └── visualizer.py
└── requirements.txt    # Project dependencies
```

## Development

To contribute or modify the application:

1. Create a new branch for your feature
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## License

MIT License
