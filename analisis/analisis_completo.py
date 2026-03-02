#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
=============================================================================
ANALISIS ESTADISTICO COMPLETO
Estudio cuasi-experimental: Navegacion espacial en personas con discapacidad
visual (DV) vs normovidentes (NDV)

Autor: Script generado para analisis exhaustivo
Fecha: 2026-03-01
=============================================================================
"""

# ---------------------------------------------------------------------------
# 0. SETUP: imports, paths, install missing packages
# ---------------------------------------------------------------------------
import subprocess
import sys

def install_if_missing(package, pip_name=None):
    """Install a package if it is not already available."""
    try:
        __import__(package)
    except ImportError:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", pip_name or package, "-q"]
        )

for pkg, pip_name in [
    ("pandas", None), ("numpy", None), ("scipy", None),
    ("statsmodels", None), ("pingouin", None),
    ("matplotlib", None), ("seaborn", None), ("openpyxl", None),
]:
    install_if_missing(pkg, pip_name)

import warnings
warnings.filterwarnings("ignore")

import os
import numpy as np
import pandas as pd
import scipy.stats as stats
import statsmodels.api as sm
from statsmodels.formula.api import ols
from statsmodels.stats.anova import AnovaRM
from statsmodels.stats.diagnostic import het_breuschpagan
import pingouin as pg
import matplotlib
matplotlib.use("Agg")  # non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from itertools import combinations, product
from collections import OrderedDict
import textwrap

np.random.seed(42)

# ---------------------------------------------------------------------------
# PATHS
# ---------------------------------------------------------------------------
BASE_DIR = "/Users/mateo.belalcazar/Desktop/articulos/Navegación ciegos"
DATA_FILE = os.path.join(BASE_DIR, "Bases de datos", "datos 26_06_2024.xlsx")
OUT_DIR = os.path.join(BASE_DIR, "empiricos")
RESULTS_FILE = os.path.join(OUT_DIR, "resultados_completos.txt")

os.makedirs(OUT_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# OUTPUT HELPERS
# ---------------------------------------------------------------------------
_output_lines = []

def out(text=""):
    """Append text to the output buffer."""
    _output_lines.append(str(text))

def section(title, level=1):
    """Print a section header."""
    if level == 1:
        sep = "=" * 80
        out(f"\n{sep}")
        out(f"  {title.upper()}")
        out(sep)
    elif level == 2:
        sep = "-" * 70
        out(f"\n{sep}")
        out(f"  {title}")
        out(sep)
    else:
        out(f"\n  >> {title}")
        out(f"  {'.' * 60}")

def flush_output():
    """Write all buffered output to the results file."""
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(_output_lines))
    print(f"Results saved to: {RESULTS_FILE}")

def fmt(x, d=3):
    """Format a number to d decimal places."""
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "NaN"
    return f"{x:.{d}f}"

def fmt_p(p):
    """Format a p-value."""
    if p is None or (isinstance(p, float) and np.isnan(p)):
        return "NaN"
    if p < 0.001:
        return "< .001"
    return f"= {fmt(p, 3)}"

def stars(p):
    """Significance stars."""
    if p < 0.001:
        return "***"
    elif p < 0.01:
        return "**"
    elif p < 0.05:
        return "*"
    else:
        return "ns"

# ---------------------------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------------------------
section("CARGA DE DATOS")
df = pd.read_excel(DATA_FILE, sheet_name="Hoja1")
out(f"Archivo: {DATA_FILE}")
out(f"Dimensiones: {df.shape[0]} filas x {df.shape[1]} columnas")

# Rename the years-of-vision column to an ASCII-safe name
if "años.vision" in df.columns:
    df.rename(columns={"años.vision": "anos.vision"}, inplace=True)

# ---------------------------------------------------------------------------
# COLUMN NAME MAPS
# ---------------------------------------------------------------------------
SHAPES = ["agudo", "obtuso"]
SIZES = ["1", "2"]
MODALITIES = ["a", "t", "p", "c"]
MODALITY_LABELS = {"a": "Cinestesica", "t": "Tacto", "p": "Accion", "c": "Control"}
MODALITY_LABELS_SHORT = {"a": "CIN", "t": "TAC", "p": "ACC", "c": "CTR"}
SHAPE_LABELS = {"agudo": "Agudo", "obtuso": "Obtuso"}
SIZE_LABELS = {"1": "2m", "2": "4m"}
GROUP_LABELS = {"DV": "DV", "NDV": "NDV"}

def col_ea(shape, size, mod):
    return f"E.A.{shape}{size}{mod}"

def col_e(shape, size, mod):
    return f"E.{shape}{size}{mod}"

def col_g(shape, size, mod):
    return f"G.{shape}{size}{mod}"

def col_ga(shape, size, mod):
    return f"G.A.{shape}{size}{mod}"

def col_t(shape, size, mod):
    """Time column - mixed T/t capitalization in data."""
    for prefix in ["T", "t"]:
        name = f"{prefix}.{shape}{size}{mod}"
        if name in df.columns:
            return name
    return None

# All 16 conditions
CONDITIONS = [(sh, sz, mo) for sh in SHAPES for sz in SIZES for mo in MODALITIES]

# Build E.A column list
EA_COLS = [col_ea(sh, sz, mo) for sh, sz, mo in CONDITIONS]
E_COLS = [col_e(sh, sz, mo) for sh, sz, mo in CONDITIONS]
G_COLS = [col_g(sh, sz, mo) for sh, sz, mo in CONDITIONS]

# ============================================================================
# SECTION 0: DATA VALIDATION
# ============================================================================
section("SECCION 0: VALIDACION DE DATOS")

# --- Group Ns ---
section("0.1 Verificacion de N por grupo", 2)
grp_counts = df["condicion"].value_counts()
for g in ["DV", "NDV"]:
    out(f"  {g}: n = {grp_counts.get(g, 0)}")
out(f"  Total: N = {len(df)}")

# --- Missing data ---
section("0.2 Datos faltantes", 2)
ea_missing = df[EA_COLS].isnull().sum()
out(f"  Datos faltantes en columnas E.A (error con signo): {ea_missing.sum()} total")
if ea_missing.sum() > 0:
    for c in EA_COLS:
        m = df[c].isnull().sum()
        if m > 0:
            out(f"    {c}: {m} faltantes")

e_missing = df[E_COLS].isnull()
out(f"\n  Datos faltantes en columnas E (error absoluto):")
for c in E_COLS:
    m = df[c].isnull().sum()
    if m > 0:
        out(f"    {c}: {m} faltantes")

g_missing_total = df[G_COLS].isnull().sum().sum()
out(f"\n  Datos faltantes en columnas G (desviacion angular): {g_missing_total} total")
for c in G_COLS:
    m = df[c].isnull().sum()
    if m > 0:
        out(f"    {c}: {m} faltantes")

# --- Verify E.A = E * E.L ---
section("0.3 Verificacion E.A = E * E.L", 2)
mismatches = 0
for sh, sz, mo in CONDITIONS:
    e_col = col_e(sh, sz, mo)
    ea_col = col_ea(sh, sz, mo)
    el_col = f"E.L.{sh}{sz}{mo}"
    if e_col in df.columns and ea_col in df.columns and el_col in df.columns:
        computed = df[e_col] * df[el_col]
        check = np.isclose(computed.fillna(0), df[ea_col].fillna(0), atol=0.5)
        n_mismatch = (~check).sum()
        if n_mismatch > 0:
            mismatches += n_mismatch
            out(f"  ALERTA: {ea_col} tiene {n_mismatch} discrepancias con E*E.L")
if mismatches == 0:
    out("  OK: E.A = E * E.L se cumple en todas las condiciones.")

# --- Demographics ---
section("0.4 Estadisticos descriptivos demograficos por grupo", 2)
for var in ["edad", "escolaridad", "anos.vision"]:
    out(f"\n  Variable: {var}")
    for g in ["DV", "NDV"]:
        sub = df[df["condicion"] == g][var].dropna()
        out(f"    {g}: M = {fmt(sub.mean(), 2)}, DE = {fmt(sub.std(), 2)}, "
            f"Min = {sub.min()}, Max = {sub.max()}, n = {len(sub)}")

out("\n  Variable: Sexo (frecuencias)")
ct = pd.crosstab(df["condicion"], df["Sexo"])
out(ct.to_string())

# --- T-tests age, education ---
section("0.5 Comparacion demografica entre grupos", 2)
for var, label in [("edad", "Edad"), ("escolaridad", "Escolaridad")]:
    dv_vals = df[df["condicion"] == "DV"][var].dropna()
    ndv_vals = df[df["condicion"] == "NDV"][var].dropna()
    t_stat, p_val = stats.ttest_ind(dv_vals, ndv_vals, equal_var=False)
    d = pg.compute_effsize(dv_vals, ndv_vals, eftype="cohen")
    out(f"\n  {label}: t = {fmt(t_stat)}, p {fmt_p(p_val)}, d de Cohen = {fmt(d)} {stars(p_val)}")
    out(f"    DV: M = {fmt(dv_vals.mean(), 2)}, DE = {fmt(dv_vals.std(), 2)}")
    out(f"    NDV: M = {fmt(ndv_vals.mean(), 2)}, DE = {fmt(ndv_vals.std(), 2)}")

# Chi-square for sex
section("0.6 Chi-cuadrado para Sexo entre grupos", 2)
ct_sex = pd.crosstab(df["condicion"], df["Sexo"])
chi2, p_chi, dof_chi, expected = stats.chi2_contingency(ct_sex)
n_total = len(df)
cramers_v = np.sqrt(chi2 / (n_total * (min(ct_sex.shape) - 1)))
out(f"  Chi2({dof_chi}) = {fmt(chi2)}, p {fmt_p(p_chi)}, V de Cramer = {fmt(cramers_v)} {stars(p_chi)}")
out(f"  Frecuencias observadas:")
out(ct_sex.to_string())
out(f"  Frecuencias esperadas:")
out(pd.DataFrame(expected, index=ct_sex.index, columns=ct_sex.columns).round(2).to_string())


# ============================================================================
# HELPER: Build long-format data
# ============================================================================
def build_long(measure_func, var_name="value"):
    """
    Build a long-format DataFrame from wide data.
    measure_func: function(shape, size, mod) -> column name
    """
    rows = []
    for idx, row in df.iterrows():
        for sh in SHAPES:
            for sz in SIZES:
                for mo in MODALITIES:
                    col = measure_func(sh, sz, mo)
                    if col and col in df.columns:
                        val = row[col]
                    else:
                        val = np.nan
                    rows.append({
                        "subject": row["id"],
                        "condicion": row["condicion"],
                        "shape": sh,
                        "size": sz,
                        "modality": mo,
                        var_name: val,
                    })
    return pd.DataFrame(rows)


def build_long_collapsed(measure_func, var_name="value"):
    """
    Build long-format collapsed across shape and size (mean of 4 cells per modality).
    """
    rows = []
    for idx, row in df.iterrows():
        for mo in MODALITIES:
            vals = []
            for sh in SHAPES:
                for sz in SIZES:
                    col = measure_func(sh, sz, mo)
                    if col and col in df.columns:
                        v = row[col]
                        if pd.notna(v):
                            vals.append(v)
            mean_val = np.mean(vals) if vals else np.nan
            rows.append({
                "subject": row["id"],
                "condicion": row["condicion"],
                "modality": mo,
                var_name: mean_val,
            })
    return pd.DataFrame(rows)


def partial_eta_sq(ss_effect, ss_error):
    """Compute partial eta-squared."""
    if (ss_effect + ss_error) == 0:
        return 0.0
    return ss_effect / (ss_effect + ss_error)


def cohens_d(g1, g2):
    """Cohen's d with pooled SD."""
    n1, n2 = len(g1), len(g2)
    m1, m2 = np.mean(g1), np.mean(g2)
    s1, s2 = np.std(g1, ddof=1), np.std(g2, ddof=1)
    sp = np.sqrt(((n1 - 1) * s1**2 + (n2 - 1) * s2**2) / (n1 + n2 - 2))
    if sp == 0:
        return 0.0
    return (m1 - m2) / sp


