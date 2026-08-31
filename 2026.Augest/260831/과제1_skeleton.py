import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager


# ══════════════════════════════════════════════════════════════════════
# 0. 환경 설정 — 수정하지 마세요
# ══════════════════════════════════════════════════════════════════════
INK, BODY, MUTED = '#0c0a09', '#4e4e4e', '#777169'
HAIR, GRAY, GRAY_D = '#d6d3d1', '#c9c5c1', '#a8a29e'
ACCENT, WARN = '#2f6f5e', '#c2543d'

def setup_font():
    '''설치된 한글 폰트를 자동으로 찾아 적용한다.'''
    candidates = [
        'Malgun Gothic',       # Windows
        'AppleGothic',         # macOS
    ]
    installed = {f.name for f in font_manager.fontManager.ttflist}
    for name in candidates:
        if name in installed:
            plt.rcParams['font.family'] = name
            break
    else:
        print('[경고] 한글 폰트를 찾지 못했습니다. 라벨이 □로 보일 수 있습니다.\n'
              '       Colab: !apt-get install -y fonts-nanum 후 런타임 재시작')
    plt.rcParams.update({
        'axes.unicode_minus': False,   # 음수 부호 깨짐 방지
    })

def save(fig, path):
    fig.savefig(path, bbox_inches='tight')
    plt.close(fig)


# ══════════════════════════════════════════════════════════════════════
# 1. 데이터 — 수정하지 마세요
# ══════════════════════════════════════════════════════════════════════
def load_data():
    '''가입 월별 신규 가입자 수와 3개월 유지율 (2025년 12개월)
    '''
    return pd.DataFrame({
        '가입월': pd.date_range('2025-01-01', periods=12, freq='MS'),
        '3개월유지율': [71.0, 70.0, 69.0, 68.0, 66.0, 64.0,
                        61.0, 59.0, 57.0, 56.0, 55.0, 54.0],
        '신규가입자': [8200, 8600, 9100, 9400, 10200, 11800,
                       13500, 14100, 13800, 13200, 12600, 12100],
    })

SOURCE_NOTE = ('자료: 구독 관리 DB · 기간 2025.01~2025.12 · '
               'N=신규 가입 137,600명 · 단위 %')

# ══════════════════════════════════════════════════════════════════════
# 2. 여기부터 작성하세요
# ══════════════════════════════════════════════════════════════════════
def my_answer():
    df = load_data()
    x = df['가입월']
    y = df['3개월유지율']
    base = y.iloc[0]    # 연초 71%
    last = y.iloc[-1]   # 연말 54%
    drop = base - last  # 17%p

    fig, ax = plt.subplots(figsize=(8.6, 4.7))

    # ── R1. 선 그래프 ─────────────────────────────────────────────
    # TODO: ax.plot(...) linewidth
    plt.plot(x, y, color=WARN, linewidth=2.5)

    # ── R2. 기준선 ────────────────────────────────────────────────
    # TODO: 연초 값에 가로 점선을 긋고 라벨을 답니다.
    #       힌트: ax.axhline(...) / ax.text()
    ax.axhline(base, color=GRAY_D, linestyle='--', linewidth=1)
    ax.text(x.iloc[0], base + 0.5, f'연초 {base:.0f}%', fontsize=10, color=GRAY_D)
    # ── R3. 낙폭 음영 ─────────────────────────────────────────────
    # TODO: 기준선과 실제 선 사이를 채웁니다.
    #       힌트: ax.fill_between() # alpha 값 조절
    ax.fill_between(x, y, base, color=WARN, alpha=0.1)

    # ── R4. 마지막 값 직접 라벨링 ─────────────────────────────────
    # TODO: 마지막 점을 찍고 그 아래에 '54%' 를 표기합니다.
    #       힌트: ax.scatter()
    # 추가로, 낙폭을 화살표로 표현 (ax.annotate(arrowprops) 활용)
    ax.scatter(x.iloc[-1], [last], s=64, color=WARN, zorder=4)
    ax.text(x.iloc[-1], last - 1.5, f'{last:.0f}%', ha='center', fontsize=10, color=WARN)

    ax.annotate("", xy=(x.iloc[-1], last + 0.1), xytext=(x.iloc[-1], base - 0.1),
                arrowprops={'arrowstyle':"<->", 'color':INK, 'lw':1})
    ax.text(x.iloc[-1], (base + last) / 2, f' -{drop:.0f}%p', fontsize=10, color=INK, va='center')

    # ── R5. 차트 정크 제거 ────────────────────────────────────────
    # TODO: 왼쪽 제외 축선을 지우고 y축 눈금을 [50, 60, 70] 으로 제한합니다.
    #       힌트: ax.spines[side].set_visible(False) side = top, right, bottom, left
    #             ax.set_yticks(); ax.set_ylim()
    for side in ('top', 'right', 'bottom'):
        ax.spines[side].set_visible(False)
    ax.spines['left'].set_color(HAIR)
    ax.set_yticks([50, 60, 70])
    ax.set_ylim(45, 75)


    # x축 라벨 설정 (참고용)
    ax.set_xticks(x[::2], [t.strftime('%y-%m') for t in x[::2]], fontsize=9)
    ax.tick_params(length=0, colors=MUTED)


    # ── R6. Action Title ──────────────────────────────────────────
    # TODO: 아래 제목을 결론 문장으로 바꾸고, 부제를 추가하세요.
    ax.set_title(f"3개월 유지율이 1년 만에 {base:.0f}% → {last:.0f}%로 {drop:.0f}%p 하락했다",
                 loc="left", fontsize=15.5, color=INK, pad=28)
    ax.text(0, 1.06, "가입 월별 3개월 유지율 · 2025년",
            transform=ax.transAxes, fontsize=9.5, color=MUTED, va="center")

    # ── R7. 메타 정보 ─────────────────────────────────────────────
    # TODO: 메타정보(SOURCE_NOTE)를 추가해주세요
    fig.text(0.005, 0.005, SOURCE_NOTE, fontsize=7, color=GRAY_D)

    return fig

# ══════════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    setup_font()

    save(my_answer(), '과제1.png')