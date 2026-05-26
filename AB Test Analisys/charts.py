import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
from pathlib import Path
from statsmodels.stats.proportion import proportion_confint, proportions_ztest

# ── Setup ────────────────────────────────────────────────────────────────────
plt.rcParams.update({
    'font.family':     'DejaVu Sans',
    'font.size':       12,
    'figure.dpi':      150,
    'savefig.bbox':    'tight',
    'savefig.facecolor': 'white',
    'axes.spines.top':   False,
    'axes.spines.right': False,
})

BASE_DIR = Path(__file__).parent
OUT = BASE_DIR / 'charts'
OUT.mkdir(exist_ok=True)

# ── Дані ─────────────────────────────────────────────────────────────────────
df = pd.read_csv(BASE_DIR / 'ab_test_task_data.csv')
for c in ['date_reg', 'date_first_payment', 'date_reminder', 'date_spent_15_credits']:
    df[c] = pd.to_datetime(df[c])

hist = pd.read_csv(BASE_DIR / 'ab_test_task_historical_data.csv')
for c in ['date_reg', 'date_first_payment', 'date_spent_15_credits']:
    hist[c] = pd.to_datetime(hist[c])

ctrl = df[df['match'] == 0]
test = df[df['match'] == 1]

# Базові метрики
c_n,   t_n   = len(ctrl),  len(test)
c_pay, t_pay = ctrl['date_first_payment'].notna().sum(), test['date_first_payment'].notna().sum()
c_conv = c_pay / c_n
t_conv = t_pay / t_n
uplift = (t_conv - c_conv) / c_conv
diff   = t_conv - c_conv

ci_c = proportion_confint(int(c_pay), c_n, alpha=0.05, method='wilson')
ci_t = proportion_confint(int(t_pay), t_n, alpha=0.05, method='wilson')
_, p_main = proportions_ztest([int(t_pay), int(c_pay)], [t_n, c_n], alternative='larger')

BLUE   = '#3A6BAC'
ORANGE = '#D4672A'
GREEN  = '#27AE60'
GRAY   = '#95A5A6'
LIGHT  = '#F4F6F8'
DARK   = '#2C3E50'


# ════════════════════════════════════════════════════════════════════════════
# CHART 1 — Основний результат: Dot-plot + Delta bar
# ════════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 2, figsize=(13, 5),
                         gridspec_kw={'width_ratios': [1.6, 1]})
fig.patch.set_facecolor('white')

# ── Лівий: dot-plot з горизонтальними лініями ──
ax = axes[0]
ax.set_facecolor(LIGHT)
ax.set_xlim(0.4, 2.6)
y_range = [c_conv * 100, t_conv * 100]
ax.set_ylim(min(y_range) * 0.992, max(y_range) * 1.008)

# Горизонтальні лінії-орієнтири
for y in np.linspace(min(y_range) * 0.993, max(y_range) * 1.007, 5):
    ax.axhline(y, color='white', linewidth=1.2, zorder=1)

# Вертикальна лінія між точками — підкреслює GAP
ax.plot([1, 2], [c_conv * 100, t_conv * 100],
        color=GRAY, linewidth=1.5, linestyle='--', zorder=2, alpha=0.6)

# Точки
ax.scatter([1], [c_conv * 100], s=280, color=BLUE,   zorder=4, edgecolors='white', linewidth=2)
ax.scatter([2], [t_conv * 100], s=280, color=ORANGE, zorder=4, edgecolors='white', linewidth=2)

# Підписи значень
ax.text(1, c_conv * 100 - 0.018, f'{c_conv*100:.2f}%',
        ha='center', va='top', fontsize=15, fontweight='bold', color=BLUE)
ax.text(2, t_conv * 100 + 0.018, f'{t_conv*100:.2f}%',
        ha='center', va='bottom', fontsize=15, fontweight='bold', color=ORANGE)

for x, ci, c in [(1, ci_c, BLUE), (2, ci_t, ORANGE)]:
    ax.plot([x, x], [ci[0]*100, ci[1]*100], color=c, linewidth=3, alpha=0.35, zorder=3)