# ============================================================================
# SECTION 1: REPRODUCE ORIGINAL ANALYSES
# ============================================================================
section("SECCION 1: REPRODUCCION DE ANALISIS ORIGINALES")

# ---- 1a: Descriptive statistics table ----
section("1a. Tabla de estadisticos descriptivos - Error de posicion con signo (E.A)", 2)
out(f"\n{'Condicion':<12} {'Forma':<10} {'Tamano':<6} {'Modalidad':<14} {'M':>8} {'DE':>8} {'n':>4}")
out("-" * 66)
for g in ["DV", "NDV"]:
    sub = df[df["condicion"] == g]
    for sh in SHAPES:
        for sz in SIZES:
            for mo in MODALITIES:
                col = col_ea(sh, sz, mo)
                vals = sub[col].dropna()
                out(f"{g:<12} {SHAPE_LABELS[sh]:<10} {SIZE_LABELS[sz]:<6} "
                    f"{MODALITY_LABELS[mo]:<14} {fmt(vals.mean(), 2):>8} "
                    f"{fmt(vals.std(), 2):>8} {len(vals):>4}")

# Also show collapsed by modality
section("Descriptivos colapsados por modalidad (E.A)", 3)
df_coll = build_long_collapsed(col_ea, "EA")
out(f"\n{'Condicion':<12} {'Modalidad':<14} {'M':>8} {'DE':>8} {'n':>4}")
out("-" * 52)
for g in ["DV", "NDV"]:
    for mo in MODALITIES:
        vals = df_coll[(df_coll["condicion"] == g) & (df_coll["modality"] == mo)]["EA"].dropna()
        out(f"{g:<12} {MODALITY_LABELS[mo]:<14} {fmt(vals.mean(), 2):>8} "
            f"{fmt(vals.std(), 2):>8} {len(vals):>4}")

# ---- 1b: Full factorial ANOVA 2x2x2x4 on E.A ----
section("1b. ANOVA factorial completo: 2(CE) x 2(Forma) x 2(Tamano) x 4(Modalidad) sobre E.A", 2)

try:
    df_long_ea = build_long(col_ea, "EA")
    df_long_ea = df_long_ea.dropna(subset=["EA"])

    # Levene's test for between-subjects factor
    section("Test de Levene para el factor entre-sujetos (condicion)", 3)
    # Use the mean EA per subject
    subj_means = df_long_ea.groupby(["subject", "condicion"])["EA"].mean().reset_index()
    dv_means = subj_means[subj_means["condicion"] == "DV"]["EA"]
    ndv_means = subj_means[subj_means["condicion"] == "NDV"]["EA"]
    lev_stat, lev_p = stats.levene(dv_means, ndv_means)
    out(f"  Levene: F = {fmt(lev_stat)}, p {fmt_p(lev_p)} {stars(lev_p)}")

    # Mixed ANOVA using pingouin
    out("\n  ANOVA mixto con pingouin (4 factores):")
    out("  Nota: pingouin maneja hasta 2 factores within. Se realiza con statsmodels.")

    # For the 4-way ANOVA we need a custom approach using statsmodels
    # Create proper coding for the repeated measures
    df_long_ea["shape_code"] = df_long_ea["shape"].map({"agudo": -0.5, "obtuso": 0.5})
    df_long_ea["size_code"] = df_long_ea["size"].map({"1": -0.5, "2": 0.5})

    # Use pingouin for the full mixed ANOVA through a workaround:
    # Pingouin can only handle one within factor at a time, so we create
    # a combined within factor for the full model
    df_long_ea["within_cond"] = (df_long_ea["shape"] + "_" +
                                  df_long_ea["size"] + "_" +
                                  df_long_ea["modality"])

    # Check we have complete cases for the full design
    complete_subjects = df_long_ea.groupby("subject")["within_cond"].nunique()
    complete_subjects = complete_subjects[complete_subjects == 16].index
    df_complete = df_long_ea[df_long_ea["subject"].isin(complete_subjects)].copy()
    out(f"\n  Sujetos con datos completos (16 condiciones): {len(complete_subjects)} de {df['id'].nunique()}")

    # Perform full ANOVA using AnovaRM from statsmodels for the omnibus,
    # then decompose manually
    # First, the combined within-subject ANOVA
    aov_full = pg.mixed_anova(
        data=df_complete, dv="EA", within="within_cond",
        between="condicion", subject="subject"
    )
    out("\n  ANOVA mixto (factor within combinado 16 niveles):")
    out(aov_full.to_string())

    # Now do the proper decomposition: iterate through all effects
    # We'll use a series of targeted ANOVAs to extract each effect

    out("\n  --- Descomposicion de efectos (ANOVAs separados) ---")

    # Helper to run 2-way mixed ANOVA and report
    def run_mixed_anova_2way(data, dv, within, between, subject, label):
        """Run and report a 2-way mixed ANOVA."""
        try:
            aov = pg.mixed_anova(data=data, dv=dv, within=within,
                                  between=between, subject=subject)
            out(f"\n  {label}:")
            for _, row in aov.iterrows():
                src = row["Source"]
                f_val = row.get("F", np.nan)
                df1 = row.get("DF1", row.get("ddof1", np.nan))
                df2 = row.get("DF2", row.get("ddof2", np.nan))
                p_val = row.get("p-unc", np.nan)
                eta = row.get("np2", np.nan)
                out(f"    {src}: F({fmt(df1,0)},{fmt(df2,0)}) = {fmt(f_val)}, "
                    f"p {fmt_p(p_val)}, eta_p2 = {fmt(eta)} {stars(p_val)}")
            return aov
        except Exception as e:
            out(f"\n  {label}: ERROR - {e}")
            return None

    # 1. Effect of shape (collapsing size and modality)
    df_by_shape = df_complete.groupby(["subject", "condicion", "shape"])["EA"].mean().reset_index()
    run_mixed_anova_2way(df_by_shape, "EA", "shape", "condicion", "subject",
                         "Efecto principal de Forma (colapsando tamano y modalidad)")

    # 2. Effect of size
    df_by_size = df_complete.groupby(["subject", "condicion", "size"])["EA"].mean().reset_index()
    run_mixed_anova_2way(df_by_size, "EA", "size", "condicion", "subject",
                         "Efecto principal de Tamano (colapsando forma y modalidad)")

    # 3. Effect of modality
    df_by_mod = df_complete.groupby(["subject", "condicion", "modality"])["EA"].mean().reset_index()
    run_mixed_anova_2way(df_by_mod, "EA", "modality", "condicion", "subject",
                         "Efecto principal de Modalidad (colapsando forma y tamano)")

    # 4. Shape x Size interaction
    df_sh_sz = df_complete.groupby(["subject", "condicion", "shape", "size"])["EA"].mean().reset_index()
    df_sh_sz["sh_sz"] = df_sh_sz["shape"] + "_" + df_sh_sz["size"]
    run_mixed_anova_2way(df_sh_sz, "EA", "sh_sz", "condicion", "subject",
                         "Interaccion Forma x Tamano")

    # 5. Shape x Modality
    df_sh_mo = df_complete.groupby(["subject", "condicion", "shape", "modality"])["EA"].mean().reset_index()
    df_sh_mo["sh_mo"] = df_sh_mo["shape"] + "_" + df_sh_mo["modality"]
    run_mixed_anova_2way(df_sh_mo, "EA", "sh_mo", "condicion", "subject",
                         "Interaccion Forma x Modalidad")

    # 6. Size x Modality
    df_sz_mo = df_complete.groupby(["subject", "condicion", "size", "modality"])["EA"].mean().reset_index()
    df_sz_mo["sz_mo"] = df_sz_mo["size"] + "_" + df_sz_mo["modality"]
    run_mixed_anova_2way(df_sz_mo, "EA", "sz_mo", "condicion", "subject",
                         "Interaccion Tamano x Modalidad")

    # 7. Full 4-way: already done above with within_cond
    # The full combined model captures all variance

    # --- Mauchly's sphericity ---
    section("Test de esfericidad de Mauchly (para factor modalidad, 4 niveles)", 3)
    try:
        sph = pg.sphericity(df_by_mod, dv="EA", within="modality", subject="subject",
                            method="mauchly")
        out(f"  Mauchly's W = {fmt(sph.W)}, chi2 = {fmt(sph.chi2)}, "
            f"df = {sph.dof}, p {fmt_p(sph.pval)}")
        if sph.pval < 0.05:
            out("  ** Esfericidad violada. Se aplica correccion Greenhouse-Geisser. **")
        else:
            out("  Esfericidad asumida (p > .05).")
    except Exception as e:
        out(f"  Error en test de esfericidad: {e}")

