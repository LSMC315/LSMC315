import streamlit as st
import sqlite3
from datetime import date

# ==========================================
# 1. DATABASE & SQL INITIALIZATION
# ==========================================
def init_db():
    conn = sqlite3.connect("outreach.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS outings (
            outing_id INTEGER PRIMARY KEY AUTOINCREMENT,
            outing_date TEXT NOT NULL,
            leader_name TEXT NOT NULL,
            location_name TEXT NOT NULL,
            supply_item TEXT NOT NULL,
            quantity_given INTEGER NOT NULL
        )
    """)
    conn.commit()
    conn.close()

init_db()

# ==========================================
# 2. APP USER INTERFACE (Web Form)
# ==========================================
st.set_page_config(page_title="Streams of Love Log", page_icon="🕊️")

st.title("🕊️ Streams of Love - Outreach Log")
st.write("Save field data directly to the church SQL database during community outings.")

with st.form("outreach_entry_form", clear_on_submit=True):
    st.subheader("📋 Log New Distribution")
    outing_date = st.date_input("Outing Date", date.today())
    leader_name = st.text_input("Outing Leader Name", placeholder="e.g., Clark Kent, Izuku Midoriya")
    location_name = st.text_input("Location / Cross Streets", placeholder="e.g., Downtown Overpass, Sector 4 Encampment")
    supply_item = st.selectbox(
        "Supply Item Handed Out",
        ["Hygiene Kits", "Socks", "Bottled Water", "Blankets", "Hot Meals"]
    )
    quantity_given = st.number_input("Quantity Distributed", min_value=1, step=1)
    submit_button = st.form_submit_button("Save Log Entry")

# ==========================================
# 3. DATABASE WRITE OPERATION (SQL INSERT)
# ==========================================
if submit_button:
    if leader_name.strip() and location_name.strip():
        conn = sqlite3.connect("outreach.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO outings (outing_date, leader_name, location_name, supply_item, quantity_given)
            VALUES (?, ?, ?, ?, ?)
        """, (str(outing_date), leader_name, location_name, supply_item, quantity_given))
        conn.commit()
        conn.close()
        st.success(f"🎉 Log entry successfully saved for {leader_name}!")
    else:
        st.error("⚠️ Please fill out both the Leader Name and Location fields.")

# ==========================================
# 4. DATABASE READ OPERATION (SQL SELECT)
# ==========================================
st.markdown("---")
st.subheader("📊 Live Historical Database Records")

conn = sqlite3.connect("outreach.db")
cursor = conn.cursor()
cursor.execute("SELECT * FROM outings ORDER BY outing_id DESC")
rows = cursor.fetchall()
conn.close()

if rows:
    for row in rows:
        st.write(f"**Log ID {row[0]}** | 📅 {row[1]} | 👤 **Leader:** {row[2]} | 📍 **Where:** {row[3]} | 📦 **Gave:** {row[5]}x {row[4]}")
else:
    st.info("The database is currently empty. Try submitting your first log above!")

# ==========================================
# 5. LIVE INVENTORY DASHBOARD (SQL SUM & GROUP BY)
# ==========================================
st.markdown("---")
st.subheader("📈 Total Supplies Distributed to Date")
st.write("This dashboard uses a custom SQL aggregation query to calculate real-time totals.")

# 1. CONNECT: Open the communication pipe to your local database file
conn = sqlite3.connect("outreach.db")
cursor = conn.cursor()

# 2. EXECUTE QUERY: Ask SQL to combine matching items and sum their total quantities
cursor.execute("""
    SELECT supply_item, SUM(quantity_given) 
    FROM outings 
    GROUP BY supply_item
    ORDER BY SUM(quantity_given) DESC
""")

# 3. FETCH: Grab all the calculated summary rows out of the database memory
summary_rows = cursor.fetchall()

# 4. CLOSE: Close the connection pipe safely so the file doesn't lock up
conn.close()

# 5. DISPLAY: Check if any data exists to build the visual cards
if summary_rows:
    # Dynamically split the web page layout into equal side-by-side columns
    cols = st.columns(len(summary_rows))
    
    # Loop through each calculated database item summary row one-by-one
    for index, row in enumerate(summary_rows):
        item_name = row[0]   # Grabs the supply item text name
        total_given = row[1] # Grabs the calculated mathematical sum total
        
        # Step into the correct column and draw a beautiful summary metric card
        with cols[index]:
            st.metric(label=item_name, value=f"{total_given} units")
else:
    # If the database is completely blank, show a blue info box instead
    st.info("No distribution totals to calculate yet. Start logging outings to see metrics!")
