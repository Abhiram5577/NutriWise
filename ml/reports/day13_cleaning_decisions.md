# Day 13 — Data Cleaning Decisions Report
## Milestone 2: ML Nutritional Deficiency Detection Engine

---

## Cleaning Rules Applied

| Rule ID | Description |
|---------|-------------|
| CR-01 | Remove exact duplicate rows (excluding subject_id) |
| CR-02 | Remove records with age outside [18, 110] |
| CR-03 | Remove records with BMI outside [10, 80] |
| CR-04 | Remove records with hemoglobin outside [3, 25] g/dL |
| CR-05 | Replace negative dietary values with NaN |
| CR-06 | Clamp lab and dietary values to physiological domain bounds |
| CR-07 | Validate target labels; set to NaN if primary lab marker missing |
| CR-08 | Impute lab features with gender-stratified medians |
| CR-09 | Impute dietary features with overall median |
| CR-10 | Validate categorical variable encodings |

## Cleaning Log

```
[CR-01] Removed exact duplicates | Records affected: 15
[CR-02] Removed records with age outside [18, 110]; invalid values: [150.0, 200.0, -5.0, 200.0, 0.0] | Records affected: 5
[CR-03] Removed records with BMI outside [10, 80]; values: [0.0, 0.0, 0.0] | Records affected: 3
[CR-04] Removed records with hemoglobin outside [3, 25] g/dL; values: [-1.0, 99.0, 0.0, 50.0, 50.0, 0.0, 0.0, 0.0, 0.0, 99.0] | Records affected: 10
[CR-05] Replaced 8 negative values in 'dietary_iron_mg' with NaN | Records affected: 8
[CR-06] No lab/dietary values required clamping | Records affected: 0
[CR-07] Set iron_deficiency=NaN where both Hgb and ferritin are missing | Records affected: 19
[CR-07] Confirmed vitamin_d_deficiency=NaN where 25OHD is missing | Records affected: 542
[CR-07] Confirmed vitamin_b12_deficiency=NaN where B12 is missing | Records affected: 493
[CR-07] Confirmed calcium_deficiency=NaN where serum Ca is missing | Records affected: 356
[CR-07] Confirmed folate_deficiency=NaN where serum folate is missing | Records affected: 506
[CR-08] Imputed 'hemoglobin_g_dl' for gender=0 with median=13.506 | Records affected: 140
[CR-08] Imputed 'hemoglobin_g_dl' for gender=1 with median=15.517 | Records affected: 117
[CR-08] Imputed 'serum_ferritin_ng_ml' for gender=0 with median=34.486 | Records affected: 197
[CR-08] Imputed 'serum_ferritin_ng_ml' for gender=1 with median=79.389 | Records affected: 196
[CR-08] Imputed 'serum_iron_mcg_dl' for gender=0 with median=98.001 | Records affected: 217
[CR-08] Imputed 'serum_iron_mcg_dl' for gender=1 with median=99.150 | Records affected: 190
[CR-08] Imputed 'tibc_mcg_dl' for gender=0 with median=298.747 | Records affected: 204
[CR-08] Imputed 'tibc_mcg_dl' for gender=1 with median=299.811 | Records affected: 208
[CR-08] Imputed 'transferrin_saturation_pct' for gender=0 with median=33.034 | Records affected: 210
[CR-08] Imputed 'transferrin_saturation_pct' for gender=1 with median=33.110 | Records affected: 196
[CR-08] Imputed 'vitamin_d_25ohd_ng_ml' for gender=0 with median=25.434 | Records affected: 271
[CR-08] Imputed 'vitamin_d_25ohd_ng_ml' for gender=1 with median=25.308 | Records affected: 271
[CR-08] Imputed 'vitamin_b12_pg_ml' for gender=0 with median=410.151 | Records affected: 246
[CR-08] Imputed 'vitamin_b12_pg_ml' for gender=1 with median=408.375 | Records affected: 247
[CR-08] Imputed 'serum_calcium_mg_dl' for gender=0 with median=9.399 | Records affected: 183
[CR-08] Imputed 'serum_calcium_mg_dl' for gender=1 with median=9.371 | Records affected: 173
[CR-08] Imputed 'serum_folate_ng_ml' for gender=0 with median=12.544 | Records affected: 263
[CR-08] Imputed 'serum_folate_ng_ml' for gender=1 with median=12.459 | Records affected: 243
[CR-08] Imputed 'rbc_folate_ng_ml' for gender=0 with median=319.947 | Records affected: 335
[CR-08] Imputed 'rbc_folate_ng_ml' for gender=1 with median=311.971 | Records affected: 296
[CR-09] Imputed 'dietary_iron_mg' missing values with median=14.806 | Records affected: 8
[CR-10] activity_level values validated: [0, 1, 2, 3, 4] | Records affected: 0
[CR-10] dietary_preference values validated: [0, 1, 2] | Records affected: 0
[CR-10] gender values validated: [0, 1] | Records affected: 0
```

## Decisions NOT Taken and Why

- **Did NOT use IQR-based outlier removal** for lab values: Lab distributions are often
  right-skewed (log-normal); IQR would remove genuine extreme values (e.g., very high
  ferritin in haemochromatosis). Domain-based clamping is more appropriate.

- **Did NOT set negative dietary values to 0**: Zero means 'did not eat any'; NaN means
  'the value is unknown/invalid'. Negative values are data errors, so NaN is correct.

- **Did NOT remove records with missing lab values**: Lab values are missing systematically
  (some subjects skip blood draws). Imputing allows retention of their other valid features.

- **Did NOT remove records where targets are NaN**: These records still contain valid
  features and can be used by other deficiency models whose targets are available.

- **Did NOT use mean imputation for lab features**: Lab distributions are skewed;
  median is more robust to outliers.