except Exception as e:
    out(f"\n  ERROR en ANOVA 4 factores: {e}")
    import traceback
    out(traceback.format_exc())

# ---- 1c: Collapsed ANOVA 2(CE) x 4(MS) on E.A ----
section("1c. ANOVA colapsado: 2(CE) x 4(Modalidad) sobre E.A (error de posicion con signo)", 2)

try:
    df_coll_ea = build_long_collapsed(col_ea, "EA")
    df_coll_ea = df_coll_ea.dropna(subset=["EA"])

    # Check complete cases
    complete_subj_coll = df_coll_ea.groupby("subject")["modality"].nunique()
    complete_subj_coll = complete_subj_coll[complete_subj_coll == 4].index
    df_coll_complete = df_coll_ea[df_coll_ea["subject"].isin(complete_subj_coll)].copy()
    out(f"  Sujetos completos: {len(complete_subj_coll)}")

    # Mixed ANOVA
    aov_coll = pg.mixed_anova(
        data=df_coll_complete, dv="EA", within="modality",
        between="condicion", subject="subject"
    )
    out("\n  ANOVA mixto 2(CE) x 4(Modalidad):")
    for _, row in aov_coll.iterrows():
        src = row["Source"]
        f_val = row.get("F", np.nan)
        df1 = row.get("DF1", row.get("ddof1", np.nan))
        df2 = row.get("DF2", row.get("ddof2", np.nan))
        p_val = row.get("p-unc", np.nan)
        p_gg = row.get("p-GG-corr", np.nan)
        eta = row.get("np2", np.nan)
        eps = row.get("eps", np.nan)
        line = (f"    {src}: F({fmt(df1,0)},{fmt(df2,0)}) = {fmt(f_val)}, "
                f"p {fmt_p(p_val)}, eta_p2 = {fmt(eta)} {stars(p_val)}")
        if pd.notna(eps):
            line += f", epsilon = {fmt(eps)}"
        if pd.notna(p_gg):
            line += f", p(GG) {fmt_p(p_gg)}"
        out(line)

    # Sphericity test for modality
    section("Esfericidad (Mauchly) para Modalidad", 3)
    try:
        sph_coll = pg.sphericity(df_coll_complete, dv="EA", within="modality",
                                  subject="subject", method="mauchly")
        out(f"  W = {fmt(sph_coll.W)}, chi2 = {fmt(sph_coll.chi2)}, "
            f"df = {sph_coll.dof}, p {fmt_p(sph_coll.pval)}")
        if sph_coll.pval < 0.05:
            out("  ** Esfericidad violada - usar correccion GG **")
        else:
            out("  Esfericidad asumida.")
    except Exception as e:
        out(f"  Error: {e}")

    # Post-hoc: pairwise comparisons for modality main effect
    section("Post-hoc: Comparaciones por pares de Modalidad (Bonferroni)", 3)
    ph_mod = pg.pairwise_tests(
        data=df_coll_complete, dv="EA", within="modality",
        subject="subject", padjust="bonf"
    )
    out(ph_mod.to_string())

    # Post-hoc: interaction decomposition
    section("Post-hoc: Efectos simples de Modalidad DENTRO de cada grupo", 3)
    for g in ["DV", "NDV"]:
        sub = df_coll_complete[df_coll_complete["condicion"] == g]
        out(f"\n  Grupo {g}:")
        try:
            rm_aov = pg.rm_anova(data=sub, dv="EA", within="modality", subject="subject")
            for _, row in rm_aov.iterrows():
                # pingouin rm_anova returns ng2 (generalized), not np2 (partial)
                eta_col = "np2" if "np2" in rm_aov.columns else "ng2"
                eta_val = row[eta_col]
                eta_label = "eta_p2" if eta_col == "np2" else "eta_g2"
                out(f"    F({fmt(row['ddof1'],0)},{fmt(row['ddof2'],0)}) = {fmt(row['F'])}, "
                    f"p {fmt_p(row['p-unc'])}, {eta_label} = {fmt(eta_val)}, "
                    f"eps = {fmt(row.get('eps', np.nan))} {stars(row['p-unc'])}")
            ph = pg.pairwise_tests(data=sub, dv="EA", within="modality",
                                    subject="subject", padjust="bonf")
            out(ph[["A", "B", "T", "p-unc", "p-corr", "hedges"]].to_string())
        except Exception as e:
            out(f"    Error: {e}")

    section("Post-hoc: Efectos simples de Grupo DENTRO de cada modalidad", 3)
    for mo in MODALITIES:
        sub = df_coll_complete[df_coll_complete["modality"] == mo]
        dv_vals = sub[sub["condicion"] == "DV"]["EA"].values
        ndv_vals = sub[sub["condicion"] == "NDV"]["EA"].values
        t_stat, p_val = stats.ttest_ind(dv_vals, ndv_vals, equal_var=False)
        d = cohens_d(dv_vals, ndv_vals)
        ci_diff = pg.compute_esci(stat=d, nx=len(dv_vals), ny=len(ndv_vals), eftype="cohen")
        out(f"\n  Modalidad {MODALITY_LABELS[mo]}:")
        out(f"    DV: M = {fmt(dv_vals.mean(), 2)}, DE = {fmt(dv_vals.std(), 2)}")
        out(f"    NDV: M = {fmt(ndv_vals.mean(), 2)}, DE = {fmt(ndv_vals.std(), 2)}")
        out(f"    t = {fmt(t_stat)}, p {fmt_p(p_val)}, d = {fmt(d)} {stars(p_val)}")

except Exception as e:
    out(f"\n  ERROR en ANOVA colapsado E.A: {e}")
    import traceback
    out(traceback.format_exc())

# ---- 1d: Same for Angular Error (G) ----
section("1d. ANOVA para Error Angular (G - desviacion respecto a 90 grados)", 2)

try:
    # Descriptives
    section("Descriptivos G por grupo y modalidad (colapsado)", 3)
    df_coll_g = build_long_collapsed(col_g, "G")
    df_coll_g = df_coll_g.dropna(subset=["G"])
    out(f"\n{'Condicion':<12} {'Modalidad':<14} {'M':>8} {'DE':>8} {'n':>4}")
    out("-" * 52)
    for g in ["DV", "NDV"]:
        for mo in MODALITIES:
            vals = df_coll_g[(df_coll_g["condicion"] == g) & (df_coll_g["modality"] == mo)]["G"].dropna()
            out(f"{g:<12} {MODALITY_LABELS[mo]:<14} {fmt(vals.mean(), 2):>8} "
                f"{fmt(vals.std(), 2):>8} {len(vals):>4}")

    # Full 4-way ANOVA on G
    section("ANOVA 4 factores sobre G", 3)
    df_long_g = build_long(col_g, "G")
    df_long_g = df_long_g.dropna(subset=["G"])

    complete_subj_g = df_long_g.groupby("subject").size()
    complete_subj_g = complete_subj_g[complete_subj_g == 16].index
    df_long_g_complete = df_long_g[df_long_g["subject"].isin(complete_subj_g)].copy()
    out(f"  Sujetos con datos completos en G: {len(complete_subj_g)}")

    # By modality (collapsed)
    df_g_mod = df_long_g_complete.groupby(["subject", "condicion", "modality"])["G"].mean().reset_index()
    aov_g_mod = pg.mixed_anova(data=df_g_mod, dv="G", within="modality",
                                between="condicion", subject="subject")
    out("\n  ANOVA mixto 2(CE) x 4(Modalidad) sobre G:")
    for _, row in aov_g_mod.iterrows():
        src = row["Source"]
        f_val = row.get("F", np.nan)
        df1 = row.get("DF1", row.get("ddof1", np.nan))
        df2 = row.get("DF2", row.get("ddof2", np.nan))
        p_val = row.get("p-unc", np.nan)
        eta = row.get("np2", np.nan)
        out(f"    {src}: F({fmt(df1,0)},{fmt(df2,0)}) = {fmt(f_val)}, "
            f"p {fmt_p(p_val)}, eta_p2 = {fmt(eta)} {stars(p_val)}")

    # Decompose by shape, size
    df_g_shape = df_long_g_complete.groupby(["subject", "condicion", "shape"])["G"].mean().reset_index()
    run_mixed_anova_2way(df_g_shape, "G", "shape", "condicion", "subject",
                         "G: Efecto de Forma")

    df_g_size = df_long_g_complete.groupby(["subject", "condicion", "size"])["G"].mean().reset_index()
    run_mixed_anova_2way(df_g_size, "G", "size", "condicion", "subject",
                         "G: Efecto de Tamano")

    # Post-hoc for G modality
    section("Post-hoc G: Comparaciones por pares de Modalidad", 3)
    complete_subj_g_coll = df_coll_g.groupby("subject")["modality"].nunique()
    complete_subj_g_coll = complete_subj_g_coll[complete_subj_g_coll == 4].index
    df_coll_g_comp = df_coll_g[df_coll_g["subject"].isin(complete_subj_g_coll)]

    ph_g = pg.pairwise_tests(data=df_coll_g_comp, dv="G", within="modality",
                              subject="subject", padjust="bonf")
    out(ph_g.to_string())

