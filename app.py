import streamlit as st
from datetime import datetime


# ============================================================
# CẤU HÌNH TRANG
# ============================================================

st.set_page_config(
    page_title="Hóa đơn Trà Sữa",
    page_icon="🧋",
    layout="wide"
)


# ============================================================
# CSS
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
# LOGO
# ============================================================

try:
    st.image("TRASUA.jpg", use_container_width=True)
except:
    pass


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


# ============================================================
# TOPPING
# ============================================================

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


# ============================================================
# GIÁ SIZE
# ============================================================

SIZE_PRICE = {
    "S": 0,
    "M": 5000,
    "L": 10000
}


# ============================================================
# LUẬT CHATBOT
# ============================================================

# ------------------------------------------------------------
# Gợi ý topping cho từng loại đồ uống
# ------------------------------------------------------------

TOPPING_RECOMMENDATIONS = {

    "Trà sữa truyền thống": [
        "Trân châu đen",
        "Trân châu trắng",
        "Pudding trứng"
    ],

    "Trà sữa trân châu": [
        "Trân châu đen",
        "Trân châu trắng",
        "Pudding trứng"
    ],

    "Trà sữa matcha": [
        "Trân châu trắng",
        "Pudding trứng",
        "Kem cheese"
    ],

    "Trà sữa socola": [
        "Pudding trứng",
        "Kem cheese",
        "Trân châu đen"
    ],

    "Trà sữa khoai môn": [
        "Khoai môn",
        "Trân châu trắng",
        "Pudding trứng"
    ],

    "Trà sữa dâu": [
        "Trân châu trắng",
        "Thạch dừa",
        "Kem cheese"
    ],

    "Trà đào": [
        "Thạch dừa",
        "Thạch rau câu"
    ],

    "Trà vải": [
        "Thạch dừa",
        "Thạch rau câu"
    ],

    "Trà chanh": [
        "Thạch rau câu",
        "Thạch dừa"
    ],

    "Trà xoài": [
        "Thạch dừa",
        "Thạch rau câu"
    ]
}


# ------------------------------------------------------------
# Phân loại độ ngọt theo luật
#
# Đây là quy ước của chatbot, không phải dữ liệu dinh dưỡng.
# ------------------------------------------------------------

SWEET_DRINKS = [
    "Trà sữa socola",
    "Trà sữa khoai môn",
    "Trà sữa dâu"
]

MEDIUM_SWEET_DRINKS = [
    "Trà sữa truyền thống",
    "Trà sữa trân châu",
    "Trà sữa matcha"
]

LIGHT_DRINKS = [
    "Trà đào",
    "Trà vải",
    "Trà chanh",
    "Trà xoài"
]


# ============================================================
# HÀM ĐỊNH DẠNG TIỀN
# ============================================================

def format_money(value):
    return f"{value:,} VNĐ"


# ============================================================
# HÀM CHATBOT RULE-BASED
# ============================================================

