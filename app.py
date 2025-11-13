import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
import ast

st.set_page_config(page_title="Electric Phactory Winter Sim League", layout="wide")

st.title("⚡ Electric Phactory Winter Sim League")
st.markdown("by Corey Gunter")

# Mobile-friendly meta + CSS
_RESPONSIVE_CSS = '''
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
    .resp-metrics { display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; align-items:stretch; }
    .metric-box { background: var(--background,#fff); border-radius:10px; padding:10px 12px; box-shadow: 0 0 0 1px rgba(0,0,0,0.03); }
    .metric-title { font-size:12px; color: #6c757d; margin:0; }
    .metric-value { font-size:20px; font-weight:600; margin-top:6px; }
    @media (max-width: 780px) { .resp-metrics { grid-template-columns: repeat(2,1fr); } }
    @media (max-width: 420px) { .resp-metrics { grid-template-columns: 1fr; } .block-container { padding-left: 12px; padding-right:12px; } }
</style>
'''

def _render_metrics_html(items, cols=3):
        # items: list of (title, value)
        html = _RESPONSIVE_CSS
        html += '<div class="resp-metrics">'
        for title, value in items:
                html += f'<div class="metric-box"><div class="metric-title">{title}</div><div class="metric-value">{value}</div></div>'
        html += '</div>'
        return html

# Load data from CSV
DATA_FILE = Path(__file__).parent / "data" / "round_tracking.csv"

def load_round_data():
    """Load round data from CSV file."""
    if DATA_FILE.exists():
        data = {}
        with open(DATA_FILE, 'r') as f:
            for line in f:
                line = line.strip()
                if ',' in line:
                    key, value = line.split(',', 1)
                    data[key] = value
        return data
    return None

# Sidebar navigation (compact hamburger-style selector)
with st.sidebar:
    st.header("Navigation")
    # Small hamburger-style header followed by a compact selectbox
    st.markdown("### ☰ Menu")
    page = st.selectbox("", ["Dashboard", "Hole Analysis", "Round Notes", "Season"])  

# Load data
round_data = load_round_data()

def _parse_numeric_list(data_dict, key):
    """Parse a CSV-stored list into a list of ints."""
    raw = data_dict.get(key, '[]')
    # Handle pandas NaN and None
    try:
        import pandas as _pd
        if isinstance(raw, float) and _pd.isna(raw):
            return []
    except Exception:
        pass

    # If it's already a list, use it; otherwise try to coerce to a list
    parts = []
    if isinstance(raw, list):
        parts = raw
    else:
        s = str(raw)
        # Try to parse Python literal like "[1,2,3]"
        try:
            lst = ast.literal_eval(s)
            if isinstance(lst, list):
                parts = lst
            else:
                parts = [p.strip() for p in s.split(',') if p.strip() != '']
        except Exception:
            parts = [p.strip() for p in s.split(',') if p.strip() != '']

    parsed = []
    for v in parts:
        try:
            parsed.append(int(str(v).strip()))
        except Exception:
            # skip non-numeric entries
            pass
    return parsed

def _parse_str_list(data_dict, key):
    """Parse a CSV-stored list into a list of normalized strings."""
    raw = data_dict.get(key, '[]')
    # Handle pandas NaN and None
    try:
        import pandas as _pd
        if isinstance(raw, float) and _pd.isna(raw):
            return []
    except Exception:
        pass

    parts = []
    if isinstance(raw, list):
        parts = raw
    else:
        s = str(raw)
        try:
            lst = ast.literal_eval(s)
            if isinstance(lst, list):
                parts = lst
            else:
                parts = [p.strip() for p in s.split(',') if p.strip() != '']
        except Exception:
            parts = [p.strip() for p in s.split(',') if p.strip() != '']

    normalized = []
    for v in parts:
        val = str(v).strip().lower()
        if val in ('na', 'n/a'):
            normalized.append('-')
        else:
            normalized.append(val)
    return normalized

def load_rounds():
    """Load multiple rounds from `data/rounds.csv` if present."""
    ROUNDS_FILE = Path(__file__).parent / "data" / "rounds.csv"
    if ROUNDS_FILE.exists():
        try:
            df = pd.read_csv(ROUNDS_FILE)
            return df
        except Exception:
            return None
    return None