except Exception as e:
    out(f"\n  ERROR en analisis angular: {e}")
    import traceback
    out(traceback.format_exc())


# ============================================================================
# SECTION 2: ENHANCED ANALYSES
# ============================================================================
section("SECCION 2: ANALISIS MEJORADOS")

# ---- 2a: Effect sizes everywhere ----
section("2a. Tamanos del efecto y ICs para comparaciones clave", 2)

try:
    df_coll_ea2 = build_long_collapsed(col_ea, "EA").dropna(subset=["EA"])

    out("\n  Cohen's d e IC 95% para diferencia DV-NDV por modalidad:")
    out(f"  {'Modalidad':<14} {'d Cohen':>10} {'IC 95%':>20} {'Dif medias':>12}")
    out("  " + "-" * 60)
    for mo in MODALITIES:
        dv_v = df_coll_ea2[(df_coll_ea2["condicion"]=="DV") & (df_coll_ea2["modality"]==mo)]["EA"]
        ndv_v = df_coll_ea2[(df_coll_ea2["condicion"]=="NDV") & (df_coll_ea2["modality"]==mo)]["EA"]
        d = cohens_d(dv_v.values, ndv_v.values)
        diff = dv_v.mean() - ndv_v.mean()
        se_diff = np.sqrt(dv_v.var()/len(dv_v) + ndv_v.var()/len(ndv_v))
        ci_lo = diff - 1.96 * se_diff
        ci_hi = diff + 1.96 * se_diff
        out(f"  {MODALITY_LABELS[mo]:<14} {fmt(d):>10} [{fmt(ci_lo, 2)}, {fmt(ci_hi, 2)}]{'':<2} {fmt(diff, 2):>12}")

except Exception as e:
    out(f"  ERROR: {e}")

# ---- 2b: Power analysis ----
section("2b. Analisis de potencia", 2)

try:
    # Get the interaction effect size from the collapsed ANOVA
    if 'aov_coll' in dir():
        interaction_row = aov_coll[aov_coll["Source"] == "Interaction"]
        if len(interaction_row) > 0:
            eta_p2_int = interaction_row["np2"].values[0]
            f_effect = np.sqrt(eta_p2_int / (1 - eta_p2_int))
            out(f"  Interaccion CE x Modalidad:")
            out(f"    eta_p2 observado = {fmt(eta_p2_int)}")
            out(f"    f de Cohen = {fmt(f_effect)}")

            # Post-hoc power using pingouin
            from statsmodels.stats.power import FTestAnovaPower
            power_analysis = FTestAnovaPower()

            # For the interaction in a mixed design, approximate
            n_per_group_mean = (15 + 13) / 2
            # Observed power
            try:
                obs_power = power_analysis.power(
                    effect_size=f_effect,
                    nobs=n_per_group_mean,
                    alpha=0.05,
                    k_groups=8  # 2 groups x 4 modalities
                )
                out(f"    Potencia observada (aprox.): {fmt(obs_power)}")
            except Exception:
                out(f"    Potencia observada: calculo no disponible con este metodo.")

            # Sample size needed for 80% power
            try:
                needed_n = power_analysis.solve_power(
                    effect_size=f_effect,
                    power=0.80,
                    alpha=0.05,
                    k_groups=8
                )
                out(f"    N necesario por grupo para potencia .80: {int(np.ceil(needed_n))}")
            except Exception:
                out(f"    Calculo de N necesario no disponible.")

            # Also compute via pg.power_anova
            try:
                power_pg = pg.power_anova(eta_squared=eta_p2_int, k=4, n=int(n_per_group_mean), alpha=0.05)
                out(f"    Potencia (pg, k=4 modalidades, n={int(n_per_group_mean)}): {fmt(power_pg)}")
            except Exception:
                pass
        else:
            out("  No se encontro efecto de interaccion en el ANOVA previo.")
    else:
        out("  ANOVA colapsado no disponible para extraer tamano del efecto.")

except Exception as e:
    out(f"  ERROR: {e}")

# ---- 2c: Normality assessment ----
section("2c. Evaluacion de normalidad", 2)

try:
    df_coll_ea3 = build_long_collapsed(col_ea, "EA").dropna(subset=["EA"])

    out("\n  Shapiro-Wilk por condicion x modalidad:")
    out(f"  {'Grupo':<6} {'Modalidad':<14} {'W':>8} {'p':>10} {'Normal?':>10}")
    out("  " + "-" * 52)
    normality_violations = 0
    for g in ["DV", "NDV"]:
        for mo in MODALITIES:
            vals = df_coll_ea3[(df_coll_ea3["condicion"]==g) & (df_coll_ea3["modality"]==mo)]["EA"]
            if len(vals) >= 3:
                w, p = stats.shapiro(vals)
                normal = "Si" if p > 0.05 else "NO"
                if p <= 0.05:
                    normality_violations += 1
                out(f"  {g:<6} {MODALITY_LABELS[mo]:<14} {fmt(w):>8} {fmt_p(p):>10} {normal:>10}")

    out(f"\n  Celdas con normalidad violada (p < .05): {normality_violations} de 8")

except Exception as e:
    out(f"  ERROR: {e}")

# ---- 2d: Robust alternatives ----
section("2d. Alternativas robustas", 2)

try:
    section("Mann-Whitney U por modalidad (DV vs NDV)", 3)
    df_coll_ea4 = build_long_collapsed(col_ea, "EA").dropna(subset=["EA"])

    out(f"  {'Modalidad':<14} {'U':>10} {'p':>10} {'r (efecto)':>12} {'Sig':>6}")
    out("  " + "-" * 56)
    for mo in MODALITIES:
        dv_v = df_coll_ea4[(df_coll_ea4["condicion"]=="DV") & (df_coll_ea4["modality"]==mo)]["EA"].values
        ndv_v = df_coll_ea4[(df_coll_ea4["condicion"]=="NDV") & (df_coll_ea4["modality"]==mo)]["EA"].values
        u_stat, p_val = stats.mannwhitneyu(dv_v, ndv_v, alternative="two-sided")
        # Effect size r = Z / sqrt(N)
        z_val = stats.norm.ppf(1 - p_val/2) if p_val < 1.0 else 0
        r_eff = z_val / np.sqrt(len(dv_v) + len(ndv_v))
        out(f"  {MODALITY_LABELS[mo]:<14} {fmt(u_stat, 1):>10} {fmt_p(p_val):>10} "
            f"{fmt(r_eff):>12} {stars(p_val):>6}")

    # Friedman test as non-parametric alternative for within-subject modality effect
    section("Friedman test (alternativa no parametrica para efecto de modalidad)", 3)
    for g in ["DV", "NDV"]:
        sub = df_coll_ea4[df_coll_ea4["condicion"] == g].pivot(
            index="subject", columns="modality", values="EA"
        ).dropna()
        if len(sub) >= 3 and all(m in sub.columns for m in MODALITIES):
            chi2_f, p_f = stats.friedmanchisquare(
                sub["a"].values, sub["t"].values, sub["p"].values, sub["c"].values
            )
            k = 4
            n_f = len(sub)
            w_kendall = chi2_f / (n_f * (k - 1))
            out(f"  Grupo {g}: chi2({k-1}) = {fmt(chi2_f)}, p {fmt_p(p_f)}, "
                f"W de Kendall = {fmt(w_kendall)} {stars(p_f)}")

    # Aligned Rank Transform (ART) - simplified implementation
    section("ART ANOVA (Aligned Rank Transform) - Analisis de sensibilidad", 3)
    out("  Implementacion simplificada del ART para el modelo 2(CE) x 4(MS):")

    df_art = df_coll_ea4.copy()
    # Complete cases only
    complete_art = df_art.groupby("subject")["modality"].nunique()
    complete_art = complete_art[complete_art == 4].index
    df_art = df_art[df_art["subject"].isin(complete_art)].copy()

    # ART procedure: align and rank
    # For each effect, strip other effects and rank
    # Effect of condicion: align by removing modality effect
    mod_means = df_art.groupby("modality")["EA"].transform("mean")
    grand_mean = df_art["EA"].mean()
    df_art["aligned_cond"] = df_art["EA"] - mod_means + grand_mean
    df_art["ranked_cond"] = stats.rankdata(df_art["aligned_cond"])

    # Test on ranked aligned data
    aov_art_cond = pg.mixed_anova(data=df_art, dv="ranked_cond", within="modality",
                                   between="condicion", subject="subject")
    cond_row = aov_art_cond[aov_art_cond["Source"] == "condicion"]
    if len(cond_row) > 0:
        out(f"  ART - Efecto de Condicion: F = {fmt(cond_row['F'].values[0])}, "
            f"p {fmt_p(cond_row['p-unc'].values[0])}")

    # Effect of modality: align by removing condicion effect
    cond_means = df_art.groupby("condicion")["EA"].transform("mean")
    df_art["aligned_mod"] = df_art["EA"] - cond_means + grand_mean
    df_art["ranked_mod"] = stats.rankdata(df_art["aligned_mod"])

    aov_art_mod = pg.mixed_anova(data=df_art, dv="ranked_mod", within="modality",
                                  between="condicion", subject="subject")
    mod_row = aov_art_mod[aov_art_mod["Source"] == "modality"]
    if len(mod_row) > 0:
        out(f"  ART - Efecto de Modalidad: F = {fmt(mod_row['F'].values[0])}, "
            f"p {fmt_p(mod_row['p-unc'].values[0])}")

    # Interaction: align by removing main effects
    subj_means = df_art.groupby("subject")["EA"].transform("mean")
    df_art["aligned_int"] = df_art["EA"] - mod_means - cond_means + grand_mean
    df_art["ranked_int"] = stats.rankdata(df_art["aligned_int"])

    aov_art_int = pg.mixed_anova(data=df_art, dv="ranked_int", within="modality",
                                  between="condicion", subject="subject")
    int_row = aov_art_int[aov_art_int["Source"] == "Interaction"]
    if len(int_row) > 0:
        out(f"  ART - Interaccion CE x MS: F = {fmt(int_row['F'].values[0])}, "
            f"p {fmt_p(int_row['p-unc'].values[0])}")