ax.set_xticks([1, 2])
ax.set_xticklabels(['Control', 'Test'], fontsize=13)
ax.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.2f%%'))
ax.set_ylabel('Конверсія в першу оплату', fontsize=11, color=DARK)
ax.spines['bottom'].set_visible(False)
ax.tick_params(bottom=False)
ax.set_facecolor(LIGHT)

# ── Правий: великі цифри — Delta панель ──
ax2 = axes[1]
ax2.axis('off')
ax2.set_facecolor('white')

# Фон-картка
card = mpatches.FancyBboxPatch((0.05, 0.08), 0.90, 0.84,
                                boxstyle='round,pad=0.03',
                                facecolor='#EAF6EF', edgecolor=GREEN, linewidth=2,
                                transform=ax2.transAxes, zorder=1)
ax2.add_patch(card)

ax2.text(0.5, 0.88, 'Результат тесту', transform=ax2.transAxes,
         ha='center', va='top', fontsize=11, color='#555', style='italic')

ax2.text(0.5, 0.68, f'+{uplift*100:.1f}%',
         transform=ax2.transAxes, ha='center', va='center',
         fontsize=44, fontweight='bold', color=GREEN)

ax2.text(0.5, 0.50, 'відносний uplift',
         transform=ax2.transAxes, ha='center', va='center',
         fontsize=11, color='#555')

ax2.plot([0.15, 0.85], [0.44, 0.44], color='#ccc', linewidth=1,
         transform=ax2.transAxes)

ax2.text(0.5, 0.34, f'+{diff*100:.2f} п.п.',
         transform=ax2.transAxes, ha='center', va='center',
         fontsize=18, fontweight='bold', color=DARK)
ax2.text(0.5, 0.22, 'абсолютна різниця',
         transform=ax2.transAxes, ha='center', va='center',
         fontsize=10, color='#666')

ax2.text(0.5, 0.11, f'p-value = {p_main:.4f}  ✓',
         transform=ax2.transAxes, ha='center', va='center',
         fontsize=10, color=GREEN, fontweight='bold')

plt.tight_layout()
plt.savefig(OUT / '1_main_result.png')
plt.close()
print("✅ Chart 1: Main result")


# ════════════════════════════════════════════════════════════════════════════
# CHART 2 — Slope chart: Eligible vs Non-eligible
# ════════════════════════════════════════════════════════════════════════════
ce = ctrl[ctrl['date_spent_15_credits'].notna()]
te = test[test['date_spent_15_credits'].notna()]
cn = ctrl[ctrl['date_spent_15_credits'].isna()]
tn = test[test['date_spent_15_credits'].isna()]

ce_conv = ce['date_first_payment'].notna().sum() / len(ce) * 100
te_conv = te['date_first_payment'].notna().sum() / len(te) * 100
cn_conv = cn['date_first_payment'].notna().sum() / len(cn) * 100
tn_conv = tn['date_first_payment'].notna().sum() / len(tn) * 100

ce_n, te_n = int(ce['date_first_payment'].notna().sum()), int(te['date_first_payment'].notna().sum())
_, p_elig = proportions_ztest([te_n, ce_n], [len(te), len(ce)], alternative='larger')
_, p_nelig = proportions_ztest(
    [int(tn['date_first_payment'].notna().sum()), int(cn['date_first_payment'].notna().sum())],
    [len(tn), len(cn)], alternative='larger'
)

fig, ax = plt.subplots(figsize=(10, 6))
ax.set_facecolor('white')

X = [0, 1]  
GAP = 0.22   

# ── Eligible — ефект є ──
ax.plot(X, [ce_conv, te_conv], color=ORANGE, linewidth=3, zorder=3, marker='o',
        markersize=10, markerfacecolor='white', markeredgewidth=2.5)
ax.fill_between(X, [ce_conv, te_conv], alpha=0.08, color=ORANGE)

ax.text(-GAP, ce_conv, f'{ce_conv:.1f}%', ha='right', va='center',
        fontsize=13, fontweight='bold', color=ORANGE)
ax.text(1 + GAP, te_conv, f'{te_conv:.1f}%', ha='left', va='center',
        fontsize=13, fontweight='bold', color=ORANGE)
