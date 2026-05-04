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
</style>
""", unsafe_allow_html=True)

COLORS = ["#1D9E75","#E07B39","#185FA5","#BA7517","#7B3FA0","#C23B5A","#2B8C9B","#8B7355"]

# ── Sample data ───────────────────────────────────────────────────────────────
SAMPLE = """Subcategory\tLink\tRatings\tImage_src\tBrand\tTitle\tPrice\tCampaign_Type\tRanking
Stiletto Heels\thttps://www.zalora.com.hk/p/forcast-kelsey-stiletto-heel-6783657\t3\thttps://img1.jpg\tFORCAST\tKelsey Stiletto Heel\t264.5\tX Pay HK$20 off\t1
Stiletto Heels\thttps://www.zalora.com.hk/p/forcast-kelsey-stiletto-heel-6783661\t3\thttps://img2.jpg\tFORCAST\tKelsey Stiletto Heel\t264.5\tX Pay HK$20 off\t2
Stiletto Heels\thttps://www.zalora.com.hk/p/forcast-kelsey-leather-stiletto-heel-6783656\t4\thttps://img3.jpg\tFORCAST\tKelsey Leather Stiletto Heel\t379.5\tX Pay HK$20 off\t3
Stiletto Heels\thttps://www.zalora.com.hk/p/rag-co-microfiber-stiletto-sandals-in-taupe-7051748\t4.8\thttps://img4.jpg\tRag & CO.\tMicrofiber Stiletto Sandals in Taupe\t188.3\t30% off\t4
Stiletto Heels\thttps://www.zalora.com.hk/p/rag-co-suede-stiletto-mules-in-black-7081384\t5\thttps://img5.jpg\tRag & CO.\tSuede Stiletto Mules In Black\t293.3\t30% off\t5
Stiletto Heels\thttps://www.zalora.com.hk/p/twenty-eight-shoes-10cm-silk-6783456\t4.8\thttps://img6.jpg\tTwenty Eight Shoes\t10CM Silk Fabrics Pointed High Heel Shoes\t431.1\t10% off\t6
Stiletto Heels\thttps://www.zalora.com.hk/p/rag-co-patent-heel-7081390\t4.5\thttps://img7.jpg\tRag & CO.\tPatent Leather Stiletto Pumps\t245.0\t30% off\t7
Stiletto Heels\thttps://www.zalora.com.hk/p/forcast-mini-stiletto-6783700\t3.5\thttps://img8.jpg\tFORCAST\tMini Block Stiletto Heel\t199.0\tX Pay HK$20 off\t8
Ankle Boots\thttps://www.zalora.com.hk/p/london-rag-ankle-1\t5\thttps://img9.jpg\tLondon Rag\tBlock Heel Chelsea Ankle Boots Black\t899.0\tNo campaign\t1
Ankle Boots\thttps://www.zalora.com.hk/p/london-rag-ankle-2\t5\thttps://img10.jpg\tLondon Rag\tCroc Embossed Ankle Boots Nude\t1099.0\tNo campaign\t2
Ankle Boots\thttps://www.zalora.com.hk/p/rag-co-ankle-1\t4.8\thttps://img11.jpg\tRag & CO.\tSuede Effect Ankle Boots Tan\t1599.0\t15% off\t3
Ankle Boots\thttps://www.zalora.com.hk/p/london-rag-ankle-3\t4.5\thttps://img12.jpg\tLondon Rag\tSquare Toe Chelsea Boots Camel\t799.0\tNo campaign\t4
Ankle Boots\thttps://www.zalora.com.hk/p/rag-co-ankle-2\t5\thttps://img13.jpg\tRag & CO.\tLeather Ankle Boots Brown\t1799.0\t15% off\t5
Ankle Boots\thttps://www.zalora.com.hk/p/london-rag-ankle-4\t4\thttps://img14.jpg\tLondon Rag\tPlatform Sole Ankle Boots White\t949.0\tNo campaign\t6
Long Boots\thttps://www.zalora.com.hk/p/london-rag-long-1\t4.5\thttps://img15.jpg\tLondon Rag\tKnee High Stretch Boots Black\t1399.0\tNo campaign\t1
Long Boots\thttps://www.zalora.com.hk/p/rag-co-long-1\t4.8\thttps://img16.jpg\tRag & CO.\tLeather Knee High Boots Tan\t2199.0\t20% off\t2
Long Boots\thttps://www.zalora.com.hk/p/london-rag-long-2\t4\thttps://img17.jpg\tLondon Rag\tBlock Heel Long Boots Camel\t1199.0\tNo campaign\t3
Long Boots\thttps://www.zalora.com.hk/p/rag-co-long-2\t5\thttps://img18.jpg\tRag & CO.\tSuede Knee High Boots Brown\t2499.0\t20% off\t4
Long Boots\thttps://www.zalora.com.hk/p/twenty-eight-long-1\t4.2\thttps://img19.jpg\tTwenty Eight Shoes\tHeeled Long Boots Black\t1650.0\t10% off\t5"""

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

    # Clean
    df = df_raw.copy()
    df.columns = [c.strip() for c in df.columns]
    for col in ["Ratings","Price","Ranking"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["Brand","Price","Ratings"])
    df["Campaign_Has"] = df["Campaign_Type"].apply(
        lambda x: "Has Campaign" if pd.notna(x) and x.strip() not in ["","No campaign","nan"] else "No Campaign"
    )

    st.markdown("**Filters**")
    cats = ["All"] + sorted(df["Subcategory"].dropna().unique().tolist())
    sel_cat = st.selectbox("Subcategory", cats)
    brands = sorted(df["Brand"].dropna().unique().tolist())
    sel_brands = st.multiselect("Brands", brands, default=brands)

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