except Exception as e:
    out(f"  ERROR: {e}")
    import traceback
    out(traceback.format_exc())


# ============================================================================
# SECTION 3: NEW PERSPECTIVES
# ============================================================================
section("SECCION 3: NUEVAS PERSPECTIVAS")

# ---- 3a: Individual differences ----
section("3a. Diferencias individuales: anos de ceguera", 2)

try:
    dv_data = df[df["condicion"] == "DV"].copy()

    out("\n  Correlaciones: anos de ceguera vs error de posicion medio por modalidad (grupo DV)")
    out(f"  {'Modalidad':<14} {'r':>8} {'p':>10} {'n':>4}")
    out("  " + "-" * 40)
    for mo in MODALITIES:
        # Mean EA across shapes and sizes for this modality
        ea_cols_mo = [col_ea(sh, sz, mo) for sh in SHAPES for sz in SIZES]
        dv_data[f"mean_EA_{mo}"] = dv_data[ea_cols_mo].mean(axis=1)
        valid = dv_data[["anos.vision", f"mean_EA_{mo}"]].dropna()
        if len(valid) >= 3:
            r, p = stats.pearsonr(valid["anos.vision"], valid[f"mean_EA_{mo}"])
            out(f"  {MODALITY_LABELS[mo]:<14} {fmt(r):>8} {fmt_p(p):>10} {len(valid):>4} {stars(p)}")

    # Benefit of touch/action: kinesthetic - touch, kinesthetic - action
    out("\n  Correlaciones: anos de ceguera vs 'beneficio' de modalidades externas")
    dv_data["benefit_touch"] = dv_data["mean_EA_a"].abs() - dv_data["mean_EA_t"].abs()
    dv_data["benefit_action"] = dv_data["mean_EA_a"].abs() - dv_data["mean_EA_p"].abs()

    for label, col in [("Beneficio Tacto (|CIN| - |TAC|)", "benefit_touch"),
                        ("Beneficio Accion (|CIN| - |ACC|)", "benefit_action")]:
        valid = dv_data[["anos.vision", col]].dropna()
        if len(valid) >= 3:
            r, p = stats.pearsonr(valid["anos.vision"], valid[col])
            out(f"  {label}: r = {fmt(r)}, p {fmt_p(p)}, n = {len(valid)} {stars(p)}")

except Exception as e:
    out(f"  ERROR: {e}")

# ---- 3b: Variability as DV ----
section("3b. Variabilidad como variable dependiente", 2)

try:
    # Levene's test per collapsed modality
    section("Levene's test por modalidad (DV vs NDV en EA colapsado)", 3)
    df_coll_lev = build_long_collapsed(col_ea, "EA").dropna(subset=["EA"])

    out(f"  {'Modalidad':<14} {'F Levene':>10} {'p':>10} {'Sig':>6}")
    out("  " + "-" * 44)
    for mo in MODALITIES:
        dv_v = df_coll_lev[(df_coll_lev["condicion"]=="DV") & (df_coll_lev["modality"]==mo)]["EA"]
        ndv_v = df_coll_lev[(df_coll_lev["condicion"]=="NDV") & (df_coll_lev["modality"]==mo)]["EA"]
        f_lev, p_lev = stats.levene(dv_v, ndv_v)
        out(f"  {MODALITY_LABELS[mo]:<14} {fmt(f_lev):>10} {fmt_p(p_lev):>10} {stars(p_lev):>6}")

    # Within-participant SD across 4 geometric conditions per modality
    section("Consistencia intra-participante (DE a traves de las 4 condiciones geometricas)", 3)
    consistency = []
    for idx, row in df.iterrows():
        for mo in MODALITIES:
            vals = []
            for sh in SHAPES:
                for sz in SIZES:
                    v = row[col_ea(sh, sz, mo)]
                    if pd.notna(v):
                        vals.append(v)
            sd_val = np.std(vals, ddof=1) if len(vals) >= 2 else np.nan
            consistency.append({
                "subject": row["id"],
                "condicion": row["condicion"],
                "modality": mo,
                "within_sd": sd_val,
            })
    df_consist = pd.DataFrame(consistency).dropna(subset=["within_sd"])

    out(f"\n  {'Grupo':<6} {'Modalidad':<14} {'M(DE)':>10} {'DE(DE)':>10}")
    out("  " + "-" * 44)
    for g in ["DV", "NDV"]:
        for mo in MODALITIES:
            vals = df_consist[(df_consist["condicion"]==g) & (df_consist["modality"]==mo)]["within_sd"]
            out(f"  {g:<6} {MODALITY_LABELS[mo]:<14} {fmt(vals.mean(), 2):>10} {fmt(vals.std(), 2):>10}")

    # Test DV vs NDV on consistency
    section("Comparacion de consistencia DV vs NDV", 3)
    for mo in MODALITIES:
        dv_sd = df_consist[(df_consist["condicion"]=="DV") & (df_consist["modality"]==mo)]["within_sd"]
        ndv_sd = df_consist[(df_consist["condicion"]=="NDV") & (df_consist["modality"]==mo)]["within_sd"]
        t_stat, p_val = stats.ttest_ind(dv_sd, ndv_sd, equal_var=False)
        d = cohens_d(dv_sd.values, ndv_sd.values)
        out(f"  {MODALITY_LABELS[mo]}: t = {fmt(t_stat)}, p {fmt_p(p_val)}, d = {fmt(d)} {stars(p_val)}")

except Exception as e:
    out(f"  ERROR: {e}")

# ---- 3c: Error direction analysis ----
section("3c. Analisis de la direccion del error (sesgo sistematico)", 2)

try:
    df_coll_dir = build_long_collapsed(col_ea, "EA").dropna(subset=["EA"])

    out("\n  Test t de una muestra: ?Es el error medio significativamente diferente de 0?")
    out(f"  {'Grupo':<6} {'Modalidad':<14} {'M':>8} {'DE':>8} {'t':>8} {'p':>10} {'d':>8} {'Dir':>12}")
    out("  " + "-" * 80)
    for g in ["DV", "NDV"]:
        for mo in MODALITIES:
            vals = df_coll_dir[(df_coll_dir["condicion"]==g) & (df_coll_dir["modality"]==mo)]["EA"]
            t_stat, p_val = stats.ttest_1samp(vals, 0)
            d = vals.mean() / vals.std() if vals.std() > 0 else 0
            direction = "Sobreest." if vals.mean() > 0 else "Subestim." if vals.mean() < 0 else "Sin sesgo"
            out(f"  {g:<6} {MODALITY_LABELS[mo]:<14} {fmt(vals.mean(), 2):>8} {fmt(vals.std(), 2):>8} "
                f"{fmt(t_stat):>8} {fmt_p(p_val):>10} {fmt(d):>8} {direction:>12} {stars(p_val)}")

except Exception as e:
    out(f"  ERROR: {e}")

# ---- 3d: Absolute vs signed error ----
section("3d. Error absoluto vs error con signo", 2)

try:
    df_coll_abs = build_long_collapsed(col_e, "E_abs").dropna(subset=["E_abs"])

    # Complete cases
    complete_abs = df_coll_abs.groupby("subject")["modality"].nunique()
    complete_abs = complete_abs[complete_abs == 4].index
    df_coll_abs_comp = df_coll_abs[df_coll_abs["subject"].isin(complete_abs)].copy()

    out(f"  Sujetos completos para error absoluto: {len(complete_abs)}")

    section("ANOVA 2(CE) x 4(Modalidad) sobre Error Absoluto (E)", 3)
    aov_abs = pg.mixed_anova(
        data=df_coll_abs_comp, dv="E_abs", within="modality",
        between="condicion", subject="subject"
    )
    for _, row in aov_abs.iterrows():
        src = row["Source"]
        f_val = row.get("F", np.nan)
        df1 = row.get("DF1", row.get("ddof1", np.nan))
        df2 = row.get("DF2", row.get("ddof2", np.nan))
        p_val = row.get("p-unc", np.nan)
        eta = row.get("np2", np.nan)
        out(f"    {src}: F({fmt(df1,0)},{fmt(df2,0)}) = {fmt(f_val)}, "
            f"p {fmt_p(p_val)}, eta_p2 = {fmt(eta)} {stars(p_val)}")

    # Descriptives for comparison
    out("\n  Comparacion Descriptiva: Error Absoluto vs Error con Signo")
    out(f"  {'Grupo':<6} {'Mod':<6} {'M(|E|)':>10} {'M(E.A)':>10} {'Dif':>10}")
    out("  " + "-" * 46)
    df_coll_ea_comp = build_long_collapsed(col_ea, "EA").dropna(subset=["EA"])
    for g in ["DV", "NDV"]:
        for mo in MODALITIES:
            abs_v = df_coll_abs[(df_coll_abs["condicion"]==g) & (df_coll_abs["modality"]==mo)]["E_abs"]
            sgn_v = df_coll_ea_comp[(df_coll_ea_comp["condicion"]==g) & (df_coll_ea_comp["modality"]==mo)]["EA"]
            out(f"  {g:<6} {MODALITY_LABELS_SHORT[mo]:<6} {fmt(abs_v.mean(), 2):>10} "
                f"{fmt(sgn_v.mean(), 2):>10} {fmt(abs_v.mean() - abs(sgn_v.mean()), 2):>10}")

