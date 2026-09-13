"""Run the portfolio analysis without starting a dashboard or web server."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from analytics import ROOT, load_data, filter_data, batting, bowling


def main():
    matches, deliveries = load_data()
    m, d = filter_data(matches, deliveries, sorted(matches.season.unique()))
    bat, bowl = batting(d), bowling(d)
    finals = m[m.match_type.eq('Final')]
    titles = finals.winner.value_counts().rename_axis('Team').reset_index(name='Titles')
    trend = d.groupby('season').agg(Runs=('total_runs', 'sum'), Legal_balls=('legal_ball', 'sum')).reset_index()
    trend['Runs_per_over'] = (trend.Runs * 6 / trend.Legal_balls).round(2)
    output = ROOT / 'reports'
    output.mkdir(exist_ok=True)
    for name, table in [('batting', bat), ('bowling', bowl), ('titles', titles), ('season_trends', trend)]:
        table.to_csv(output / f'{name}.csv', index=False)

    plt.rcParams.update({'font.family': 'DejaVu Sans', 'text.color': '#e9eef4',
                         'axes.labelcolor': '#a9b6c5', 'xtick.color': '#a9b6c5', 'ytick.color': '#a9b6c5'})
    fig, axes = plt.subplots(2, 2, figsize=(15, 9), facecolor='#0b1118', layout='constrained')
    fig.suptitle('BOUNDARY  /  IPL 2008–2024', fontsize=23, fontweight='bold', color='#c7f36b')
    for ax in axes.flat:
        ax.set_facecolor('#151f2a')
        ax.spines[['top', 'right']].set_visible(False)
        ax.spines[['left', 'bottom']].set_color('#344153')
        ax.tick_params(labelsize=9)
    top = bat.head(8).sort_values('Runs')
    axes[0, 0].barh(top.batter, top.Runs, color='#c7f36b')
    axes[0, 0].set_title('Leading run scorers', loc='left', pad=15, color='#e9eef4')
    axes[0, 0].set_xlabel('Batter runs')
    top = bowl.head(8).sort_values('Wickets')
    axes[0, 1].barh(top.bowler, top.Wickets, color='#7baaff')
    axes[0, 1].set_title('Leading wicket takers', loc='left', pad=15, color='#e9eef4')
    axes[0, 1].set_xlabel('Bowler-attributed wickets')
    axes[1, 0].plot(trend.season, trend.Runs_per_over, color='#c7f36b', marker='o', linewidth=2)
    axes[1, 0].set_title('Scoring pace by season', loc='left', pad=15, color='#e9eef4')
    axes[1, 0].set_ylabel('Runs per legal over, including extras')
    axes[1, 0].set_xticks([2008, 2012, 2016, 2020, 2024])
    ordered = titles.sort_values('Titles')
    axes[1, 1].barh(ordered.Team, ordered.Titles, color='#cf9cff')
    axes[1, 1].set_title('Championships from recorded finals', loc='left', pad=15, color='#e9eef4')
    axes[1, 1].set_xlabel('Titles')
    fig.savefig(output / 'analysis-overview.png', dpi=150, facecolor=fig.get_facecolor())
    plt.close(fig)
    leader, wicket_leader = bat.iloc[0], bowl.iloc[0]
    report = f'''# IPL analysis findings

Generated from the bundled Kaggle snapshot by `python analyze.py`.

## Scope

{len(m):,} matches across {m.season.nunique()} seasons ({m.season.min()}–{m.season.max()}).
{len(deliveries):,} raw delivery records; {len(d):,} records after excluding super overs.

## Findings

- **{leader.batter}** leads the run table with **{leader.Runs:,} runs**.
- **{wicket_leader.bowler}** leads with **{wicket_leader.Wickets:,} bowler-attributed wickets**.
- Scoring pace was **{trend.iloc[0].Runs_per_over:.2f}** runs per legal over in {int(trend.iloc[0].season)} and **{trend.iloc[-1].Runs_per_over:.2f}** in {int(trend.iloc[-1].season)}.
- Fours and sixes account for **{(d.four.sum()*4+d.six.sum()*6)/d.batsman_runs.sum():.1%}** of batter runs.
- **{', '.join(titles[titles.Titles.eq(titles.Titles.max())].Team)}** share the most titles in this snapshot, with **{titles.Titles.max()} each**.

![IPL analysis overview](analysis-overview.png)

## Interpretation

Career totals reflect opportunity as well as performance. Compare strike rate and economy alongside balls faced or bowled, and apply minimum-ball thresholds when comparing players.
Seasonal scoring differences are descriptive. This analysis does not establish causes such as venue conditions or rule changes.

## Reproduce

Run `python analyze.py` from the repository after installing requirements. The four adjacent CSVs contain the underlying aggregate tables. See the README for definitions, exclusions and source attribution.
'''
    (output / 'findings.md').write_text(report, encoding='utf-8')
    print(f'Analysis complete: {output}')


if __name__ == '__main__':
    main()
