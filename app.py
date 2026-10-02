import streamlit as st
from datetime import datetime
st.image("TRASUA.jpg")
# ============================================================
# CẤU HÌNH TRANG
# ============================================================

st.set_page_config(
    page_title="Hóa đơn Trà Sữa",
    page_icon="🧋",
    layout="wide"
)

# ============================================================
# CSS GIAO DIỆN
# ============================================================

st.markdown("""
<style>

    .main-title {
        text-align: center;
        font-size: 40px;
        font-weight: bold;
        margin-bottom: 5px;
    }

    .sub-title {
        text-align: center;
        color: #666;
        font-size: 18px;
        margin-bottom: 30px;
    }

    .total-box {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 12px;
        border: 2px solid #ddd;
        text-align: center;
        margin-top: 20px;
    }

    .total-money {
        font-size: 32px;
        font-weight: bold;
    }

    .bill-box {
        background-color: white;
        padding: 25px;
        border-radius: 12px;
        border: 1px solid #ddd;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.08);
    }

    .bill-title {
        text-align: center;
        font-size: 28px;
        font-weight: bold;
    }

    .bill-center {
        text-align: center;
    }

    .item-row {
        padding: 8px 0;
        border-bottom: 1px solid #eee;
    }

    .footer {
        text-align: center;
        color: #777;
        margin-top: 30px;
    }

</style>
""", unsafe_allow_html=True)


# ============================================================
# DANH SÁCH SẢN PHẨM
# ============================================================

MENU = {
    "Trà sữa truyền thống": 30000,
    "Trà sữa trân châu": 35000,
    "Trà sữa matcha": 38000,
    "Trà sữa socola": 38000,
    "Trà sữa khoai môn": 40000,
    "Trà sữa dâu": 38000,
    "Trà đào": 32000,
    "Trà vải": 32000,
    "Trà chanh": 25000,
    "Trà xoài": 32000
}

TOPPINGS = {
    "Trân châu đen": 5000,
    "Trân châu trắng": 6000,
    "Thạch rau câu": 5000,
    "Thạch dừa": 5000,
    "Pudding trứng": 7000,
    "Kem cheese": 10000,
    "Đậu đỏ": 6000,
    "Khoai môn": 7000
}

SIZE_PRICE = {
    "S": 0,
    "M": 5000,
    "L": 10000
}


# ============================================================
# KHỞI TẠO SESSION STATE
# ============================================================

if "cart" not in st.session_state:
    st.session_state.cart = []

if "payment_done" not in st.session_state:
    st.session_state.payment_done = False


# ============================================================
# TIÊU ĐỀ
# ============================================================

st.markdown(
    '<div class="main-title">🧋 TRÀ SỮA - HÓA ĐƠN</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">Hệ thống tính hóa đơn quán trà sữa</div>',
    unsafe_allow_html=True
)


# ============================================================
# THÔNG TIN KHÁCH HÀNG
# ============================================================

st.subheader("👤 Thông tin khách hàng")

customer_name = st.text_input(
    "Tên khách hàng",
    placeholder="Nhập tên khách hàng..."
)


# ============================================================
# NHẬP MÓN
# ============================================================

st.subheader("🧋 Chọn món")

col1, col2 = st.columns(2)

with col1:

    product = st.selectbox(
        "Loại trà sữa / đồ uống",
        list(MENU.keys())
    )

    size = st.selectbox(
        "Size ly",
        ["S", "M", "L"]
    )

    quantity = st.number_input(
        "Số lượng",
        min_value=1,
        max_value=50,
        value=1,
        step=1
    )

with col2:

    sugar = st.selectbox(
        "Mức độ đường",
        [
            "100% đường",
            "70% đường",
            "50% đường",
            "30% đường",
            "0% đường"
        ]
    )

    ice = st.selectbox(
        "Mức độ đá",
        [
            "100% đá",
            "70% đá",
            "50% đá",
            "30% đá",
            "Không đá"
        ]
    )

    toppings = st.multiselect(
        "Topping",
        list(TOPPINGS.keys())
    )


# ============================================================
# TÍNH GIÁ MÓN HIỆN TẠI
# ============================================================

