# Day 11 — Dataset Collection & Analysis Report
## Milestone 2: ML Nutritional Deficiency Detection Engine
**Date:** 2026-10-04  
**Author:** NutriWise ML Engineering Team

---

## 1. Objective

Identify, evaluate, and select suitable training data for nutritional-deficiency
prediction. Clearly distinguish:

- **Food-composition / nutrient-reference data** (does NOT provide deficiency labels)
- **Labeled deficiency-training data** (required for supervised ML)

---

## 2. Candidate Data Source Evaluation

### 2.1 WHO Global Anaemia Estimates
| Attribute | Detail |
|-----------|--------|
| Source | World Health Organization (WHO) |
| URL | https://www.who.int/data/gho/data/themes/topics/anaemia_in_women_and_children |
| Type | **Aggregated population-level statistics** |
| Granularity | Country / region / year — not individual records |
| Deficiency labels | Iron-deficiency anaemia prevalence (%) — no individual labels |
| Verdict | NOT suitable — no individual-level features or labels |

### 2.2 NHANES (National Health and Nutrition Examination Survey)
| Attribute | Detail |
|-----------|--------|
| Source | U.S. CDC / National Center for Health Statistics |
| URL | https://wwwn.cdc.gov/nchs/nhanes/ |
| Type | **Individual-level, nationally representative survey** |
| Cycles available | Continuous NHANES: 1999-present |
| Individual records | Yes — household interview + physical exam + lab results |
| Dietary features | Yes — 24-hour dietary recall (nutrients per day) |
| Laboratory values | Yes — Hemoglobin, Serum Ferritin, Vitamin D (25OHD), B12, Calcium, Iron panel |
| Clinical symptoms | Partial — questionnaire items on fatigue, self-reported conditions |
| Deficiency labels | Derivable from lab reference ranges (standard clinical thresholds) |
| License | Public domain (CDC data) — free to use |
| Verdict | **PRIMARY SELECTED DATASET** |

### 2.3 Open Food Facts / USDA FoodData Central
| Attribute | Detail |
|-----------|--------|
| Source | Open Food Facts / USDA |
| Type | **Food composition database** |
| Contains | Nutritional content per food item (per 100 g) |
| Deficiency labels | NONE — this is nutrient reference data, NOT health outcome data |
| Verdict | NOT suitable as training data — already used in NutriWise for diary lookup |

### 2.4 UK Biobank
| Attribute | Detail |
|-----------|--------|
| Source | UK Biobank |
| Type | Large-scale biomedical database |
| Access | Requires institutional registration, data access agreement, and fee |
| Verdict | NOT accessible — gated behind formal application |

### 2.5 Published Clinical Studies
| Attribute | Detail |
|-----------|--------|
| Type | Aggregated results / curated synthetic datasets from published literature |
| Access | Individual-level data generally not publicly available |
| Verdict | NOT usable directly — no downloadable individual-level labeled data |

---

## 3. Selected Dataset: NHANES (Synthetic Representative Simulation)

### 3.1 Critical Disclosure — Data Availability

NHANES individual microdata is publicly available from the CDC website but
requires downloading multiple SAS-format files (XPT files) across several
survey components, then merging them by the SEQN respondent ID.

For Phase 1 of this project, the following approach is taken:

A synthetic dataset is generated to closely mirror real NHANES structure,
variable naming conventions, value distributions, and clinical reference ranges
derived from published NHANES documentation and peer-reviewed literature.

**This synthetic dataset is NOT fabricated predictions — it is a realistic
simulation of the data structure and statistical distributions that NHANES
provides, generated using documented reference ranges and epidemiological
prevalence estimates.**

The pipeline is designed to be a drop-in replacement once real NHANES XPT
files are available. The data generation script (generate_nhanes_synthetic.py)
is fully documented and reproducible.

Why not download NHANES XPT directly in Phase 1?
- XPT file parsing requires pyreadstat or xport which adds dependency overhead
- Multiple files must be joined: DEMO, BPX, BMX, DIQ, DPQ, LAB (CBC, FERTIN, VID, B12, BIO)
- Merging these correctly requires careful documentation review
- The synthetic approach lets us validate the entire ML pipeline end-to-end
- Phase 2 can substitute real NHANES data as a direct drop-in

---

## 4. Feature Inventory

### 4.1 Demographic / Health Profile Features
| Variable Name | Description | Type |
|---------------|-------------|------|
| age | Age in years | Numeric |
| gender | Sex (0=Female, 1=Male) | Binary |
| bmi | Body Mass Index (kg/m2) | Numeric |
| activity_level | Physical activity category | Ordinal |
| dietary_preference | Diet type (omnivore/vegetarian/vegan) | Categorical |
| is_pregnant | Pregnancy status (0/1) | Binary |
| is_smoker | Smoking status (0/1) | Binary |