# Анотація eligible — ПРАВОРУЧ від лінії, по середині між двома точками
ax.annotate(
    f'▲ +{(te_conv-ce_conv)/ce_conv*100:.1f}%\np={p_elig:.3f}',
    xy=(0.5, (ce_conv + te_conv) / 2),
    xytext=(0.72, (ce_conv + te_conv) / 2),
    ha='left', fontsize=11, fontweight='bold', color=ORANGE,
    bbox=dict(boxstyle='round,pad=0.35', facecolor='#FFF3E0', edgecolor=ORANGE, alpha=0.95),
    arrowprops=dict(arrowstyle='->', color=ORANGE, lw=1.5)
)

# ── Non-eligible — ефекту нема ──
ax.plot(X, [cn_conv, tn_conv], color=GRAY, linewidth=2.5, zorder=3, marker='o',
        markersize=9, markerfacecolor='white', markeredgewidth=2, linestyle='--')

ax.text(-GAP, cn_conv, f'{cn_conv:.3f}%', ha='right', va='center',
        fontsize=11, color=GRAY)
ax.text(1 + GAP, tn_conv, f'{tn_conv:.3f}%', ha='left', va='center',
        fontsize=11, color=GRAY)

# Анотація non-eligible — під лінією, по центру
ax.annotate(
    f'≈ без змін  p={p_nelig:.2f}',
    xy=(0.5, (cn_conv + tn_conv) / 2),
    xytext=(0.72, (cn_conv + tn_conv) / 2 + 0.8),
    ha='left', fontsize=10, color=GRAY,
    bbox=dict(boxstyle='round,pad=0.3', facecolor='#F5F5F5', edgecolor=GRAY, alpha=0.95),
    arrowprops=dict(arrowstyle='->', color=GRAY, lw=1.2)
)

ax.set_xticks([0, 1])
ax.set_xticklabels(['Control', 'Test'], fontsize=13, fontweight='bold')
ax.set_xlim(-0.55, 1.55)
ax.set_ylabel('Конверсія в першу оплату, %', fontsize=11)
ax.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.1f%%'))
ax.grid(axis='y', alpha=0.25, linestyle=':')

legend_items = [
    mpatches.Patch(color=ORANGE, label='Eligible — могли побачити reminder'),
    mpatches.Patch(color=GRAY,   label='Non-eligible — не потрапляли під умову'),
]
ax.legend(handles=legend_items, fontsize=10, loc='lower right',
          framealpha=0.9, edgecolor='#ddd')

plt.tight_layout()
plt.savefig(OUT / '2_mechanism_proof.png')
plt.close()
print("✅ Chart 2: Mechanism proof (slope)")


# ════════════════════════════════════════════════════════════════════════════
# CHART 3 — Forest plot: різниця конверсій з CI
# ════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(10, 4))
ax.set_facecolor('white')

# Різниця і її CI (approximation via Wilson CIs)
diff_val  = (t_conv - c_conv) * 100
diff_low  = (ci_t[0] - ci_c[1]) * 100   # консервативна нижня межа
diff_high = (ci_t[1] - ci_c[0]) * 100   # консервативна верхня межа

# Нульова лінія
ax.axvline(0, color='#E74C3C', linewidth=2, linestyle='--', zorder=1, alpha=0.8)

# CI відрізок
ax.plot([diff_low, diff_high], [0, 0],
        color=GREEN, linewidth=5, solid_capstyle='round', zorder=2, alpha=0.5)

# Точкова оцінка
ax.scatter([diff_val], [0], s=200, color=GREEN, zorder=3,
           edgecolors='white', linewidth=2)

# Підписи
ax.text(diff_val, 0.55, f'Різниця: +{diff_val:.2f} п.п.',
        ha='center', va='bottom', fontsize=13, fontweight='bold', color=GREEN,
        transform=ax.get_xaxis_transform())

ax.text(diff_low - 0.01, 0, f'{diff_low:.2f} п.п.',
        ha='right', va='center', fontsize=10, color='#555')
ax.text(diff_high + 0.01, 0, f'{diff_high:.2f} п.п.',
        ha='left', va='center', fontsize=10, color='#555')