base_price = MENU[product]

size_price = SIZE_PRICE[size]

topping_price = sum(
    TOPPINGS[topping]
    for topping in toppings
)

unit_price = base_price + size_price + topping_price

item_total = unit_price * quantity


# ============================================================
# HIỂN THỊ GIÁ
# ============================================================

st.markdown("### 💰 Giá món")

price_col1, price_col2, price_col3, price_col4 = st.columns(4)

with price_col1:
    st.metric(
        "Giá cơ bản",
        f"{base_price:,} đ"
    )

with price_col2:
    st.metric(
        f"Size {size}",
        f"+{size_price:,} đ"
    )

with price_col3:
    st.metric(
        "Topping",
        f"+{topping_price:,} đ"
    )

with price_col4:
    st.metric(
        "Thành tiền",
        f"{item_total:,} đ"
    )


# ============================================================
# NÚT THÊM MÓN
# ============================================================

if st.button(
    "➕ Thêm món",
    use_container_width=True
):

    if not customer_name.strip():
        st.warning("⚠️ Vui lòng nhập tên khách hàng trước.")

    else:

        new_item = {
            "product": product,
            "size": size,
            "quantity": quantity,
            "sugar": sugar,
            "ice": ice,
            "toppings": toppings.copy(),
            "unit_price": unit_price,
            "total": item_total
        }

        st.session_state.cart.append(new_item)

        st.session_state.payment_done = False

        st.success(
            f"✅ Đã thêm {quantity} ly {product} vào hóa đơn."
        )


# ============================================================
# HIỂN THỊ GIỎ HÀNG
# ============================================================

st.divider()

st.subheader("🛒 Danh sách món đã chọn")

if len(st.session_state.cart) == 0:

    st.info(
        "Chưa có món nào trong hóa đơn. "
        "Hãy chọn món và nhấn 'Thêm món'."
    )

