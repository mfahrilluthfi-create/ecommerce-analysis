"""Dashboard E-Commerce Public Dataset (Streamlit).

Membaca dashboard/main_data.csv, yaitu data bersih hasil notebook.ipynb (pesanan delivered, 1 Jan 2017 - 31 Agu 2018).
Struktur data: 1 baris per ITEM pesanan. Jumlah pesanan/pelanggan dihitung dari kode unik (order_code, customer_code)
agar tidak terhitung ganda; revenue = jumlah kolom price (tidak termasuk ongkos kirim).

Jalankan:  cd dashboard  ->  streamlit run dashboard.py
"""
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="E-Commerce Dashboard", page_icon="🛒", layout="wide")

DATA_PATH = Path(__file__).resolve().parent / "main_data.csv"
DELAY_ORDER = ["Tepat waktu / lebih cepat", "Telat <= 3 hari", "Telat 3-7 hari", "Telat 7-14 hari", "Telat > 14 hari"]
SEG_ORDER = ["Repeat Customers", "Recent High-Value", "Recent Low/Mid-Value", "Mid-Recency Customers", "Lapsed High-Value", "Lapsed Low/Mid-Value"]

BQ1 = ("Kategori Produk dengan Revenue Tertinggi",
       "Kategori produk apa saja yang menghasilkan total revenue produk tertinggi dari pesanan berstatus delivered, dan berapa persen kontribusi kategori teratas terhadap total revenue?")
BQ2 = ("Tren Bulanan Pesanan dan Revenue",
       "Bagaimana tren jumlah pesanan dan total revenue produk per bulan, bulan mana yang menjadi puncak, dan berapa persen pertumbuhan Januari–Agustus 2018 dibanding Januari–Agustus 2017?")
BQ3 = ("Keterlambatan Pengiriman dan Skor Ulasan Pelanggan",
       "Berapa selisih rata-rata skor ulasan antara pesanan yang tiba terlambat dan tepat waktu, berapa persen pesanan terlambat, dan negara bagian mana yang tingkat keterlambatannya tertinggi?")


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, parse_dates=["purchase_date"])
    df["month"] = df["purchase_date"].dt.to_period("M").astype(str)
    return df


def idn(x, nd=0):
    """Format angka gaya Indonesia (titik ribuan, koma desimal)."""
    return f"{x:,.{nd}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def order_level(frame: pd.DataFrame) -> pd.DataFrame:
    """Satu baris per pesanan (atribut pesanan sama pada semua itemnya)."""
    return frame.drop_duplicates("order_code")


def review_subset(frame: pd.DataFrame) -> pd.DataFrame:
    """Pesanan yang punya tanggal tiba dan skor ulasan (dasar analisis BQ3 di notebook)."""
    o = order_level(frame).dropna(subset=["days_late", "review_score"]).copy()
    o["status_kirim"] = np.where(o["is_late"] == 1, "Terlambat", "Tepat waktu / lebih cepat")
    return o


df = load_data()

# ------------------------------------------------------------------ header
st.title("🛒 E-Commerce Dashboard")
st.caption(
    "Analisis pesanan marketplace e-commerce Brasil (E-Commerce Public Dataset). Cakupan: pesanan berstatus **delivered**, "
    f"dibeli **{df['purchase_date'].min():%d %b %Y} – {df['purchase_date'].max():%d %b %Y}**. "
    "Data identik dengan hasil pembersihan pada notebook analisis."
)
st.caption("💡 Gunakan filter di sidebar kiri (periode, kategori, negara bagian) dan slider jumlah kategori. KPI dan semua grafik ikut berubah.")

with st.expander("Dataset overview"):
    a, b, c, d = st.columns(4)
    a.metric("Pesanan delivered", idn(df["order_code"].nunique()))
    b.metric("Item terjual", idn(len(df)))
    c.metric("Pelanggan unik", idn(df["customer_code"].nunique()))
    d.metric("Kategori produk", idn(df["category"].nunique()))
    st.write("Struktur `main_data.csv`: 1 baris per item pesanan. Contoh 10 baris pertama:")
    st.dataframe(df.drop(columns="month").head(10), width="stretch")