except Exception as e:
    out(f"  ERROR: {e}")
    import traceback
    out(traceback.format_exc())

# ---- 3e: Bayesian analysis ----
section("3e. Analisis bayesiano", 2)

try:
    df_coll_bayes = build_long_collapsed(col_ea, "EA").dropna(subset=["EA"])
    complete_bayes = df_coll_bayes.groupby("subject")["modality"].nunique()
    complete_bayes = complete_bayes[complete_bayes == 4].index
    df_bayes = df_coll_bayes[df_coll_bayes["subject"].isin(complete_bayes)].copy()

    out("\n  Factores de Bayes (BF10) para cada efecto del modelo 2(CE) x 4(MS):")
    out("  (BF10 > 3: evidencia moderada, > 10: fuerte, > 100: muy fuerte)")
    out("  (BF10 < 1/3: evidencia moderada para H0)")

    # Bayesian t-tests for group effect within each modality
    section("BF10 para diferencia DV vs NDV por modalidad", 3)
    for mo in MODALITIES:
        dv_v = df_bayes[(df_bayes["condicion"]=="DV") & (df_bayes["modality"]==mo)]["EA"].values
        ndv_v = df_bayes[(df_bayes["condicion"]=="NDV") & (df_bayes["modality"]==mo)]["EA"].values
        try:
            bf = pg.bayesfactor_ttest(
                stats.ttest_ind(dv_v, ndv_v)[0],
                len(dv_v), len(ndv_v), paired=False
            )
            out(f"  {MODALITY_LABELS[mo]}: BF10 = {fmt(bf, 2)}")
        except Exception as e2:
            out(f"  {MODALITY_LABELS[mo]}: Error - {e2}")

    # Bayesian paired t-tests within each group for modality differences
    section("BF10 para comparaciones de modalidad dentro de cada grupo", 3)
    for g in ["DV", "NDV"]:
        out(f"\n  Grupo {g}:")
        sub = df_bayes[df_bayes["condicion"] == g].pivot(
            index="subject", columns="modality", values="EA"
        ).dropna()
        for m1, m2 in combinations(MODALITIES, 2):
            if m1 in sub.columns and m2 in sub.columns:
                t_val, _ = stats.ttest_rel(sub[m1], sub[m2])
                try:
                    bf = pg.bayesfactor_ttest(t_val, len(sub), paired=True)
                    out(f"    {MODALITY_LABELS_SHORT[m1]} vs {MODALITY_LABELS_SHORT[m2]}: "
                        f"BF10 = {fmt(bf, 2)}")
                except Exception:
                    out(f"    {MODALITY_LABELS_SHORT[m1]} vs {MODALITY_LABELS_SHORT[m2]}: "
                        f"BF10 = calculo no disponible")

    # Bayesian ANOVA (using pingouin if available)
    section("ANOVA bayesiano RM", 3)
    try:
        # pingouin doesn't have a direct Bayesian mixed ANOVA, so we'll compute
        # BF for the interaction by comparing models
        # Model with interaction vs model without
        # We approximate using BIC comparison from OLS
        df_bayes_coded = df_bayes.copy()
        df_bayes_coded["group_code"] = (df_bayes_coded["condicion"] == "DV").astype(int)
        df_bayes_coded = pd.get_dummies(df_bayes_coded, columns=["modality"], drop_first=False, dtype=int)
        mod_cols = [c for c in df_bayes_coded.columns if c.startswith("modality_")]

        # Approximate BF from BIC of full vs reduced models
        # Full model: group + modality + group:modality
        # Reduced: group + modality (no interaction)
        formula_full = "EA ~ C(condicion) * C(modality)"
        formula_red = "EA ~ C(condicion) + C(modality)"

        # Need to reconstruct modality as a column
        df_bayes2 = df_bayes.copy()
        model_full = ols(formula_full, data=df_bayes2).fit()
        model_red = ols(formula_red, data=df_bayes2).fit()

        bic_full = model_full.bic
        bic_red = model_red.bic
        # BF approximation: BF10 approx exp(-0.5 * (BIC_full - BIC_red))
        bf_interaction = np.exp(-0.5 * (bic_full - bic_red))

        out(f"  Aproximacion BF para la interaccion CE x MS (basado en BIC):")
        out(f"    BIC modelo completo (con interaccion) = {fmt(bic_full, 1)}")
        out(f"    BIC modelo reducido (sin interaccion) = {fmt(bic_red, 1)}")
        out(f"    BF10 (interaccion) ~ {fmt(bf_interaction, 3)}")
        if bf_interaction > 3:
            out(f"    Interpretacion: Evidencia a favor de la interaccion")
        elif bf_interaction < 1/3:
            out(f"    Interpretacion: Evidencia a favor de la hipotesis nula (sin interaccion)")
        else:
            out(f"    Interpretacion: Evidencia no concluyente")

    except Exception as e2:
        out(f"  Error en ANOVA bayesiano: {e2}")

except Exception as e:
    out(f"  ERROR: {e}")
    import traceback
    out(traceback.format_exc())

# ---- 3f: Time analysis ----
section("3f. Analisis del tiempo de navegacion (exploratorio)", 2)

try:
    df_coll_time = build_long_collapsed(col_t, "Time").dropna(subset=["Time"])

    out(f"\n  Datos de tiempo disponibles: {len(df_coll_time)} observaciones")

    section("Descriptivos de tiempo por grupo y modalidad", 3)
    out(f"  {'Grupo':<6} {'Modalidad':<14} {'M (seg)':>10} {'DE':>10} {'n':>4}")
    out("  " + "-" * 48)
    for g in ["DV", "NDV"]:
        for mo in MODALITIES:
            vals = df_coll_time[(df_coll_time["condicion"]==g) & (df_coll_time["modality"]==mo)]["Time"]
            if len(vals) > 0:
                out(f"  {g:<6} {MODALITY_LABELS[mo]:<14} {fmt(vals.mean(), 2):>10} "
                    f"{fmt(vals.std(), 2):>10} {len(vals):>4}")

    # Mixed ANOVA on time
    complete_time = df_coll_time.groupby("subject")["modality"].nunique()
    complete_time = complete_time[complete_time == 4].index
    df_time_comp = df_coll_time[df_coll_time["subject"].isin(complete_time)].copy()

    if len(complete_time) >= 5:
        section("ANOVA mixto 2(CE) x 4(Modalidad) sobre Tiempo", 3)
        aov_time = pg.mixed_anova(
            data=df_time_comp, dv="Time", within="modality",
            between="condicion", subject="subject"
        )
        for _, row in aov_time.iterrows():
            src = row["Source"]
            f_val = row.get("F", np.nan)
            df1 = row.get("DF1", row.get("ddof1", np.nan))
            df2 = row.get("DF2", row.get("ddof2", np.nan))
            p_val = row.get("p-unc", np.nan)
            eta = row.get("np2", np.nan)
            out(f"    {src}: F({fmt(df1,0)},{fmt(df2,0)}) = {fmt(f_val)}, "
                f"p {fmt_p(p_val)}, eta_p2 = {fmt(eta)} {stars(p_val)}")

        # Speed-accuracy correlation
        section("Correlacion velocidad-precision (por grupo)", 3)
        # Merge time and EA
        df_coll_ea_for_time = build_long_collapsed(col_ea, "EA").dropna(subset=["EA"])
        merged = df_coll_time.merge(df_coll_ea_for_time, on=["subject", "condicion", "modality"])

        for g in ["DV", "NDV"]:
            sub = merged[merged["condicion"] == g]
            if len(sub) >= 5:
                r, p = stats.pearsonr(sub["Time"], sub["EA"].abs())
                out(f"  Grupo {g}: r(tiempo, |error|) = {fmt(r)}, p {fmt_p(p)} {stars(p)}")
    else:
        out(f"  Insuficientes sujetos completos para ANOVA de tiempo: {len(complete_time)}")

except Exception as e:
    out(f"  ERROR: {e}")
    import traceback
    out(traceback.format_exc())

# ---- 3g: Compensation index ----
section("3g. Indice de compensacion", 2)

