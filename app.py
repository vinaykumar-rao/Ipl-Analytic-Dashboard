from html import escape
import pandas as pd
import plotly.express as px
import streamlit as st
from pathlib import Path
from champion_photos import PHOTOS

ROOT = Path(__file__).resolve().parent
BOWLER_WICKETS = {'caught', 'bowled', 'lbw', 'caught and bowled', 'stumped', 'hit wicket'}
ALIASES = {'Delhi Daredevils': 'Delhi Capitals', 'Kings XI Punjab': 'Punjab Kings',
           'Royal Challengers Bangalore': 'Royal Challengers Bengaluru',
           'Rising Pune Supergiants': 'Rising Pune Supergiant'}

def prepare(matches, deliveries):
    m, d = matches.copy(), deliveries.copy()
    required_m = {'id', 'date', 'team1', 'team2', 'winner', 'match_type', 'venue', 'result'}
    required_d = {'match_id', 'inning', 'over', 'batter', 'bowler', 'batsman_runs', 'total_runs',
                  'extra_runs', 'extras_type', 'dismissal_kind', 'is_wicket', 'batting_team', 'bowling_team'}
    for frame, required, label in [(m, required_m, 'matches.csv'), (d, required_d, 'deliveries.csv')]:
        missing = required - set(frame.columns)
        if missing:
            raise ValueError(f'{label} is missing columns: {", ".join(sorted(missing))}.')
        if frame.empty:
            raise ValueError(f'{label} is empty.')
    if m.id.isna().any() or m.id.duplicated().any():
        raise ValueError('Match IDs must be present and unique.')
    m['date'] = pd.to_datetime(m.date, errors='raise')
    m['season'] = m.date.dt.year
    for col in ['inning', 'over', 'batsman_runs', 'total_runs', 'extra_runs', 'is_wicket']:
        d[col] = pd.to_numeric(d[col], errors='raise')
        if d[col].isna().any() or (d[col] < 0).any() or (d[col] % 1 != 0).any():
            raise ValueError(f'Delivery column {col} must contain nonnegative integers.')
    if d[['batter', 'bowler', 'batting_team', 'bowling_team']].isna().any().any():
        raise ValueError('Delivery player and team names cannot be missing.')
    if not d.match_id.isin(m.id).all():
        raise ValueError('Some deliveries have no matching match ID.')
    if not d.total_runs.eq(d.batsman_runs + d.extra_runs).all():
        raise ValueError('Total runs do not reconcile with batter runs plus extras.')
    for frame, columns in [(m, ['team1', 'team2', 'winner', 'toss_winner']), (d, ['batting_team', 'bowling_team'])]:
        for col in columns:
            if col in frame:
                frame[col] = frame[col].replace(ALIASES)
    d = d.merge(m[['id', 'season']], left_on='match_id', right_on='id', validate='many_to_one').drop(columns='id')
    d['extras_type'] = d.extras_type.fillna('').str.lower().str.strip()
    d['dismissal_kind'] = d.dismissal_kind.fillna('').str.lower().str.strip()
    d['ball_faced'] = d.extras_type.ne('wides').astype(int)
    d['legal_ball'] = (~d.extras_type.isin(['wides', 'noballs'])).astype(int)
    d['bowler_wicket'] = d.dismissal_kind.isin(BOWLER_WICKETS).astype(int)
    d['conceded'] = d.batsman_runs + d.extra_runs.where(d.extras_type.isin(['wides', 'noballs']), 0)
    d['four'] = d.batsman_runs.eq(4).astype(int)
    d['six'] = d.batsman_runs.eq(6).astype(int)
    return m, d

def load_data():
    return prepare(pd.read_csv(ROOT / 'data/matches.csv'), pd.read_csv(ROOT / 'data/deliveries.csv'))

def batting(d, keys=None):
    keys = keys or ['batter']
    result = d.groupby(keys).agg(Runs=('batsman_runs', 'sum'), Balls=('ball_faced', 'sum'),
        Innings=('match_id', 'nunique'), Fours=('four', 'sum'), Sixes=('six', 'sum')).reset_index()
    result['Strike rate'] = (100 * result.Runs / result.Balls.replace(0, float('nan'))).round(2)
    return result.sort_values('Runs', ascending=False)