def chatbot_answer(question):

    q = question.lower().strip()

    # --------------------------------------------------------
    # CHÀO HỎI
    # --------------------------------------------------------

    if any(word in q for word in [
        "xin chào",
        "chào",
        "hello",
        "hi"
    ]):

        return (
            "Xin chào 👋 Tôi là chatbot của quán trà sữa. "
            "Bạn có thể hỏi tôi về giá trà sữa, topping, "
            "size hoặc gợi ý topping."
        )


    # --------------------------------------------------------
    # CẢM ƠN
    # --------------------------------------------------------

    if "cảm ơn" in q or "thanks" in q:

        return "Không có gì ạ 🧋 Chúc bạn uống trà sữa thật ngon!"


    # --------------------------------------------------------
    # GIÁ CAO NHẤT
    # --------------------------------------------------------

    if (
        "cao nhất" in q
        or "đắt nhất" in q
        or "mắc nhất" in q
    ):

        max_price = max(MENU.values())

        products = [
            name
            for name, price in MENU.items()
            if price == max_price
        ]

        product_text = ", ".join(products)

        return (
            f"💰 Loại có giá cao nhất là "
            f"{product_text}, giá {format_money(max_price)}."
        )


    # --------------------------------------------------------
    # GIÁ THẤP NHẤT
    # --------------------------------------------------------

    if (
        "thấp nhất" in q
        or "rẻ nhất" in q
        or "giá thấp" in q
    ):

        min_price = min(MENU.values())

        products = [
            name
            for name, price in MENU.items()
            if price == min_price
        ]

        product_text = ", ".join(products)

        return (
            f"💰 Loại có giá thấp nhất là "
            f"{product_text}, giá {format_money(min_price)}."
        )


    # --------------------------------------------------------
    # TOPPING ĐẮT NHẤT
    # --------------------------------------------------------

    if (
        "topping" in q
        and (
            "đắt nhất" in q
            or "cao nhất" in q
            or "mắc nhất" in q
        )
    ):

        max_price = max(TOPPINGS.values())

        toppings = [
            name
            for name, price in TOPPINGS.items()
            if price == max_price
        ]

        return (
            f"🍮 Topping có giá cao nhất là "
            f"{', '.join(toppings)}, "
            f"giá {format_money(max_price)}."
        )


    # --------------------------------------------------------
    # TOPPING RẺ NHẤT
    # --------------------------------------------------------

    if (
        "topping" in q
        and (
            "rẻ nhất" in q
            or "thấp nhất" in q
        )
    ):

        min_price = min(TOPPINGS.values())

        toppings = [
            name
            for name, price in TOPPINGS.items()
            if price == min_price
        ]

        return (
            f"🍮 Topping có giá thấp nhất là "
            f"{', '.join(toppings)}, "
            f"giá {format_money(min_price)}."
        )


    # --------------------------------------------------------
    # DANH SÁCH TRÀ SỮA
    # --------------------------------------------------------

    if (
        "có những loại" in q
        or "các loại trà sữa" in q
        or "danh sách trà sữa" in q
        or "menu" in q
    ):

        result = "🧋 Quán hiện có các loại đồ uống:\n\n"

        for name, price in MENU.items():

            result += (
                f"• {name}: "
                f"{format_money(price)}\n"
            )

        return result


    # --------------------------------------------------------
    # DANH SÁCH TOPPING
    # --------------------------------------------------------

    if (
        "có những topping" in q
        or "các topping" in q
        or "danh sách topping" in q
    ):

        result = "🍮 Các topping hiện có:\n\n"

        for name, price in TOPPINGS.items():

            result += (
                f"• {name}: "
                f"{format_money(price)}\n"
            )

        return result


    # --------------------------------------------------------
    # GIÁ SIZE
    # --------------------------------------------------------

    if "size" in q:

        return (
            "🥤 Giá size:\n\n"
            "• Size S: không phụ thu\n"
            "• Size M: +5.000 VNĐ\n"
            "• Size L: +10.000 VNĐ"
        )


    # --------------------------------------------------------
    # NGỌT
    # --------------------------------------------------------

    if (
        "ngọt" in q
        or "ngọt nhất" in q
        or "uống ngọt" in q
    ):

        sweet_text = ", ".join(SWEET_DRINKS)

        return (
            "🍫 Theo quy tắc tư vấn của chatbot, "
            f"nhóm đồ uống có vị ngọt nổi bật gồm: "
            f"{sweet_text}.\n\n"
            "Nếu bạn thích ngọt, bạn có thể chọn mức "
            "100% hoặc 70% đường."
        )


    # --------------------------------------------------------
    # KHÔNG THÍCH NGỌT
    # --------------------------------------------------------

    if (
        "không ngọt" in q
        or "ít ngọt" in q
        or "thanh" in q
        or "ít đường" in q
    ):

        light_text = ", ".join(LIGHT_DRINKS)

        return (
            "🍋 Nếu bạn thích vị nhẹ, thanh hơn, "
            f"có thể tham khảo: {light_text}.\n\n"
            "Bạn cũng có thể chọn mức 30% hoặc 0% đường."
        )


    # --------------------------------------------------------
    # TÌM TÊN ĐỒ UỐNG TRONG CÂU HỎI
    # --------------------------------------------------------

    selected_product = None

    for product_name in MENU.keys():

        if product_name.lower() in q:

            selected_product = product_name
            break


    # --------------------------------------------------------
    # HỎI GIÁ MỘT LOẠI ĐỒ UỐNG
    # --------------------------------------------------------

    if selected_product:

        price = MENU[selected_product]

        # Hỏi giá
        if (
            "giá" in q
            or "bao nhiêu" in q
            or "tiền" in q
        ):

            return (
                f"🧋 {selected_product} có giá cơ bản "
                f"{format_money(price)} cho size S.\n\n"
                f"Size M: {format_money(price + SIZE_PRICE['M'])}\n"
                f"Size L: {format_money(price + SIZE_PRICE['L'])}"
            )


        # Hỏi topping
        if (
            "topping" in q
            or "ăn kèm" in q
            or "dùng kèm" in q
            or "hợp với" in q
            or "phù hợp" in q
        ):

            recommendations = TOPPING_RECOMMENDATIONS.get(
                selected_product,
                []
            )

            return (
                f"🧋 Với {selected_product}, "
                f"bạn có thể dùng kèm:\n\n"
                + "\n".join(
                    f"• {x}"
                    for x in recommendations
                )
            )


        # Hỏi vị ngọt
        if (
            "ngọt" in q
            or "vị" in q
        ):

            if selected_product in SWEET_DRINKS:

                return (
                    f"🍫 {selected_product} được chatbot "
                    "xếp vào nhóm vị ngọt nổi bật."
                )

            elif selected_product in MEDIUM_SWEET_DRINKS:

                return (
                    f"🧋 {selected_product} được chatbot "
                    "xếp vào nhóm vị ngọt vừa."
                )

            else:

                return (
                    f"🍋 {selected_product} được chatbot "
                    "xếp vào nhóm vị nhẹ, thanh."
                )


    # --------------------------------------------------------
    # HỎI TOPPING CỦA MỘT SẢN PHẨM
    # --------------------------------------------------------

    for product_name, recommendations in TOPPING_RECOMMENDATIONS.items():

        short_name = product_name.lower().replace(
            "trà sữa ", ""
        )

        if short_name in q:

            return (
                f"🧋 Với {product_name}, "
                f"tôi gợi ý:\n\n"
                + "\n".join(
                    f"• {x}"
                    for x in recommendations
                )
            )


    # --------------------------------------------------------
    # TỔNG QUAN
    # --------------------------------------------------------

    if (
        "bạn làm được gì" in q
        or "hỏi gì" in q
        or "trợ giúp" in q
        or "help" in q
    ):

        return (
            "🤖 Tôi có thể trả lời các câu hỏi như:\n\n"
            "• Loại trà sữa nào giá cao nhất?\n"
            "• Loại nào rẻ nhất?\n"
            "• Trà sữa matcha giá bao nhiêu?\n"
            "• Trà sữa matcha hợp topping nào?\n"
            "• Loại trà sữa nào ngọt?\n"
            "• Topping nào đắt nhất?\n"
            "• Topping nào rẻ nhất?\n"
            "• Size M thêm bao nhiêu?\n"
            "• Quán có những loại trà sữa nào?"
        )


    # --------------------------------------------------------
    # KHÔNG HIỂU
    # --------------------------------------------------------

    return (
        "🤔 Tôi chưa hiểu câu hỏi này.\n\n"
        "Bạn có thể hỏi:\n"
        "• Loại trà sữa nào giá cao nhất?\n"
        "• Loại nào rẻ nhất?\n"
        "• Matcha nên dùng topping gì?\n"
        "• Loại nào ngọt?\n"
        "• Topping nào đắt nhất?\n"
        "• Size L thêm bao nhiêu tiền?"
    )


