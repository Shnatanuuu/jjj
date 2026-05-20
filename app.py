import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from io import StringIO

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Zalora Competitor Intelligence",
    page_icon="👠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Styles ────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .metric-card {
        background: #F8F6F3;
        border-radius: 12px;
        padding: 16px 20px;
        border: 1px solid #E8E4DE;
    }
    .metric-value { font-size: 28px; font-weight: 600; color: #1A1A1A; margin: 0; }
    .metric-label { font-size: 12px; color: #6B6B6B; margin: 0; margin-top: 4px; }
    .section-title { font-size: 15px; font-weight: 600; color: #1A1A1A; margin-bottom: 4px; }
    .insight-box {
        background: #EEF6F1;
        border-left: 3px solid #1D9E75;
        padding: 10px 14px;
        border-radius: 0 8px 8px 0;
        font-size: 13px;
        color: #1A1A1A;
        margin-top: 8px;
    }
    .warn-box {
        background: #FEF6E7;
        border-left: 3px solid #EF9F27;
        padding: 10px 14px;
        border-radius: 0 8px 8px 0;
        font-size: 13px;
        color: #1A1A1A;
        margin-top: 8px;
    }
    [data-testid="stSidebar"] { background: #F4F1ED; }
    /* Icon-only export button */
    div[data-testid="stDownloadButton"] button {
        padding: 4px 8px !important;
        font-size: 14px !important;
        min-height: 0 !important;
        height: 28px !important;
        width: 28px !important;
        border-radius: 6px !important;
        background: #F4F1ED !important;
        border: 1px solid #E8E4DE !important;
        color: #1A1A1A !important;
    }
</style>
""", unsafe_allow_html=True)

COLORS = ["#1D9E75","#E07B39","#185FA5","#BA7517","#7B3FA0","#C23B5A","#2B8C9B","#8B7355"]

# ── CSV export helper ─────────────────────────────────────────────────────────
# Use a stable counter stored in session_state so keys never change on re-run
if "dl_counter" not in st.session_state:
    st.session_state["dl_counter"] = 0

def export_csv(df_export: pd.DataFrame, filename: str):
    """Render a small right-aligned icon-only CSV download button."""
    csv_bytes = df_export.to_csv(index=False).encode("utf-8-sig")
    _, btn_col = st.columns([12, 1])
    with btn_col:
        st.download_button(
            label="⬇",
            data=csv_bytes,
            file_name=filename,
            mime="text/csv",
            key=f"dl_{filename}",   # stable key — same file, same key every run
            use_container_width=False,
        )

# ── Sample data ───────────────────────────────────────────────────────────────
SAMPLE = """Subcategory\tLink\tRatings\tImage_src\tBrand\tTitle\tPrice\tCampaign_Type\tRanking
Stiletto Heels\thttps://www.zalora.com.hk/p/forcast-kelsey-stiletto-heel-6783657\t3\thttps://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=80\tFORCAST\tKelsey Stiletto Heel\t264.5\tX Pay HK$20 off\t1
Stiletto Heels\thttps://www.zalora.com.hk/p/forcast-kelsey-stiletto-heel-6783661\t3\thttps://images.unsplash.com/photo-1515347619252-60a4bf4fff4f?w=80\tFORCAST\tKelsey Stiletto Heel\t264.5\tX Pay HK$20 off\t2
Stiletto Heels\thttps://www.zalora.com.hk/p/forcast-kelsey-leather-stiletto-heel-6783656\t4\thttps://images.unsplash.com/photo-1611048267451-e6ed903d4a38?w=80\tFORCAST\tKelsey Leather Stiletto Heel\t379.5\tX Pay HK$20 off\t3
Stiletto Heels\thttps://www.zalora.com.hk/p/rag-co-microfiber-stiletto-sandals-in-taupe-7051748\t4.8\thttps://images.unsplash.com/photo-1596703263926-eb0762ee17e4?w=80\tRag & CO.\tMicrofiber Stiletto Sandals in Taupe\t188.3\t30% off\t4
Stiletto Heels\thttps://www.zalora.com.hk/p/rag-co-suede-stiletto-mules-in-black-7081384\t5\thttps://images.unsplash.com/photo-1518049362265-d5b2a6467637?w=80\tRag & CO.\tSuede Stiletto Mules In Black\t293.3\t30% off\t5
Stiletto Heels\thttps://www.zalora.com.hk/p/twenty-eight-shoes-10cm-silk-6783456\t4.8\thttps://images.unsplash.com/photo-1599643477877-530eb83abc8e?w=80\tTwenty Eight Shoes\t10CM Silk Fabrics Pointed High Heel Shoes\t431.1\t10% off\t6
Stiletto Heels\thttps://www.zalora.com.hk/p/rag-co-patent-heel-7081390\t4.5\thttps://images.unsplash.com/photo-1490481651871-ab68de25d43d?w=80\tRag & CO.\tPatent Leather Stiletto Pumps\t245.0\t30% off\t7
Stiletto Heels\thttps://www.zalora.com.hk/p/forcast-mini-stiletto-6783700\t3.5\thttps://images.unsplash.com/photo-1512361436605-a484bdb34b5f?w=80\tFORCAST\tMini Block Stiletto Heel\t199.0\tX Pay HK$20 off\t8
Ankle Boots\thttps://www.zalora.com.hk/p/london-rag-ankle-1\t5\thttps://images.unsplash.com/photo-1608256246200-53e635b5b65f?w=80\tLondon Rag\tBlock Heel Chelsea Ankle Boots Black\t899.0\tNo campaign\t1
Ankle Boots\thttps://www.zalora.com.hk/p/london-rag-ankle-2\t5\thttps://images.unsplash.com/photo-1520639888713-7851133b1ed0?w=80\tLondon Rag\tCroc Embossed Ankle Boots Nude\t1099.0\tNo campaign\t2
Ankle Boots\thttps://www.zalora.com.hk/p/rag-co-ankle-1\t4.8\thttps://images.unsplash.com/photo-1542291026-7eec264c27ff?w=80\tRag & CO.\tSuede Effect Ankle Boots Tan\t1599.0\t15% off\t3
Ankle Boots\thttps://www.zalora.com.hk/p/london-rag-ankle-3\t4.5\thttps://images.unsplash.com/photo-1606107557195-0e29a4b5b4aa?w=80\tLondon Rag\tSquare Toe Chelsea Boots Camel\t799.0\tNo campaign\t4
Ankle Boots\thttps://www.zalora.com.hk/p/rag-co-ankle-2\t5\thttps://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=80\tRag & CO.\tLeather Ankle Boots Brown\t1799.0\t15% off\t5
Ankle Boots\thttps://www.zalora.com.hk/p/london-rag-ankle-4\t4\thttps://images.unsplash.com/photo-1579338908476-3a3a1d71a706?w=80\tLondon Rag\tPlatform Sole Ankle Boots White\t949.0\tNo campaign\t6
Long Boots\thttps://www.zalora.com.hk/p/london-rag-long-1\t4.5\thttps://images.unsplash.com/photo-1548036328-c9fa89d128fa?w=80\tLondon Rag\tKnee High Stretch Boots Black\t1399.0\tNo campaign\t1
Long Boots\thttps://www.zalora.com.hk/p/rag-co-long-1\t4.8\thttps://images.unsplash.com/photo-1543163521-1bf539c55dd2?w=80\tRag & CO.\tLeather Knee High Boots Tan\t2199.0\t20% off\t2
Long Boots\thttps://www.zalora.com.hk/p/london-rag-long-2\t4\thttps://images.unsplash.com/photo-1515347619252-60a4bf4fff4f?w=80\tLondon Rag\tBlock Heel Long Boots Camel\t1199.0\tNo campaign\t3
Long Boots\thttps://www.zalora.com.hk/p/rag-co-long-2\t5\thttps://images.unsplash.com/photo-1611048267451-e6ed903d4a38?w=80\tRag & CO.\tSuede Knee High Boots Brown\t2499.0\t20% off\t4
Long Boots\thttps://www.zalora.com.hk/p/twenty-eight-long-1\t4.2\thttps://images.unsplash.com/photo-1596703263926-eb0762ee17e4?w=80\tTwenty Eight Shoes\tHeeled Long Boots Black\t1650.0\t10% off\t5"""

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 👠 Zalora Intel")
    st.markdown("---")
    st.markdown("**Upload your scraped data**")
    uploaded = st.file_uploader("CSV or TSV file", type=["csv","tsv","txt"])
    st.markdown("---")

    if uploaded:
        sep = "\t" if uploaded.name.endswith((".tsv",".txt")) else ","
        raw_bytes = uploaded.read()
        for enc in ["utf-8", "latin-1", "cp1252", "utf-8-sig"]:
            try:
                df_raw = pd.read_csv(StringIO(raw_bytes.decode(enc)), sep=sep)
                break
            except (UnicodeDecodeError, Exception):
                continue
        else:
            st.error("Could not decode your file. Try saving it as UTF-8 CSV from Excel.")
            st.stop()
    else:
        st.info("No file uploaded — using sample data.")
        df_raw = pd.read_csv(StringIO(SAMPLE), sep="\t")

    # ── Clean ─────────────────────────────────────────────────────────────────
    df_all = df_raw.copy()
    df_all.columns = [c.strip() for c in df_all.columns]

    CANONICAL = {
        "subcategory": "Subcategory", "link": "Link", "ratings": "Ratings",
        "image_src": "Image_src", "brand": "Brand", "title": "Title",
        "price": "Price", "campaign_type": "Campaign_Type", "ranking": "Ranking",
    }
    df_all.rename(columns={c: CANONICAL.get(c.lower(), c) for c in df_all.columns}, inplace=True)

    for col in ["Ratings","Price","Ranking"]:
        if col in df_all.columns:
            df_all[col] = pd.to_numeric(df_all[col], errors="coerce")
    df_all = df_all.dropna(subset=["Brand","Price","Ratings"])
    df_all["Campaign_Has"] = df_all["Campaign_Type"].apply(
        lambda x: "Has Campaign" if pd.notna(x) and str(x).strip() not in ["","No campaign","nan"] else "No Campaign"
    )

    # ── Filters ───────────────────────────────────────────────────────────────
    st.markdown("**Filters**")
    cats = ["All"] + sorted(df_all["Subcategory"].dropna().unique().tolist())
    sel_cat = st.selectbox("Subcategory", cats)
    brands = sorted(df_all["Brand"].dropna().unique().tolist())
    sel_brands = st.multiselect("Brands", brands, default=brands)

    df = df_all.copy()
    if sel_cat != "All":
        df = df[df["Subcategory"] == sel_cat]
    if sel_brands:
        df = df[df["Brand"].isin(sel_brands)]

    st.markdown("---")
    st.markdown(f"**{len(df)} products** loaded")

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("# Zalora Competitor Intelligence Dashboard")
st.markdown("Upload your scraped Zalora data and get instant competitive insights across price, ratings, rankings, and campaigns.")
st.markdown("---")

if df.empty:
    st.warning("No data matches your filters.")
    st.stop()

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Overview & Charts",
    "📁 Category × Brand Pricing",
    "🏷️ Brand Scorecard",
    "📣 Campaign Intelligence",
])

# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — Overview
# ════════════════════════════════════════════════════════════════════════════
with tab1:

    # ── ROW 1 — Share of shelf + Rating distribution ─────────────────────────
    c1, c2 = st.columns([1,1])

    with c1:
        st.markdown('<p class="section-title">Share of shelf by brand</p>', unsafe_allow_html=True)
        shelf = df["Brand"].value_counts().reset_index()
        shelf.columns = ["Brand","Count"]
        shelf["Share"] = (shelf["Count"] / shelf["Count"].sum() * 100).round(1)
        fig = px.pie(shelf, values="Count", names="Brand",
                     color_discrete_sequence=COLORS, hole=0.45)
        fig.update_traces(
            textposition="inside", textinfo="percent",
            textfont=dict(size=13, color="white"),
            insidetextorientation="horizontal",
            pull=[0.03]*len(shelf),
        )
        fig.update_layout(
            margin=dict(t=20, b=20, l=20, r=20), height=340, showlegend=True,
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.02, font=dict(size=12)),
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True)
        top = shelf.iloc[0]
        st.markdown(f'<div class="insight-box">🏆 <b>{top.Brand}</b> owns <b>{top.Share}%</b> of shelf space — the brand you need to displace or differentiate from.</div>', unsafe_allow_html=True)
        export_csv(shelf[["Brand","Count","Share"]], "share_of_shelf.csv")

    with c2:
        st.markdown('<p class="section-title">Rating distribution by brand</p>', unsafe_allow_html=True)
        # Sort brands alphabetically so x-axis reads left-to-right naturally
        brand_order_rating = sorted(df["Brand"].unique().tolist())
        fig2 = px.box(df, x="Brand", y="Ratings", color="Brand",
                      color_discrete_sequence=COLORS, points="all",
                      category_orders={"Brand": brand_order_rating})
        fig2.update_layout(showlegend=False, margin=dict(t=10,b=60,l=0,r=0),
                           height=320, paper_bgcolor="rgba(0,0,0,0)",
                           plot_bgcolor="rgba(0,0,0,0)",
                           yaxis=dict(range=[0,5.5], gridcolor="#E8E4DE"),
                           xaxis=dict(tickangle=0),   # upright labels
                           xaxis_title="", yaxis_title="Rating")
        fig2.update_traces(marker_size=6)
        st.plotly_chart(fig2, use_container_width=True)
        low_brand = df.groupby("Brand")["Ratings"].mean().idxmin()
        st.markdown(f'<div class="warn-box">⚠️ <b>{low_brand}</b> has the lowest average rating — their unhappy customers are your acquisition opportunity.</div>', unsafe_allow_html=True)
        rating_summary = df.groupby("Brand")["Ratings"].agg(["mean","min","max","count"]).round(2).reset_index()
        rating_summary.columns = ["Brand","Avg_Rating","Min_Rating","Max_Rating","Products"]
        export_csv(rating_summary, "rating_distribution.csv")

    st.markdown("---")

    # ── ROW 2 — Price positioning + Price vs Rating scatter ──────────────────
    c3, c4 = st.columns([1,1])

    with c3:
        st.markdown('<p class="section-title">Price positioning by brand</p>', unsafe_allow_html=True)
        brand_order_price = sorted(df["Brand"].unique().tolist())
        fig3 = px.violin(df, x="Brand", y="Price", color="Brand",
                         color_discrete_sequence=COLORS, box=True, points="all",
                         category_orders={"Brand": brand_order_price})
        fig3.update_layout(showlegend=False, margin=dict(t=10,b=60,l=0,r=0),
                           height=340, paper_bgcolor="rgba(0,0,0,0)",
                           plot_bgcolor="rgba(0,0,0,0)",
                           yaxis=dict(gridcolor="#E8E4DE"),
                           xaxis=dict(tickangle=0),   # upright labels
                           xaxis_title="", yaxis_title="Price (HK$)")
        st.plotly_chart(fig3, use_container_width=True)
        price_summary = df.groupby("Brand")["Price"].agg(["median","mean","min","max","count"]).round(1).reset_index()
        price_summary.columns = ["Brand","Median_Price","Avg_Price","Min_Price","Max_Price","Products"]
        export_csv(price_summary, "price_positioning.csv")

    with c4:
        st.markdown('<p class="section-title">Price vs rating — where is the value gap?</p>', unsafe_allow_html=True)
        fig4 = px.scatter(df, x="Price", y="Ratings", color="Brand", size_max=14,
                          hover_data=["Title","Subcategory","Ranking"],
                          color_discrete_sequence=COLORS,
                          size=[12]*len(df))
        med_price = df["Price"].median()
        med_rating = df["Ratings"].median()
        fig4.add_hline(y=med_rating, line_dash="dot", line_color="#AAAAAA",
                       annotation_text="Median rating", annotation_position="top left")
        fig4.add_vline(x=med_price, line_dash="dot", line_color="#AAAAAA",
                       annotation_text="Median price", annotation_position="top right")
        fig4.update_layout(margin=dict(t=10,b=10,l=0,r=0), height=340,
                           paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           xaxis=dict(gridcolor="#E8E4DE"), yaxis=dict(gridcolor="#E8E4DE"),
                           legend=dict(orientation="h", yanchor="bottom", y=1.01))
        st.plotly_chart(fig4, use_container_width=True)
        st.markdown('<div class="insight-box">💡 Products in the <b>top-left quadrant</b> (high rating, low price) are your biggest competitive threats. Top-right = premium sweet spot to aspire to.</div>', unsafe_allow_html=True)
        scatter_export = df[["Brand","Title","Subcategory","Price","Ratings","Ranking"]].copy()
        export_csv(scatter_export, "price_vs_rating.csv")

    st.markdown("---")

    # ── ROW 3 — Search ranking analysis ──────────────────────────────────────
    st.markdown('<p class="section-title">Search ranking by brand — who wins page 1?</p>', unsafe_allow_html=True)
    if "Ranking" in df.columns and df["Ranking"].notna().sum() > 0:
        rank_df = df.groupby("Brand")["Ranking"].agg(["mean","min","count"]).reset_index()
        rank_df.columns = ["Brand","Avg Rank","Best Rank","Products"]
        best = rank_df.loc[rank_df["Avg Rank"].idxmin()]
        rank_df = rank_df.sort_values("Avg Rank", ascending=False)
        fig5 = px.bar(rank_df, x="Brand", y="Avg Rank", color="Brand",
                      color_discrete_sequence=COLORS, text="Avg Rank",
                      hover_data=["Best Rank","Products"],
                      category_orders={"Brand": rank_df["Brand"].tolist()})
        fig5.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        fig5.update_layout(showlegend=False, margin=dict(t=10,b=60,l=0,r=0),
                           height=320, paper_bgcolor="rgba(0,0,0,0)",
                           plot_bgcolor="rgba(0,0,0,0)",
                           yaxis=dict(autorange="reversed", gridcolor="#E8E4DE",
                                      title="Avg ranking position (lower = better)"),
                           xaxis=dict(tickangle=0),   # upright labels
                           xaxis_title="")
        st.plotly_chart(fig5, use_container_width=True)
        st.markdown(f'<div class="insight-box">🔍 <b>{best.Brand}</b> has the best avg ranking position ({best["Avg Rank"]:.1f}). Study their title keywords and campaign types.</div>', unsafe_allow_html=True)
        export_csv(rank_df.reset_index(drop=True), "search_ranking.csv")
    else:
        st.info("No Ranking data available.")

    st.markdown("---")

    # ── ROW 4 — Category heatmap + Price tier ────────────────────────────────
    c7, c9 = st.columns([1,1])

    with c7:
        st.markdown('<p class="section-title">Brand × category presence heatmap</p>', unsafe_allow_html=True)
        heatmap_df = df.groupby(["Brand","Subcategory"]).size().unstack(fill_value=0)
        row_order = heatmap_df.sum(axis=1).sort_values(ascending=False).index
        col_order = heatmap_df.sum(axis=0).sort_values(ascending=False).index
        heatmap_df = heatmap_df.loc[row_order, col_order]
        fig7 = px.imshow(heatmap_df, color_continuous_scale="Greens", text_auto=True, aspect="auto")
        fig7.update_layout(margin=dict(t=10,b=10,l=0,r=0), height=320,
                           paper_bgcolor="rgba(0,0,0,0)",
                           coloraxis_showscale=False, xaxis_title="", yaxis_title="",
                           xaxis=dict(tickangle=0))
        fig7.update_traces(textfont_size=13)
        st.plotly_chart(fig7, use_container_width=True)
        st.markdown('<div class="insight-box">📊 Dark cells = dominant brand-category combinations. White/empty cells = gaps your brand can enter with less competition.</div>', unsafe_allow_html=True)
        heatmap_export = heatmap_df.reset_index()
        export_csv(heatmap_export, "brand_category_presence.csv")

    with c9:
        q1, q3 = df["Price"].quantile(0.25), df["Price"].quantile(0.75)
        def tier(p):
            if p <= q1: return "Budget"
            elif p <= q3: return "Mid-market"
            else: return "Premium"
        df["Tier"] = df["Price"].apply(tier)

        st.markdown(
            f'<p class="section-title">Price tier distribution — where is the crowd?'
            f'&nbsp;<span style="font-weight:400;font-size:12px;color:#6B6B6B;">'
            f'Budget ≤ HK${q1:,.0f} &nbsp;|&nbsp; Mid-market HK${q1:,.0f}–HK${q3:,.0f} &nbsp;|&nbsp; Premium > HK${q3:,.0f}'
            f'</span></p>',
            unsafe_allow_html=True
        )
        tier_df = df.groupby(["Tier","Brand"]).size().reset_index(name="Count")
        tier_totals = tier_df.groupby("Tier")["Count"].sum().sort_values(ascending=False)
        tier_order_sorted = tier_totals.index.tolist()
        fig9 = px.bar(tier_df, x="Tier", y="Count", color="Brand",
                      color_discrete_sequence=COLORS,
                      category_orders={"Tier": tier_order_sorted})
        fig9.update_layout(margin=dict(t=10,b=10,l=0,r=0), height=320,
                           paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                           yaxis=dict(gridcolor="#E8E4DE", title="Products"),
                           xaxis=dict(tickangle=0),
                           xaxis_title="",
                           legend=dict(orientation="h", yanchor="bottom", y=1.01))
        st.plotly_chart(fig9, use_container_width=True)
        export_csv(tier_df, "price_tier_distribution.csv")

    st.markdown("---")

    # ── ROW 5 — All ranked products table WITH IMAGES ────────────────────────
    n_products = len(df)
    st.markdown(
        f'<p class="section-title">🏅 All ranked products — your benchmark list'
        f'&nbsp;<span style="font-weight:400;font-size:12px;color:#6B6B6B;">{n_products} SKUs · sorted by ranking</span></p>',
        unsafe_allow_html=True,
    )

    show_cols = [c for c in ["Ranking","Image_src","Brand","Title","Subcategory","Price","Ratings","Campaign_Type"] if c in df.columns]
    all_products = df.sort_values("Ranking", na_position="last")[show_cols].reset_index(drop=True)
    all_products.index += 1

    col_cfg = {
        "Price":   st.column_config.NumberColumn("Price (HK$)", format="HK$%.1f"),
        "Ratings": st.column_config.NumberColumn("Ratings ⭐", format="%.1f"),
        "Ranking": st.column_config.NumberColumn("Rank #", format="%d"),
    }
    if "Image_src" in all_products.columns:
        col_cfg["Image_src"] = st.column_config.ImageColumn("Preview", help="Product thumbnail from retailer", width="small")

    tbl_height = min(1400, max(400, n_products * 120 + 40))
    st.dataframe(all_products, column_config=col_cfg, use_container_width=True, height=tbl_height, row_height=120)

    export_cols = [c for c in show_cols if c != "Image_src"]
    export_csv(df.sort_values("Ranking", na_position="last")[export_cols].reset_index(drop=True), "all_ranked_products.csv")

    st.markdown("---")
    st.markdown('<p style="font-size:12px;color:#888">Built for Zalora competitive intelligence · Upload fresh scraped data weekly for trend tracking</p>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — Category × Brand Pricing Matrix
# ════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("## 📁 Category × Brand Average Price Matrix")
    st.markdown("Filtered by the sidebar — select **All** in Subcategory and all brands to see the full picture.")
    st.markdown("---")

    grp = (
        df.groupby(["Subcategory","Brand"])
        .agg(
            Avg_Price=("Price","mean"),
            Products=("Price","count"),
            Avg_Rating=("Ratings","mean"),
        )
        .reset_index()
    )
    grp["Avg_Price"] = grp["Avg_Price"].round(1)
    grp["Avg_Rating"] = grp["Avg_Rating"].round(2)

    pivot = grp.pivot_table(index="Brand", columns="Subcategory", values="Avg_Price", aggfunc="mean")
    pivot = pivot.round(1)
    pivot = pivot.loc[pivot.mean(axis=1).sort_values(ascending=False).index]

    st.markdown('<p class="section-title">Average price heatmap — Subcategory × Brand (HK$)</p>', unsafe_allow_html=True)

    fig_heat = px.imshow(
        pivot,
        color_continuous_scale="RdYlGn_r",
        text_auto=True,
        aspect="auto",
        labels=dict(color="Avg Price (HK$)"),
    )
    fig_heat.update_layout(
        margin=dict(t=80, b=10, l=0, r=10),
        height=max(300, len(pivot) * 60),
        paper_bgcolor="rgba(0,0,0,0)",
        xaxis_title="",
        yaxis_title="",
        coloraxis_colorbar=dict(title="HK$"),
        xaxis=dict(
            side="top",
            tickangle=0,      # ← upright, not slanted
            tickfont=dict(size=12),
        ),
    )
    fig_heat.update_traces(textfont_size=12)
    st.plotly_chart(fig_heat, use_container_width=True)
    st.markdown('<div class="insight-box">🟥 Red = higher avg price in that cell &nbsp;|&nbsp; 🟩 Green = lower avg price. Use this to spot where competitors price aggressively in specific categories.</div>', unsafe_allow_html=True)

    export_csv(grp, "avg_price_heatmap.csv")

    st.markdown("---")

    st.markdown('<p class="section-title">Full detail — subcategory × brand breakdown</p>', unsafe_allow_html=True)
    grp_display = grp.sort_values(["Subcategory","Avg_Price"], ascending=[True, False]).reset_index(drop=True)
    grp_display.index += 1

    st.dataframe(
        grp_display,
        column_config={
            "Avg_Price": st.column_config.NumberColumn("Avg Price (HK$)", format="HK$%.1f"),
            "Avg_Rating": st.column_config.NumberColumn("Avg Rating ⭐", format="%.2f"),
            "Products": st.column_config.NumberColumn("# Products", format="%d"),
            "Subcategory": st.column_config.TextColumn("Subcategory"),
            "Brand": st.column_config.TextColumn("Brand"),
        },
        use_container_width=True,
        height=500,
    )
    export_csv(grp_display.reset_index(drop=True), "subcategory_brand_detail.csv")

    st.markdown("---")
    st.markdown('<p style="font-size:12px;color:#888">Filtered by sidebar selections. Select All to see full dataset.</p>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — Brand Scorecard
# ════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("## 🏷️ Brand Scorecard")
    st.markdown("A single table summarising every brand's competitive position across all key metrics.")
    st.markdown("---")

    sc = df.groupby("Brand").agg(
        Total_Products=("Brand","count"),
        Avg_Price=("Price","mean"),
        Min_Price=("Price","min"),
        Max_Price=("Price","max"),
        Avg_Rating=("Ratings","mean"),
        Best_Ranking=("Ranking","min"),
        Avg_Ranking=("Ranking","mean"),
        Categories=("Subcategory","nunique"),
    ).reset_index()

    camp_pct = (
        df.groupby("Brand")["Campaign_Has"]
        .apply(lambda x: round((x == "Has Campaign").sum() / len(x) * 100, 1))
        .reset_index()
    )
    camp_pct.columns = ["Brand","Campaign_Coverage_%"]
    sc = sc.merge(camp_pct, on="Brand", how="left")

    for col in ["Avg_Price","Avg_Rating","Avg_Ranking"]:
        sc[col] = sc[col].round(2)
    sc["Min_Price"] = sc["Min_Price"].round(1)
    sc["Max_Price"] = sc["Max_Price"].round(1)

    sc = sc.sort_values("Avg_Ranking").reset_index(drop=True)
    sc.index += 1

    st.dataframe(
        sc,
        column_config={
            "Brand": st.column_config.TextColumn("Brand", width="medium"),
            "Total_Products": st.column_config.NumberColumn("# Products", format="%d"),
            "Avg_Price": st.column_config.NumberColumn("Avg Price (HK$)", format="HK$%.2f"),
            "Min_Price": st.column_config.NumberColumn("Min Price (HK$)", format="HK$%.1f"),
            "Max_Price": st.column_config.NumberColumn("Max Price (HK$)", format="HK$%.1f"),
            "Avg_Rating": st.column_config.NumberColumn("Avg Rating ⭐", format="%.2f"),
            "Best_Ranking": st.column_config.NumberColumn("Best Rank #", format="%d"),
            "Avg_Ranking": st.column_config.NumberColumn("Avg Rank #", format="%.1f"),
            "Categories": st.column_config.NumberColumn("Categories Covered", format="%d"),
            "Campaign_Coverage_%": st.column_config.ProgressColumn(
                "Campaign Coverage %",
                help="% of products running a campaign",
                min_value=0, max_value=100, format="%.1f%%",
            ),
        },
        use_container_width=True,
        height=450,
    )
    export_csv(sc.reset_index(drop=True), "brand_scorecard.csv")

    st.markdown("---")

    st.markdown('<p class="section-title">Brand radar — normalised performance comparison</p>', unsafe_allow_html=True)
    st.caption("Each axis is min-max normalised (higher = better). Ranking and Price are inverted so lower numbers score higher.")

    radar_df = sc[["Brand","Avg_Rating","Campaign_Coverage_%","Categories","Avg_Ranking","Avg_Price"]].copy()
    for col in ["Avg_Rating","Campaign_Coverage_%","Categories"]:
        mn, mx = radar_df[col].min(), radar_df[col].max()
        radar_df[col] = (radar_df[col] - mn) / (mx - mn + 1e-9)
    for col in ["Avg_Ranking","Avg_Price"]:
        mn, mx = radar_df[col].min(), radar_df[col].max()
        radar_df[col] = 1 - (radar_df[col] - mn) / (mx - mn + 1e-9)

    categories_radar = ["Avg Rating","Campaign Coverage","Category Width","Ranking Strength","Price Competitiveness"]
    top_brands = radar_df["Brand"].head(min(5, len(radar_df))).tolist()

    fig_radar = go.Figure()
    for i, brand in enumerate(top_brands):
        row = radar_df[radar_df["Brand"] == brand].iloc[0]
        vals = [row["Avg_Rating"], row["Campaign_Coverage_%"], row["Categories"], row["Avg_Ranking"], row["Avg_Price"]]
        vals_closed = vals + [vals[0]]
        cats_closed = categories_radar + [categories_radar[0]]
        fig_radar.add_trace(go.Scatterpolar(
            r=vals_closed, theta=cats_closed, fill="toself", name=brand,
            line_color=COLORS[i % len(COLORS)],
            fillcolor=COLORS[i % len(COLORS)], opacity=0.25,
        ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0,1])),
        showlegend=True, height=420,
        margin=dict(t=20,b=20,l=40,r=40),
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=-0.15),
    )
    st.plotly_chart(fig_radar, use_container_width=True)

    radar_export = radar_df[["Brand","Avg_Rating","Campaign_Coverage_%","Categories","Avg_Ranking","Avg_Price"]].copy()
    radar_export.columns = ["Brand","Norm_Avg_Rating","Norm_Campaign_Coverage","Norm_Category_Width","Norm_Ranking_Strength","Norm_Price_Competitiveness"]
    export_csv(radar_export, "brand_radar_scores.csv")

    st.markdown("---")
    st.markdown('<p style="font-size:12px;color:#888">Filtered by sidebar selections.</p>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# TAB 4 — Campaign Intelligence
# ════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("## 📣 Campaign Intelligence")
    st.markdown("Understand which campaign types are driving shelf presence, and how discounting correlates with ratings and price.")
    st.markdown("---")

    st.markdown('<p class="section-title">Campaign type breakdown — who is discounting, and how?</p>', unsafe_allow_html=True)

    camp_summary = (
        df.groupby("Campaign_Type")
        .agg(
            Products=("Brand","count"),
            Brands=("Brand","nunique"),
            Avg_Price=("Price","mean"),
            Avg_Rating=("Ratings","mean"),
            Avg_Ranking=("Ranking","mean"),
        )
        .reset_index()
        .sort_values("Products", ascending=False)
    )
    camp_summary["Avg_Price"] = camp_summary["Avg_Price"].round(1)
    camp_summary["Avg_Rating"] = camp_summary["Avg_Rating"].round(2)
    camp_summary["Avg_Ranking"] = camp_summary["Avg_Ranking"].round(1)
    camp_summary["Share_%"] = (camp_summary["Products"] / camp_summary["Products"].sum() * 100).round(1)
    camp_summary = camp_summary.reset_index(drop=True)
    camp_summary.index += 1

    st.dataframe(
        camp_summary,
        column_config={
            "Campaign_Type": st.column_config.TextColumn("Campaign Type", width="large"),
            "Products": st.column_config.NumberColumn("# Products", format="%d"),
            "Brands": st.column_config.NumberColumn("Brands Using", format="%d"),
            "Avg_Price": st.column_config.NumberColumn("Avg Price (HK$)", format="HK$%.1f"),
            "Avg_Rating": st.column_config.NumberColumn("Avg Rating ⭐", format="%.2f"),
            "Avg_Ranking": st.column_config.NumberColumn("Avg Rank #", format="%.1f"),
            "Share_%": st.column_config.ProgressColumn(
                "Share of Products %", min_value=0, max_value=100, format="%.1f%%",
            ),
        },
        use_container_width=True,
        height=380,
    )
    export_csv(camp_summary.reset_index(drop=True), "campaign_type_breakdown.csv")

    st.markdown("---")

    st.markdown('<p class="section-title">Campaign coverage by brand — who is running the most promotions?</p>', unsafe_allow_html=True)

    camp_brand = df.groupby(["Brand","Campaign_Has"]).size().reset_index(name="Count")
    camp_brand_total = camp_brand.groupby("Brand")["Count"].transform("sum")
    camp_brand["Pct"] = (camp_brand["Count"] / camp_brand_total * 100).round(1)

    fig_camp = px.bar(
        camp_brand, x="Brand", y="Pct", color="Campaign_Has",
        color_discrete_map={"Has Campaign":"#1D9E75","No Campaign":"#E8E4DE"},
        barmode="stack", text="Pct",
    )
    fig_camp.update_traces(texttemplate="%{text:.0f}%", textposition="inside")
    fig_camp.update_layout(
        height=340, margin=dict(t=10,b=60,l=0,r=0),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(title="% of products", gridcolor="#E8E4DE"),
        xaxis=dict(tickangle=0),   # upright
        xaxis_title="",
        legend=dict(orientation="h", yanchor="bottom", y=1.01, title=""),
        showlegend=True,
    )
    st.plotly_chart(fig_camp, use_container_width=True)

    top_camp_brand = (
        df[df["Campaign_Has"]=="Has Campaign"]
        .groupby("Brand").size()
        .div(df.groupby("Brand").size())
        .idxmax()
    )
    st.markdown(f'<div class="insight-box">📣 <b>{top_camp_brand}</b> has the highest campaign coverage among its products — they are the most aggressive promoter on shelf.</div>', unsafe_allow_html=True)
    export_csv(camp_brand, "campaign_coverage_by_brand.csv")

    st.markdown("---")

    st.markdown('<p class="section-title">Does running a campaign correlate with higher ratings?</p>', unsafe_allow_html=True)

    camp_rating = df.groupby("Campaign_Has")["Ratings"].mean().reset_index()
    camp_rating["Ratings"] = camp_rating["Ratings"].round(2)

    fig_cr = px.bar(
        camp_rating, x="Campaign_Has", y="Ratings", color="Campaign_Has",
        color_discrete_map={"Has Campaign":"#1D9E75","No Campaign":"#E07B39"},
        text="Ratings",
    )
    fig_cr.update_traces(texttemplate="%{text:.2f} ⭐", textposition="outside")
    fig_cr.update_layout(
        height=300, showlegend=False, margin=dict(t=10,b=10,l=0,r=0),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        yaxis=dict(range=[0,6], gridcolor="#E8E4DE", title="Avg Rating"),
        xaxis=dict(tickangle=0),
        xaxis_title="",
    )
    st.plotly_chart(fig_cr, use_container_width=True)
    export_csv(camp_rating, "campaign_vs_rating.csv")

    st.markdown("---")
    st.markdown('<p style="font-size:12px;color:#888">Filtered by sidebar selections.</p>', unsafe_allow_html=True)