else:

    grand_total = 0

    for i, item in enumerate(st.session_state.cart):

        grand_total += item["total"]

        with st.container(border=True):

            col_a, col_b, col_c, col_d = st.columns(
                [3, 1, 2, 1]
            )

            with col_a:

                st.markdown(
                    f"**{i + 1}. {item['product']}**"
                )

                topping_text = ", ".join(
                    item["toppings"]
                )

                if not topping_text:
                    topping_text = "Không topping"

                st.caption(
                    f"Size: {item['size']} | "
                    f"Đường: {item['sugar']} | "
                    f"Đá: {item['ice']}"
                )

                st.caption(
                    f"Topping: {topping_text}"
                )

            with col_b:

                st.write(
                    f"SL: **{item['quantity']}**"
                )

            with col_c:

                st.write(
                    f"{item['unit_price']:,} đ/ly"
                )

            with col_d:

                st.write(
                    f"**{item['total']:,} đ**"
                )

                if st.button(
                    "🗑️ Xóa",
                    key=f"delete_{i}"
                ):

                    st.session_state.cart.pop(i)

                    st.rerun()


    # ========================================================
    # TỔNG TIỀN
    # ========================================================

    st.markdown(
        f"""
        <div class="total-box">
            <div>TỔNG THANH TOÁN</div>
            <div class="total-money">
                {grand_total:,} VNĐ
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


    # ========================================================
    # NÚT XÓA TOÀN BỘ
    # ========================================================

    col_clear, col_payment = st.columns(2)

    with col_clear:

        if st.button(
            "🗑️ Xóa toàn bộ hóa đơn",
            use_container_width=True
        ):

            st.session_state.cart = []

            st.session_state.payment_done = False

            st.rerun()


    # ========================================================
    # THANH TOÁN
    # ========================================================

    with col_payment:

        if st.button(
            "💳 THANH TOÁN",
            type="primary",
            use_container_width=True
        ):

            st.session_state.payment_done = True

            st.rerun()


# ============================================================
# HÓA ĐƠN SAU KHI THANH TOÁN
# ============================================================

if (
    st.session_state.payment_done
    and len(st.session_state.cart) > 0
):

    st.divider()

    st.subheader("🧾 HÓA ĐƠN THANH TOÁN")

    now = datetime.now()

    bill_time = now.strftime(
        "%d/%m/%Y %H:%M:%S"
    )

    grand_total = sum(
        item["total"]
        for item in st.session_state.cart
    )

    # --------------------------------------------------------
    # TẠO NỘI DUNG HÓA ĐƠN
    # --------------------------------------------------------

    bill_html = f"""
    <div class="bill-box">

        <div class="bill-title">
            🧋 QUÁN TRÀ SỮA
        </div>

        <div class="bill-center">
            <p>HÓA ĐƠN THANH TOÁN</p>
        </div>

        <hr>

        <p>
            <b>Khách hàng:</b> {customer_name}
        </p>

        <p>
            <b>Thời gian:</b> {bill_time}
        </p>

        <hr>
    """

    for i, item in enumerate(
        st.session_state.cart
    ):

        topping_text = ", ".join(
            item["toppings"]
        )

        if not topping_text:
            topping_text = "Không topping"

        bill_html += f"""
        <div class="item-row">

            <b>
                {i + 1}. {item['product']}
            </b>

            <br>

            Size: {item['size']}
            &nbsp; | &nbsp;
            SL: {item['quantity']}

            <br>

            Đường: {item['sugar']}
            &nbsp; | &nbsp;
            Đá: {item['ice']}

            <br>

            Topping: {topping_text}

            <br>

            Đơn giá:
            {item['unit_price']:,} đ

            <br>

            <b>
                Thành tiền:
                {item['total']:,} đ
            </b>

        </div>
        """

    bill_html += f"""

        <hr>

        <div style="text-align:right;">
            <h2>
                TỔNG CỘNG:
                {grand_total:,} VNĐ
            </h2>
        </div>

        <hr>

        <div class="bill-center">
            <b>Cảm ơn quý khách!</b>
            <br>
            Hẹn gặp lại quý khách lần sau ❤️
        </div>

    </div>
    """

    st.markdown(
        bill_html,
        unsafe_allow_html=True
    )


    # ========================================================
    # NỘI DUNG TEXT ĐỂ IN / TẢI HÓA ĐƠN
    # ========================================================

    bill_text = ""

    bill_text += "================================\n"
    bill_text += "          QUÁN TRÀ SỮA\n"
    bill_text += "        HÓA ĐƠN THANH TOÁN\n"
    bill_text += "================================\n"

    bill_text += f"Khách hàng: {customer_name}\n"
    bill_text += f"Thời gian: {bill_time}\n"

    bill_text += "--------------------------------\n"

    for i, item in enumerate(
        st.session_state.cart
    ):

        topping_text = ", ".join(
            item["toppings"]
        )

        if not topping_text:
            topping_text = "Không topping"

        bill_text += (
            f"{i + 1}. {item['product']}\n"
        )

        bill_text += (
            f"   Size: {item['size']}\n"
        )

        bill_text += (
            f"   SL: {item['quantity']}\n"
        )

        bill_text += (
            f"   Đường: {item['sugar']}\n"
        )

        bill_text += (
            f"   Đá: {item['ice']}\n"
        )

        bill_text += (
            f"   Topping: {topping_text}\n"
        )

        bill_text += (
            f"   Đơn giá: "
            f"{item['unit_price']:,} VNĐ\n"
        )

        bill_text += (
            f"   Thành tiền: "
            f"{item['total']:,} VNĐ\n"
        )

        bill_text += "--------------------------------\n"

    bill_text += (
        f"TỔNG THANH TOÁN: "
        f"{grand_total:,} VNĐ\n"
    )

    bill_text += "================================\n"
    bill_text += "       CẢM ƠN QUÝ KHÁCH!\n"
    bill_text += "================================\n"


    # ========================================================
    # NÚT TẢI HÓA ĐƠN
    # ========================================================

    st.download_button(
        label="🖨️ Tải hóa đơn",
        data=bill_text,
        file_name=(
            f"hoa_don_"
            f"{now.strftime('%Y%m%d_%H%M%S')}.txt"
        ),
        mime="text/plain",
        use_container_width=True
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        🧋 Hệ thống quản lý hóa đơn trà sữa
    </div>
    """,
    unsafe_allow_html=True
)
