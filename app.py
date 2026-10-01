
import streamlit as st
from datetime import datetime
import io
st.image("TRASUA.jpg")

# =========================================================
# CẤU HÌNH TRANG
# =========================================================

st.set_page_config(
    page_title="Tính Bill Trà Sữa",
    page_icon="🧋",
    layout="centered"
)


# =========================================================
# CSS GIAO DIỆN
# =========================================================

st.markdown("""
<style>

.main-title {
    text-align: center;
    font-size: 35px;
    font-weight: bold;
    margin-bottom: 5px;
}

.sub-title {
    text-align: center;
    color: gray;
    margin-bottom: 25px;
}

.total-box {
    padding: 18px;
    border-radius: 12px;
    background-color: #f0f2f6;
    text-align: center;
    margin-top: 20px;
    margin-bottom: 20px;
}

.total-money {
    font-size: 30px;
    font-weight: bold;
}

.bill-box {
    border: 1px solid #dddddd;
    border-radius: 10px;
    padding: 15px;
    margin-top: 10px;
}

</style>
""", unsafe_allow_html=True)


# =========================================================
# DỮ LIỆU MENU
# =========================================================

MENU = {
    "Trà sữa truyền thống": 30000,
    "Trà sữa matcha": 35000,
    "Trà sữa socola": 35000,
    "Trà sữa khoai môn": 35000,
    "Trà sữa dâu": 35000,
    "Trà sữa thái xanh": 30000,
    "Trà sữa thái đỏ": 30000,
    "Trà đào": 30000,
    "Trà vải": 30000,
    "Trà chanh": 25000,
}


# Giá topping
TOPPINGS = {
    "Không topping": 0,
    "Trân châu đen": 5000,
    "Trân châu trắng": 5000,
    "Thạch trái cây": 5000,
    "Pudding trứng": 7000,
    "Thạch phô mai": 7000,
    "Kem cheese": 10000,
}


# =========================================================
# KHỞI TẠO SESSION STATE
# =========================================================

if "cart" not in st.session_state:
    st.session_state.cart = []


# =========================================================
# TIÊU ĐỀ
# =========================================================

st.markdown(
    '<div class="main-title"> ☕ QUÁN TRÀ SỮA</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title"> APP TÍNH BILL HÓA ĐƠN TRÀ SỮA</div>',
    unsafe_allow_html=True
)


# =========================================================
# THÔNG TIN KHÁCH HÀNG
# =========================================================

st.subheader("👤 Thông tin khách hàng")

customer_name = st.text_input(
    "Tên khách hàng",
    placeholder="Nhập tên khách hàng..."
)


# =========================================================
# CHỌN MÓN
# =========================================================

st.subheader("🧋 Chọn món")

col1, col2 = st.columns(2)

with col1:

    drink = st.selectbox(
        "Loại trà sữa / đồ uống",
        list(MENU.keys())
    )

    quantity = st.number_input(
        "Số lượng",
        min_value=1,
        max_value=20,
        value=1,
        step=1
    )

    sugar = st.selectbox(
        "Mức độ đường",
        ["100%", "70%", "0%"]
    )


with col2:

    topping = st.selectbox(
        "Topping",
        list(TOPPINGS.keys())
    )

    ice = st.selectbox(
        "Mức độ đá",
        ["100%", "70%", "0%"]
    )


# =========================================================
# TÍNH TIỀN MÓN HIỆN TẠI
# =========================================================

drink_price = MENU[drink]
topping_price = TOPPINGS[topping]

unit_price = drink_price + topping_price
item_total = unit_price * quantity


st.markdown("### 💰 Thông tin món")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Giá đồ uống",
        f"{drink_price:,} VNĐ"
    )

with col2:
    st.metric(
        "Giá topping",
        f"{topping_price:,} VNĐ"
    )

with col3:
    st.metric(
        "Thành tiền",
        f"{item_total:,} VNĐ"
    )


# =========================================================
# NÚT THÊM VÀO HÓA ĐƠN
# =========================================================

if st.button(
    "➕ THÊM MÓN VÀO HÓA ĐƠN",
    use_container_width=True
):

    if not customer_name.strip():
        st.warning("⚠️ Vui lòng nhập tên khách hàng.")

    else:

        item = {
            "drink": drink,
            "quantity": quantity,
            "topping": topping,
            "sugar": sugar,
            "ice": ice,
            "drink_price": drink_price,
            "topping_price": topping_price,
            "unit_price": unit_price,
            "total": item_total
        }

        st.session_state.cart.append(item)

        st.success(
            f"✅ Đã thêm {quantity} ly {drink} vào hóa đơn."
        )


