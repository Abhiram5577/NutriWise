
# Day 12 — Exploratory Data Analysis Report
## Milestone 2: ML Nutritional Deficiency Detection Engine

---

## 1. Dataset Structure

- **Shape:** 5015 rows x 41 columns
- **File:** nhanes_synthetic_raw.csv
- **Source:** Synthetic NHANES-structured dataset (see Day 11 report)

### Column Groups
- Demographic features: 7
- Laboratory features: 10
- Dietary features: 9
- Symptom features: 9
- Target labels: 5
- ID column: 1 (subject_id)

### Data Types
  - `float64`: 26 columns
  - `int64`: 15 columns

## 2. Missing Value Analysis

**15 columns** have missing values:

| Column | Missing Count | Missing % |
|--------|--------------|-----------|
| rbc_folate_ng_ml | 634 | 12.64% |
| vitamin_d_deficiency | 544 | 10.85% |
| vitamin_d_25ohd_ng_ml | 544 | 10.85% |
| serum_folate_ng_ml | 509 | 10.15% |
| folate_deficiency | 509 | 10.15% |
| vitamin_b12_pg_ml | 498 | 9.93% |
| vitamin_b12_deficiency | 498 | 9.93% |
| tibc_mcg_dl | 415 | 8.28% |
| serum_iron_mcg_dl | 410 | 8.18% |
| transferrin_saturation_pct | 408 | 8.14% |
| serum_ferritin_ng_ml | 395 | 7.88% |
| calcium_deficiency | 359 | 7.16% |
| serum_calcium_mg_dl | 359 | 7.16% |
| hemoglobin_g_dl | 259 | 5.16% |
| iron_deficiency | 19 | 0.38% |

**Figure saved:** fig01_missing_values.png

## 3. Duplicate Record Analysis

- Total rows: 5015
- Exact duplicate rows (excluding subject_id): **15**
- Duplicate rate: 0.30%

**Action (deferred to Day 13):** Duplicates identified; will be removed in cleaning.
Duplicates were deliberately injected (see generate_nhanes_synthetic.py, inject_data_quality_issues).

## 4. Invalid Value Analysis

- `age`: 6 records outside [18, 110] range
  Values: [-5.0, 0.0, 18.0, 19.0, 20.0]
- `bmi`: 3 records outside [10, 80] range
- `hemoglobin_g_dl`: 10 records outside [3, 25] g/dL range
  Values found: [-1.0, 0.0, 0.0, 0.0, 0.0]
- `dietary_iron_mg`: 8 negative values (physiologically impossible)

**Total invalid value issues found: 4**
**Action (deferred to Day 13):** Invalid records will be flagged and handled in cleaning.

## 5. Target Label Distribution

| Deficiency | Positive (Deficient) | Negative (Normal) | Missing | Prevalence (%) |
|-----------|---------------------|------------------|---------|----------------|
| iron_deficiency | 805 | 4191 | 19 | 16.1% |
| vitamin_d_deficiency | 1514 | 2957 | 544 | 33.9% |
| vitamin_b12_deficiency | 442 | 4075 | 498 | 9.8% |
| calcium_deficiency | 172 | 4484 | 359 | 3.7% |
| folate_deficiency | 107 | 4399 | 509 | 2.4% |

### Class Imbalance Assessment

- Iron deficiency: ~16% — moderately imbalanced
- Vitamin D deficiency: ~34% — moderate imbalance (near 1:2)
- Vitamin B12 deficiency: ~10% — imbalanced
- Calcium deficiency: ~4% — highly imbalanced
- Folate deficiency: ~2% — highly imbalanced

**Implication:** Class weights or SMOTE oversampling may be needed for B12, Calcium, Folate models.

**Figure saved:** fig02_target_distributions.png

## 6. Demographic Feature Distributions

### Continuous Demographic Summary Statistics

           age      bmi
count  5015.00  5015.00
mean     48.96    28.35
std      18.57     6.47
min      -5.00     0.00
25%      33.00    24.02
50%      49.00    28.23
75%      65.00    32.67
max     200.00    55.48

### Categorical Demographic Counts

**Gender:** (0=Female, 1=Male)
gender
0    2600
1    2415

