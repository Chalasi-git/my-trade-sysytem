import streamlit as st
from datetime import datetime

# -----------------------------
# 1. Data Models
# -----------------------------

class Product:
    def __init__(self, name, certs, price, qty, producer):
        self.name = name
        self.certs = certs
        self.price = price
        self.qty = qty
        self.producer = producer


class Review:
    def __init__(self, producer_email, trader_email, rating, comment):
        self.producer_email = producer_email
        self.trader_email = trader_email
        self.rating = rating
        self.comment = comment
        self.date = datetime.now().strftime("%Y-%m-%d")


# -----------------------------
# 2. Dashboard Logic
# -----------------------------

class Dashboard:

    # ---------------- LOGOUT ----------------
    def logout(self):
        st.session_state.logged_in = False
        st.session_state.email = None
        st.session_state.role = None
        st.session_state.page = "login"
        st.rerun()

    # ---------------- LOGIN ----------------
    def login_page(self):

        st.title("Export Gateway")

        email = st.text_input("Email Address")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Select Role", ["Producer", "Trader"])

        if st.button("Login"):

            for user in st.session_state.users:

                if (
                    user["email"] == email
                    and user["password"] == password
                    and user["role"] == role
                ):

                    st.session_state.logged_in = True
                    st.session_state.email = email
                    st.session_state.role = role

                    if role == "Trader":
                        st.session_state.page = "catalogue"
                    else:
                        st.session_state.page = "dashboard"

                    st.rerun()

            st.error("Invalid credentials")

        if st.button("Register"):
            st.session_state.page = "register"
            st.rerun()

    # ---------------- REGISTER ----------------
    def register_page(self):

        st.title("Create Account")

        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        role = st.selectbox("Role", ["Producer", "Trader"])

        if st.button("Register"):

            st.session_state.users.append(
                {
                    "email": email,
                    "password": password,
                    "role": role,
                }
            )

            st.success("Account created successfully!")
            st.session_state.page = "login"
            st.rerun()

    # ---------------- PRODUCER DASHBOARD ----------------
    def producer_dashboard(self):

        col1, col2 = st.columns([6,1])

        with col1:
            st.title("Producer Dashboard")

        with col2:
            if st.button("Logout"):
                self.logout()

        tab1, tab2 = st.tabs(["Add Product", "Export Assistant"])

        # -------- ADD PRODUCT --------
        with tab1:

            name = st.text_input("Product Name")

            certs = st.multiselect(
                "Certifications",
                ["SLS", "ISO 22000", "HACCP", "GMP", "Organic"],
            )

            price = st.number_input("Price ($)", min_value=0.0)
            qty = st.number_input("Quantity (kg)", min_value=0)

            if st.button("Save Product"):

                if name:

                    new_prod = Product(
                        name,
                        ", ".join(certs),
                        price,
                        qty,
                        st.session_state.email,
                    )

                    st.session_state.products.append(new_prod)

                    st.success("Product saved successfully!")

                else:
                    st.error("Please enter product name.")

        # -------- AI ASSISTANT --------
        with tab2:

            st.subheader("Export Guide")

            query = st.text_input("Ask about export requirements")

            if query:

                q = query.lower()

                if "tea" in q:
                    st.info(
                        "Tea export requires registration with Sri Lanka Tea Board."
                    )

                elif "document" in q:
                    st.write(
                        "Required documents:\n"
                        "1. CusDec\n"
                        "2. TIN\n"
                        "3. Certificate of Origin"
                    )

                else:
                    st.write("Ask me about export procedures.")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("View Catalogue"):
                st.session_state.page = "catalogue"
                st.rerun()

        with col2:
            if st.button("Search Products"):
                st.session_state.page = "search"
                st.rerun()

    # ---------------- PRODUCT CATALOGUE ----------------
    def product_catalogue(self):

        col1, col2 = st.columns([6,1])

        with col1:
            st.title("Product Catalogue")

        with col2:
            if st.button("Logout"):
                self.logout()

        if not st.session_state.products:
            st.warning("No products available.")

        else:

            for p in st.session_state.products:

                with st.container():

                    col1, col2 = st.columns([3,1])

                    with col1:
                        st.subheader(p.name)
                        st.write(f"Producer: {p.producer}")
                        st.write(f"Price: ${p.price}")
                        st.write(f"Certifications: {p.certs}")

                    with col2:
                        avg = self.get_avg_rating(p.producer)
                        st.metric("Rating", f"{avg} ⭐")

                    with st.expander("Reviews"):

                        if st.session_state.role == "Trader":

                            with st.form(f"review_{p.producer}"):

                                r_rate = st.slider("Rating", 1, 5, 5)
                                r_comm = st.text_area("Comment")

                                if st.form_submit_button("Submit"):

                                    st.session_state.reviews.append(
                                        Review(
                                            p.producer,
                                            st.session_state.email,
                                            r_rate,
                                            r_comm,
                                        )
                                    )

                                    st.rerun()

                        revs = [
                            r
                            for r in st.session_state.reviews
                            if r.producer_email == p.producer
                        ]

                        for r in revs:
                            st.write(f"{r.rating}⭐ - {r.comment}")

                    st.divider()

        if st.button("Search Products"):
            st.session_state.page = "search"
            st.rerun()

    # ---------------- SEARCH PAGE ----------------
    def search_page(self):

        col1, col2 = st.columns([6,1])

        with col1:
            st.title("Search Products")

        with col2:
            if st.button("Logout"):
                self.logout()

        search = st.text_input("Enter product name").lower()

        if search:

            results = [
                p for p in st.session_state.products
                if search in p.name.lower()
            ]

            if not results:
                st.warning("No matching products found.")

            else:

                for p in results:

                    st.subheader(p.name)
                    st.write(f"Producer: {p.producer}")
                    st.write(f"Price: ${p.price}")
                    st.write(f"Certifications: {p.certs}")
                    st.divider()

        if st.button("Back to Catalogue"):
            st.session_state.page = "catalogue"
            st.rerun()

    # ---------------- RATING ----------------
    def get_avg_rating(self, email):

        ratings = [
            r.rating
            for r in st.session_state.reviews
            if r.producer_email == email
        ]

        return round(sum(ratings) / len(ratings), 1) if ratings else "N/A"


# -----------------------------
# 3. Session Initializer
# -----------------------------

if "users" not in st.session_state:
    st.session_state.users = []

if "products" not in st.session_state:
    st.session_state.products = []

if "reviews" not in st.session_state:
    st.session_state.reviews = []

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "page" not in st.session_state:
    st.session_state.page = "login"

db = Dashboard()

# -----------------------------
# 4. Routing
# -----------------------------

if not st.session_state.logged_in:

    if st.session_state.page == "login":
        db.login_page()

    elif st.session_state.page == "register":
        db.register_page()

else:

    if st.session_state.page == "dashboard":
        db.producer_dashboard()

    elif st.session_state.page == "catalogue":
        db.product_catalogue()

    elif st.session_state.page == "search":
        db.search_page()