# ── KPI row ───────────────────────────────────────────────────────────────────
k1,k2,k3,k4,k5 = st.columns(5)
kpis = [
    (k1, len(df["Brand"].unique()), "Brands tracked"),
    (k2, len(df["Subcategory"].unique()), "Subcategories"),
    (k3, f"HK${df['Price'].median():,.0f}", "Median price"),
    (k4, f"{df['Ratings'].mean():.2f} ★", "Avg rating"),
    (k5, f"{(df['Campaign_Has']=='Has Campaign').sum()}", "Promoted products"),
]
for col, val, lbl in kpis:
    col.markdown(f"""<div class="metric-card">
        <p class="metric-value">{val}</p>
        <p class="metric-label">{lbl}</p>
    </div>""", unsafe_allow_html=True)

st.markdown("---")

# ════════════════════════════════════════════════════════════════════════════
# ROW 1 — Share of shelf + Rating distribution
# ════════════════════════════════════════════════════════════════════════════
c1, c2 = st.columns([1,1])

with c1:
    st.markdown('<p class="section-title">Share of shelf by brand</p>', unsafe_allow_html=True)
    shelf = df["Brand"].value_counts().reset_index()
    shelf.columns = ["Brand","Count"]
    shelf["Share"] = (shelf["Count"] / shelf["Count"].sum() * 100).round(1)
    fig = px.pie(shelf, values="Count", names="Brand",
                 color_discrete_sequence=COLORS, hole=0.45)
    fig.update_traces(textposition="outside", textinfo="label+percent",
                      textfont_size=12, pull=[0.03]*len(shelf))
    fig.update_layout(margin=dict(t=10,b=10,l=10,r=10), height=320,
                      showlegend=False,
                      paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig, use_container_width=True)
    top = shelf.iloc[0]
    st.markdown(f'<div class="insight-box">🏆 <b>{top.Brand}</b> owns <b>{top.Share}%</b> of shelf space — the brand you need to displace or differentiate from.</div>', unsafe_allow_html=True)

with c2:
    st.markdown('<p class="section-title">Rating distribution by brand</p>', unsafe_allow_html=True)
    fig2 = px.box(df, x="Brand", y="Ratings", color="Brand",
                  color_discrete_sequence=COLORS, points="all")
    fig2.update_layout(showlegend=False, margin=dict(t=10,b=10,l=0,r=0),
                       height=320, paper_bgcolor="rgba(0,0,0,0)",
                       plot_bgcolor="rgba(0,0,0,0)",
                       yaxis=dict(range=[0,5.5], gridcolor="#E8E4DE"),
                       xaxis_title="", yaxis_title="Rating")
    fig2.update_traces(marker_size=6)
    st.plotly_chart(fig2, use_container_width=True)
    low_brand = df.groupby("Brand")["Ratings"].mean().idxmin()
    st.markdown(f'<div class="warn-box">⚠️ <b>{low_brand}</b> has the lowest average rating — their unhappy customers are your acquisition opportunity.</div>', unsafe_allow_html=True)

st.markdown("---")

# ════════════════════════════════════════════════════════════════════════════
# ROW 2 — Price positioning + Price vs Rating scatter
# ════════════════════════════════════════════════════════════════════════════
c3, c4 = st.columns([1,1])

with c3:
    st.markdown('<p class="section-title">Price positioning by brand</p>', unsafe_allow_html=True)
    fig3 = px.violin(df, x="Brand", y="Price", color="Brand",
                     color_discrete_sequence=COLORS, box=True, points="all")
    fig3.update_layout(showlegend=False, margin=dict(t=10,b=10,l=0,r=0),
                       height=340, paper_bgcolor="rgba(0,0,0,0)",
                       plot_bgcolor="rgba(0,0,0,0)",
                       yaxis=dict(gridcolor="#E8E4DE"),
                       xaxis_title="", yaxis_title="Price (HK$)")
    st.plotly_chart(fig3, use_container_width=True)

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

