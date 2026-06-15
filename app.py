"""
WareNav - Smart Warehouse Navigation & Product Locator
A demo prototype built with Streamlit.
Tagline: "The shortest path to every product."
"""
import streamlit as st
import pandas as pd
import random
# -----------------------------------------------------------------
# PAGE CONFIG
# -----------------------------------------------------------------
st.set_page_config(page_title="WareNav", page_icon=" ", layout="wide")
# -----------------------------------------------------------------
# DEMO DATA  (this acts as our fake "database")
# In a real app this would come from a real database.
# -----------------------------------------------------------------
GRID_ROWS = 6          # warehouse is a 6 x 8 grid of bins
GRID_COLS = 8
PACKING_STATION = (0, 0)   # top-left corner is where orders are packed
# Sample products. Each product lives in one bin (row, col).
if "products" not in st.session_state:
    st.session_state.products = pd.DataFrame([
        {"SKU": "SKU-1001", "Product": "Wireless Mouse",   "Bin": "B-12", "Row": 1, "Col": 2, "Qty": 40},
        {"SKU": "SKU-1002", "Product": "USB-C Cable",      "Bin": "B-25", "Row": 2, "Col": 5, "Qty": 12},
        {"SKU": "SKU-1003", "Product": "Notebook A5",      "Bin": "B-31", "Row": 3, "Col": 1, "Qty": 80},
        {"SKU": "SKU-1004", "Product": "Water Bottle",     "Bin": "B-47", "Row": 4, "Col": 7, "Qty": 6},
        {"SKU": "SKU-1005", "Product": "Desk Lamp",        "Bin": "B-53", "Row": 5, "Col": 3, "Qty": 25},
        {"SKU": "SKU-1006", "Product": "Headphones",       "Bin": "B-18", "Row": 1, "Col": 6, "Qty": 9},
        {"SKU": "SKU-1007", "Product": "Power Bank",       "Bin": "B-42", "Row": 4, "Col": 2, "Qty": 33},
        {"SKU": "SKU-1008", "Product": "Sticky Notes",     "Bin": "B-36", "Row": 3, "Col": 6, "Qty": 4},
    ])
products = st.session_state.products
LOW_STOCK_THRESHOLD = 10
# -----------------------------------------------------------------
# HELPER: build the shortest pick route (nearest-neighbour algorithm)
# -----------------------------------------------------------------
def manhattan(a, b):
    """Distance between two bins if you can only walk along aisles."""
    return abs(a[0] - b[0]) + abs(a[1] - b[1])
def build_route(stops):
    """Greedy shortest route: always walk to the nearest remaining bin."""
    route = [PACKING_STATION]
    remaining = stops.copy()
    current = PACKING_STATION
    while remaining:
        nxt = min(remaining, key=lambda p: manhattan(current, p))
        route.append(nxt)
        remaining.remove(nxt)
        current = nxt
    route.append(PACKING_STATION)  # return to packing
    return route
def route_distance(route):
    return sum(manhattan(route[i], route[i+1]) for i in range(len(route)-1))
# -----------------------------------------------------------------
# HELPER: draw the warehouse grid as a simple visual map
# -----------------------------------------------------------------
def draw_map(highlight=None, route=None):
    highlight = highlight or []
    route = route or []
    route_cells = set(route)
    html = "<div style='font-family:monospace; line-height:1.1'>"
    for r in range(GRID_ROWS):
        html += "<div style='display:flex'>"
        for c in range(GRID_COLS):
            cell = (r, c)
            bg, label = "#eee", ""
            if cell == PACKING_STATION:
                bg, label = "#2563eb", "PACK"
            elif cell in highlight:
                bg, label = "#f59e0b", "★"
            elif cell in route_cells:
                bg, label = "#86efac", "·"
            html += (
                f"<div style='width:46px;height:38px;margin:2px;border-radius:6px;"
                f"background:{bg};color:white;display:flex;align-items:center;"
                f"justify-content:center;font-size:12px;font-weight:bold'>{label}</div>"
            )
        html += "</div>"
    html += "</div>"
    return html
# -----------------------------------------------------------------
# SIDEBAR NAVIGATION
# -----------------------------------------------------------------
st.sidebar.title(" WareNav")
st.sidebar.caption("The shortest path to every product.")
page = st.sidebar.radio(
    "Go to",
    [" Home", " Product Search", " Pick Route", " QR Verify",
     " Manager Dashboard", " Add Product"]
)
# ==================================================================
# PAGE 1: HOME
# ==================================================================
if page == " Home":
    st.title("WareNav — Smart Warehouse Navigation")
    st.subheader("The shortest path to every product.")
    st.markdown("""
    **The problem:** Warehouse employees waste up to **50% of their time**
    searching for products because of poor inventory visibility and
    inefficient picking routes — causing delays, errors and higher costs.
    **Our solution:** WareNav guides workers *directly* to products using a
    digital warehouse map, the shortest pick route, QR verification and
    real-time inventory — **no robots, no expensive automation.**
    """)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Picking Time", "↓ 30–40%")
    c2.metric("Picking Errors", "↓ 50%")
    c3.metric("Search Time", "↓ 60–70%")
    c4.metric("Inventory Accuracy", "> 95%")
    st.info("Use the sidebar to explore the live demo features. ")