def bowling(d):
    result = d.groupby('bowler').agg(Wickets=('bowler_wicket', 'sum'), Balls=('legal_ball', 'sum'),
        Conceded=('conceded', 'sum'), Matches=('match_id', 'nunique')).reset_index()
    result['Economy'] = (6 * result.Conceded / result.Balls.replace(0, float('nan'))).round(2)
    return result.sort_values(['Wickets', 'Economy'], ascending=[False, True])

def filter_data(m, d, seasons):
    selected = m[m.season.isin(seasons)]
    return selected, d[d.match_id.isin(selected.id) & d.inning.le(2)]

st.set_page_config(page_title='Boundary | IPL Analytics', page_icon='🏏', layout='wide')
COLORS = ['#c7f36b', '#7baaff', '#efb56c', '#cf9cff', '#6ed6c1', '#fa8496']
st.markdown('''<style>
.stApp{background:#0b1118;color:#e9eef4}
[data-testid="stAppDeployButton"]{display:none!important}
header[data-testid="stHeader"]{display:none!important}
.block-container{max-width:1450px;padding-top:2rem;padding-bottom:3rem}
[data-testid="stSidebar"]{background:#111a24;border-right:1px solid #26313e}
h1,h2,h3{letter-spacing:-.035em} h1{font-size:clamp(2.2rem,5vw,4.3rem)!important}
.brand{font-weight:800;letter-spacing:.12em;color:#c7f36b;font-size:1.15rem;margin-bottom:1.5rem}
.hero{padding:40px 36px;border-radius:20px;min-height:270px;background-size:cover;background-position:center 55%;border:1px solid #34434d;margin-bottom:8px}
.hero h1{margin:10px 0;max-width:700px;color:white;line-height:1.08}
.hero p{color:#e1e8ec;font-size:1rem;max-width:510px}
.eyebrow{color:#c7f36b;font-size:.75rem;font-weight:700;letter-spacing:.15em}
[data-testid="stMetric"]{background:#151f2a;padding:20px;border-radius:14px;border:1px solid #2a3541}
[data-testid="stMetricValue"]{color:#c7f36b}
[data-testid="stPlotlyChart"]{border:1px solid #293442;border-radius:14px;overflow:hidden}
@media(max-width:700px){.hero{padding:24px 20px;min-height:230px}.block-container{padding:4rem 1rem 1rem}.hero p{font-size:.9rem}}

.champion-hero{display:grid;grid-template-columns:1fr 1.25fr;border:1px solid #34434d;border-radius:20px;overflow:hidden;margin:16px 0 26px;background:linear-gradient(125deg,#1a2936,#111923)}
.champion-copy{padding:32px;align-self:center}
.champion-copy h1{font-size:clamp(2rem,3.5vw,3.6rem)!important;line-height:1.08;margin:18px 0}
.champion-label{color:#c7f36b;font-size:1.1rem;font-weight:700;margin-bottom:18px}
.champion-copy p{color:#dde5ed;line-height:1.5;margin-bottom:10px}
.final-detail{font-size:.8rem;color:#a4b4c5;line-height:1.6}
.title-pill{display:inline-block;padding:7px 12px;border:1px solid #456340;border-radius:30px;color:#c7f36b;font-size:.8rem;margin-top:20px}
.champion-photo{display:flex;align-items:center;background:#101922;min-width:0}
.champion-photo img{width:100%;height:400px;object-fit:contain;display:block}
.photo-empty{font-size:5rem;text-align:center;width:100%}
.sidebar-champion{width:100%;height:165px;object-fit:cover;object-position:center 25%;border-radius:12px;margin-top:8px}
@media(max-width:900px){.champion-hero{grid-template-columns:1fr}.champion-photo{order:-1}.champion-copy{padding:24px}.champion-copy h1{font-size:2.2rem!important}}

[data-testid="stSidebar"] [data-testid="stButton"] button{min-height:44px;border-radius:12px;justify-content:flex-start;padding:10px 16px;border:1px solid #2b3a49;background:linear-gradient(120deg,#182431,#111c27);transition:background .15s,border-color .15s}
[data-testid="stSidebar"] [data-testid="stButton"] button:hover{border-color:#c7f36b;background:#223247}
[data-testid="stSidebar"] [data-testid="stButton"] button[kind="primary"]{background:linear-gradient(110deg,#c7f36b,#9edb5d);color:#102014;border-color:#c7f36b;box-shadow:0 4px 18px #9edb5d20;font-weight:700}
</style>''', unsafe_allow_html=True)