st.markdown("---")

# ════════════════════════════════════════════════════════════════════════════
# ROW 3 — Search ranking analysis + Campaign impact
# ════════════════════════════════════════════════════════════════════════════
c5, c6 = st.columns([1,1])

with c5:
    st.markdown('<p class="section-title">Search ranking by brand — who wins page 1?</p>', unsafe_allow_html=True)
    if "Ranking" in df.columns and df["Ranking"].notna().sum() > 0:
        rank_df = df.groupby("Brand")["Ranking"].agg(["mean","min","count"]).reset_index()
        rank_df.columns = ["Brand","Avg Rank","Best Rank","Products"]
        rank_df = rank_df.sort_values("Avg Rank")
        fig5 = px.bar(rank_df, x="Brand", y="Avg Rank", color="Brand",
                      color_discrete_sequence=COLORS, text="Avg Rank",
                      hover_data=["Best Rank","Products"])
        fig5.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        fig5.update_layout(showlegend=False, margin=dict(t=10,b=10,l=0,r=0),
                           height=320, paper_bgcolor="rgba(0,0,0,0)",
                           plot_bgcolor="rgba(0,0,0,0)",
                           yaxis=dict(autorange="reversed", gridcolor="#E8E4DE",
                                      title="Avg ranking position (lower = better)"),
                           xaxis_title="")
        st.plotly_chart(fig5, use_container_width=True)
        best = rank_df.iloc[0]
        st.markdown(f'<div class="insight-box">🔍 <b>{best.Brand}</b> has the best avg ranking position ({best["Avg Rank"]:.1f}). Study their title keywords and campaign types.</div>', unsafe_allow_html=True)
    else:
        st.info("No Ranking data available.")

with c6:
    st.markdown('<p class="section-title">Campaign type — discount strategy breakdown</p>', unsafe_allow_html=True)
    camp_df = df.groupby(["Brand","Campaign_Has"]).size().reset_index(name="Count")
    fig6 = px.bar(camp_df, x="Brand", y="Count", color="Campaign_Has",
                  barmode="group", color_discrete_map={
                      "Has Campaign":"#1D9E75","No Campaign":"#D5CFC6"},
                  text="Count")
    fig6.update_traces(textposition="outside")
    fig6.update_layout(margin=dict(t=10,b=10,l=0,r=0), height=320,
                       paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                       yaxis=dict(gridcolor="#E8E4DE", title="Product count"),
                       xaxis_title="", legend_title="",
                       legend=dict(orientation="h", yanchor="bottom", y=1.01))
    st.plotly_chart(fig6, use_container_width=True)
    promo_pct = (df["Campaign_Has"]=="Has Campaign").mean() * 100
    st.markdown(f'<div class="insight-box">🎯 <b>{promo_pct:.0f}%</b> of listed products run a campaign/discount. If your products have no campaign, you\'re at a visibility disadvantage in Zalora\'s algorithm.</div>', unsafe_allow_html=True)

st.markdown("---")

# ════════════════════════════════════════════════════════════════════════════
# ROW 4 — Category heatmap + Rating vs Ranking
# ════════════════════════════════════════════════════════════════════════════
c7, c8 = st.columns([1,1])

with c7:
    st.markdown('<p class="section-title">Brand × category presence heatmap</p>', unsafe_allow_html=True)
    heatmap_df = df.groupby(["Brand","Subcategory"]).size().unstack(fill_value=0)
    fig7 = px.imshow(heatmap_df, color_continuous_scale="Greens",
                     text_auto=True, aspect="auto")
    fig7.update_layout(margin=dict(t=10,b=10,l=0,r=0), height=320,
                       paper_bgcolor="rgba(0,0,0,0)",
                       coloraxis_showscale=False,
                       xaxis_title="", yaxis_title="")
    fig7.update_traces(textfont_size=13)
    st.plotly_chart(fig7, use_container_width=True)
    st.markdown('<div class="insight-box">📊 Dark cells = dominant brand-category combinations. White/empty cells = gaps your brand can enter with less competition.</div>', unsafe_allow_html=True)

with c8:
    st.markdown('<p class="section-title">Does higher rating = better ranking?</p>', unsafe_allow_html=True)
    if "Ranking" in df.columns and df["Ranking"].notna().sum() > 0:
        fig8 = px.scatter(df, x="Ratings", y="Ranking", color="Brand",
                          size="Price", size_max=20,
                          hover_data=["Title","Brand","Price"],
                          color_discrete_sequence=COLORS,
                          trendline="ols")
        fig8.update_layout(margin=dict(t=10,b=10,l=0,r=0), height=320,
                           paper_bgcolor="rgba(0,0,0,0)",
                           plot_bgcolor="rgba(0,0,0,0)",
                           yaxis=dict(autorange="reversed", gridcolor="#E8E4DE",
                                      title="Ranking (1 = top)"),
                           xaxis=dict(gridcolor="#E8E4DE", title="Rating"),
                           legend=dict(orientation="h", yanchor="bottom", y=1.01))
        st.plotly_chart(fig8, use_container_width=True)
        st.markdown('<div class="warn-box">💡 If the trendline slopes down-left, ratings alone don\'t drive ranking — campaigns and price also matter. Use this to calibrate your optimisation priority.</div>', unsafe_allow_html=True)
    else:
        st.info("No Ranking data available.")