# ==================================================================
# PAGE 2: PRODUCT SEARCH
# ==================================================================
elif page == " Product Search":
    st.title(" Product Search")
    st.caption("Instantly find where any product is stored.")
    query = st.text_input("Search by product name or SKU", "")
    if query:
        mask = (
            products["Product"].str.contains(query, case=False)
            | products["SKU"].str.contains(query, case=False)
        )
        results = products[mask]
    else:
        results = products
    st.dataframe(results, use_container_width=True, hide_index=True)
    if query and not results.empty:
        row = results.iloc[0]
        st.success(f"**{row['Product']}** is in bin **{row['Bin']}** — Qty available: **{row['Qty']}**")
        st.markdown("Bin location on the map:")
        st.markdown(draw_map(highlight=[(row["Row"], row["Col"])]), unsafe_allow_html=True)
# ==================================================================
# PAGE 3: PICK ROUTE
# ==================================================================
elif page == " Pick Route":
    st.title(" Smart Pick Route")
    st.caption("Select the products in an order — WareNav builds the shortest route.")
    picks = st.multiselect(
        "Products to pick",
        options=products["Product"].tolist(),
        default=products["Product"].tolist()[:3],
    )
    if picks:
        chosen = products[products["Product"].isin(picks)]
        stops = list(zip(chosen["Row"], chosen["Col"]))
        route = build_route(stops)
        dist = route_distance(route)
        # naive route = visit in listed order, for comparison
        naive = [PACKING_STATION] + stops + [PACKING_STATION]
        naive_dist = route_distance(naive)
        saved = max(naive_dist - dist, 0)
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("**Optimized route** (green = path, ★ = pick bins, PACK = packing station):")
            st.markdown(draw_map(highlight=stops, route=route), unsafe_allow_html=True)
        with col2:
            st.metric("Optimized distance", f"{dist} steps")
            st.metric("Unoptimized distance", f"{naive_dist} steps")
            st.metric("Steps saved", f"{saved} steps")
        st.markdown("### Step-by-step guidance")
        for i, b in enumerate(picks, 1):
            row = products[products["Product"] == b].iloc[0]
            st.write(f"**{i}.** Walk to bin **{row['Bin']}** → pick **{row['Product']}** (Qty needed: 1)")
        st.write(f"**{len(picks)+1}.** Return to **packing station** 
    else:
        st.info("Select at least one product to generate a route.")
")
# ==================================================================
# PAGE 4: QR VERIFY
# ==================================================================
elif page == " QR Verify":
    st.title(" QR Bin Verification")
    st.caption("Before picking, the worker scans the bin QR to confirm the right product.")
    product = st.selectbox("Product the worker is picking", products["Product"].tolist())
    correct_bin = products[products["Product"] == product].iloc[0]["Bin"]
    scanned = st.text_input("Scanned bin QR code (try the correct one or a wrong one)", "")
    if st.button("Verify"):
        if scanned.strip().upper() == correct_bin:
            st.success(f" Correct! {product} belongs in {correct_bin}. Pick confirmed.")
        elif scanned.strip() == "":
            st.warning("Please scan / enter a bin code.")
        else:
            st.error(f" Wrong bin! You scanned {scanned.upper()}, but {product} is in {correct_bin}.")
    st.info(f" Hint for the demo: the correct bin for **{product}** is **{correct_bin}**.")
# ==================================================================
# PAGE 5: MANAGER DASHBOARD
# ==================================================================
elif page == " Manager Dashboard":
    st.title(" Manager Dashboard")
    st.caption("Real-time visibility into inventory and operations.")
    total_skus = len(products)
    total_units = int(products["Qty"].sum())
    low_stock = products[products["Qty"] < LOW_STOCK_THRESHOLD]
    c1, c2, c3 = st.columns(3)
    c1.metric("Total SKUs", total_skus)
    c2.metric("Total Units in Stock", total_units)
    c3.metric("Low-Stock Items", len(low_stock))
    st.markdown("###  Stock by Product")
    st.bar_chart(products.set_index("Product")["Qty"])
    if not low_stock.empty:
        st.markdown("###  Low-Stock Alerts")
        st.dataframe(low_stock[["SKU", "Product", "Bin", "Qty"]],
                     use_container_width=True, hide_index=True)
    else:
        st.success("All products above the low-stock threshold.")
    st.markdown("###  Simulated Employee Performance")
    perf = pd.DataFrame({
        "Employee": ["Asha", "Ravi", "Meena", "Karthik"],
        "Orders Completed": [random.randint(20, 40) for _ in range(4)],
        "Picking Accuracy %": [random.randint(92, 99) for _ in range(4)],
        "Avg Pick Time (s)": [random.randint(40, 70) for _ in range(4)],
    })
    st.dataframe(perf, use_container_width=True, hide_index=True)
# ==================================================================
# PAGE 6: ADD PRODUCT
# ==================================================================
elif page == " Add Product":
    st.title(" Add / Map a New Product")
    st.caption("Managers can map a product to a bin location.")
    sku = st.text_input("SKU", "SKU-1009")
    name = st.text_input("Product name", "")
    binc = st.text_input("Bin code", "B-99")
    row = st.number_input("Row (0–5)", 0, GRID_ROWS - 1, 2)
    col = st.number_input("Column (0–7)", 0, GRID_COLS - 1, 4)
    qty = st.number_input("Quantity", 0, 1000, 20)
    if st.button("Add product"):
        if name.strip() == "":
            st.warning("Please enter a product name.")
        else:
            new = pd.DataFrame([{
                "SKU": sku, "Product": name, "Bin": binc,
                "Row": int(row), "Col": int(col), "Qty": int(qty)
            }])
            st.session_state.products = pd.concat([products, new], ignore_index=True)
            st.success(f"Added {name} to bin {binc}. Go to Product Search to find it!")