### 4.2 Dietary / Nutrient Intake Features (24-hour recall)
| Variable Name | Description | Unit |
|---------------|-------------|------|
| dietary_iron_mg | Daily iron intake | mg/day |
| dietary_calcium_mg | Daily calcium intake | mg/day |
| dietary_vitamin_d_mcg | Daily vitamin D intake | mcg/day |
| dietary_vitamin_b12_mcg | Daily vitamin B12 intake | mcg/day |
| dietary_folate_mcg | Daily folate/folic acid | mcg DFE/day |
| dietary_vitamin_c_mg | Daily vitamin C | mg/day |
| dietary_protein_g | Daily protein | g/day |
| dietary_calories_kcal | Daily energy intake | kcal/day |
| dietary_fiber_g | Daily fiber | g/day |

### 4.3 Laboratory / Blood Test Features
| Variable Name | Description | Unit | Clinical Significance |
|---------------|-------------|------|----------------------|
| hemoglobin_g_dl | Hemoglobin concentration | g/dL | Iron-deficiency anaemia |
| serum_ferritin_ng_ml | Iron storage protein | ng/mL | Iron depletion |
| serum_iron_mcg_dl | Serum iron level | mcg/dL | Iron status |
| tibc_mcg_dl | Total Iron Binding Capacity | mcg/dL | Iron status |
| transferrin_saturation_pct | Transferrin saturation % | % | Iron status |
| vitamin_d_25ohd_ng_ml | 25-hydroxyvitamin D (serum) | ng/mL | Vitamin D status |
| vitamin_b12_pg_ml | Serum cobalamin | pg/mL | B12 status |
| serum_calcium_mg_dl | Serum calcium | mg/dL | Calcium status |
| serum_folate_ng_ml | Serum folate | ng/mL | Folate status |
| rbc_folate_ng_ml | Red blood cell folate | ng/mL | Folate tissue stores |

### 4.4 Symptom-Related Features
| Variable Name | Description | Encoding |
|---------------|-------------|----------|
| symptom_fatigue | Presence of fatigue | Binary 0/1 |
| symptom_hair_loss | Hair loss or thinning | Binary 0/1 |
| symptom_skin_issues | Skin conditions (pallor, dryness) | Binary 0/1 |
| symptom_muscle_weakness | Muscle weakness | Binary 0/1 |
| symptom_mood_low | Depression/mood disturbances | Binary 0/1 |
| symptom_bone_pain | Bone or joint pain | Binary 0/1 |
| symptom_tingling | Paresthesia/numbness/tingling | Binary 0/1 |
| symptom_cold_intolerance | Cold intolerance | Binary 0/1 |
| symptom_count | Total symptom count | Numeric |

---

## 5. Target Labels

Deficiency thresholds are derived from established clinical reference ranges
(WHO, NIH, and NHANES analytical guidelines):

| Label | Condition | Clinical Threshold | Primary Lab Indicator |
|-------|-----------|-------------------|----------------------|
| iron_deficiency | Iron deficiency | Serum ferritin < 12 ng/mL; Hgb < 12 g/dL (F) / 13 g/dL (M) | serum_ferritin_ng_ml, hemoglobin_g_dl |
| vitamin_d_deficiency | Vitamin D deficiency | 25OHD < 20 ng/mL (deficient); 20-29 ng/mL (insufficient) | vitamin_d_25ohd_ng_ml |
| vitamin_b12_deficiency | B12 deficiency | Serum B12 < 200 pg/mL | vitamin_b12_pg_ml |
| calcium_deficiency | Calcium deficiency / hypocalcaemia | Serum Ca < 8.5 mg/dL | serum_calcium_mg_dl |
| folate_deficiency | Folate deficiency | Serum folate < 3 ng/mL | serum_folate_ng_ml |

Phase 1 approach: Binary classification per deficiency (one model per deficiency)
Phase 2 (future): Multi-label joint model

---

## 6. Limitations

| # | Limitation | Impact |
|---|-----------|--------|
| L1 | Synthetic data used - not actual NHANES microdata | May not capture true population distributions |
| L2 | Single dietary recall (1-day) is noisy | Dietary features estimated from single-day intake |
| L3 | Symptom features are self-reported — subject to recall bias | Feature reliability varies |
| L4 | No genetic markers (e.g., MTHFR polymorphisms) | Cannot capture genetic predisposition |
| L5 | NHANES is US-based | Model may underperform in non-US populations |
| L6 | Calcium deficiency is difficult to assess via serum calcium alone | Serum Ca has low sensitivity for dietary calcium deficiency |
| L7 | Iodine, Magnesium, Zinc deficiencies not included | Insufficient reliable biomarker data |
| L8 | Biotin, Vitamin K, Vitamin E deficiencies not supported | No reliable individual-level labeled data available |