# =========================================================
# HIỂN THỊ HÓA ĐƠN
# =========================================================

st.divider()

st.subheader("🧾 HÓA ĐƠN HIỆN TẠI")


if len(st.session_state.cart) == 0:

    st.info(
        "Chưa có món nào trong hóa đơn. "
        "Hãy chọn món và bấm 'THÊM MÓN VÀO HÓA ĐƠN'."
    )

else:

    total_bill = 0

    for index, item in enumerate(st.session_state.cart):

        total_bill += item["total"]

        st.markdown(
            f"""
            <div class="bill-box">

            <b>{index + 1}. {item['drink']}</b>

            <br>
            Số lượng: {item['quantity']} ly

            <br>
            Topping: {item['topping']}

            <br>
            Đường: {item['sugar']}

            <br>
            Đá: {item['ice']}

            <br>
            Đơn giá: {item['unit_price']:,} VNĐ

            <br>
            <b>Thành tiền: {item['total']:,} VNĐ</b>

            </div>
            """,
            unsafe_allow_html=True
        )


    # =====================================================
    # TỔNG TIỀN
    # =====================================================

    st.markdown(
        f"""
        <div class="total-box">

        <div>TỔNG TIỀN THANH TOÁN</div>

        <div class="total-money">
        {total_bill:,} VNĐ
        </div>

        </div>
        """,
        unsafe_allow_html=True
    )


    # =====================================================
    # NÚT XÓA HÓA ĐƠN
    # =====================================================

    col1, col2 = st.columns(2)

    with col1:

        if st.button(
            "🗑️ XÓA HÓA ĐƠN",
            use_container_width=True
        ):

            st.session_state.cart = []

            st.rerun()


    # =====================================================
    # THANH TOÁN
    # =====================================================

    with col2:

        if st.button(
            "💳 THANH TOÁN & XUẤT HÓA ĐƠN",
            use_container_width=True
        ):

            # Thời gian thanh toán
            payment_time = datetime.now()

            # Tạo nội dung hóa đơn
            bill_text = ""

            bill_text += "========================================\n"
            bill_text += "             QUÁN TRÀ SỮA\n"
            bill_text += "          HÓA ĐƠN THANH TOÁN\n"
            bill_text += "========================================\n\n"

            bill_text += f"Khách hàng: {customer_name}\n"

            bill_text += (
                f"Thời gian: "
                f"{payment_time.strftime('%d/%m/%Y %H:%M:%S')}\n"
            )

            bill_text += "\n"
            bill_text += "----------------------------------------\n"

            for index, item in enumerate(st.session_state.cart):

                bill_text += (
                    f"{index + 1}. {item['drink']}\n"
                )

                bill_text += (
                    f"   Số lượng: {item['quantity']} ly\n"
                )

                bill_text += (
                    f"   Topping: {item['topping']}\n"
                )

                bill_text += (
                    f"   Đường: {item['sugar']}\n"
                )

                bill_text += (
                    f"   Đá: {item['ice']}\n"
                )

                bill_text += (
                    f"   Đơn giá: {item['unit_price']:,} VNĐ\n"
                )

                bill_text += (
                    f"   Thành tiền: {item['total']:,} VNĐ\n"
                )

                bill_text += (
                    "----------------------------------------\n"
                )


            bill_text += "\n"

            bill_text += (
                f"TỔNG THANH TOÁN: {total_bill:,} VNĐ\n"
            )

            bill_text += "\n"

            bill_text += "Cảm ơn quý khách đã sử dụng dịch vụ!\n"

            bill_text += "Hẹn gặp lại quý khách!\n"

            bill_text += "\n"
            bill_text += "========================================\n"


            # =================================================
            # THÔNG BÁO THANH TOÁN
            # =================================================

            st.success(
                f"✅ THANH TOÁN THÀNH CÔNG! "
                f"Tổng tiền: {total_bill:,} VNĐ"
            )


            # =================================================
            # TẠO FILE HÓA ĐƠN
            # =================================================

            file_data = io.BytesIO(
                bill_text.encode("utf-8")
            )

            filename = (
                "hoa_don_"
                + payment_time.strftime("%Y%m%d_%H%M%S")
                + ".txt"
            )


            st.download_button(
                label="📥 TẢI HÓA ĐƠN",
                data=file_data,
                file_name=filename,
                mime="text/plain",
                use_container_width=True
            )