@st.cache_data(show_spinner=False)
def bundled():
    return load_data()


def chart(fig, title):
    fig.update_layout(title=dict(text=title, font=dict(size=18)), template='plotly_dark',
                      paper_bgcolor='#151f2a', plot_bgcolor='#151f2a', font_color='#dce4ed',
                      margin=dict(l=20, r=20, t=65, b=30), height=380,
                      colorway=COLORS, legend_title_text='')
    fig.update_xaxes(gridcolor='#293442')
    fig.update_yaxes(gridcolor='#293442')
    st.plotly_chart(fig, width='stretch', config={'displaylogo': False, 'scrollZoom': False})


def metrics(items):
    for col, (label, value) in zip(st.columns(len(items)), items):
        col.metric(label, value)


def export(df, filename, label='Download CSV'):
    st.download_button(label, df.to_csv(index=False).encode('utf-8-sig'), filename, 'text/csv')


with st.sidebar:
    st.markdown('<div class="brand">◉ BOUNDARY</div>', unsafe_allow_html=True)
    if 'page' not in st.session_state:
        st.session_state.page = 'Overview'
    navigation = [('Overview', '◈'), ('Top Batsmen', '🏏'),
                  ('Top Bowlers', '🎯'), ('Player Comparison', '⇄'), ('Batting lab', '▥'),
                  ('Bowling lab', '◎'), ('Data explorer', '▦')]
    if st.session_state.page == 'Teams & champions':
        st.session_state.page = 'Overview'
    def navigate(destination):
        st.session_state.page = destination
        st.session_state.season = None
    def choose_season():
        if st.session_state.season is not None:
            st.session_state.active_season = st.session_state.season
            st.session_state.page = 'Season Winner'
    for label, icon in navigation:
        st.button(f'{icon}  {label}', key=f'nav_{label}', width='stretch',
                  type='primary' if st.session_state.page == label else 'secondary',
                  on_click=navigate, args=(label,))
    page = st.session_state.page
    st.divider()
    try:
        matches, deliveries = bundled()
    except (ValueError, OSError, pd.errors.ParserError) as exc:
        st.error(str(exc))
        st.info('Place matches.csv and deliveries.csv in the data folder and restart.')
        st.stop()
    seasons = sorted(matches.season.unique().tolist())
    st.selectbox('Season', seasons, index=None, placeholder='Choose a year to see the winner', key='season', on_change=choose_season)
    season = st.session_state.get('active_season', seasons[-1])
    selected = [season]
    teams = sorted(set(matches.team1) | set(matches.team2))
    finals = matches[matches.season.eq(season) & matches.match_type.str.lower().eq('final')]
    final = finals.iloc[0] if not finals.empty else None
    champion = str(final.winner) if final is not None and pd.notna(final.winner) else None

m, d = filter_data(matches, deliveries, selected)
if page == 'Season Winner' and champion:
    opponent = final.team2 if final.team1 == champion else final.team1
    title_count = int((matches.match_type.str.lower().eq('final') & matches.season.le(season) & matches.winner.eq(champion)).sum())
    result = f'Won by {int(final.result_margin)} {final.result}' if pd.notna(final.result_margin) else 'Final winner'
    if pd.notna(final.get('method')):
        result += f' ({final.method})'
    photo = PHOTOS.get(season)
    photo_markup = f'<img src="{photo}" alt="{escape(champion)} winning IPL {season}">' if photo else '<div class="photo-empty">🏆</div>'
    st.markdown(f'''<section class="champion-hero">
<div class="champion-copy"><div class="eyebrow">INDIAN PREMIER LEAGUE / {season}</div>
<h1>{escape(champion)}</h1><div class="champion-label">🏆 Season champions</div>
<p>{escape(result)} against {escape(str(opponent))}</p>
<div class="final-detail">{escape(str(final.venue))}</div>
<div class="title-pill">{title_count} title{'s' if title_count != 1 else ''} through {season}</div></div>
<div class="champion-photo">{photo_markup}</div></section>''', unsafe_allow_html=True)
elif page == 'Season Winner':
    st.info('No recorded champion for this season.')