**Activity Level:** (0=Sedentary, 1=Light, 2=Moderate, 3=Active, 4=Very Active)
activity_level
0    1503
1    1205
2    1291
3     763
4     253

**Dietary Preference:** (0=Omnivore, 1=Vegetarian, 2=Vegan)
dietary_preference
0    4661
1     245
2     109

**Is Pregnant:**
is_pregnant
0    4963
1      52

**Is Smoker:**
is_smoker
0    4342
1     673

**Figure saved:** fig03_demographics.png

## 7. Laboratory Feature Distributions

### Laboratory Feature Summary Statistics

       hemoglobin_g_dl  serum_ferritin_ng_ml  serum_iron_mcg_dl  tibc_mcg_dl  transferrin_saturation_pct  vitamin_d_25ohd_ng_ml  vitamin_b12_pg_ml  serum_calcium_mg_dl  serum_folate_ng_ml  rbc_folate_ng_ml
count         4756.000              4620.000           4605.000     4600.000                    4607.000               4471.000           4517.000             4656.000            4506.000          4381.000
mean            14.499                81.986             99.043      299.560                      33.874                 30.113            467.336                9.398              15.659           374.997
std              2.668                90.001             29.944       44.686                      11.619                 18.846            265.147                0.507              11.488           248.708
min             -1.000                 1.677             20.000      150.000                       5.499                  4.000             50.000                7.659               1.130            50.000
25%             13.199                26.397             79.430      268.725                      25.956                 17.090            282.031                9.053               7.709           189.136
50%             14.448                51.676             98.565      299.143                      33.078                 25.419            409.455                9.385              12.494           315.228
75%             15.713                99.609            119.135      329.995                      40.994                 37.620            584.009                9.732              20.073           502.230
max             99.000               500.000            250.000      483.844                      90.000                100.000           2000.000               11.195              78.000          1000.000

**Figure saved:** fig04_lab_distributions.png

## 8. Dietary Feature Distributions

### Dietary Feature Summary Statistics

       dietary_iron_mg  dietary_calcium_mg  dietary_vitamin_d_mcg  dietary_vitamin_b12_mcg  dietary_folate_mcg  dietary_vitamin_c_mg  dietary_protein_g  dietary_calories_kcal  dietary_fiber_g
count          5015.00             5015.00                5015.00                  5015.00             5015.00               5015.00            5015.00                5015.00          5015.00
mean             14.73             1039.30                   6.91                     5.59              426.75                113.94              77.13                2000.60            17.61
std               5.53              378.83                   6.21                     4.56              194.73                 87.47              32.09                 538.80             7.44
min              -8.20               50.00                   0.11                     0.14               30.00                  6.41               4.25                 500.00             0.00
25%              10.91              785.97                   2.96                     2.60              290.29                 55.67              54.69                1641.10            12.51
50%              14.78             1037.09                   5.09                     4.28              423.79                 90.27              77.34                1991.03            17.45
75%              18.53             1292.57                   8.72                     7.03              557.93                144.65              99.57                2352.15            22.29
max              36.45             2384.86                  60.00                    30.00             1250.31                996.66             199.47                4139.93            52.90

**Figure saved:** fig05_dietary_distributions.png

## 9. Symptom Feature Analysis

### Symptom Prevalence (% of subjects reporting each symptom)

| Symptom | Count | Prevalence % |
|---------|-------|-------------|
| symptom_fatigue | 1725 | 34.4% |
| symptom_hair_loss | 1054 | 21.0% |
| symptom_skin_issues | 775 | 15.5% |
| symptom_muscle_weakness | 630 | 12.6% |
| symptom_mood_low | 1055 | 21.0% |
| symptom_bone_pain | 606 | 12.1% |
| symptom_tingling | 460 | 9.2% |
| symptom_cold_intolerance | 472 | 9.4% |

### Symptom Count Distribution
count    5015.00
mean        1.35
std         1.10
min         0.00
25%         1.00
50%         1.00
75%         2.00
max         7.00

**Figure saved:** fig06_symptom_analysis.png

## 10. Outlier Investigation