st.markdown("---")

# ════════════════════════════════════════════════════════════════════════════
# ROW 5 — Price tier analysis + Avg price per subcategory
# ════════════════════════════════════════════════════════════════════════════
c9, c10 = st.columns([1,1])

with c9:
    st.markdown('<p class="section-title">Price tier distribution — where is the crowd?</p>', unsafe_allow_html=True)
    q1, q3 = df["Price"].quantile(0.25), df["Price"].quantile(0.75)
    def tier(p):
        if p <= q1: return "Budget"
        elif p <= q3: return "Mid-market"
        else: return "Premium"
    df["Tier"] = df["Price"].apply(tier)
    tier_order = ["Budget","Mid-market","Premium"]
    tier_colors = {"Budget":"#1D9E75","Mid-market":"#BA7517","Premium":"#185FA5"}
    tier_df = df.groupby(["Tier","Brand"]).size().reset_index(name="Count")
    fig9 = px.bar(tier_df, x="Tier", y="Count", color="Brand",
                  color_discrete_sequence=COLORS,
                  category_orders={"Tier":tier_order})
    fig9.update_layout(margin=dict(t=10,b=10,l=0,r=0), height=320,
                       paper_bgcolor="rgba(0,0,0,0)",
                       plot_bgcolor="rgba(0,0,0,0)",
                       yaxis=dict(gridcolor="#E8E4DE", title="Products"),
                       xaxis_title="",
                       legend=dict(orientation="h", yanchor="bottom", y=1.01))
    st.plotly_chart(fig9, use_container_width=True)

with c10:
    st.markdown('<p class="section-title">Average price by subcategory</p>', unsafe_allow_html=True)
    sub_price = df.groupby("Subcategory")["Price"].agg(["mean","min","max","count"]).reset_index()
    sub_price.columns = ["Subcategory","Avg","Min","Max","Count"]
    sub_price = sub_price.sort_values("Avg", ascending=True)
    fig10 = go.Figure()
    fig10.add_trace(go.Bar(
        y=sub_price["Subcategory"], x=sub_price["Avg"],
        orientation="h", marker_color=COLORS[:len(sub_price)],
        text=[f"HK${v:,.0f}" for v in sub_price["Avg"]],
        textposition="outside",
        error_x=dict(
            type="data",
            array=(sub_price["Max"]-sub_price["Avg"]).tolist(),
            arrayminus=(sub_price["Avg"]-sub_price["Min"]).tolist(),
            visible=True, color="#AAAAAA"
        )
    ))
    fig10.update_layout(margin=dict(t=10,b=10,l=0,r=80), height=320,
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        xaxis=dict(gridcolor="#E8E4DE", title="Price (HK$)"),
                        yaxis_title="")
    st.plotly_chart(fig10, use_container_width=True)
    st.markdown('<div class="insight-box">📌 Error bars show price range per category. Wide bars = high price variance = room to position at multiple tiers within one category.</div>', unsafe_allow_html=True)

st.markdown("---")

# ════════════════════════════════════════════════════════════════════════════
# ROW 6 — Top 10 products table
# ════════════════════════════════════════════════════════════════════════════
st.markdown('<p class="section-title">🏅 Top ranked products — your benchmark list</p>', unsafe_allow_html=True)
show_cols = [c for c in ["Ranking","Brand","Title","Subcategory","Price","Ratings","Campaign_Type"] if c in df.columns]
top10 = df.sort_values("Ranking").head(15)[show_cols].reset_index(drop=True)
top10.index += 1

def color_rating(val):
    if val >= 4.5: return "background-color:#E1F5EE;color:#085041"
    elif val >= 3.5: return "background-color:#FAEEDA;color:#633806"
    else: return "background-color:#FCEBEB;color:#791F1F"

try:
    styled = top10.style.map(color_rating, subset=["Ratings"])
except AttributeError:
    styled = top10.style.applymap(color_rating, subset=["Ratings"])
st.dataframe(
    styled.format({"Price":"HK${:.1f}","Ratings":"{:.1f}"}),
    use_container_width=True, height=420
)

st.markdown("---")
st.markdown('<p style="font-size:12px;color:#888">Built for Zalora competitive intelligence · Upload fresh scraped data weekly for trend tracking</p>', unsafe_allow_html=True)