ax.axvspan(0, diff_high * 1.3, alpha=0.05, color=GREEN, zorder=0)

ax.set_yticks([])
ax.set_xlabel('Різниця в конверсії (Test − Control), п.п.', fontsize=11)
ax.set_xlim(diff_low * 1.8, diff_high * 1.5)
ax.spines['left'].set_visible(False)
ax.grid(axis='x', alpha=0.25, linestyle=':')

plt.tight_layout()
plt.savefig(OUT / '3_forest_plot.png')
plt.close()
print("✅ Chart 3: Forest plot (CI difference)")


# ════════════════════════════════════════════════════════════════════════════
# CHART 4 — Counterfactual: поведінка в момент тригера З reminder і БЕЗ
# ════════════════════════════════════════════════════════════════════════════

# ── Test: реакція від моменту витрати 15 кредитів (той самий тригер) ──
test_eligible = test[
    test['date_spent_15_credits'].notna() & test['date_first_payment'].notna()
].copy()
test_eligible['days_after'] = (
    test_eligible['date_first_payment'] - test_eligible['date_spent_15_credits']
).dt.days
test_reaction = test_eligible[test_eligible['days_after'] >= 0]['days_after']

# ── Control: реакція від моменту витрати 15 кредитів ──
ctrl_eligible = ctrl[
    ctrl['date_spent_15_credits'].notna() & ctrl['date_first_payment'].notna()
].copy()
ctrl_eligible['days_after'] = (
    ctrl_eligible['date_first_payment'] - ctrl_eligible['date_spent_15_credits']
).dt.days
hist_reaction = ctrl_eligible[ctrl_eligible['days_after'] >= 0]['days_after']

# ── Метрики для підписів ──
cap = 15
bins = np.arange(0, cap + 2, 1)

t_within3  = (test_reaction <= 3).sum()
h_within3  = (hist_reaction <= 3).sum()
t_med      = int(test_reaction.median())
h_med      = int(hist_reaction.median())
t_pct3     = t_within3 / len(test_reaction) * 100
h_pct3     = h_within3 / len(hist_reaction) * 100

# Нормалізація до % щоб порівнювати групи різного розміру
t_hist_vals, _ = np.histogram(test_reaction.clip(upper=cap), bins=bins)
h_hist_vals, _ = np.histogram(hist_reaction.clip(upper=cap), bins=bins)
t_pct_vals = t_hist_vals / len(test_reaction) * 100
h_pct_vals = h_hist_vals / len(hist_reaction) * 100

fig, axes = plt.subplots(1, 2, figsize=(14, 5),
                         gridspec_kw={'width_ratios': [1, 2.2]})
fig.patch.set_facecolor('white')

# ── Лівий: зведена статистика ──
ax_l = axes[0]
ax_l.axis('off')

for y_top, val, label, color in [
    (0.88, f'{t_pct3:.0f}%',  'заплатили ≤3 дні\nвід тригеру\n(Test)',    ORANGE),
    (0.50, f'{h_pct3:.0f}%',  'заплатили ≤3 дні\nвід тригеру\n(Control)', BLUE),
]:
    card_c = mpatches.FancyBboxPatch(
        (0.05, y_top - 0.33), 0.90, 0.36,
        boxstyle='round,pad=0.03',
        facecolor='white', edgecolor=color, linewidth=2,
        transform=ax_l.transAxes
    )
    ax_l.add_patch(card_c)
    ax_l.text(0.5, y_top - 0.05, val, transform=ax_l.transAxes,
              ha='center', fontsize=34, fontweight='bold', color=color)
    ax_l.text(0.5, y_top - 0.22, label, transform=ax_l.transAxes,
              ha='center', fontsize=9.5, color='#555', linespacing=1.4)

ax_l.plot([0.1, 0.9], [0.52, 0.52], color='#ddd', linewidth=1,
          transform=ax_l.transAxes)

ax_l.text(0.5, 0.11,
          f'Медіана: {t_med} дн. (Test) vs {h_med} дн. (Hist)',
          transform=ax_l.transAxes, ha='center', fontsize=9,
          color='#777', style='italic')