# ------------------------------------------------------------------ filter
st.sidebar.header("Filter")
min_d, max_d = df["purchase_date"].min().date(), df["purchase_date"].max().date()
date_range = st.sidebar.date_input("Periode pembelian", (min_d, max_d), min_value=min_d, max_value=max_d)
all_cats = sorted(df["category"].unique())
sel_cats = st.sidebar.multiselect("Kategori produk", all_cats, default=all_cats)
all_states = sorted(df["customer_state"].dropna().unique())
sel_states = st.sidebar.multiselect("Negara bagian pelanggan", all_states, default=all_states)
top_n = st.sidebar.slider("Jumlah kategori teratas (BQ1)", 3, 15, 10)

if not isinstance(date_range, (tuple, list)) or len(date_range) != 2:
    st.info("Pilih tanggal awal dan tanggal akhir pada filter periode.")
    st.stop()

mask = (
    (df["purchase_date"].dt.date >= date_range[0]) & (df["purchase_date"].dt.date <= date_range[1])
    & df["category"].isin(sel_cats) & df["customer_state"].isin(sel_states)
)
f = df[mask]
if f.empty:
    st.warning("Tidak ada data untuk kombinasi filter ini. Longgarkan filter di sidebar.")
    st.stop()

orders = order_level(f)
rv = review_subset(f)

# ------------------------------------------------------------------ KPI
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Pesanan", idn(orders["order_code"].nunique()))
k2.metric("Total revenue produk", f"R$ {idn(f['price'].sum())}")
k3.metric("Pelanggan unik", idn(f["customer_code"].nunique()))
k4.metric("Pesanan terlambat", f"{rv['is_late'].mean() * 100:.2f}%".replace(".", ",") if len(rv) else "n/a")
k5.metric("Rata-rata skor ulasan", f"{orders['review_score'].mean():.2f}".replace(".", ",") if orders["review_score"].notna().any() else "n/a")
st.divider()

tab1, tab2, tab3, tab4 = st.tabs(["📦 BQ1: Kategori Produk", "📈 BQ2: Tren Bulanan", "⏱️ BQ3: Keterlambatan & Ulasan", "👥 Segmentasi RFM"])

# ------------------------------------------------------------------ BQ1
with tab1:
    st.subheader(f"Business Question 1: {BQ1[0]}")
    st.markdown(f"**Pertanyaan bisnis:** {BQ1[1]}")
    cat = f.groupby("category", as_index=False).agg(revenue=("price", "sum"), item_terjual=("price", "size"))
    cat["kontribusi_pct"] = cat["revenue"] / cat["revenue"].sum() * 100
    cat = cat.sort_values("revenue", ascending=False)
    top = cat.head(top_n).sort_values("revenue")
    fig = px.bar(top, x="revenue", y="category", orientation="h", text=top["kontribusi_pct"].map(lambda v: f"{v:.1f}%"),
                 labels={"revenue": "Total revenue produk (R$)", "category": "Kategori produk"}, color_discrete_sequence=["#1f77b4"])
    fig.update_layout(title=f"{min(top_n, len(cat))} kategori dengan revenue tertinggi (label = % dari total revenue terfilter)")
    fig.update_traces(textposition="outside", cliponaxis=False)
    st.plotly_chart(fig)
    best = cat.iloc[0]
    st.info(
        f"**Insight (sesuai filter):** kategori teratas adalah **{best['category']}** (R$ {idn(best['revenue'])}; {idn(best['kontribusi_pct'], 1)}% dari total). "
        f"{min(top_n, len(cat))} kategori teratas bersama-sama menyumbang **{idn(cat['kontribusi_pct'].head(top_n).sum(), 1)}%** dari total revenue terfilter."
    )

