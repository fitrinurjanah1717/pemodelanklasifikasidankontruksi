"""
Script Analisis Data Infrastruktur & IKID-DS (2024 - 2025)
Dikonversi dan dioptimalkan untuk dijalankan di Visual Studio Code (VS Code).
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree

# ==========================================
# 1. LOAD & PREPROCESSING DATASET
# ==========================================
# Pastikan file Excel berada di folder kerja yang sama dengan script ini di VS Code
file_path = "Data Persentase.xlsx"

try:
    df = pd.read_excel(file_path)
    print("✅ Berhasil memuat dataset asli.")
except Exception as e:
    print(
        f"❌ Gagal memuat file '{file_path}'. Pastikan file ada di folder yang"
        f" sama: {e}"
    )
    exit()

# Pembersihan Tipe Data Awal
df["Akses Komputer"] = pd.to_numeric(df["Akses Komputer"], errors="coerce")

# Filter Data: Hanya ambil tahun 2024 dan 2025
df_filtered = df[df["Tahun"].isin([2024, 2025])].copy()

# Simpan ke File Excel Baru yang Bersih
new_file_path = "Data_Persentase_2024_2025_Clean.xlsx"
df_filtered.to_excel(new_file_path, index=False)
print(
    f"📁 File baru berhasil dibuat: '{new_file_path}' (Total Baris:"
    f" {len(df_filtered)})\n"
)


# ==========================================
# 2. VALIDASI KUALITAS DATA (DATA VALIDATION)
# ==========================================
print("=" * 60)
print("HASIL VALIDASI DATA PADA FILE (2024 & 2025)")
print("=" * 60)

# A. Validasi Rentang Nilai (Range Check: 0 - 100%)
percentage_cols = ["Akses Listrik", "Akses Komputer", "Akses Internet"]
for col in percentage_cols:
    invalid_range = df_filtered[
        (df_filtered[col] < 0) | (df_filtered[col] > 100)
    ]
    if not invalid_range.empty:
        print(
            f"⚠️ [Peringatan] Kolom '{col}' memiliki {len(invalid_range)} baris"
            " di luar rentang 0-100%."
        )
    else:
        print(f"✅ Kolom '{col}' valid (semua nilai berada di rentang 0-100%).")

# B. Validasi Missing Values (Nilai Kosong / NaN)
missing_counts = df_filtered.isnull().sum()
print("\n--- Pengecekan Missing Values ---")
if missing_counts.sum() > 0:
    print(missing_counts[missing_counts > 0])
    print("⚠️ Ditemukan nilai kosong yang perlu ditinjau kembali.")
else:
    print("✅ Tidak ada nilai kosong (missing values) pada dataset terfilter.")

# C. Validasi Konsistensi Kategori Tingkat Pendidikan
print("\n--- Pengecekan Kategori Tingkat Pendidikan ---")
unique_edu = df_filtered["Tingkat Pendidikan"].unique()
print(f"Ditemukan kategori jenjang: {list(unique_edu)}")

# D. Validasi Logika Silang (Cross-Field Check)
anomaly_check = df_filtered[
    (df_filtered["Akses Komputer"] > 0) & (df_filtered["Akses Listrik"] == 0)
]
if not anomaly_check.empty:
    print(
        f"\n⚠️ [Anomali Logika] Ditemukan {len(anomaly_check)} baris data dengan"
        " akses komputer > 0% tetapi akses listrik 0%."
    )
    print(anomaly_check.head())
else:
    print("\n✅ Validasi logika silang (listrik vs komputer) aman.")

print("=" * 60 + "\n")


# ==========================================
# 3. ANALISIS KORELASI PEARSON & HEATMAP
# ==========================================
file_ikid_path = "Data_Persentase_2024_2025_dengan_IKID_DS.xlsx"

try:
    df_ikid = pd.read_excel(file_ikid_path)
    df_ikid = df_ikid.rename(
        columns={
            "Akses Listrik": "Akses_Listrik",
            "Akses Komputer": "Akses_Komputer",
            "Akses Internet": "Akses_Internet",
        }
    )

    vars_to_test = ["Akses_Listrik", "Akses_Komputer", "Akses_Internet", "IKID_DS"]
    df_subset = df_ikid[vars_to_test].dropna()

    print("=" * 60)
    print("MATRIKS KORELASI PEARSON ANTARVARIABEL")
    print("=" * 60)
    corr_matrix = df_subset.corr(method="pearson").round(4)
    print(corr_matrix.to_string())
    print("=" * 60 + "\n")

    # Visualisasi Heatmap Korelasi
    print("🎨 Sedang merender heatmap matriks korelasi...")
    plt.figure(figsize=(8, 6), dpi=300)
    sns.heatmap(
        corr_matrix,
        annot=True,
        cmap="Blues",
        fmt=".2f",
        linewidths=0.8,
        cbar=True,
        vmin=0,
        vmax=1,
    )
    plt.title(
        "Matriks Korelasi Pearson Antarvariabel Infrastruktur & IKID-DS",
        fontsize=11,
        fontweight="bold",
        pad=15,
    )
    plt.tight_layout()

    output_corr_img = "Matriks_Korelasi_Pearson.png"
    plt.savefig(
        output_corr_img,
        dpi=300,
        bbox_inches="tight",
        facecolor="white",
        edgecolor="none",
    )
    plt.show()
    print(f"✅ Heatmap korelasi berhasil disimpan sebagai '{output_corr_img}'!\n")

except Exception as e:
    print(
        f"ℹ️ Bagian korelasi dilewati karena file '{file_ikid_path}' belum"
        f" tersedia: {e}"
    )


# ==========================================
# 4. MACHINE LEARNING: RANDOM FOREST
# ==========================================
try:
    df_rf = pd.read_excel("Data_Persentase_2024_2025_dengan_IKID_DS.xlsx")
    df_rf["Kategori_IKID"] = pd.qcut(
        df_rf["IKID_DS"], q=3, labels=["Rendah", "Sedang", "Tinggi"]
    )

    X_rf = df_rf[["Akses Listrik", "Akses Komputer", "Akses Internet"]]
    y_rf = df_rf["Kategori_IKID"]

    X_train_rf, X_test_rf, y_train_rf, y_test_rf = train_test_split(
        X_rf, y_rf, test_size=0.2, random_state=42
    )

    rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_model.fit(X_train_rf, y_train_rf)

    y_pred_rf = rf_model.predict(X_test_rf)
    accuracy_rf = accuracy_score(y_test_rf, y_pred_rf)

    print("=" * 50)
    print(f"🎯 AKURASI MODEL RANDOM FOREST: {accuracy_rf * 100:.2f}%")
    print("=" * 50)
    print("\n📊 Laporan Klasifikasi (Classification Report) - Random Forest:")
    print(classification_report(y_test_rf, y_pred_rf))

    # Feature Importance
    feature_names = X_rf.columns
    importances = rf_model.feature_importances_
    df_importance = pd.DataFrame(
        {"Fitur": feature_names, "Tingkat_Kepentingan": importances}
    ).sort_values(by="Tingkat_Kepentingan", ascending=False)

    print("=" * 50)
    print("🔍 TINGKAT KEPENTINGAN FITUR (RANDOM FOREST)")
    print("=" * 50)
    print(df_importance.to_string(index=False))

    plt.figure(figsize=(8, 5), dpi=300)
    sns.barplot(
        x="Tingkat_Kepentingan",
        y="Fitur",
        data=df_importance,
        palette="Blues_r",
        hue="Fitur",
        legend=False,
    )
    plt.title(
        "Tingkat Kepentingan Fitur Infrastruktur terhadap Kategori IKID-DS\n(Random"
        " Forest)",
        fontsize=11,
        fontweight="bold",
        pad=15,
    )
    plt.xlabel("Skor Kepentingan (Importance Score)", fontsize=10)
    plt.ylabel("Variabel Infrastruktur", fontsize=10)
    plt.tight_layout()

    output_rf_img = "Random_Forest_Feature_Importance.png"
    plt.savefig(
        output_rf_img,
        dpi=300,
        bbox_inches="tight",
        facecolor="white",
        edgecolor="none",
    )
    plt.show()
    print(f"✅ Grafik Random Forest berhasil disimpan sebagai '{output_rf_img}'!\n")

except Exception as e:
    print(
        "ℹ️ Pelatihan Random Forest dilewati karena file dataset belum lengkap:"
        f" {e}"
    )


# ==========================================
# 5. MACHINE LEARNING: DECISION TREE
# ==========================================
try:
    df_dt = pd.read_excel("Data_Persentase_2024_2025_dengan_IKID_DS.xlsx")
    df_dt["Kategori_IKID"] = pd.qcut(
        df_dt["IKID_DS"], q=3, labels=["Rendah", "Sedang", "Tinggi"]
    )

    X_dt = df_dt[["Akses Listrik", "Akses Komputer", "Akses Internet"]]
    y_dt = df_dt["Kategori_IKID"]

    X_train_dt, X_test_dt, y_train_dt, y_test_dt = train_test_split(
        X_dt, y_dt, test_size=0.2, random_state=42
    )

    dt_model = DecisionTreeClassifier(max_depth=4, random_state=42)
    dt_model.fit(X_train_dt, y_train_dt)

    y_pred_dt = dt_model.predict(X_test_dt)
    accuracy_dt = accuracy_score(y_test_dt, y_pred_dt)

    print("=" * 50)
    print(f"🎯 AKURASI MODEL DECISION TREE: {accuracy_dt * 100:.2f}%")
    print("=" * 50)
    print("\n📊 Laporan Klasifikasi (Classification Report) - Decision Tree:")
    print(classification_report(y_test_dt, y_pred_dt))

    # Visualisasi Pohon Keputusan
    print("\n🎨 Sedang merender diagram struktur Decision Tree...")
    plt.figure(figsize=(12, 8), dpi=300)
    plot_tree(
        dt_model,
        feature_names=X_dt.columns,
        class_names=dt_model.classes_,
        filled=True,
        rounded=True,
        fontsize=10,
    )
    plt.title(
        "Diagram Struktur Decision Tree untuk Kategori IKID-DS",
        fontsize=11,
        fontweight="bold",
        pad=15,
    )
    plt.tight_layout()

    output_dt_img = "Decision_Tree_Structure.png"
    plt.savefig(
        output_dt_img,
        dpi=300,
        bbox_inches="tight",
        facecolor="white",
        edgecolor="none",
    )
    plt.show()
    print(f"✅ Diagram Decision Tree berhasil disimpan sebagai '{output_dt_img}'!")

except Exception as e:
    print(
        "ℹ️ Pelatihan Decision Tree dilewati karena file dataset belum lengkap:"
        f" {e}"
    )