if page == "Dashboard":
    st.header("Dashboard")

    # Load season data
    rounds_df = load_rounds()
    if rounds_df is None or rounds_df.empty:
        st.info("No season data found (`data/rounds.csv`).")
    else:
        # Compute season metrics
        totals = []
        all_beers = []
        wins = 0
        losses = 0
        
        for idx, row in rounds_df.iterrows():
            r = row.to_dict()
            my_scores = _parse_numeric_list(r, 'my_scores')
            if my_scores:
                totals.append(sum(my_scores))
            
            beers_val = r.get('beers', 0)
            try:
                all_beers.append(int(beers_val))
            except:
                pass
            
            result = str(r.get('match_result', '')).lower().strip()
            if result == 'win':
                wins += 1
            elif result == 'loss':
                losses += 1
        
        rounds_played = len(totals)
        avg_score = sum(totals) / rounds_played if rounds_played > 0 else None
        best_score = min(totals) if totals else None
        avg_beers = sum(all_beers) / len(all_beers) if all_beers else None
        total_beers = sum(all_beers) if all_beers else 0
        total_matches = wins + losses
        win_loss_ratio = f"{wins}-{losses}" if total_matches > 0 else "0-0"

        # Top section: Key metrics (rendered responsively)
        metrics_items = [
            ("Rounds Played", rounds_played),
            ("Average Score", f"{avg_score:.1f}" if avg_score is not None else "--"),
            ("Best Score", f"{best_score}" if best_score is not None else "--"),
            ("Average Beers", f"{avg_beers:.1f}" if avg_beers is not None else "--"),
            ("Total Beers", total_beers),
            ("Win/Loss Ratio", win_loss_ratio)
        ]
        st.markdown(_render_metrics_html(metrics_items), unsafe_allow_html=True)

        st.divider()

        # Bottom section: Rounds table
        st.subheader("Season Rounds")
        display = []
        for idx, row in rounds_df.iterrows():
            r = row.to_dict()
            my_scores = _parse_numeric_list(r, 'my_scores')
            result_val = r.get('match_result')
            # Handle NaN or missing values - convert to string and check
            if result_val is None or (isinstance(result_val, float) and pd.isna(result_val)):
                result_str = 'N/A'
            else:
                result_str = str(result_val).strip().upper()

            # Temp and beers
            temp = r.get('outside_temp')
            beers = r.get('beers')
            try:
                beers_val = int(beers)
            except Exception:
                beers_val = beers

            display.append({
                'Week': r.get('week'),
                'Date': r.get('date'),
                'Temp': temp,
                'Course': r.get('course'),
                'Score': sum(my_scores) if my_scores else None,
                'Beers': beers_val,
                'Result': result_str
            })
        # Ensure column order: Week, Date, Temp, Course, Score, Beers, Result
        df_display = pd.DataFrame(display)
        cols = ['Week', 'Date', 'Temp', 'Course', 'Score', 'Beers', 'Result']
        cols = [c for c in cols if c in df_display.columns]
        st.dataframe(df_display[cols], use_container_width=True)

