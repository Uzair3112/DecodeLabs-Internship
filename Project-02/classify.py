import os
import warnings
warnings.filterwarnings("ignore")

import numpy  as np
import pandas as pd
import matplotlib.pyplot  as plt
import matplotlib.gridspec as gridspec
import seaborn as sns

from sklearn.model_selection  import train_test_split
from sklearn.preprocessing    import StandardScaler, LabelEncoder
from sklearn.neighbors        import KNeighborsClassifier
from sklearn.metrics          import (
    accuracy_score,
    confusion_matrix,
    classification_report,
    f1_score,
    ConfusionMatrixDisplay,
)

# ══════════════════════════════════════════════════════════════════════════
#  SECTION 1 – INPUT
#  Load the raw Excel workbook and preview its structure.
# ══════════════════════════════════════════════════════════════════════════

FILE_PATH = "Dataset for Data Analytics.xlsx"   # ← same directory as script

print("=" * 65)
print("  KNN ORDER-STATUS CLASSIFIER  |  IPO Framework")
print("=" * 65)

# ── 1a. Load ───────────────────────────────────────────────────────────────
print("\n[ INPUT ]  Loading dataset …")
df_raw = pd.read_excel(FILE_PATH, engine="openpyxl")

print(f"  ✓ Rows: {df_raw.shape[0]:,}  |  Columns: {df_raw.shape[1]}")
print(f"  Columns: {list(df_raw.columns)}")
print(f"\n  Target distribution (OrderStatus):")
print(df_raw["OrderStatus"].value_counts().to_string(index=True))


# ══════════════════════════════════════════════════════════════════════════
#  SECTION 2 – PROCESS
#  2a  Clean  →  2b  Feature engineering  →  2c  Scale  →  2d  Split
#  →  2e  Instantiate KNN  →  2f  Fit  →  2g  Predict
# ══════════════════════════════════════════════════════════════════════════

print("\n[ PROCESS ]")

# ── 2a. Clean ──────────────────────────────────────────────────────────────
print("  Step 1 / 5  –  Cleaning …")
df = df_raw.copy()

# Drop columns that are identifiers or leak the target
DROP_COLS = ["OrderID", "Date", "CustomerID", "ShippingAddress",
             "TrackingNumber", "CouponCode"]
df.drop(columns=[c for c in DROP_COLS if c in df.columns], inplace=True)

# Drop rows where the target is missing
df.dropna(subset=["OrderStatus"], inplace=True)

# Fill remaining numeric NaNs with the column median
num_cols = df.select_dtypes(include=[np.number]).columns
df[num_cols] = df[num_cols].fillna(df[num_cols].median())

# Fill categorical NaNs with the mode
cat_cols = df.select_dtypes(include=["object"]).columns.difference(["OrderStatus"])
for col in cat_cols:
    df[col].fillna(df[col].mode()[0], inplace=True)

print(f"  ✓ Shape after cleaning: {df.shape}")

# ── 2b. Feature Engineering ────────────────────────────────────────────────
print("  Step 2 / 5  –  Encoding categorical features …")

# Label-encode each remaining categorical column
le_dict: dict[str, LabelEncoder] = {}
for col in cat_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col].astype(str))
    le_dict[col] = le

# Encode the target separately so we can invert it later
le_target = LabelEncoder()
y_encoded = le_target.fit_transform(df["OrderStatus"])
class_names = le_target.classes_                   # e.g. ['Cancelled', 'Delivered', …]

print(f"  ✓ Classes: {list(class_names)}")

# ── 2c. Define feature matrix X and target vector y ────────────────────────
FEATURE_COLS = [c for c in df.columns if c != "OrderStatus"]
X = df[FEATURE_COLS].values
y = y_encoded

print(f"  ✓ Features used ({len(FEATURE_COLS)}): {FEATURE_COLS}")

# ── 2d. Shuffle + 80/20 Train-Test Split ──────────────────────────────────
print("  Step 3 / 5  –  Shuffling & splitting (80 / 20) …")
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size    = 0.20,
    random_state = 42,    # reproducibility
    shuffle      = True,  # shuffle before splitting
    stratify     = y,     # keep class proportions in both splits
)
print(f"  ✓ Train: {X_train.shape[0]:,}  |  Test: {X_test.shape[0]:,}")

