import numpy as np
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
    '''가입 후 경과 기간별 이탈 비중.
    '''
    return pd.DataFrame({
        '가입후경과': ['1개월 내', '1~3개월', '3~6개월', '6~12개월', '12개월 이상'],
        '이탈비중': [23.0, 28.0, 19.0, 17.0, 13.0],
    })


EARLY = ['1개월 내', '1~3개월']        # 강조할 초기 구간
SOURCE_NOTE = ('자료: 구독 관리 DB · 기간 2025.01~2025.12 · '
               'N=이탈 고객 41,300명 · 단위 %')


# ══════════════════════════════════════════════════════════════════════
# 2. 여기부터 작성하세요
# ══════════════════════════════════════════════════════════════════════
def my_answer():
    df = load_data()
    early_sum = df.loc[df['가입후경과'].isin(EARLY), '이탈비중'].sum()

    # 가로 막대는 아래에서 위로 쌓이므로, 시간 순서를 위→아래로 보이게 하려면
    # 데이터를 뒤집어야 합니다. (R2 — 정렬이 아니라 순서 유지)
    d = df.iloc[::-1].reset_index(drop=True)
    y = np.arange(len(d))

    fig, ax = plt.subplots(figsize=(8.6, 4.3))

    # ── R3. 회색조 + 강조 1색 ─────────────────────────────────────
    # TODO: 초기 두 구간(EARLY)만 WARN, 나머지는 GRAY 로 색을 정하세요.
    colors = [WARN if r in EARLY else GRAY for r in d['가입후경과']]

    # ── R1. 가로 막대 ─────────────────────────────────────────────
    # TODO: ax.barh() height: 0.62
    ax.barh(y, d['이탈비중'], color=colors, height=0.6)

    # ── R4. 직접 라벨링 ───────────────────────────────────────────
    # TODO: 막대 끝에 값을 표기하세요.
    for i, v in enumerate(d['이탈비중']):
        ax.text(v + 0.2, i, f'{v:.0f}%', va='center', fontsize=10, color=colors[i])

    # ── R4. x축 눈금 제거 + 정크 정리 ─────────────────────────────
    # TODO: 축선 4개를 모두 지우고 x축 눈금을 없애세요. (limit 0 ~ 40)
    for sp in ax.spines.values():
        sp.set_visible(False)
    ax.set_xticks([])
    ax.tick_params(length=0, color=INK)
    ax.set_xlim(0, 40)
    # ── R5. 주석 ──────────────────────────────────────────────────
    # TODO: '초기 3개월에\n51% 집중' 을 화살표와 함께 답니다.
    #       힌트: ax.annotate(arrowprops={connectionstyle: ???})
    ax.annotate(f'초기 3개월에\n{early_sum:.0f}% 집중',
                xy=(30, 3.5), xytext=(38, 2.4),
                fontsize=11, color=WARN, ha='right', va='center',
                arrowprops={'arrowstyle':'->', 'color':WARN, 'lw':1.1,
                                'connectionstyle':'arc3,rad=-0.25'})
    # 축 라벨 (참고용)
    ax.set_yticks(y, d['가입후경과'], fontsize=10.5)


    # ── R6. Action Title ──────────────────────────────────────────
    # TODO: 아래 제목을 결론 문장으로 바꾸고, 부제를 추가하세요.
    ax.set_title(f'이탈의 {early_sum:.0f}%가 가입 후 3개월 안에 발생한다', loc='left',
                 fontsize=16, color=INK, pad=28)
    ax.text(0,1.06, '가입 후 경과 기간별 이탈 비중',transform=ax.transAxes, fontsize=11, color=MUTED, va='bottom')

    # ── R7. 메타 정보 ─────────────────────────────────────────────
    # TODO: 메타정보(SOURCE_NOTE)를 추가해주세요
    fig.text(0.005, 0.005, SOURCE_NOTE, fontsize=8, color=GRAY_D)

    return fig

if __name__ == '__main__':
    setup_font()

    save(my_answer(), '과제2.png')
