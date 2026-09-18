#!/usr/bin/env python3
"""Build a visual, self-contained research brief from frozen experiment artifacts."""
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, Image, KeepTogether, PageBreak, Paragraph,
    Spacer, Table, TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "output" / "pdf" / "generic_structural_prior_research_brief.pdf"
FIG = ROOT / "figures"
FONT = "/System/Library/Fonts/Supplemental/AppleGothic.ttf"
PAGE_W, PAGE_H = A4
MARGIN = 1.65 * cm

pdfmetrics.registerFont(TTFont("AppleGothic", FONT))

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name="KTitle", parent=styles["Title"], fontName="AppleGothic", fontSize=25,
    leading=34, textColor=colors.HexColor("#12355b"), alignment=TA_CENTER, spaceAfter=12,
))
styles.add(ParagraphStyle(
    name="KSubTitle", parent=styles["Normal"], fontName="AppleGothic", fontSize=11,
    leading=17, textColor=colors.HexColor("#406080"), alignment=TA_CENTER,
))
styles.add(ParagraphStyle(
    name="H1K", parent=styles["Heading1"], fontName="AppleGothic", fontSize=17,
    leading=24, textColor=colors.HexColor("#12355b"), spaceBefore=4, spaceAfter=9,
))
styles.add(ParagraphStyle(
    name="H2K", parent=styles["Heading2"], fontName="AppleGothic", fontSize=12,
    leading=17, textColor=colors.HexColor("#1d5a8a"), spaceBefore=7, spaceAfter=5,
))
styles.add(ParagraphStyle(
    name="BodyK", parent=styles["BodyText"], fontName="AppleGothic", fontSize=9.2,
    leading=15, textColor=colors.HexColor("#202b38"), spaceAfter=6,
))
styles.add(ParagraphStyle(
    name="SmallK", parent=styles["BodyText"], fontName="AppleGothic", fontSize=7.4,
    leading=11, textColor=colors.HexColor("#4a5563"), spaceAfter=3,
))
styles.add(ParagraphStyle(
    name="TableHeaderK", parent=styles["BodyText"], fontName="AppleGothic", fontSize=7.4,
    leading=11, textColor=colors.white, spaceAfter=0,
))
styles.add(ParagraphStyle(
    name="CalloutK", parent=styles["BodyText"], fontName="AppleGothic", fontSize=11,
    leading=18, textColor=colors.HexColor("#12355b"), leftIndent=10, rightIndent=10,
    borderColor=colors.HexColor("#72a7c8"), borderWidth=.8, borderPadding=9,
    backColor=colors.HexColor("#edf6fb"), spaceBefore=7, spaceAfter=10,
))
styles.add(ParagraphStyle(
    name="CaptionK", parent=styles["BodyText"], fontName="AppleGothic", fontSize=7.5,
    leading=11, textColor=colors.HexColor("#4e6478"), alignment=TA_CENTER, spaceBefore=3,
    spaceAfter=8,
))


def p(text, style="BodyK"):
    return Paragraph(text, styles[style])


def fig(name, max_width=17.0*cm, max_height=15.0*cm):
    image = Image(str(FIG / name))
    image._restrictSize(max_width, max_height)
    image.hAlign = "CENTER"
    return image


def metric_table(headers, rows, widths):
    data = [[p(x, "TableHeaderK") for x in headers]] + [[p(x, "SmallK") for x in row] for row in rows]
    table = Table(data, colWidths=widths, repeatRows=1, hAlign="CENTER")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#12355b")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("GRID", (0, 0), (-1, -1), .25, colors.HexColor("#c8d5df")),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f9fc")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5), ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return table


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(colors.HexColor("#c5d5e2"))
    canvas.line(MARGIN, .92*cm, PAGE_W-MARGIN, .92*cm)
    canvas.setFont("AppleGothic", 7)
    canvas.setFillColor(colors.HexColor("#597080"))
    canvas.drawString(MARGIN, .58*cm, "Generic Structural-Prior Extrapolation Lab | synthetic development evidence")
    canvas.drawRightString(PAGE_W-MARGIN, .58*cm, f"{doc.page}")
    canvas.restoreState()