Method: IQR-based flagging (value < Q1 - 1.5*IQR or > Q3 + 1.5*IQR)

                   feature  lower_fence  upper_fence  n_outliers  outlier_pct
      serum_ferritin_ng_ml      -83.422      209.428         365         7.90
     dietary_vitamin_d_mcg       -5.694       17.375         302         6.02
   dietary_vitamin_b12_mcg       -4.051       13.678         300         5.98
     vitamin_d_25ohd_ng_ml      -13.705       68.415         240         5.37
      dietary_vitamin_c_mg      -77.794      278.118         251         5.00
        serum_folate_ng_ml      -10.837       38.620         224         4.97
          rbc_folate_ng_ml     -280.505      971.870         214         4.88
         vitamin_b12_pg_ml     -170.936     1036.977         174         3.85
transferrin_saturation_pct        3.399       63.551          61         1.32
           dietary_fiber_g       -2.165       36.961          56         1.12
       serum_calcium_mg_dl        8.035       10.750          33         0.71
     dietary_calories_kcal      574.532     3418.718          35         0.70
               tibc_mcg_dl      176.821      421.899          28         0.61
                       bmi       11.041       45.650          27         0.54
        dietary_folate_mcg     -111.159      959.383          27         0.54
           dietary_iron_mg       -0.519       29.961          26         0.52
           hemoglobin_g_dl        9.429       19.483          23         0.48
         serum_iron_mcg_dl       19.872      178.693          14         0.30
        dietary_calcium_mg       26.076     2052.464          14         0.28
         dietary_protein_g      -12.647      166.906          13         0.26
                       age      -15.000      113.000           3         0.06

### Outlier Treatment Decision (deferred to Day 13)

- Log-normal features (serum_ferritin, vitamin_b12, dietary_vitamin_b12): IQR outliers may be genuine
- Invalid values (negative, impossible) will be removed in cleaning
- Extreme but physiologically plausible values will be retained with capping consideration
- No records silently deleted here; decisions documented in cleaning script

**Figure saved:** fig07_outlier_boxplots.png

## 11. Feature Correlations

**Figure saved:** fig08_correlation_heatmap.png

### Key Correlation Observations
- hemoglobin and serum_ferritin: expected positive correlation (both iron markers)
- serum_iron and tibc: mildly negative (iron deficiency raises TIBC)
- transferrin_saturation = serum_iron / TIBC — strong correlation with both
- iron_deficiency: negatively correlated with hemoglobin, ferritin
- vitamin_d_deficiency: negatively correlated with vitamin_d_25ohd_ng_ml

## 12. Deficiency vs. Key Feature Analysis

**Figure saved:** fig09_deficiency_vs_features.png

## 13. EDA Conclusions Relevant to Model Development

1. **Class imbalance is significant** for calcium and folate deficiency (~4% and ~2%).
   Use class_weight='balanced' in Random Forest or SMOTE in Day 13/14.

2. **Missing values are lab-test specific** (5-12%). Lab features missing together for
   the same subject (systematic missing, not random). Impute with median by gender.

3. **Invalid values confirmed**: negative hemoglobin, age=0/150/200, negative dietary iron,
   impossible BMI. All must be removed in Day 13 cleaning.

4. **15 exact duplicate rows** detected (injected deliberately). Remove in Day 13.

5. **Lab markers are strong predictors** of their corresponding deficiencies (by design —
   labels are derived from those same lab values). In inference, lab values may not always
   be available; dietary + symptom features are the secondary signal.

6. **Log-normal distributions** for serum_ferritin, vitamin_b12, dietary_vitamin_b12:
   log-transform before modeling or use tree-based models that are scale-invariant.

7. **Symptom features are soft signals**: individual symptoms have low specificity.
   symptom_count may be more useful than individual binary flags.

8. **Dietary features are single-day estimates**: high variability; treat as rough signal
   rather than precise nutritional assessment.

9. **Vegetarian/Vegan dietary preference** is a strong risk modifier for B12 deficiency.
   Include as categorical feature.

10. **Transferrin saturation** is a derived variable (serum_iron/TIBC*100).
    May introduce leakage if all three are included simultaneously — consider dropping
    one or using it in place of its components.