if page == 'Overview':
    st.markdown(f'''<div class="hero" style="background-image:linear-gradient(90deg,rgba(8,16,24,.93),rgba(8,16,24,.40)),url('https://images.unsplash.com/photo-1730739628981-6537b299aea3?auto=format&fit=crop&w=1800&q=85')">
<div class="eyebrow">BOUNDARY / IPL {season}</div><h1>The game behind<br>the numbers.</h1>
<p>Explore the runs, wickets and performances that shaped the season.</p></div>''', unsafe_allow_html=True)
st.subheader('Final match highlights' if page == 'Season Winner' else page)
st.caption(f'IPL {season}')
if m.empty or d.empty:
    st.info('No deliveries are available for this season.')
    st.stop()

bat = batting(d)
bowl = bowling(d)

if page == 'Overview':
    metrics([('Matches', f'{len(m):,}'), ('Runs incl. extras', f'{d.total_runs.sum():,}'),
             ('Batters', f'{d.batter.nunique():,}'), ('Boundary runs', f'{(d.four.sum()*4+d.six.sum()*6)/d.batsman_runs.sum():.1%}' if d.batsman_runs.sum() else 'N/A')])
    st.write('')
    left, right = st.columns([1.5, 1])
    trend = d.groupby('match_id').agg(Runs=('total_runs', 'sum'), Balls=('legal_ball', 'sum')).reset_index()
    trend = trend.merge(m[['id', 'date']], left_on='match_id', right_on='id').sort_values(['date', 'id'])
    trend['Match'] = range(1, len(trend) + 1)
    trend['Runs per over'] = 6 * trend.Runs / trend.Balls.replace(0, float('nan'))
    with left:
        chart(px.area(trend, x='Match', y='Runs per over', hover_data=['date'], color_discrete_sequence=COLORS), 'Scoring pace through the season')
    with right:
        top = bat.head(7).sort_values('Runs')
        chart(px.bar(top, x='Runs', y='batter', orientation='h', color_discrete_sequence=COLORS), 'Leading run scorers')
    left, right = st.columns(2)
    with left:
        outcomes = m['result'].fillna('Unknown').value_counts().rename_axis('Result').reset_index(name='Matches')
        chart(px.pie(outcomes, names='Result', values='Matches', hole=.65, color_discrete_sequence=COLORS), 'How matches were decided')
    with right:
        venues = m.venue.value_counts().head(7).sort_values().rename_axis('Venue').reset_index(name='Matches')
        chart(px.bar(venues, x='Matches', y='Venue', orientation='h', color_discrete_sequence=[COLORS[1]]), 'Most-used venue labels')
    st.info(f"{bat.iloc[0]['batter']} leads this selection with {int(bat.iloc[0]['Runs']):,} runs. {bowl.iloc[0]['bowler']} leads with {int(bowl.iloc[0]['Wickets']):,} bowler-attributed wickets.")

elif page == 'Batting lab':
    names = sorted(d.batter.unique())
    player = st.selectbox('Player', names, index=names.index(bat.iloc[0].batter))
    p = d[d.batter.eq(player)]
    row = bat[bat.batter.eq(player)].iloc[0]
    metrics([('Runs', f'{row.Runs:,}'), ('Balls faced', f'{row.Balls:,}'), ('Strike rate', f'{row["Strike rate"]:.2f}'), ('Fours / Sixes', f'{row.Fours} / {row.Sixes}')])
    left, right = st.columns([1.4, 1])
    with left:
        stats = batting(p, ['match_id']).merge(m[['id', 'date']], left_on='match_id', right_on='id').sort_values(['date', 'id'])
        stats['Innings'] = range(1, len(stats) + 1)
        chart(px.bar(stats, x='Innings', y='Runs', hover_data=['date', 'Balls', 'Strike rate'], color_discrete_sequence=COLORS), f'{player}: runs by innings')
    with right:
        distribution = p[p.ball_faced.eq(1)].batsman_runs.value_counts().sort_index().rename_axis('Runs off bat').reset_index(name='Balls')
        distribution['Runs off bat'] = distribution['Runs off bat'].astype(str)
        chart(px.pie(distribution, names='Runs off bat', values='Balls', hole=.65, color_discrete_sequence=COLORS), 'Scoring outcomes (balls faced)')
    minimum = 100
    st.caption('Scatter plot includes batters with at least 100 balls faced in this season.')
    chart(px.scatter(bat[bat.Balls.ge(minimum)], x='Runs', y='Strike rate', size='Balls', hover_name='batter', color='Strike rate', color_continuous_scale=['#7baaff', '#c7f36b']), 'Run volume vs strike rate')
    export(bat, 'batting_summary.csv', 'Download filtered batting summary')