# ── 2d. Standard Scaling ──────────────────────────────────────────────────
# KNN is distance-based → features MUST be on the same scale.
# Fit on train ONLY to prevent data leakage.
print("  Step 4 / 5  –  Standard Scaling (fit on train only) …")
scaler  = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test  = scaler.transform(X_test)          # transform with train statistics
print("  ✓ All features scaled to μ=0, σ=1")

# ── 2e → 2g. Instantiate → Fit → Predict (KNN) ───────────────────────────
print("  Step 5 / 5  –  KNN: Instantiate → Fit → Predict …")

# Instantiate
knn = KNeighborsClassifier(
    n_neighbors = 5,          # k=5 (majority vote among 5 nearest neighbours)
    metric      = "euclidean",
    weights     = "uniform",  # all neighbours vote equally
    n_jobs      = -1,         # use all CPU cores for speed
)

# Fit
knn.fit(X_train, y_train)
print(f"  ✓ Model fitted on {X_train.shape[0]:,} samples")

# Predict
y_pred  = knn.predict(X_test)
y_proba = knn.predict_proba(X_test)          # class probabilities


# ══════════════════════════════════════════════════════════════════════════
#  SECTION 3 – OUTPUT
#  3a  Console metrics  →  3b  Dashboard figure (saved as PNG)
# ══════════════════════════════════════════════════════════════════════════

print("\n[ OUTPUT ]  Evaluation Metrics")
print("-" * 65)

# ── 3a. Console metrics ───────────────────────────────────────────────────
accuracy = accuracy_score(y_test, y_pred)
f1_w     = f1_score(y_test, y_pred, average="weighted")   # handles imbalance
f1_macro = f1_score(y_test, y_pred, average="macro")

print(f"  Accuracy          : {accuracy * 100:.2f}%")
print(f"  F1-Score (weighted): {f1_w:.4f}   ← primary metric")
print(f"  F1-Score (macro)   : {f1_macro:.4f}")
print()
print("  Per-class Report:")
print(
    classification_report(
        y_test, y_pred,
        target_names = class_names,
        zero_division = 0,
    )
)

cm = confusion_matrix(y_test, y_pred)

# ── 3b. Visualisation Dashboard ───────────────────────────────────────────
print("  Building visualisation dashboard …")

# ── colour palette ────────────────────────────────────────────────────────
PALETTE  = "#4C72B0"          # primary blue
ACCENT   = "#DD8452"          # orange accent
BG       = "#F8F9FA"
GRID_CLR = "#E0E0E0"

plt.rcParams.update({
    "font.family"      : "DejaVu Sans",
    "axes.spines.top"  : False,
    "axes.spines.right": False,
    "axes.facecolor"   : BG,
    "figure.facecolor" : BG,
})

fig = plt.figure(figsize=(20, 14))
fig.suptitle(
    "KNN Order-Status Classifier  |  Evaluation Dashboard",
    fontsize=18, fontweight="bold", y=0.98
)

gs = gridspec.GridSpec(
    2, 3,
    figure    = fig,
    hspace    = 0.42,
    wspace    = 0.38,
    top       = 0.91,
    bottom    = 0.07,
    left      = 0.07,
    right     = 0.97,
)

# ── Panel 1: Confusion Matrix ──────────────────────────────────────────────
ax1 = fig.add_subplot(gs[0, :2])
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=class_names)
disp.plot(
    ax              = ax1,
    colorbar        = False,
    cmap            = "Blues",
    xticks_rotation = 30,
)
ax1.set_title("Confusion Matrix", fontsize=13, fontweight="bold", pad=10)
ax1.set_xlabel("Predicted Label", fontsize=10)
ax1.set_ylabel("True Label",      fontsize=10)

# ── Panel 2: Summary Scorecard ─────────────────────────────────────────────
ax2 = fig.add_subplot(gs[0, 2])
ax2.axis("off")
metrics = {
    "Accuracy"          : f"{accuracy*100:.2f} %",
    "F1 Weighted"       : f"{f1_w:.4f}",
    "F1 Macro"          : f"{f1_macro:.4f}",
    "Test Samples"      : f"{len(y_test):,}",
    "Train Samples"     : f"{len(y_train):,}",
    "k (neighbours)"    : "5",
    "Scaling"           : "StandardScaler",
    "Classes"           : str(len(class_names)),
}
rows = list(metrics.items())
tbl = ax2.table(
    cellText    = rows,
    colLabels   = ["Metric", "Value"],
    loc         = "center",
    cellLoc     = "center",
)
tbl.auto_set_font_size(False)
tbl.set_fontsize(10)
tbl.scale(1.15, 1.8)
# header style
for j in range(2):
    tbl[0, j].set_facecolor(PALETTE)
    tbl[0, j].set_text_props(color="white", fontweight="bold")