# ── Правий: накладені гістограми (%) ──
ax_r = axes[1]
bar_w = 0.42
x = np.arange(cap + 1)

# Control — фон
bars_h = ax_r.bar(x - bar_w / 2, h_pct_vals, width=bar_w,
                   color=BLUE, alpha=0.55, edgecolor='white',
                   linewidth=0.8, label=f'Без reminder — Control (n={len(hist_reaction):,})',
                   zorder=2)

# Test — передній план
bars_t = ax_r.bar(x + bar_w / 2, t_pct_vals, width=bar_w,
                   color=ORANGE, alpha=0.85, edgecolor='white',
                   linewidth=0.8, label=f'З reminder — Test (n={len(test_reaction):,})',
                   zorder=3)

# Підсвіт перших 3 днів
for i in range(4):
    bars_h[i].set_facecolor('#6BAED6')
    bars_h[i].set_alpha(0.7)
    bars_t[i].set_facecolor(GREEN)
    bars_t[i].set_alpha(0.95)

# Вертикальна лінія-межа 3 днів
ax_r.axvline(3.5, color='#888', linewidth=1.5, linestyle=':', zorder=4, alpha=0.7)
ax_r.text(3.55, ax_r.get_ylim()[1] * 0.98 if ax_r.get_ylim()[1] > 0
          else max(t_pct_vals.max(), h_pct_vals.max()) * 0.98,
          '3 дні', fontsize=9, color='#888', va='top')

ax_r.set_xlabel('Днів від тригера до першої оплати',
                fontsize=11)
ax_r.set_ylabel('% юзерів групи', fontsize=11)
ax_r.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.1f%%'))
ax_r.set_xticks(np.arange(0, cap + 1, 2))
ax_r.set_xticklabels([str(x) if x < cap else f'{cap}+' for x in np.arange(0, cap + 1, 2)])
ax_r.grid(axis='y', alpha=0.2, linestyle=':')
ax_r.legend(fontsize=10, framealpha=0.95, loc='upper right')

plt.tight_layout()
plt.savefig(OUT / '4_reminder_reaction.png')
plt.close()
print("✅ Chart 4: Reminder counterfactual comparison")

# ════════════════════════════════════════════════════════════════════════════
# CHART 5 — Накопичена конверсія по днях (eligible юзери)
# ════════════════════════════════════════════════════════════════════════════
df_el = df[df['date_spent_15_credits'].notna()].copy()
df_el['days_to_payment'] = (df_el['date_first_payment'] - df_el['date_reg']).dt.days

fig, ax = plt.subplots(figsize=(10, 5))

curves = {}
for group, color, name in [(0, BLUE, 'Control'), (1, ORANGE, 'Test')]:
    total   = (df_el['match'] == group).sum()
    subset  = df_el[(df_el['match'] == group) & df_el['days_to_payment'].notna()]
    counts  = subset.groupby('days_to_payment')['id_user'].count().sort_index()
    cum     = counts.cumsum() / total * 100
    conv    = subset.shape[0] / total * 100
    ax.plot(cum.index, cum.values, label=f'{name}  ({conv:.1f}%)',
            linewidth=2.5, color=color)
    curves[name] = (cum.index.values, cum.values)

# Підсвіт різниці між кривими
idx_c, val_c = curves['Control']
idx_t, val_t = curves['Test']
common_x = np.intersect1d(idx_c, idx_t)
common_x = common_x[common_x <= 30]
vc = np.interp(common_x, idx_c, val_c)
vt = np.interp(common_x, idx_t, val_t)
ax.fill_between(common_x, vc, vt, alpha=0.12, color=ORANGE, label='Gap (ефект reminder)')

ax.set_xlim(0, 30)
ax.set_xlabel('Днів від реєстрації до першої оплати', fontsize=11)
ax.set_ylabel('% eligible юзерів що заплатили', fontsize=11)
ax.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.0f%%'))
ax.grid(True, alpha=0.2, linestyle=':')
ax.legend(fontsize=11, loc='lower right', framealpha=0.9)

plt.tight_layout()
plt.savefig(OUT / '5_cumulative_conversion.png')
plt.close()
print("✅ Chart 5: Cumulative conversion")