elif page == 'Bowling lab':
    metrics([('Bowler wickets', f'{d.bowler_wicket.sum():,}'), ('Bowlers', f'{d.bowler.nunique():,}'),
             ('Legal balls', f'{d.legal_ball.sum():,}'), ('Runs charged', f'{d.conceded.sum():,}')])
    left, right = st.columns(2)
    with left:
        chart(px.bar(bowl.head(10).sort_values('Wickets'), x='Wickets', y='bowler', orientation='h', color_discrete_sequence=[COLORS[1]]), 'Leading wicket takers')
    with right:
        wickets = d[d.bowler_wicket.eq(1)].dismissal_kind.value_counts().rename_axis('Dismissal').reset_index(name='Wickets')
        chart(px.pie(wickets, names='Dismissal', values='Wickets', hole=.6, color_discrete_sequence=COLORS), 'Bowler dismissal types')
    name = st.selectbox('Bowler', sorted(d.bowler.unique()))
    st.dataframe(bowl[bowl.bowler.eq(name)], hide_index=True, width='stretch')
    minimum = 120
    st.caption('Economy ranking includes bowlers with at least 120 legal balls in this season.')
    st.dataframe(bowl[bowl.Balls.ge(minimum)].sort_values('Economy'), hide_index=True, width='stretch')
    st.caption('Economy = runs charged × 6 / legal balls. Byes, leg-byes and penalties are excluded from runs charged. Run-outs, retirements and obstructing the field are not bowler wickets.')
    export(bowl, 'bowling_summary.csv', 'Download filtered bowling summary')

elif page == 'Data explorer':
    metrics([('Source matches', f'{len(matches):,}'), ('Source deliveries', f'{len(deliveries):,}'), ('Selected deliveries', f'{len(d):,}'), ('Coverage', f'{min(seasons)}–{max(seasons)}')])
    kind = st.selectbox('Table', ['Matches', 'Deliveries', 'Batting summary', 'Bowling summary'])
    table = {'Matches': m, 'Deliveries': d, 'Batting summary': bat, 'Bowling summary': bowl}[kind]
    st.caption(f'{len(table):,} rows. Preview shows the first 1,000; download includes all filtered rows.')
    st.dataframe(table.head(1000), hide_index=True, width='stretch')
    export(table, kind.lower().replace(' ', '_') + '.csv')


elif page == 'Season Winner':
    if champion:
        final_balls = d[d.match_id.eq(final.id)]
        if final_balls.empty:
            st.info('Delivery statistics for this final are unavailable.')
        else:
            final_bat = batting(final_balls)
            final_bowl = bowling(final_balls)
            top_batters = final_bat[final_bat.Runs.eq(final_bat.Runs.max())]
            top_bowlers = final_bowl[final_bowl.Wickets.eq(final_bowl.Wickets.max())]
            left, right = st.columns(2)
            with left:
                with st.container(border=True):
                    st.markdown('### 🏏 Top batter in the final')
                    for _, player in top_batters.iterrows():
                        st.subheader(player.batter)
                        metrics([('Runs', int(player.Runs)), ('Balls faced', int(player.Balls)), ('Strike rate', f'{player["Strike rate"]:.2f}')])
            with right:
                with st.container(border=True):
                    st.markdown('### 🎯 Top bowler in the final')
                    for _, player in top_bowlers.iterrows():
                        st.subheader(player.bowler)
                        metrics([('Wickets', int(player.Wickets)), ('Runs conceded', int(player.Conceded)), ('Economy', f'{player.Economy:.2f}')])
            st.caption('Final match only, across both teams. Batters ranked by runs and bowlers by credited wickets; joint leaders are shown.')
            st.markdown(f'**Player of the match:** {final.player_of_match}')
            left, right = st.columns(2)
            with left:
                chart(px.bar(final_bat.head(5).sort_values('Runs'), x='Runs', y='batter', orientation='h', text='Runs', color_discrete_sequence=COLORS), 'Final: top five batting scores')
            with right:
                chart(px.bar(final_bowl.head(5).sort_values('Wickets'), x='Wickets', y='bowler', orientation='h', text='Wickets', color_discrete_sequence=[COLORS[1]]), 'Final: leading wicket takers')