# alternate row shading
for i in range(1, len(rows) + 1):
    clr = "#EAF0FB" if i % 2 == 0 else "white"
    for j in range(2):
        tbl[i, j].set_facecolor(clr)
ax2.set_title("Model Scorecard", fontsize=13, fontweight="bold", pad=10)

# ── Panel 3: Per-Class F1-Score bar chart ─────────────────────────────────
ax3 = fig.add_subplot(gs[1, 0])
f1_per_class = f1_score(y_test, y_pred, average=None, zero_division=0)
bars = ax3.barh(class_names, f1_per_class, color=PALETTE, edgecolor="white")
ax3.set_xlim(0, 1.05)
ax3.set_xlabel("F1-Score", fontsize=10)
ax3.set_title("Per-Class F1-Score", fontsize=13, fontweight="bold")
ax3.axvline(f1_w, color=ACCENT, linestyle="--", linewidth=1.5,
            label=f"Weighted avg ({f1_w:.2f})")
ax3.legend(fontsize=8)
for bar, val in zip(bars, f1_per_class):
    ax3.text(val + 0.01, bar.get_y() + bar.get_height() / 2,
             f"{val:.2f}", va="center", fontsize=9)
ax3.set_facecolor(BG)

# ── Panel 4: Class Distribution (true vs predicted) ────────────────────────
ax4 = fig.add_subplot(gs[1, 1])
x_idx  = np.arange(len(class_names))
width  = 0.35
true_counts = [np.sum(y_test   == i) for i in range(len(class_names))]
pred_counts = [np.sum(y_pred   == i) for i in range(len(class_names))]
ax4.bar(x_idx - width/2, true_counts, width, label="True",      color=PALETTE, alpha=0.85)
ax4.bar(x_idx + width/2, pred_counts, width, label="Predicted", color=ACCENT,  alpha=0.85)
ax4.set_xticks(x_idx)
ax4.set_xticklabels(class_names, rotation=30, ha="right", fontsize=9)
ax4.set_ylabel("Count")
ax4.set_title("True vs Predicted Class Distribution", fontsize=13, fontweight="bold")
ax4.legend(fontsize=9)
ax4.yaxis.grid(True, linestyle="--", linewidth=0.6, color=GRID_CLR)
ax4.set_facecolor(BG)

# ── Panel 5: Precision-Recall per class ───────────────────────────────────
ax5 = fig.add_subplot(gs[1, 2])
from sklearn.metrics import precision_score, recall_score
prec = precision_score(y_test, y_pred, average=None, zero_division=0)
rec  = recall_score   (y_test, y_pred, average=None, zero_division=0)
x2   = np.arange(len(class_names))
w2   = 0.35
ax5.bar(x2 - w2/2, prec, w2, label="Precision", color="#55A868", alpha=0.85)
ax5.bar(x2 + w2/2, rec,  w2, label="Recall",    color="#C44E52", alpha=0.85)
ax5.set_xticks(x2)
ax5.set_xticklabels(class_names, rotation=30, ha="right", fontsize=9)
ax5.set_ylim(0, 1.1)
ax5.set_ylabel("Score")
ax5.set_title("Precision & Recall per Class", fontsize=13, fontweight="bold")
ax5.legend(fontsize=9)
ax5.yaxis.grid(True, linestyle="--", linewidth=0.6, color=GRID_CLR)
ax5.set_facecolor(BG)

# ── Save ──────────────────────────────────────────────────────────────────
OUT_PATH = "knn_dashboard.png"
plt.savefig(OUT_PATH, dpi=150, bbox_inches="tight")
print(f"  ✓ Dashboard saved → {OUT_PATH}")
print("\n" + "=" * 65)
print("  Done. KNN pipeline complete.")
print("=" * 65)