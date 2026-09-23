# E15-B frozen result index

## Contract and corpus

- Confirmatory manifest SHA-256: `b5d12de2c27db01823a905f03bd8523a1a8461fab69077da5d37db40edc0f413`.
- Corpus: 2,520 latent tasks, 317,520 policy rows; corpus row SHA-256: `05093edf39d1bf7a4b49851756b982c1c80d2824a3411522494eefebf22ee858`.
- Integrity and no-future-leakage audits passed before outcomes were opened.
- All inferential intervals below are 5,000-replicate latent-task paired-bootstrap, cellwise 95% CIs.

## Frozen primary results

1. **D1 — uncertainty retention versus local scope commitment.**
   `weighted scope mixture − hard local MAP` was strongly negative under weak scope evidence and contracted toward zero as exposure increased. Its gain was concentrated post-scope.
   - Source: `E15B_D1_CELLWISE_PAIRED_BOOTSTRAP.csv`
   - SHA-256: `208d4b80027756cfceab80ae02da6c9391382c39cfb10ac7b90a86c858c89ead`

2. **D2 — precursor-likelihood weighting versus uniform scope averaging.**
   `weighted scope mixture − uniform scope ensemble` was positive in the frozen covered-scope conditions. The penalty diminished with exposure but did not become a general predictive advantage.
   - Source: `E15B_D2_CELLWISE_PAIRED_BOOTSTRAP.csv`
   - SHA-256: `386262a1ccb369b9e18faf5251669fe06ca1e0756cfde3d7f524d5c6ae8adae2`

3. **Exposure modification.**
   High-minus-low paired contrasts confirm D1 contraction and D2 penalty contraction.
   - Source: `E15B_EXPOSURE_CHANGE_PAIRED_BOOTSTRAP.csv`
   - SHA-256: `3fbc5bbf5d1698b816f62972d30b730e9ba5c725f4b592143d66a0aef06200a8`

4. **Scope-window decomposition.**
   D1 retention gains and D2 weighting penalties were both amplified beyond the guaranteed scope.
   - Sources: `E15B_SCOPE_WINDOW_CELLWISE_PAIRED_BOOTSTRAP.csv`, `E15B_SCOPE_WINDOW_CHANGE_PAIRED_BOOTSTRAP.csv`
   - SHA-256: `19b1ebcdb94f980a541f3cb94f8f022453b9ed5185b88f5a112bd2a03bef76fd`, `06c584f7ea13dbb63a94733934247da1c1783962acf316a62c898de13ec26b46`

5. **Global-overextension stress.**
   In exact-scope tasks, global direction enforcement had realization-dependent post-scope consequences. At high exposure in reverse realizations, hard-global versus hard-local MAP was `+0.2618` NRMSE, 95% CI `[+0.2472, +0.2771]`; persist/strengthen realizations can instead align incidentally with global enforcement. Thus a mode-balanced average is not an endorsement of globally enforcing the prior.
   - Support-invariance audit: `E15B_GLOBAL_POLICY_SUPPORT_INVARIANCE_AUDIT.json`, SHA-256 `73ab36949b3e7dbd2f3cc932c2de46936afc569bbdbbd18be470f256a2a66672`
   - Sources: `E15B_GLOBAL_STRESS_CELLWISE_PAIRED_BOOTSTRAP.csv`, `E15B_GLOBAL_STRESS_WINDOW_CHANGE_PAIRED_BOOTSTRAP.csv`
   - SHA-256: `1bf9b83f7a9ef522e837fec6e5e3788b62aff2c1431fdf90c7e8b21526aa2af3`, `5fe40c0fe8b3b36019bffb4903e9c96384c53fb1e0413a4dd5cf23515ff21472`

## Figures derived only from frozen artifacts

- `figures/E15B_D1_EXPOSURE_CELLWISE.png`
- `figures/E15B_D2_EXPOSURE_CELLWISE.png`
- `figures/E15B_D1_D2_EXPOSURE_CHANGE.png`
- `figures/E15B_D1_SCOPE_WINDOWS.png`
- `figures/E15B_D2_SCOPE_WINDOWS.png`
- `figures/E15B_GHARD_BY_MODE.png`
- `figures/E15B_GLOBAL_RELAXATION.png`

## Frozen conclusion and boundary

**Prior utilization should follow the uncertainty dimension resolved by the evidence, not evidence strength alone.**

For this frozen directional-prior family, evidence about the guaranteed scope endpoint did not identify the post-scope realization. Scope uncertainty should therefore be preserved when it remains predictive; endpoint-identification likelihood should not automatically be used as a predictive weighting signal for post-scope futures. This is not a universal claim for other prior families.