# ------------------------------------------------------------------ BQ2
with tab2:
    st.subheader(f"Business Question 2: {BQ2[0]}")
    st.markdown(f"**Pertanyaan bisnis:** {BQ2[1]}")
    mo = orders.groupby("month").agg(pesanan=("order_code", "nunique")).join(f.groupby("month")["price"].sum().rename("revenue")).reset_index()
    c1, c2 = st.columns(2)
    f1 = px.line(mo, x="month", y="pesanan", markers=True, labels={"month": "Bulan pembelian", "pesanan": "Jumlah pesanan per bulan"})
    f1.update_yaxes(rangemode="tozero"); f1.update_layout(title="Jumlah pesanan per bulan")
    c1.plotly_chart(f1)
    f2 = px.line(mo, x="month", y="revenue", markers=True, labels={"month": "Bulan pembelian", "revenue": "Revenue produk per bulan (R$)"},
                 color_discrete_sequence=["#2ca02c"])
    f2.update_yaxes(rangemode="tozero"); f2.update_layout(title="Total revenue produk per bulan")
    c2.plotly_chart(f2)
    pk = mo.loc[mo["pesanan"].idxmax()]
    msg = f"**Insight (sesuai filter):** puncak pesanan pada **{pd.Period(pk['month']).strftime('%b %Y')}** ({idn(pk['pesanan'])} pesanan; revenue R$ {idn(pk['revenue'])})."
    ytd = mo.assign(y=mo["month"].str[:4], m=mo["month"].str[5:7].astype(int))
    ytd = ytd[ytd["m"] <= 8].groupby("y")[["pesanan", "revenue"]].sum()
    full_both = all(((mo["month"] == f"{y}-{mm:02d}").any()) for y in ("2017", "2018") for mm in range(1, 9))
    if full_both:
        g_o = (ytd.loc["2018", "pesanan"] / ytd.loc["2017", "pesanan"] - 1) * 100
        g_r = (ytd.loc["2018", "revenue"] / ytd.loc["2017", "revenue"] - 1) * 100
        msg += f" Jan–Agu 2018 vs Jan–Agu 2017: pesanan **{g_o:+.1f}%** dan revenue **{g_r:+.1f}%**."
    else:
        msg += " Pertumbuhan Jan–Agu 2018 vs 2017 ditampilkan bila filter periode mencakup Jan–Agu 2017 dan 2018."
    st.info(msg)