try:
    comp_data = []
    for idx, row in df.iterrows():
        for ref_mo, ext_mo, label in [("a", "t", "tacto"), ("a", "p", "accion")]:
            kin_vals = []
            ext_vals = []
            for sh in SHAPES:
                for sz in SIZES:
                    kin_v = row[col_ea(sh, sz, ref_mo)]
                    ext_v = row[col_ea(sh, sz, ext_mo)]
                    if pd.notna(kin_v) and pd.notna(ext_v):
                        kin_vals.append(abs(kin_v))
                        ext_vals.append(abs(ext_v))
            if kin_vals and ext_vals:
                mean_kin = np.mean(kin_vals)
                mean_ext = np.mean(ext_vals)
                if mean_kin > 0:
                    comp_idx = (mean_kin - mean_ext) / mean_kin
                else:
                    comp_idx = 0
                comp_data.append({
                    "subject": row["id"],
                    "condicion": row["condicion"],
                    "type": label,
                    "comp_index": comp_idx,
                    "mean_kin": mean_kin,
                    "mean_ext": mean_ext,
                    "anos_vision": row["anos.vision"],
                })

    df_comp = pd.DataFrame(comp_data)

    out("\n  Indice de compensacion = (|error_CIN| - |error_EXT|) / |error_CIN|")
    out("  Valores positivos = mejora con ayuda externa; negativos = empeoramiento")

    out(f"\n  {'Grupo':<6} {'Tipo':<10} {'M':>8} {'DE':>8} {'n':>4}")
    out("  " + "-" * 40)
    for g in ["DV", "NDV"]:
        for t in ["tacto", "accion"]:
            vals = df_comp[(df_comp["condicion"]==g) & (df_comp["type"]==t)]["comp_index"]
            out(f"  {g:<6} {t.capitalize():<10} {fmt(vals.mean(), 3):>8} {fmt(vals.std(), 3):>8} {len(vals):>4}")

    # Test DV vs NDV
    section("Comparacion del indice de compensacion DV vs NDV", 3)
    for t in ["tacto", "accion"]:
        dv_ci = df_comp[(df_comp["condicion"]=="DV") & (df_comp["type"]==t)]["comp_index"]
        ndv_ci = df_comp[(df_comp["condicion"]=="NDV") & (df_comp["type"]==t)]["comp_index"]
        t_stat, p_val = stats.ttest_ind(dv_ci, ndv_ci, equal_var=False)
        d = cohens_d(dv_ci.values, ndv_ci.values)
        out(f"  {t.capitalize()}: t = {fmt(t_stat)}, p {fmt_p(p_val)}, d = {fmt(d)} {stars(p_val)}")

    # One-sample test: is index different from 0?
    section("Test de una muestra: ?Indice significativamente diferente de 0?", 3)
    for g in ["DV", "NDV"]:
        for t in ["tacto", "accion"]:
            vals = df_comp[(df_comp["condicion"]==g) & (df_comp["type"]==t)]["comp_index"]
            if len(vals) >= 3:
                t_stat, p_val = stats.ttest_1samp(vals, 0)
                out(f"  {g} - {t.capitalize()}: M = {fmt(vals.mean(), 3)}, "
                    f"t = {fmt(t_stat)}, p {fmt_p(p_val)} {stars(p_val)}")

    # Correlation with years of blindness (DV only)
    section("Correlacion: indice de compensacion vs anos de ceguera (grupo DV)", 3)
    for t in ["tacto", "accion"]:
        sub = df_comp[(df_comp["condicion"]=="DV") & (df_comp["type"]==t)].dropna(subset=["anos_vision", "comp_index"])
        if len(sub) >= 3:
            r, p = stats.pearsonr(sub["anos_vision"], sub["comp_index"])
            out(f"  {t.capitalize()}: r = {fmt(r)}, p {fmt_p(p)}, n = {len(sub)} {stars(p)}")

except Exception as e:
    out(f"  ERROR: {e}")
    import traceback
    out(traceback.format_exc())


# ============================================================================
# SECTION 4: FIGURES
# ============================================================================
section("SECCION 4: FIGURAS")

# Style settings
plt.rcParams.update({
    "font.size": 11,
    "axes.titlesize": 13,
    "axes.labelsize": 12,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "savefig.bbox": "tight",
    "font.family": "sans-serif",
})

COLORS = {"DV": "#2166AC", "NDV": "#B2182B"}
COLORS_LIGHT = {"DV": "#92C5DE", "NDV": "#F4A582"}

# ---- Figure 1: Interaction CE x MS ----
try:
    out("\n  Generando fig1_interaction_CE_MS.png...")
    df_coll_fig = build_long_collapsed(col_ea, "EA").dropna(subset=["EA"])

    fig, ax = plt.subplots(figsize=(8, 5.5))

    mod_order = ["a", "t", "p", "c"]
    mod_labels = [MODALITY_LABELS[m] for m in mod_order]

    for g_idx, g in enumerate(["DV", "NDV"]):
        means = []
        ci_lower = []
        ci_upper = []
        for mo in mod_order:
            vals = df_coll_fig[(df_coll_fig["condicion"]==g) & (df_coll_fig["modality"]==mo)]["EA"]
            m = vals.mean()
            se = vals.std() / np.sqrt(len(vals))
            means.append(m)
            ci_lower.append(m - 1.96*se)
            ci_upper.append(m + 1.96*se)

        x = np.arange(len(mod_order)) + g_idx * 0.15 - 0.075
        yerr_low = [m - cl for m, cl in zip(means, ci_lower)]
        yerr_high = [cu - m for m, cu in zip(means, ci_upper)]

        ax.errorbar(x, means, yerr=[yerr_low, yerr_high],
                    fmt="o-", color=COLORS[g], linewidth=2, markersize=8,
                    capsize=5, capthick=1.5, label=g, markeredgecolor="white",
                    markeredgewidth=1)

    ax.axhline(y=0, color="gray", linestyle="--", alpha=0.5, linewidth=0.8)
    ax.set_xticks(range(len(mod_order)))
    ax.set_xticklabels(mod_labels)
    ax.set_xlabel("Modalidad Sensorial")
    ax.set_ylabel("Error de Posicion con Signo (cm)")
    ax.set_title("Interaccion Condicion x Modalidad Sensorial\n(Medias Marginales Estimadas, IC 95%)")
    ax.legend(title="Condicion", framealpha=0.9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "fig1_interaction_CE_MS.png"))
    plt.close(fig)
    out("  OK: fig1_interaction_CE_MS.png guardada.")
except Exception as e:
    out(f"  ERROR fig1: {e}")

# ---- Figure 2: Spaghetti plot ----
try:
    out("\n  Generando fig2_individual_trajectories.png...")
    df_coll_fig2 = build_long_collapsed(col_ea, "EA").dropna(subset=["EA"])

    fig, ax = plt.subplots(figsize=(8, 5.5))

    for subj in df_coll_fig2["subject"].unique():
        sub = df_coll_fig2[df_coll_fig2["subject"] == subj].sort_values("modality")
        grp = sub["condicion"].values[0]
        x_vals = [mod_order.index(m) for m in sub["modality"]]
        ax.plot(x_vals, sub["EA"].values, "o-", color=COLORS[grp], alpha=0.3,
                linewidth=1, markersize=4)

    # Add group means
    for g in ["DV", "NDV"]:
        means = []
        for mo in mod_order:
            vals = df_coll_fig2[(df_coll_fig2["condicion"]==g) & (df_coll_fig2["modality"]==mo)]["EA"]
            means.append(vals.mean())
        ax.plot(range(len(mod_order)), means, "s-", color=COLORS[g], linewidth=3,
                markersize=10, label=f"Media {g}", markeredgecolor="white",
                markeredgewidth=1.5, zorder=5)

    ax.axhline(y=0, color="gray", linestyle="--", alpha=0.5, linewidth=0.8)
    ax.set_xticks(range(len(mod_order)))
    ax.set_xticklabels(mod_labels)
    ax.set_xlabel("Modalidad Sensorial")
    ax.set_ylabel("Error de Posicion con Signo (cm)")
    ax.set_title("Trayectorias Individuales por Modalidad Sensorial")
    ax.legend(framealpha=0.9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "fig2_individual_trajectories.png"))
    plt.close(fig)
    out("  OK: fig2_individual_trajectories.png guardada.")
except Exception as e:
    out(f"  ERROR fig2: {e}")

# ---- Figure 3: Absolute vs signed ----
try:
    out("\n  Generando fig3_absolute_vs_signed.png...")
    df_abs_fig = build_long_collapsed(col_e, "E_abs").dropna(subset=["E_abs"])
    df_sgn_fig = build_long_collapsed(col_ea, "EA").dropna(subset=["EA"])

    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5), sharey=False)

    for ax_idx, (dff, var, title) in enumerate([
        (df_sgn_fig, "EA", "Error con Signo (E.A)"),
        (df_abs_fig, "E_abs", "Error Absoluto (E)")
    ]):
        ax = axes[ax_idx]
        for g_idx, g in enumerate(["DV", "NDV"]):
            means = []
            ses = []
            for mo in mod_order:
                vals = dff[(dff["condicion"]==g) & (dff["modality"]==mo)][var]
                means.append(vals.mean())
                ses.append(1.96 * vals.std() / np.sqrt(len(vals)))

            x = np.arange(len(mod_order)) + g_idx * 0.15 - 0.075
            ax.errorbar(x, means, yerr=ses, fmt="o-", color=COLORS[g],
                        linewidth=2, markersize=8, capsize=5, capthick=1.5,
                        label=g, markeredgecolor="white", markeredgewidth=1)

        if var == "EA":
            ax.axhline(y=0, color="gray", linestyle="--", alpha=0.5, linewidth=0.8)
        ax.set_xticks(range(len(mod_order)))
        ax.set_xticklabels(mod_labels)
        ax.set_xlabel("Modalidad Sensorial")
        ax.set_ylabel("Error (cm)")
        ax.set_title(title)
        ax.legend(title="Condicion", framealpha=0.9)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    plt.suptitle("Comparacion: Error Absoluto vs Error con Signo", fontsize=14, y=1.02)
    plt.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "fig3_absolute_vs_signed.png"))
    plt.close(fig)
    out("  OK: fig3_absolute_vs_signed.png guardada.")
except Exception as e:
    out(f"  ERROR fig3: {e}")

