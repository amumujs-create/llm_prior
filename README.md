# Generic Prior Observability Lab

도메인(배터리·설비·의료 등)과 분리된, **구조적 prior가 언제 외삽에 유익한가**를
검증하는 독립 synthetic laboratory다. PP-X, PAE, CA-CSS의 코드·결과·주장과
공유하지 않는다.

## 핵심 명제

`prior truth != prior observability != prior utility`

용어의 정확한 구분은 [TERMINOLOGY.md](TERMINOLOGY.md)를 따른다. 여기서 평가한
“matching prior”는 **generative-family oracle**이며 full-information oracle이 아니다.

정답 구조 family를 알고 있어도, 관측 prefix에서 그 구조를 식별할 evidence가 없으면
parameter fit은 불안정하고 far-OOD extrapolation은 linear fallback보다 나빠질 수 있다.

## v1 구성

세 가지 범용 prior를 sweep한다.

| Generic prior | 관측되어야 할 증거 | Observability 조작 |
|---|---|---|
| Regime change | 이후 mechanism의 onset / exposure | boundary와 change-point의 거리 |
| Emergent curvature | 증가하는 curvature의 exposure | boundary와 curvature-onset의 거리 |
| Asymptotic bound | asymptote로 굽는 curvature | `k * boundary` |

각 trajectory는 noisy prefix `t <= .60`만 사용해 fit하며, clean tail `t > .70`은
평가 전까지 숨긴다. 상세 사전 규약은 [RULES.md](RULES.md), 논리 사슬은
[EXPERIMENT_LOGIC.md](EXPERIMENT_LOGIC.md)에 있다.

## 산출물

- `experiments/generic_observability_sweep_v1.py` — 재현 가능한 generator·fit·평가
- `results/generic_observability_sweep_v1/results.json` — 기계 판독 결과
- `figures/` — PPT 재사용용 PNG
- `RESULTS_V1.md` — 결과 해석 및 발표용 문장
- `PPT_STORYBOARD.md` — 그림별 슬라이드 역할과 안전한 claim
- `ORACLE_DECOMPOSITION_PROTOCOL.md` / `RESULTS_ORACLE_DECOMPOSITION_V1.md` — family
  knowledge와 realization knowledge를 분해한 실험
- `EXPOSURE_IDENTIFIABILITY_EXTENSION_PROTOCOL.md` — high-exposure에서 family-only
  realization이 parameter oracle에 수렴하는지 묻는 후속 규약
- `RESULTS_EXPOSURE_IDENTIFIABILITY_EXTENSION_V1.md` — `O=.90`까지 확장한 결과와
  수렴 실패의 범위 제한 해석

## 실행

```bash
MPLCONFIGDIR=/private/tmp/generic_prior_mpl \
python experiments/generic_observability_sweep_v1.py
```