elif page == "Hole Analysis":
    st.header("Hole-by-Hole Analysis")
    
    # Load all rounds and create dropdown options
    rounds_df = load_rounds()
    if rounds_df is None or rounds_df.empty:
        st.info("No match data found (`data/rounds.csv`).")
    else:
        # Create dropdown options with match descriptions
        match_options = []
        for idx, row in rounds_df.iterrows():
            r = row.to_dict()
            week = r.get('week', 'N/A')
            date = r.get('date', 'N/A')
            course = r.get('course', 'N/A')
            opponent = r.get('opponent_name', 'N/A')
            match_label = f"Week {week} - {date} - {course} vs {opponent}"
            match_options.append((match_label, idx))
        
        # Dropdown to select a match
        selected_match_label = st.selectbox("Select a Match:", [opt[0] for opt in match_options])
        selected_idx = next(opt[1] for opt in match_options if opt[0] == selected_match_label)
        
        # Get the selected row data
        selected_row = rounds_df.iloc[selected_idx]
        r = selected_row.to_dict()
        
        hole_pars = _parse_numeric_list(r, 'hole_par')
        my_scores = _parse_numeric_list(r, 'my_scores')
        opponent_scores = _parse_numeric_list(r, 'opponent_scores')
        fairways = _parse_str_list(r, 'fairways')
        greens = _parse_str_list(r, 'greens')
        putts = _parse_numeric_list(r, 'putts')

        # Ensure all lists are the same length — truncate to the shortest
        lists = {
            'Par': hole_pars,
            'My Score': my_scores,
            'Opp Score': opponent_scores,
            'Fairway': fairways,
            'Green': greens,
            'Putts': putts
        }
        lengths = {k: len(v) for k, v in lists.items()}
        min_len = min(lengths.values()) if lengths else 0
        
        if min_len == 0:
            st.info("No hole data available for this match.")
        else:
            # Truncate all lists to the same (minimum) length
            hole_pars = hole_pars[:min_len]
            my_scores = my_scores[:min_len]
            opponent_scores = opponent_scores[:min_len]
            fairways = fairways[:min_len]
            greens = greens[:min_len]
            putts = putts[:min_len]

            # Top section: Stats (responsive)
            fairways_hit = sum(1 for f in fairways if f == 'y')
            fairway_attempts = len([f for f in fairways if f != '-'])
            greens_hit = sum(1 for g in greens if g == 'y')
            greens_total = len(greens)
            total_putts = sum(putts) if putts else 0

            stat_items = [
                ("Fairways Hit", f"{fairways_hit}/{fairway_attempts}"),
                ("Greens Hit", f"{greens_hit}/{greens_total}"),
                ("Total Putts", total_putts)
            ]
            st.markdown(_render_metrics_html(stat_items), unsafe_allow_html=True)

            st.divider()

            # Middle section: Hole data table
            st.subheader("Hole Details")
            df = pd.DataFrame({
                'Hole': list(range(1, min_len + 1)),
                'Par': hole_pars,
                'My Score': my_scores,
                'vs Par': [s - p for s, p in zip(my_scores, hole_pars)],
                'Opp Score': opponent_scores,
                'Fairway': fairways,
                'Green': greens,
                'Putts': putts
            })
            st.dataframe(df, use_container_width=True)

            st.divider()

            # Bottom section: Score vs Par scatter plot
            st.subheader("Score vs Par by Hole")
            fig = px.scatter(df, x='Hole', y='vs Par', 
                            title='Hole vs Par',
                            labels={'vs Par': 'Score vs Par'},
                            size='vs Par',
                            color='vs Par',
                            color_continuous_scale=['green', 'white', 'red'],
                            hover_data=['Par', 'My Score'])
            fig.add_hline(y=0, line_dash="dash", line_color="black", annotation_text="Par")
            st.plotly_chart(fig, use_container_width=True)

elif page == "Match Stats":
    st.header("Match Statistics")
    st.info("The Match Stats page has been removed. Use 'Hole Analysis' for per-match hole detail or 'Season' for aggregate stats.")