# ------------------------------------------------------------------ BQ3
with tab3:
    st.subheader(f"Business Question 3: {BQ3[0]}")
    st.markdown(f"**Pertanyaan bisnis:** {BQ3[1]}")
    if rv.empty:
        st.warning("Tidak ada pesanan dengan tanggal tiba dan skor ulasan pada filter ini.")
    else:
        c1, c2 = st.columns(2)
        stt = rv.groupby("status_kirim").agg(rata_rata=("review_score", "mean"), pesanan=("order_code", "nunique")).reset_index()
        fa = px.bar(stt, x="status_kirim", y="rata_rata", text=stt["rata_rata"].round(2), color="status_kirim",
                    color_discrete_map={"Tepat waktu / lebih cepat": "#2ca02c", "Terlambat": "#d62728"}, hover_data=["pesanan"],
                    labels={"status_kirim": "Status pengiriman", "rata_rata": "Rata-rata skor ulasan (1-5)"})
        fa.update_yaxes(range=[0, 5]); fa.update_layout(showlegend=False, title="Rata-rata skor ulasan: tepat waktu vs terlambat")
        c1.plotly_chart(fa)
        bk = rv.groupby("delay_bucket").agg(rata_rata=("review_score", "mean"), pesanan=("order_code", "nunique")).reindex(DELAY_ORDER).dropna().reset_index()
        fb = px.bar(bk, x="delay_bucket", y="rata_rata", text=bk["rata_rata"].round(2), hover_data=["pesanan"],
                    labels={"delay_bucket": "Selisih tanggal tiba terhadap estimasi", "rata_rata": "Rata-rata skor ulasan (1-5)"},
                    color_discrete_sequence=["#d73027"])
        fb.update_yaxes(range=[0, 5]); fb.update_layout(title="Rata-rata skor ulasan menurut lama keterlambatan")
        c2.plotly_chart(fb)

        stt_i = stt.set_index("status_kirim")["rata_rata"]
        late_pct = rv["is_late"].mean() * 100
        msg = f"**Insight (sesuai filter):** {idn(late_pct, 2)}% pesanan terlambat."
        if {"Terlambat", "Tepat waktu / lebih cepat"} <= set(stt_i.index):
            msg += (f" Rata-rata skor tepat waktu **{idn(stt_i['Tepat waktu / lebih cepat'], 2)}** vs terlambat **{idn(stt_i['Terlambat'], 2)}** "
                    f"(selisih **{idn(stt_i['Tepat waktu / lebih cepat'] - stt_i['Terlambat'], 2)} poin**, dihitung dari nilai tanpa pembulatan).")
        st.info(msg)

        st.markdown("**Tingkat keterlambatan per negara bagian** (hanya negara bagian dengan minimal jumlah pesanan yang dipilih di bawah):")
        min_ord = st.slider("Minimal jumlah pesanan per negara bagian", 1, 1000, 500, step=50)
        stg = (rv.groupby("customer_state").agg(pesanan=("order_code", "nunique"), tingkat_terlambat_pct=("is_late", lambda s: s.mean() * 100),
                                                 skor_rata2=("review_score", "mean")).query("pesanan >= @min_ord")
               .sort_values("tingkat_terlambat_pct", ascending=False).reset_index())
        if stg.empty:
            st.caption("Tidak ada negara bagian yang memenuhi batas minimal pesanan. Turunkan batasnya.")
        else:
            fs = px.bar(stg, x="customer_state", y="tingkat_terlambat_pct", text=stg["tingkat_terlambat_pct"].round(1), hover_data=["pesanan", "skor_rata2"],
                        labels={"customer_state": "Negara bagian", "tingkat_terlambat_pct": "Pesanan terlambat (%)"}, color_discrete_sequence=["#d62728"])
            fs.update_layout(title="Persentase pesanan terlambat per negara bagian")
            st.plotly_chart(fs)
            t3 = stg.head(3)
            st.info("**Insight:** tingkat keterlambatan tertinggi pada " + ", ".join(f"**{r.customer_state}** ({idn(r.tingkat_terlambat_pct, 1)}%)" for r in t3.itertuples()) + ".")

# ------------------------------------------------------------------ RFM
with tab4:
    st.subheader("Segmentasi Pelanggan (RFM Analysis)")
    st.caption("Segmen dihitung di notebook pada seluruh pelanggan periode analisis (Recency, Frequency, Monetary); dashboard menampilkan jumlah pelanggan "
               "per segmen untuk pelanggan yang lolos filter.")
    seg = f.drop_duplicates("customer_code").groupby("rfm_segment").size().reindex(SEG_ORDER).dropna().rename("pelanggan").reset_index()
    seg["proporsi_pct"] = seg["pelanggan"] / seg["pelanggan"].sum() * 100
    fr = px.bar(seg, x="pelanggan", y="rfm_segment", orientation="h", text=seg["proporsi_pct"].map(lambda v: f"{v:.1f}%"),
                labels={"pelanggan": "Jumlah pelanggan unik", "rfm_segment": "Segmen RFM"}, color_discrete_sequence=["#1f77b4"],
                category_orders={"rfm_segment": SEG_ORDER})
    fr.update_layout(title="Jumlah pelanggan per segmen RFM"); fr.update_traces(textposition="outside", cliponaxis=False)
    st.plotly_chart(fr)
    big = seg.loc[seg["pelanggan"].idxmax()]
    st.info(f"**Insight (sesuai filter):** segmen terbesar adalah **{big['rfm_segment']}** ({idn(big['pelanggan'])} pelanggan; {idn(big['proporsi_pct'], 1)}%). "
            "Pada data penuh, mayoritas pelanggan hanya membeli satu kali, sehingga segmen *Repeat Customers* kecil.")

st.caption("Sumber data: E-Commerce Public Dataset (Olist). Dikerjakan oleh M Fahril Luthfi.")