elif page == 'Top Batsmen':
    leader = bat.iloc[0]
    metrics([('Leading batter', leader.batter), ('Runs', f'{leader.Runs:,}'),
             ('Strike rate', f'{leader["Strike rate"]:.2f}'), ('Sixes', int(leader.Sixes))])
    top = bat.head(10).sort_values('Runs')
    chart(px.bar(top, x='Runs', y='batter', orientation='h', text='Runs',
                 hover_data=['Balls', 'Strike rate', 'Fours', 'Sixes'], color_discrete_sequence=COLORS), 'Top 10 batsmen by runs')
    st.dataframe(bat.rename(columns={'batter': 'Player'}).reset_index(drop=True), hide_index=True, width='stretch')
    export(bat, f'top_batsmen_{season}.csv')

elif page == 'Top Bowlers':
    leader = bowl.iloc[0]
    metrics([('Leading bowler', leader.bowler), ('Wickets', int(leader.Wickets)),
             ('Economy', f'{leader.Economy:.2f}'), ('Legal balls', int(leader.Balls))])
    top = bowl.head(10).sort_values('Wickets')
    chart(px.bar(top, x='Wickets', y='bowler', orientation='h', text='Wickets',
                 hover_data=['Balls', 'Economy', 'Conceded'], color_discrete_sequence=[COLORS[1]]), 'Top 10 bowlers by wickets')
    st.dataframe(bowl.rename(columns={'bowler': 'Player'}).reset_index(drop=True), hide_index=True, width='stretch')
    export(bowl, f'top_bowlers_{season}.csv')

elif page == 'Player Comparison':
    mode = st.selectbox('Compare performance', ['Batting', 'Bowling'], key='comparison_mode')
    table = bat.rename(columns={'batter': 'Player'}) if mode == 'Batting' else bowl.rename(columns={'bowler': 'Player'})
    names = sorted(table.Player.tolist())
    if len(names) < 2:
        st.info('At least two players are needed for a comparison in this season.')
        st.stop()
    left, right = st.columns(2)
    with left:
        first = st.selectbox('First player', names, index=names.index(table.iloc[0].Player), key=f'first_{mode}')
    with right:
        others = [name for name in names if name != first]
        second = st.selectbox('Second player', others, index=others.index(table[table.Player.ne(first)].iloc[0].Player), key=f'second_{mode}')
    comparison = table.set_index('Player').loc[[first, second]].reset_index()
    st.caption(f'Both players are compared over IPL {season}. Counts show opportunity; rates show scoring or bowling efficiency. No minimum-ball filter is applied to this direct comparison.')
    primary, rate = ('Runs', 'Strike rate') if mode == 'Batting' else ('Wickets', 'Economy')
    for column, (_, row) in zip(st.columns(2), comparison.iterrows()):
        with column:
            with st.container(border=True):
                st.subheader(row.Player)
                st.metric(primary, f'{int(row[primary]):,}')
                st.metric(rate, f'{row[rate]:.2f}' if pd.notna(row[rate]) else 'N/A')
                st.caption(f'{int(row.Balls):,} {"balls faced" if mode == "Batting" else "legal balls bowled"}')
    left, right = st.columns(2)
    with left:
        chart(px.bar(comparison, x='Player', y=primary, color='Player', text=primary, color_discrete_sequence=COLORS), f'{primary} in the same season')
    with right:
        valid = comparison.dropna(subset=[rate])
        if valid.empty:
            st.info(f'{rate} is unavailable because neither player has a nonzero ball count.')
        else:
            chart(px.bar(valid, x='Player', y=rate, color='Player', text=rate, color_discrete_sequence=COLORS), f'{rate} — {"higher" if mode == "Batting" else "lower"} is better')
    st.dataframe(comparison, hide_index=True, width='stretch')
    if mode == 'Batting':
        boundaries = comparison.melt(id_vars='Player', value_vars=['Fours', 'Sixes'], var_name='Boundary', value_name='Count')
        chart(px.bar(boundaries, x='Boundary', y='Count', color='Player', barmode='group', text='Count', color_discrete_sequence=COLORS), 'Boundary comparison')
    else:
        kinds = d[d.bowler.isin([first, second]) & d.bowler_wicket.eq(1)].groupby(['bowler', 'dismissal_kind']).size().reset_index(name='Wickets')
        if not kinds.empty:
            chart(px.bar(kinds, x='dismissal_kind', y='Wickets', color='bowler', barmode='group', color_discrete_sequence=COLORS), 'How they took wickets')
    export(comparison, f'{mode.lower()}_comparison_{season}.csv', 'Download player comparison')