elif page == "Round Notes":
    st.header("Round Notes")
    rounds_df = load_rounds()
    if rounds_df is None or rounds_df.empty:
        st.info("No rounds found (`data/rounds.csv`).")
    else:
        # Build dropdown of matches
        match_options = []
        for idx, row in rounds_df.iterrows():
            r = row.to_dict()
            week = r.get('week', 'N/A')
            date = r.get('date', 'N/A')
            course = r.get('course', 'N/A')
            opponent = r.get('opponent_name', 'N/A')
            label = f"Week {week} - {date} - {course} vs {opponent}"
            match_options.append((label, week))

        selected_label = st.selectbox("Select a round:", [opt[0] for opt in match_options])
        selected_week = next(opt[1] for opt in match_options if opt[0] == selected_label)

        md_path = Path(__file__).parent / 'tracking' / f"week{selected_week}.md"
        if md_path.exists():
            try:
                content = md_path.read_text(encoding='utf-8')
                st.markdown(content, unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Failed to read notes for Week {selected_week}: {e}")
        else:
            st.info(f"No notes file found for Week {selected_week}. Create `{md_path}` to add notes.")

elif page == "Season":
    st.header("Season Overview")
    rounds_df = load_rounds()
    if rounds_df is None or rounds_df.empty:
        st.info("No multi-round data found. Create `data/rounds.csv` or add rounds.")
    else:
        # Compute totals for display
        display_rows = []
        for idx, row in rounds_df.iterrows():
            rowd = row.to_dict()
            my_scores = _parse_numeric_list(rowd, 'my_scores')
            opp_scores = _parse_numeric_list(rowd, 'opponent_scores')
            my_total = sum(my_scores) if my_scores else None
            opp_total = sum(opp_scores) if opp_scores else None
            display_rows.append({
                'index': idx,
                'week': rowd.get('week'),
                'date': rowd.get('date'),
                'course': rowd.get('course'),
                'my_total': my_total,
                'opp_total': opp_total,
                'result': rowd.get('match_result')
            })

        df_display = pd.DataFrame(display_rows)
        st.dataframe(df_display[['week','date','course','my_total','opp_total','result']], use_container_width=True)

        # Season-level charts: score trend and fairway % by week
        trend_rows = []
        for idx, row in rounds_df.iterrows():
            rowd = row.to_dict()
            my_scores = _parse_numeric_list(rowd, 'my_scores')
            opp_scores = _parse_numeric_list(rowd, 'opponent_scores')
            fairways = _parse_str_list(rowd, 'fairways')
            my_total = sum(my_scores) if my_scores else None
            opp_total = sum(opp_scores) if opp_scores else None
            fairway_attempts = len([f for f in fairways if f != '-'])
            fairways_hit = sum(1 for f in fairways if f == 'y')
            fairway_pct = (fairways_hit / fairway_attempts * 100) if fairway_attempts > 0 else None
            try:
                week_num = int(rowd.get('week'))
            except Exception:
                week_num = rowd.get('week')
            trend_rows.append({'week': week_num, 'my_total': my_total, 'opp_total': opp_total, 'fairway_pct': fairway_pct})

        trend_df = pd.DataFrame(trend_rows)
        if not trend_df.empty:
            # Sort by week if possible
            try:
                trend_df = trend_df.sort_values('week')
            except Exception:
                pass

            st.subheader("Season Trends")
            # Score trend (you vs opponent)
            fig_scores = px.line(trend_df, x='week', y=['my_total','opp_total'], markers=True,
                                labels={'value': 'Total Score', 'week': 'Week'},
                                title='Total Score by Week')
            st.plotly_chart(fig_scores, use_container_width=True)

            # Fairway percentage trend
            if 'fairway_pct' in trend_df.columns and trend_df['fairway_pct'].notnull().any():
                fig_fw = px.bar(trend_df, x='week', y='fairway_pct', labels={'fairway_pct': 'Fairway %', 'week': 'Week'},
                                title='Fairway Hit % by Week')
                st.plotly_chart(fig_fw, use_container_width=True)

        # Allow selecting a round to view detail
        selected_idx = st.selectbox("Select round (index)", df_display['index'].tolist())
        selected_row = rounds_df.loc[selected_idx].to_dict()

        st.subheader(f"Match Detail — Week {selected_row.get('week')} — {selected_row.get('course')}")
        # Reuse existing display logic by turning selected_row into round_data
        round_data = selected_row
        # Ensure string fields are strings
        for k in ['hole_par','my_scores','opponent_scores','fairways','greens','putts']:
            if k in round_data and not isinstance(round_data[k], str):
                round_data[k] = str(round_data[k])

        # Show basic metrics
        hole_pars = _parse_numeric_list(round_data, 'hole_par')
        my_scores = _parse_numeric_list(round_data, 'my_scores')
        opponent_scores = _parse_numeric_list(round_data, 'opponent_scores')
        if hole_pars and my_scores and opponent_scores:
            st.write(f"**Your Score:** {sum(my_scores)} — **Opponent:** {sum(opponent_scores)}")
        st.write(f"**Date:** {round_data.get('date')}")
        st.write(f"**Outside Temp:** {round_data.get('outside_temp')}")
        st.write(f"**Beers:** {round_data.get('beers')}")

        # Show hole table
        fairways = _parse_str_list(round_data, 'fairways')
        greens = _parse_str_list(round_data, 'greens')
        putts = _parse_numeric_list(round_data, 'putts')
        min_len = min(len(hole_pars), len(my_scores), len(opponent_scores), len(fairways), len(greens), len(putts))
        if min_len > 0:
            df = pd.DataFrame({
                'Hole': list(range(1, min_len+1)),
                'Par': hole_pars[:min_len],
                'My Score': my_scores[:min_len],
                'Opp Score': opponent_scores[:min_len],
                'Fairway': fairways[:min_len],
                'Green': greens[:min_len],
                'Putts': putts[:min_len]
            })
            st.dataframe(df, use_container_width=True)