# ---- Figure 4: Variability ----
try:
    out("\n  Generando fig4_variability.png...")
    # df_consist was computed earlier

    fig, ax = plt.subplots(figsize=(8, 5.5))

    bar_data = []
    for g in ["DV", "NDV"]:
        for mo in mod_order:
            vals = df_consist[(df_consist["condicion"]==g) & (df_consist["modality"]==mo)]["within_sd"]
            bar_data.append({
                "Condicion": g, "Modalidad": MODALITY_LABELS[mo],
                "M": vals.mean(), "SE": vals.std() / np.sqrt(len(vals))
            })

    bar_df = pd.DataFrame(bar_data)

    x = np.arange(len(mod_order))
    width = 0.35

    for g_idx, g in enumerate(["DV", "NDV"]):
        sub = bar_df[bar_df["Condicion"] == g]
        offset = (g_idx - 0.5) * width
        bars = ax.bar(x + offset, sub["M"].values, width,
                       yerr=1.96*sub["SE"].values, color=COLORS[g],
                       label=g, capsize=4, edgecolor="white", linewidth=0.5,
                       alpha=0.85)

    ax.set_xticks(x)
    ax.set_xticklabels(mod_labels)
    ax.set_xlabel("Modalidad Sensorial")
    ax.set_ylabel("DE Intra-participante (cm)")
    ax.set_title("Variabilidad Intra-participante por Grupo y Modalidad\n(IC 95%)")
    ax.legend(title="Condicion", framealpha=0.9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "fig4_variability.png"))
    plt.close(fig)
    out("  OK: fig4_variability.png guardada.")
except Exception as e:
    out(f"  ERROR fig4: {e}")

# ---- Figure 5: Violin plots ----
try:
    out("\n  Generando fig5_error_direction.png...")
    df_violin = build_long_collapsed(col_ea, "EA").dropna(subset=["EA"])
    df_violin["Modalidad"] = df_violin["modality"].map(MODALITY_LABELS)
    df_violin["Condicion"] = df_violin["condicion"]

    fig, ax = plt.subplots(figsize=(10, 6))

    # Order modalities
    mod_order_labels = [MODALITY_LABELS[m] for m in mod_order]

    parts = sns.violinplot(
        data=df_violin, x="Modalidad", y="EA", hue="Condicion",
        order=mod_order_labels, palette=COLORS, split=True, inner="quart",
        ax=ax, alpha=0.8, linewidth=1
    )

    ax.axhline(y=0, color="gray", linestyle="--", alpha=0.6, linewidth=1)
    ax.set_xlabel("Modalidad Sensorial")
    ax.set_ylabel("Error de Posicion con Signo (cm)")
    ax.set_title("Distribucion del Error con Signo por Modalidad y Condicion")
    ax.legend(title="Condicion", framealpha=0.9)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "fig5_error_direction.png"))
    plt.close(fig)
    out("  OK: fig5_error_direction.png guardada.")
except Exception as e:
    out(f"  ERROR fig5: {e}")

# ---- Figure 6: Compensation index ----
try:
    out("\n  Generando fig6_compensation_index.png...")

    fig, axes = plt.subplots(1, 2, figsize=(12, 5.5))

    for ax_idx, t in enumerate(["tacto", "accion"]):
        ax = axes[ax_idx]
        sub = df_comp[df_comp["type"] == t]

        bp_data = [sub[sub["condicion"]==g]["comp_index"].values for g in ["DV", "NDV"]]
        bp = ax.boxplot(bp_data, labels=["DV", "NDV"], patch_artist=True,
                         widths=0.5, showmeans=True,
                         meanprops={"marker": "D", "markerfacecolor": "white",
                                    "markeredgecolor": "black", "markersize": 7})

        for patch, g in zip(bp["boxes"], ["DV", "NDV"]):
            patch.set_facecolor(COLORS_LIGHT[g])
            patch.set_edgecolor(COLORS[g])
            patch.set_linewidth(1.5)
        for median in bp["medians"]:
            median.set_color("black")
            median.set_linewidth(2)

        # Add individual points
        for g_idx, g in enumerate(["DV", "NDV"]):
            vals = sub[sub["condicion"]==g]["comp_index"].values
            x_jitter = np.random.normal(g_idx + 1, 0.05, size=len(vals))
            ax.scatter(x_jitter, vals, color=COLORS[g], alpha=0.5, s=30,
                       edgecolor="white", linewidth=0.5, zorder=3)

        ax.axhline(y=0, color="gray", linestyle="--", alpha=0.5)
        ax.set_ylabel("Indice de Compensacion")
        ax.set_title(f"Compensacion: {t.capitalize()}")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    plt.suptitle("Indice de Compensacion por Grupo\n(Positivo = mejora con ayuda externa)",
                 fontsize=13, y=1.03)
    plt.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "fig6_compensation_index.png"))
    plt.close(fig)
    out("  OK: fig6_compensation_index.png guardada.")
except Exception as e:
    out(f"  ERROR fig6: {e}")

# ---- Figure 7: Correlation years ----
try:
    out("\n  Generando fig7_correlation_years.png...")

    dv_only = df[df["condicion"] == "DV"].copy()

    fig, axes = plt.subplots(1, 4, figsize=(16, 4.5))

    for ax_idx, mo in enumerate(mod_order):
        ax = axes[ax_idx]
        ea_cols_mo = [col_ea(sh, sz, mo) for sh in SHAPES for sz in SIZES]
        dv_only[f"mean_EA_{mo}"] = dv_only[ea_cols_mo].mean(axis=1)

        valid = dv_only[["anos.vision", f"mean_EA_{mo}"]].dropna()
        x = valid["anos.vision"]
        y = valid[f"mean_EA_{mo}"]

        ax.scatter(x, y, color=COLORS["DV"], s=60, edgecolor="white",
                   linewidth=1, alpha=0.8, zorder=3)

        # Regression line
        if len(valid) >= 3:
            slope, intercept, r, p, se = stats.linregress(x, y)
            x_line = np.linspace(x.min(), x.max(), 100)
            ax.plot(x_line, intercept + slope * x_line, color=COLORS["DV"],
                    linewidth=2, alpha=0.7, linestyle="-")
            ax.text(0.05, 0.95, f"r = {fmt(r, 2)}\np {fmt_p(p)}",
                    transform=ax.transAxes, va="top", fontsize=9,
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))

        ax.set_xlabel("Anos de ceguera")
        ax.set_ylabel("Error medio con signo (cm)")
        ax.set_title(MODALITY_LABELS[mo])
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

    plt.suptitle("Correlacion: Anos de Ceguera vs Error de Posicion (Grupo DV)",
                 fontsize=13, y=1.03)
    plt.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "fig7_correlation_years.png"))
    plt.close(fig)
    out("  OK: fig7_correlation_years.png guardada.")
except Exception as e:
    out(f"  ERROR fig7: {e}")

# ---- Figure 8: QQ plot of residuals ----
try:
    out("\n  Generando fig8_qq_residuals.png...")

    # Get residuals from the collapsed ANOVA model
    df_coll_res = build_long_collapsed(col_ea, "EA").dropna(subset=["EA"])
    model_res = ols("EA ~ C(condicion) * C(modality)", data=df_coll_res).fit()
    residuals = model_res.resid

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))

    # QQ plot
    ax = axes[0]
    sm.qqplot(residuals, line="45", ax=ax, markerfacecolor=COLORS["DV"],
              markeredgecolor="white", markersize=5, alpha=0.7)
    ax.set_title("Grafico Q-Q de Residuos\n(Modelo CE x Modalidad sobre E.A)")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Histogram of residuals
    ax2 = axes[1]
    ax2.hist(residuals, bins=20, color=COLORS["DV"], alpha=0.7, edgecolor="white",
             density=True, linewidth=0.5)
    # Overlay normal curve
    x_norm = np.linspace(residuals.min(), residuals.max(), 100)
    ax2.plot(x_norm, stats.norm.pdf(x_norm, residuals.mean(), residuals.std()),
             color=COLORS["NDV"], linewidth=2, label="Normal teorica")
    ax2.set_xlabel("Residuos")
    ax2.set_ylabel("Densidad")
    ax2.set_title("Distribucion de Residuos")
    ax2.legend(framealpha=0.9)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)

    # Shapiro-Wilk on residuals
    w_res, p_res = stats.shapiro(residuals)
    fig.text(0.5, -0.02, f"Shapiro-Wilk: W = {fmt(w_res)}, p {fmt_p(p_res)} {stars(p_res)}",
             ha="center", fontsize=11)

    plt.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "fig8_qq_residuals.png"))
    plt.close(fig)
    out("  OK: fig8_qq_residuals.png guardada.")
    out(f"\n  Normalidad de residuos del modelo: W = {fmt(w_res)}, p {fmt_p(p_res)} {stars(p_res)}")

except Exception as e:
    out(f"  ERROR fig8: {e}")


# ============================================================================
# FINAL SUMMARY
# ============================================================================
section("RESUMEN FINAL")

out("""
  Este archivo contiene los resultados completos del analisis estadistico del
  estudio de navegacion espacial en personas con discapacidad visual (DV, n=15)
  y normovidentes vendados (NDV, n=13).

  Secciones:
  0. Validacion de datos
  1. Reproduccion de analisis originales (ANOVAs factoriales y colapsados)
  2. Analisis mejorados (tamanos del efecto, potencia, normalidad, robustos)
  3. Nuevas perspectivas (diferencias individuales, variabilidad, direccion
     del error, analisis bayesiano, tiempo, indice de compensacion)
  4. Figuras (8 graficos guardados como PNG en 300 dpi)

  Figuras generadas:
  - fig1_interaction_CE_MS.png: Interaccion CE x Modalidad (figura clave)
  - fig2_individual_trajectories.png: Trayectorias individuales
  - fig3_absolute_vs_signed.png: Error absoluto vs con signo
  - fig4_variability.png: Variabilidad intra-participante
  - fig5_error_direction.png: Violin plots del error con signo
  - fig6_compensation_index.png: Indice de compensacion
  - fig7_correlation_years.png: Correlacion anos de ceguera vs error
  - fig8_qq_residuals.png: QQ plot de residuos
""")

# ============================================================================
# FLUSH OUTPUT
# ============================================================================
flush_output()
print("Analisis completo. Todos los resultados guardados.")
print(f"  Resultados: {RESULTS_FILE}")
print(f"  Figuras: {OUT_DIR}/fig*.png")
