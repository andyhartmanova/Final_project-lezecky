import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.title("Analýza lezeček")

st.write(
    "Toto je můj závěrečný projekt. Analyzovala jsem údaje o lezečkách na webu https://www.4camping.cz/"
)

# Načtení dat
df = pd.read_csv("products_data (2).csv")

# --- NÁHLED DAT ---
st.subheader("Náhled dat")
st.write("Než začneme s analýzou, podíváme se na strukturu surových dat, se kterými pracujeme.")
st.dataframe(df.head())

# --- ZÁKLADNÍ INFO ---
st.subheader("Základní informace o datech")
st.write(f"Počet produktů: {df.shape[0]}")
st.write(f"Počet atributů: {df.shape[1]}")
st.write("Sloupce:")
st.write(list(df.columns))

# --- KATEGORIE ---
st.subheader("Zastoupení kategorií")
st.write("Zde vidíme, jak jsou lezečky rozděleny podle určení (např. unisex, dámské, dětské).")
category_counts = df["category"].value_counts()

fig, ax = plt.subplots()
ax.pie(category_counts, labels=category_counts.index, autopct="%1.1f%%", startangle=90)
ax.axis("equal")
st.pyplot(fig)
st.write("Z grafu vyplývá, že největší část nabídky tvoří standardní kategorie lezeček, zatímco speciální kategorie mají menší zastoupení.")

# --- PRŮMĚRNÁ CENA PODLE KATEGORIE ---
st.subheader("Průměrná cena podle kategorie")
st.write("Zajímalo mě, zda se průměrná cena liší v závislosti na tom, pro koho jsou lezečky určeny.")
avg_price_by_category = (
    df.dropna(subset=["category", "current_price"])
    .groupby("category")["current_price"]
    .mean()
    .sort_values(ascending=False)
)

st.dataframe(
    avg_price_by_category.round(0).reset_index().rename(columns={
        "category": "Category",
        "current_price": "Average price (CZK)"
    })
)
st.write("Analýza ukazuje, že cenové rozdíly mezi kategoriemi existují, nicméně nejsou nijak dramatické. Nižší cena u dětských lezeček je očekávatelná. Rozdíl mezi Dámskými a Unisex lezečkami je zanedbatelný.")

# --- CELKOVÁ CENOVÁ STATISTIKA ---
st.subheader("Cenová statistika - celková")
st.write("Zde vidíme základní statistické ukazatele cen všech lezeček v nabídce (minimum, maximum, průměr).")
st.table(df["current_price"].describe())
st.write("Statistiky ukazují poměrně velký rozptyl mezi nejlevnějšími a nejdražšími modely na trhu.")

st.subheader("Vizuální rozdělení cen (Boxplot)")

fig_box, ax_box = plt.subplots(figsize=(10, 4))
ax_box.boxplot(df["current_price"], vert=False, patch_artist=True, 
                boxprops=dict(facecolor="lightblue", color="blue"),
                medianprops=dict(color="red", linewidth=2))

ax_box.set_title("Rozložení cen lezeček")
ax_box.set_xlabel("Cena (Kč)")
ax_box.set_yticks([]) # Odstraníme osu Y, která u jednoho boxplotu není potřeba

st.pyplot(fig_box)

st.write("""
**Jak číst tento graf:**
* **Modrý box:** Znázorňuje střední polovinu hodnot (od 25 % do 75 % dat).
* **Svislá červená čára:** Označuje medián (3 099 Kč). Polovina lezeček stojí méně a polovina více.
* **Čáry:** Ukazují rozsah cen k minimu a maximu. Pokud by byly v grafu tečky mimo tyto čáry, šlo by o extrémně levné nebo drahé modely (outliery).
""")

# --- VZTAH CENY A HMOTNOSTI ---
st.subheader("Vztah ceny a hmotnosti lezeček")
st.write("Chtěla jsem ověřit hypotézu, zda lehčí lezečky (často výkonnostní) stojí více peněz.")
df_weight_price = df.dropna(subset=["current_price", "weight_value"])

fig, ax = plt.subplots()
ax.scatter(df_weight_price["weight_value"], df_weight_price["current_price"])
ax.set_xlabel("Hmotnost (g)")
ax.set_ylabel("Cena (Kč)")
ax.set_title("Závislost ceny na hmotnosti")
st.pyplot(fig)

correlation = df_weight_price["weight_value"].corr(df_weight_price["current_price"])
st.write(f"Korelace mezi hmotností a cenou: {correlation:.2f}")
st.write("Na základě analýzy vidíme, že korelace je poměrně nízká. Váha tedy není hlavním faktorem určujícím cenu lezeček.")

# --- NEJVĚTŠÍ SLEVY ---
st.subheader("Lezečky s největší slevou")
st.write("Tato tabulka ukazuje konkrétní modely, u kterých došlo k nejvýraznějšímu absolutnímu zlevnění.")
df['discount'] = df['original_price'] - df['current_price']
discounts = df.nlargest(10, 'discount')[['brand', 'name', 'original_price', 'current_price', 'discount']]
st.dataframe(discounts.rename(columns={
    'brand': 'Značka', 'name': 'Název', 'original_price': 'Původní cena (Kč)', 
    'current_price': 'Aktuální cena (Kč)', 'discount': 'Sleva (Kč)'
}))
st.write("U vybraných modelů dosahují slevy i více než tisíc korun, což může být dáno doprodejem starších kolekcí.")

# --- SLEVY PODLE ZNAČEK ---
st.subheader("Značky s největší průměrnou slevou")
st.write("Které značky jsou v průměru nejvíce zlevňovány?")
df_brand_discount = df.groupby("brand")["discount"].mean().sort_values(ascending=False).head(10)

fig, ax = plt.subplots()
ax.bar(df_brand_discount.index, df_brand_discount.values, color="teal")
ax.set_xlabel("Značka")
ax.set_ylabel("Průměrná sleva (Kč)")
plt.xticks(rotation=45)
st.pyplot(fig)
st.write("Z grafu je patrné, že některé značky pracují s výraznější slevovou politikou než jiné.")

# --- TRŽNÍ PODÍL ---
st.subheader("Tržní podíl značek (Brand Awareness)")
st.write("Nakonec se podíváme na to, jaké značky mají v e-shopu nejširší portfolio produktů.")
brand_counts = df["brand"].value_counts().reset_index()
brand_counts.columns = ["Značka", "Počet modelů"]
top_10_brands = brand_counts.head(10)

fig_share, ax_share = plt.subplots(figsize=(10, 6))
ax_share.barh(top_10_brands["Značka"], top_10_brands["Počet modelů"], color="orange")
ax_share.invert_yaxis()
st.pyplot(fig_share)

st.write(f"Největší zastoupení má značka {top_10_brands.iloc[0]['Značka']}, která tvoří { (top_10_brands.iloc[0]['Počet modelů'] / len(df) * 100):.1f}% celkové nabídky lezeček.")
st.write("Závěrem lze říci, že trh s lezečkami je ovládán několika dominantními výrobci, kteří nabízejí nejširší spektrum modelů.")