# ============================================================
# SESSION STATE
# ============================================================

if "cart" not in st.session_state:
    st.session_state.cart = []

if "payment_done" not in st.session_state:
    st.session_state.payment_done = False

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []


# ============================================================
# TIÊU ĐỀ
# ============================================================

st.markdown(
    '<div class="main-title">🧋 TRÀ SỮA - HÓA ĐƠN</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">'
    'Hệ thống tính hóa đơn & chatbot tư vấn trà sữa'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# TẠO 2 TAB
# ============================================================

tab1, tab2 = st.tabs(
    [
        "🧾 TÍNH HÓA ĐƠN",
        "🤖 CHATBOT TƯ VẤN"
    ]
)


# ============================================================
# TAB 1 - TÍNH HÓA ĐƠN
# ============================================================

with tab1:

    # --------------------------------------------------------
    # THÔNG TIN KHÁCH HÀNG
    # --------------------------------------------------------

    st.subheader("👤 Thông tin khách hàng")

    customer_name = st.text_input(
        "Tên khách hàng",
        placeholder="Nhập tên khách hàng...",
        key="customer_name"
    )


    # --------------------------------------------------------
    # CHỌN MÓN
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # TÍNH GIÁ
    # --------------------------------------------------------

    base_price = MENU[product]

    size_price = SIZE_PRICE[size]

    topping_price = sum(
        TOPPINGS[topping]
        for topping in toppings
    )

    unit_price = (
        base_price
        + size_price
        + topping_price
    )

    item_total = unit_price * quantity


    # --------------------------------------------------------
    # HIỂN THỊ GIÁ
    # --------------------------------------------------------

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


    # --------------------------------------------------------
    # THÊM MÓN
    # --------------------------------------------------------

    if st.button(
        "➕ Thêm món",
        use_container_width=True
    ):

        if not customer_name.strip():

            st.warning(
                "⚠️ Vui lòng nhập tên khách hàng trước."
            )

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

            st.session_state.cart.append(
                new_item
            )

            st.session_state.payment_done = False

            st.success(
                f"✅ Đã thêm {quantity} ly "
                f"{product} vào hóa đơn."
            )


    # --------------------------------------------------------
    # GIỎ HÀNG
    # --------------------------------------------------------

    st.divider()

    st.subheader("🛒 Danh sách món đã chọn")

    if len(st.session_state.cart) == 0:

        st.info(
            "Chưa có món nào trong hóa đơn. "
            "Hãy chọn món và nhấn 'Thêm món'."
        )

    else:

        grand_total = 0

        for i, item in enumerate(
            st.session_state.cart
        ):

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


        # ----------------------------------------------------
        # TỔNG TIỀN
        # ----------------------------------------------------

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


        # ----------------------------------------------------
        # NÚT XÓA VÀ THANH TOÁN
        # ----------------------------------------------------

        col_clear, col_payment = st.columns(2)

        with col_clear:

            if st.button(
                "🗑️ Xóa toàn bộ hóa đơn",
                use_container_width=True
            ):

                st.session_state.cart = []

                st.session_state.payment_done = False

                st.rerun()


        with col_payment:

            if st.button(
                "💳 THANH TOÁN",
                type="primary",
                use_container_width=True
            ):

                st.session_state.payment_done = True

                st.rerun()


    # ========================================================
    # HÓA ĐƠN SAU KHI THANH TOÁN
    # ========================================================

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


        # ----------------------------------------------------
        # HTML HÓA ĐƠN
        # ----------------------------------------------------

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
                <b>Khách hàng:</b>
                {customer_name}
            </p>

            <p>
                <b>Thời gian:</b>
                {bill_time}
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


        # ----------------------------------------------------
        # TEXT HÓA ĐƠN
        # ----------------------------------------------------

        bill_text = ""

        bill_text += "================================\n"
        bill_text += "          QUÁN TRÀ SỮA\n"
        bill_text += "        HÓA ĐƠN THANH TOÁN\n"
        bill_text += "================================\n"

        bill_text += (
            f"Khách hàng: {customer_name}\n"
        )

        bill_text += (
            f"Thời gian: {bill_time}\n"
        )

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
                f"{i + 1}. "
                f"{item['product']}\n"
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
                f"   Topping: "
                f"{topping_text}\n"
            )

            bill_text += (
                f"   Đơn giá: "
                f"{item['unit_price']:,} VNĐ\n"
            )

            bill_text += (
                f"   Thành tiền: "
                f"{item['total']:,} VNĐ\n"
            )

            bill_text += (
                "--------------------------------\n"
            )


        bill_text += (
            f"TỔNG THANH TOÁN: "
            f"{grand_total:,} VNĐ\n"
        )

        bill_text += (
            "================================\n"
        )

        bill_text += (
            "       CẢM ƠN QUÝ KHÁCH!\n"
        )

        bill_text += (
            "================================\n"
        )


        # ----------------------------------------------------
        # DOWNLOAD
        # ----------------------------------------------------

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
# TAB 2 - CHATBOT
# ============================================================