def build():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = BaseDocTemplate(str(OUT), pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN,
                          topMargin=1.35*cm, bottomMargin=1.35*cm)
    doc.addPageTemplates([__import__("reportlab.platypus", fromlist=["PageTemplate"]).PageTemplate(
        id="brief", frames=[Frame(MARGIN, 1.3*cm, PAGE_W-2*MARGIN, PAGE_H-2.6*cm, id="body")],
        onPage=footer,
    )])
    story = []

    # Cover
    story += [Spacer(1, 2.7*cm), p("범용 구조적 prior 외삽 연구 브리프", "KTitle"),
              p("Family label에서 uncertainty-aware extrapolative realization으로", "KSubTitle"),
              Spacer(1, .8*cm),
              p("이 문서는 현재까지의 synthetic evidence를 질문 → 실험 → 결과 → 다음 결정의 순서로 정리한 읽기용 요약본입니다. ", "CalloutK"),
              Spacer(1, .55*cm)]
    cover_rows = [
        ["핵심 발견", "True family만 알아도 안전한 외삽이 보장되지는 않는다."],
        ["핵심 메커니즘", "Structural evidence와 parameter identifiability는 다르다."],
        ["설계 결론", "RAG는 family뿐 아니라 onset, scale, shape의 제약과 uncertainty를 찾아야 한다."],
        ["현재 위치", "실제 RAG 전 단계: retrieval information specification을 고정할 시점."],
    ]
    story += [metric_table(["구분", "한 문장 요약"], cover_rows, [3.4*cm, 13.2*cm]), Spacer(1, .8*cm),
              p("읽는 순서", "H2K"),
              p("1) 관측성 현상  →  2) admission 안전성  →  3) family와 realization 분해  →  "
                "4) 고노출에서도 남은 식별 gap  →  5) 어떤 외부 지식이 필요한가  →  6) RAG 설계 명세", "BodyK"),
              Spacer(1, 1.4*cm), p("상태: synthetic development + frozen confirmation (admission-v2)\n"
                "저장소: amumujs-create/llm_prior", "KSubTitle"), PageBreak()]

    # Research state
    story += [p("1. 연구 질문이 어떻게 바뀌었는가", "H1K"),
              p("출발점은 ‘맞는 prior family를 찾으면 far-OOD 외삽이 좋아지는가?’였다. 현재의 더 정확한 질문은 "
                "‘현재 support와 외부 지식으로 이 family의 미래 realization을 안전하게 제약할 수 있는가?’이다.", "BodyK"),
              p("Family truth → Structural evidence → Parameter identifiability → Safe realization → Utility", "CalloutK"),
              p("prior는 단일 label이 아니라 다음과 같이 다룬다.", "BodyK"),
              p("P = { family, ψ: realization constraints, q: confidence / uncertainty }\n"
                "ψ = onset, scale, shape, bound, 또는 그 범위/분포", "CalloutK"),
              p("실험 전체 흐름", "H2K"),
              metric_table(["순서", "무엇을 확인했나", "현재 결론"], [
                  ["1", "관측성 sweep", "Truth ≠ observability ≠ utility"],
                  ["2", "Admission-v2", "prefix evidence로 harmful prior를 선별 가능"],
                  ["3", "Oracle decomposition", "family truth ≠ realization knowledge"],
                  ["4", "Exposure extension", "Visible ≠ identifiable"],
                  ["5", "Partial knowledge", "필요한 knowledge field와 precision은 family-dependent"],
              ], [1.2*cm, 7.0*cm, 8.4*cm]),
              Spacer(1, .4*cm), p("주의: 모든 결과는 domain-independent synthetic generator에서 나온 development evidence다. "
                "실제 data 또는 실제 RAG 성능에 대한 결론은 아직 내리지 않는다.", "SmallK"), PageBreak()]

    # Observability and admission
    story += [p("2. 관측성: true prior도 보이지 않으면 해로울 수 있다", "H1K"),
              p("세 family (regime change, emergent curvature, asymptotic bound)에서 structural behavior가 boundary 전에 얼마나 노출되었는지를 sweep했다. "
                "matching generative-family prior는 noisy prefix만으로 fit하며 clean far-OOD tail은 평가 전까지 보지 않는다.", "BodyK"),
              fig("fig01_observability_to_utility.png", 16.6*cm, 10.2*cm),
              p("관측성이 낮을 때 prior utility는 음수가 될 수 있고, evidence가 늘면 양수로 전환된다. 이 현상은 ‘family가 맞는가’와 ‘지금 사용 가능한가’를 분리해야 함을 만든 출발점이다.", "CaptionK"),
              p("Admission-v2: safety가 개발 결과에만 맞춘 효과가 아닌지, rule을 동결한 뒤 새 draws에서 확인했다.", "H2K"),
              fig("fig08_confirmation_coverage_harm_risk.png", 14.5*cm, 7.2*cm),
              p("독립 confirmation에서 harmful false admission은 64.0% → 19.3%, coverage는 62.2% → 56.0%, useful-prior admit은 61.1% → 77.3%였다. Admission의 목표는 family truth가 아니라 P(U_P > 0 | D_obs)다.", "CaptionK"), PageBreak()]

    # oracle decomposition
    story += [p("3. 왜 true family인데도 실패하는가", "H1K"),
              p("‘oracle prior’라는 표현을 분해했다. Generative-family oracle은 family만 알고 prefix에서 parameter를 fit한다. Parameter oracle은 future를 좌우하는 onset/scale/shape를 추가로 안다. Full-information oracle은 generator 전체를 안다.", "BodyK"),
              fig("fig09_oracle_decomposition_terminology.png", 16.7*cm, 15.4*cm),
              p("Low exposure에서 regime-change family oracle은 fallback보다 훨씬 나빴지만 parameter oracle은 거의 full-information bound에 도달했다. family misspecification이 아니라 realization parameter non-identifiability가 원인 후보임을 직접 지지한다.", "CaptionK"),
              p("Robustness check", "H2K"),
              p("Acceleration prior를 power law, concavity-constrained spline, constrained neural basis로 각각 realization해도 low-observability harm이 반복됐다. 따라서 이 현상은 한 parametric form의 artifact만으로 설명되기 어렵다.", "BodyK"), PageBreak()]

    # exposure
    story += [p("4. 더 오래 보면 family-only realization은 충분해지는가", "H1K"),
              p("Regime change와 curvature의 post-onset exposure를 O=.90까지 확장했다. primary endpoint는 paired realization gap: G = RMSE(family-only) − RMSE(parameter oracle). Practical convergence는 결과 전 upper 95% CI ≤ .01로 고정했다.", "BodyK"),
              fig("fig11_exposure_identifiability_extension.png", 16.7*cm, 15.3*cm),
              p("결과: O=.90에서도 regime G=.0346 [ .0310, .0383 ], curvature G=.0438 [ .0382, .0494 ]. 두 family 모두 수렴 기준을 통과하지 못했다. 그러나 family-only는 high-O에서 fallback보다 훨씬 좋아졌다.", "CaptionK"),
              p("따라서 supported claim은 ‘더 많이 보면 utility와 parameter estimate는 좋아지지만, tested support/noise/tail setting에서는 external realization knowledge의 가치가 남는다’이다. ‘family label이 본질적으로 언제나 불충분하다’는 주장은 하지 않는다.", "CalloutK"), PageBreak()]

    # partial knowledge exact
    story += [p("5. 어떤 realization knowledge가 실제로 중요한가", "H1K"),
              p("O=.90에서 family-only와 parameter oracle 사이를 onset, scale, shape의 singleton/pair/all 조합으로 분해했다. Exact external constraint는 해당 field를 고정하고 나머지는 prefix에서 fit한다. 모든 조건은 같은 400 base trajectories 위에서 paired로 비교했다.", "BodyK"),
              fig("fig13_partial_knowledge_exact_gap_closure.png", 16.7*cm, 11.8*cm),
              p("Exact information의 field importance는 family-dependent다. Regime change는 onset+scale이 97.7% gap closure, curvature는 scale+shape가 92.8% gap closure다. Curvature onset만으로는 3.6%이며 CI가 0을 포함한다.", "CaptionK"),
              metric_table(["Family", "가장 유용한 exact pair", "gap closure", "해석"], [
                  ["Regime change", "onset + scale", "97.7%", "onset/scale timing과 magnitude를 함께 제약해야 함"],
                  ["Emergent curvature", "scale + shape", "92.8%", "curvature strength와 shape가 핵심; onset 단독은 약함"],
              ], [3.0*cm, 4.4*cm, 2.4*cm, 5.6*cm]), PageBreak()]

    # precision
    story += [p("6. exact parameter가 아니라, uncertainty-aware knowledge가 필요하다", "H1K"),
              p("현실의 RAG는 exact onset/scale/shape를 가져오지 않는다. supplied field에 zero-mean retrieval noise를 주고, knowledge precision이 far-OOD utility를 어떻게 바꾸는지 sweep했다.", "BodyK"),
              fig("fig14_partial_knowledge_precision_sweep.png", 16.7*cm, 15.2*cm),
              p("여러 field를 point estimate로 고정하는 것은 retrieval error에 민감하다. Regime all-fields는 exact에서 100%지만 tier .05에서 53%, .10에서 family-only보다 나빠졌다. Curvature all-fields는 .10에서 68%, .20에서 25%를 유지하지만 .40에서는 family-only보다 나빠졌다.", "CaptionK"),
              p("설계 결론: RAG 결과는 ‘parameter value’가 아니라 field-level constraint/range + confidence + provenance로 표현되어야 한다. Admission은 retrieved uncertainty와 prefix evidence를 함께 보고 남은 risk를 판단해야 한다.", "CalloutK"), PageBreak()]

    # Next specification
    story += [p("7. 실제 RAG 전에 고정할 Information Specification", "H1K"),
              p("Partial Knowledge Sweep은 retrieval이 무엇을 제공해야 하는지에 대한 synthetic evidence를 제공했다. 따라서 실제 RAG의 첫 평가는 end-to-end RMSE가 아니라 candidate/constraint information recall로 분해해야 한다.", "BodyK"),
              p("RAG candidate record", "H2K"),
              metric_table(["필드", "예시", "왜 필요한가"], [
                  ["structural family", "regime change / curvature", "candidate mechanism을 정의"],
                  ["realization constraint", "onset range, scale range, shape sign/range", "family-only gap을 줄이는 정보"],
                  ["uncertainty", "interval width, confidence, evidence strength", "부정확한 point constraint의 harm 방지"],
                  ["provenance", "source, context, assumptions", "constraint의 적용 가능성 검증"],
              ], [3.5*cm, 6.5*cm, 5.4*cm]),
              Spacer(1, .45*cm), p("Recommended next experiment", "H2K"),
              p("1. 이 schema를 frozen retrieval target으로 정의한다.\n"
                "2. 문헌/지식 source에서 family, field constraint, uncertainty를 각각 recover하는 RAG candidate generator를 만든다.\n"
                "3. Admission-v2를 uncertainty-aware version으로 확장할지, partial-knowledge synthetic draw에서 먼저 확인한다.\n"
                "4. 그 뒤 actual RAG의 family recall, field recall/precision, and final extrapolation utility를 분리 평가한다.", "BodyK"),
              p("한 문장 결론", "H2K"),
              p("Retrieve plausible structural knowledge + constrain its realization + admit only when remaining uncertainty is safe.", "CalloutK"),
              Spacer(1, .55*cm), p("Artifact map", "H2K"),
              p("전체 논리: EXPERIMENT_NOTE.md\n결과 원문: RESULTS_*.md\n재현 코드: experiments/*.py\n기계 판독: results/*/results.json\nPPT 문장: PPT_STORYBOARD.md", "SmallK"), PageBreak()]

    # Literature grounding
    story += [p("8. 측정 설계를 뒷받침하는 선행 근거", "H1K"),
              p("아래 문헌은 이 저장소의 synthetic 결과를 독립적으로 검증하는 자료가 아니다. 대신, 왜 pointwise fit만으로는 부족하고 complexity, structural validity, derivative information을 분리해 기록해야 하는지에 대한 방법론적 근거다.", "BodyK"),
              p("A. Accuracy - complexity trade-off", "H2K"),
              p("Desmond의 recent symbolic-regression work는 accuracy와 expression complexity를 함께 선택해야 하며, likelihood를 최대화하는 매우 복잡한 함수가 overfit되어 generalization/extrapolation이 나빠질 수 있다고 논의한다. 이 브리프의 far-OOD utility와 parameter-identifiability 기록은 prefix fit만으로 model을 선택하지 않기 위한 것이다.", "BodyK"),
              p("Desmond, H. (2026). (Exhaustive) Symbolic Regression and model selection by minimum description length. Philosophical Transactions of the Royal Society A. DOI: 10.1098/rsta.2024.0584", "SmallK"),
              p("B. Shape constraints and pointwise error are distinct objectives", "H2K"),
              p("Haider et al.는 shape-constrained symbolic regression에서 prediction error와 constraint violation을 별도 objective로 다루며, low-noise setting에서 shape constraint가 training prediction error를 높이지만 test error는 소폭 낮출 수 있음을 보고한다. 이는 우리의 constrained spline/neural basis robustness check와 structural validity의 별도 기록을 뒷받침한다.", "BodyK"),
              p("Haider, C., de Franca, F. O., Burlacu, B., & Kronberger, G. (2023). Shape-constrained multi-objective genetic programming for symbolic regression. Applied Soft Computing, 132, 109855. DOI: 10.1016/j.asoc.2022.109855", "SmallK"),
              p("C. Derivative-aware learning", "H2K"),
              p("Czarnecki et al.의 Sobolev Training은 function value뿐 아니라 target derivative를 맞추는 학습을 제안하고, studied settings에서 data efficiency와 generalization 개선을 보였다. 이는 slope, curvature, derivative-sign consistency를 evidence primitive로 기록하는 방법론적 precedent다. 우리의 deployment pipeline이 true derivative를 관측한다는 뜻은 아니다.", "BodyK"),
              p("Czarnecki, W. M., Osindero, S., Jaderberg, M., Swirszcz, G., & Pascanu, R. (2017). Sobolev Training for Neural Networks. NeurIPS 2017. https://proceedings.neurips.cc/paper/2017/hash/758a06618c69880a6cee5314ee42d52f-Abstract.html", "SmallK"),
              p("실험 기록에 주는 규칙", "H2K"),
              p("prefix fit / function-value error, structural or derivative validity, parameter identifiability and realization uncertainty, far-OOD utility and harm risk를 분리해 기록한다. 한 점수에서 좋아 보이는 모델이 미래 continuation에서는 왜 실패하는지 드러내기 위함이다.", "CalloutK")]

    doc.build(story)
    print(OUT)


if __name__ == "__main__":
    build()