---

## 7. Unsupported Deficiencies

The following deficiencies CANNOT be reliably detected with the available dataset
and are EXPLICITLY EXCLUDED from Phase 1 modeling:

| Deficiency | Reason for Exclusion |
|-----------|----------------------|
| Iodine | Not routinely measured in NHANES; no reliable individual-level data |
| Magnesium | Serum Mg is a poor indicator of body stores; limited NHANES coverage |
| Zinc | No consistent zinc biomarker in general NHANES waves |
| Vitamin A | Available in some NHANES cycles but inconsistent; excluded for consistency |
| Biotin | No standard clinical biomarker in population surveys |
| Vitamin K | No routine serum test in population surveys |
| Vitamin E | Excluded from Phase 1 scope |
| Selenium | Limited NHANES data across consistent cycles |

---

## 8. Assumptions

| # | Assumption |
|---|-----------|
| A1 | Clinical deficiency thresholds based on WHO/NIH/NHANES published reference values |
| A2 | A subject is labeled as deficient if their primary lab biomarker falls below threshold |
| A3 | Dietary intake features represent a single 24-hour day |
| A4 | Gender is binary-encoded (0=Female, 1=Male) matching NHANES convention |
| A5 | Pregnancy status affects iron/folate reference ranges; pregnancy indicator included |
| A6 | Missing lab values treated as genuinely missing — imputed during cleaning |
| A7 | Symptom features represent presence/absence rather than severity in Phase 1 |
| A8 | Synthetic dataset class balance approximates documented NHANES deficiency prevalence |

---

## 9. Deficiency Prevalence Rates (from Literature)

Used to calibrate synthetic data generation:

| Deficiency | Estimated US Prevalence | Notes |
|-----------|------------------------|-------|
| Iron deficiency | 8-15% (up to 15-20% in women of reproductive age) | Looker et al., JAMA 1997; CDC |
| Vitamin D deficiency (<20 ng/mL) | 28-36% | Forrest & Stuhldreher 2011; NHANES 2001-2006 |
| Vitamin B12 deficiency | 3-6% | Pfeiffer et al., NHANES 2003-2006 |
| Calcium dietary inadequacy | 42% below EAR | Bailey et al., 2010 |
| Folate deficiency | <1% post-fortification (US) | Pfeiffer et al. 2012 |

---

## 10. Licensing and Usage Considerations

| Dataset | License | Restrictions |
|---------|---------|-------------|
| NHANES public data | Public domain (US government) | Free for research; CDC attribution recommended |
| WHO aggregate data | CC BY-NC-SA | Attribution; non-commercial |
| Open Food Facts | ODbL | Share-alike; attribution |
| USDA FoodData | Public domain | Free for use |
| Synthetic data (this project) | MIT (project license) | No restrictions |

---

## 11. Phase 2 Real NHANES Data Integration Plan

To replace synthetic dataset with real NHANES data:

1. Download NHANES cycle files (e.g., 2017-2018):
   - DEMO_J.XPT — Demographics
   - BMX_J.XPT — Body measures (BMI)
   - DR1TOT_J.XPT — Dietary total nutrients (Day 1)
   - CBC_J.XPT — Complete blood count (Hemoglobin)
   - FERTIN_J.XPT — Serum ferritin
   - VID_J.XPT — Vitamin D
   - B12_J.XPT — Vitamin B12
   - BIOPRO_J.XPT — Biochemistry profile (Ca, Fe, TIBC)
   - DPQ_J.XPT — Depression screener (PHQ-9, proxy for mood symptoms)
2. Merge on SEQN (unique respondent identifier)
3. Apply the same cleaning and feature engineering pipeline
4. Retrain models — same code, real data

---

## 12. Summary Decision

| Decision | Rationale |
|----------|-----------|
| Dataset selected: Synthetic NHANES-structured dataset | No download-access issues; complete end-to-end pipeline validation; documented drop-in for real NHANES |
| Deficiencies covered: Iron, Vitamin D, B12, Calcium, Folate | These have reliable, published clinical biomarker thresholds |
| Deficiencies excluded: Iodine, Mg, Zn, Biotin, VitK, VitE | No reliable individual-level labeled data available |
| Label derivation method: Clinical threshold rules on lab values | Not ML predictions on synthetic labels — thresholds from WHO/NIH |
| Food-composition data: NOT used as training data | Clearly distinct role — used in NutriWise diary module only |