with tab2:

    st.subheader("🤖 Chatbot tư vấn trà sữa")

    st.write(
        "Chatbot hoạt động dựa trên **luật được lập trình sẵn**, "
        "không sử dụng API và không cần kết nối AI."
    )


    # --------------------------------------------------------
    # CÂU HỎI GỢI Ý
    # --------------------------------------------------------

    st.markdown("### 💡 Bạn có thể hỏi:")

    suggestion_cols = st.columns(3)

    suggestions = [
        "Loại trà sữa nào giá cao nhất?",
        "Loại nào rẻ nhất?",
        "Trà sữa matcha nên dùng topping nào?",
        "Loại trà sữa nào ngọt?",
        "Topping nào đắt nhất?",
        "Size L thêm bao nhiêu tiền?"
    ]

    for i, suggestion in enumerate(suggestions):

        with suggestion_cols[i % 3]:

            if st.button(
                suggestion,
                key=f"suggestion_{i}",
                use_container_width=True
            ):

                st.session_state.chat_messages.append(
                    {
                        "role": "user",
                        "content": suggestion
                    }
                )

                answer = chatbot_answer(
                    suggestion
                )

                st.session_state.chat_messages.append(
                    {
                        "role": "assistant",
                        "content": answer
                    }
                )

                st.rerun()


    st.divider()


    # --------------------------------------------------------
    # HIỂN THỊ LỊCH SỬ CHAT
    # --------------------------------------------------------

    for message in st.session_state.chat_messages:

        with st.chat_message(
            message["role"]
        ):

            st.write(
                message["content"]
            )


    # --------------------------------------------------------
    # Ô NHẬP CÂU HỎI
    # --------------------------------------------------------

    user_question = st.chat_input(
        "Nhập câu hỏi về trà sữa..."
    )


    if user_question:

        # Hiển thị câu hỏi người dùng

        st.session_state.chat_messages.append(
            {
                "role": "user",
                "content": user_question
            }
        )


        # Chatbot xử lý bằng luật

        answer = chatbot_answer(
            user_question
        )


        # Lưu câu trả lời

        st.session_state.chat_messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )


        st.rerun()


    # --------------------------------------------------------
    # XÓA LỊCH SỬ CHAT
    # --------------------------------------------------------

    if st.session_state.chat_messages:

        if st.button(
            "🗑️ Xóa lịch sử trò chuyện"
        ):

            st.session_state.chat_messages = []

            st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        🧋 Hệ thống quản lý hóa đơn & chatbot trà sữa
    </div>
    """,
    unsafe_allow_html=True
)