# ════════════════════════════════════════════════════════════════════════════
# CHART 6 — Воронка: спільна вісь Control vs Test з delta-колонкою
# Кожен етап — два бари поруч, між ними — різниця
# ════════════════════════════════════════════════════════════════════════════

# Спільні етапи (без reminder — він є тільки в test)
c_elig = ctrl['date_spent_15_credits'].notna().sum()
t_elig = test['date_spent_15_credits'].notna().sum()

stages_shared = ['Зареєструвались', 'Eligible\n(витратили 15 кредитів)', 'Оплатили']
c_vals = [len(ctrl), int(c_elig), int(c_pay)]
t_vals = [len(test), int(t_elig), int(t_pay)]
c_pcts = [v / c_vals[0] * 100 for v in c_vals]
t_pcts = [v / t_vals[0] * 100 for v in t_vals]

fig, ax = plt.subplots(figsize=(12, 5))
fig.patch.set_facecolor('white')
ax.set_facecolor(LIGHT)

n = len(stages_shared)
y_pos  = np.arange(n)[::-1]   # знизу вгору
bar_h  = 0.35
offset = 0.19                  # зміщення Control/Test відносно центру

for i, (stage, y, cp, tp) in enumerate(zip(stages_shared, y_pos, c_pcts, t_pcts)):
    # Control — верхній бар
    ax.barh(y + offset, cp / 100, height=bar_h, color=BLUE,
            alpha=0.85, edgecolor='white', linewidth=1.2, label='Control' if i == 0 else '')
    ax.text(cp / 100 + 0.005, y + offset,
            f'{c_vals[i]:,}  ({cp:.1f}%)',
            va='center', ha='left', fontsize=9.5, color=BLUE, fontweight='bold')

    # Test — нижній бар
    ax.barh(y - offset, tp / 100, height=bar_h, color=ORANGE,
            alpha=0.85, edgecolor='white', linewidth=1.2, label='Test' if i == 0 else '')
    ax.text(tp / 100 + 0.005, y - offset,
            f'{t_vals[i]:,}  ({tp:.1f}%)',
            va='center', ha='left', fontsize=9.5, color=ORANGE, fontweight='bold')

    # Delta між барами — виділяємо остаточну конверсію (останній рядок)
    delta_abs  = tp - cp
    delta_rel  = (tp - cp) / cp * 100 if cp > 0 else 0
    delta_color = GREEN if delta_abs >= 0 else '#E74C3C'
    delta_sign  = '+' if delta_abs >= 0 else ''

    if i == n - 1:   # тільки для кінцевого етапу — головний результат
        ax.annotate(
            f'{delta_sign}{delta_abs:.2f} п.п.\n({delta_sign}{delta_rel:.1f}%)',
            xy=(max(cp, tp) / 100 + 0.16, y),
            fontsize=11, fontweight='bold', color=delta_color, va='center', ha='left',
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#EAF6EF', edgecolor=GREEN, linewidth=1.8)
        )
    else:
        ax.text(max(cp, tp) / 100 + 0.16, y,
                f'{delta_sign}{delta_abs:.1f} п.п.',
                fontsize=9, color=delta_color, va='center', ha='left', fontweight='bold')

    # Назва етапу — зліва
    ax.text(-0.01, y, stage, va='center', ha='right',
            fontsize=10, color=DARK, linespacing=1.4)

ax.set_xlim(-0.22, 1.55)
ax.set_ylim(-0.7, n - 0.3)
ax.set_xticks([])
ax.set_yticks([])
ax.spines['left'].set_visible(False)
ax.spines['bottom'].set_visible(False)

ax.legend(fontsize=11, loc='lower right', framealpha=0.9, edgecolor='#ddd')

fig.suptitle('Порівняння воронок',
             fontsize=14, fontweight='bold', color=DARK, y=1.01)
plt.tight_layout()
plt.savefig(OUT / '6_funnel_comparison.png')
plt.close()
print("✅ Chart 6: Funnel comparison")

print(f"\n✅ Всі графіки збережено в: {OUT}")
print("\nФайли:")
for f in sorted(OUT.glob('*.png')):
    print(f"  {f.name}")
