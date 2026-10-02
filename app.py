import streamlit as st
import requests
from datetime import datetime


# ============================================================
# CẤU HÌNH TRANG
# ============================================================

st.set_page_config(
    page_title="Trà Sữa - Hóa Đơn & AI Chatbot",
    page_icon="🧋",
    layout="wide"
)


# ============================================================
# OPENROUTER
# ============================================================

OPENROUTER_API_KEY = "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"

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Có thể đổi model sau này
AI_MODEL = "openrouter/free"


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

.ai-box {
    background-color: #f5f7ff;
    padding: 15px;
    border-radius: 10px;
    border: 1px solid #d9ddff;
}

</style>
""", unsafe_allow_html=True)


# ============================================================
# MENU
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
# LUẬT GỢI Ý TOPPING
# ============================================================

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


# ============================================================
# PHÂN LOẠI ĐỒ UỐNG THEO LUẬT
# ============================================================

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
# SESSION STATE
# ============================================================

if "cart" not in st.session_state:
    st.session_state.cart = []

if "payment_done" not in st.session_state:
    st.session_state.payment_done = False

if "ai_messages" not in st.session_state:
    st.session_state.ai_messages = []


# ============================================================
# HÀM FORMAT TIỀN
# ============================================================

def format_money(value):
    return f"{value:,} VNĐ"


# ============================================================
# CHATBOT RULE-BASED
# ============================================================

def rule_based_answer(question):

    q = question.lower().strip()

    # -----------------------------------------
    # CHÀO HỎI
    # -----------------------------------------

    if any(x in q for x in [
        "xin chào",
        "chào",
        "hello",
        "hi"
    ]):

        return (
            "Xin chào 👋 Tôi có thể tư vấn về "
            "menu, giá, topping và size."
        )


    # -----------------------------------------
    # GIÁ CAO NHẤT
    # -----------------------------------------

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

        return (
            f"Loại có giá cao nhất: "
            f"{', '.join(products)} - "
            f"{format_money(max_price)}."
        )


    # -----------------------------------------
    # GIÁ THẤP NHẤT
    # -----------------------------------------

    if (
        "rẻ nhất" in q
        or "thấp nhất" in q
    ):

        min_price = min(MENU.values())

        products = [
            name
            for name, price in MENU.items()
            if price == min_price
        ]

        return (
            f"Loại có giá thấp nhất: "
            f"{', '.join(products)} - "
            f"{format_money(min_price)}."
        )


    # -----------------------------------------
    # TOPPING ĐẮT NHẤT
    # -----------------------------------------

    if (
        "topping" in q
        and (
            "đắt nhất" in q
            or "cao nhất" in q
        )
    ):

        max_price = max(TOPPINGS.values())

        toppings = [
            name
            for name, price in TOPPINGS.items()
            if price == max_price
        ]

        return (
            f"Topping có giá cao nhất: "
            f"{', '.join(toppings)} - "
            f"{format_money(max_price)}."
        )


    # -----------------------------------------
    # TOPPING RẺ NHẤT
    # -----------------------------------------

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
            f"Topping có giá thấp nhất: "
            f"{', '.join(toppings)} - "
            f"{format_money(min_price)}."
        )


    # -----------------------------------------
    # SIZE
    # -----------------------------------------

    if "size" in q:

        return (
            "🥤 Giá size:\n\n"
            "• Size S: không phụ thu\n"
            "• Size M: +5.000 VNĐ\n"
            "• Size L: +10.000 VNĐ"
        )


    # -----------------------------------------
    # LOẠI NGỌT
    # -----------------------------------------

    if (
        "ngọt" in q
        or "uống ngọt" in q
    ):

        return (
            "🍫 Theo quy tắc tư vấn của quán, "
            "nhóm vị ngọt nổi bật gồm: "
            + ", ".join(SWEET_DRINKS)
            + ".\n\n"
            "Bạn có thể chọn 70% hoặc 100% đường."
        )


    # -----------------------------------------
    # ÍT NGỌT
    # -----------------------------------------

    if (
        "ít ngọt" in q
        or "không ngọt" in q
        or "ít đường" in q
        or "thanh" in q
    ):

        return (
            "🍋 Nếu thích vị nhẹ và thanh hơn, "
            "có thể tham khảo: "
            + ", ".join(LIGHT_DRINKS)
            + ".\n\n"
            "Bạn có thể chọn 30% hoặc 0% đường."
        )


    # -----------------------------------------
    # TÌM SẢN PHẨM
    # -----------------------------------------

    selected_product = None

    for product_name in MENU:

        if product_name.lower() in q:

            selected_product = product_name
            break


    # -----------------------------------------
    # HỎI GIÁ
    # -----------------------------------------

    if selected_product:

        price = MENU[selected_product]

        if (
            "giá" in q
            or "bao nhiêu" in q
            or "tiền" in q
        ):

            return (
                f"🧋 {selected_product}:\n\n"
                f"Size S: {format_money(price)}\n"
                f"Size M: {format_money(price + 5000)}\n"
                f"Size L: {format_money(price + 10000)}"
            )


        # -------------------------------------
        # HỎI TOPPING
        # -------------------------------------

        if (
            "topping" in q
            or "ăn kèm" in q
            or "dùng kèm" in q
            or "hợp" in q
        ):

            recommendations = TOPPING_RECOMMENDATIONS.get(
                selected_product,
                []
            )

            return (
                f"🧋 Với {selected_product}, "
                "có thể dùng kèm:\n\n"
                + "\n".join(
                    f"• {x}"
                    for x in recommendations
                )
            )


    # -----------------------------------------
    # DANH SÁCH MENU
    # -----------------------------------------

    if (
        "menu" in q
        or "danh sách" in q
        or "có những loại" in q
    ):

        text = "🧋 Menu hiện tại:\n\n"

        for name, price in MENU.items():

            text += (
                f"• {name}: "
                f"{format_money(price)}\n"
            )

        return text


    return None


# ============================================================
# GỌI OPENROUTER AI
# ============================================================

def ask_ai(question):

    # --------------------------------------------------------
    # TẠO THÔNG TIN MENU CHO AI
    # --------------------------------------------------------

    menu_text = "\n".join(
        f"- {name}: {price:,} VNĐ"
        for name, price in MENU.items()
    )

    topping_text = "\n".join(
        f"- {name}: {price:,} VNĐ"
        for name, price in TOPPINGS.items()
    )

    size_text = "\n".join(
        f"- Size {size}: +{price:,} VNĐ"
        for size, price in SIZE_PRICE.items()
    )


    # --------------------------------------------------------
    # SYSTEM PROMPT
    # --------------------------------------------------------

    system_prompt = f"""
Bạn là AI chatbot tư vấn cho một quán trà sữa tại Việt Nam.

Nhiệm vụ:
- Tư vấn menu.
- Tư vấn giá.
- Tư vấn topping.
- Tư vấn size.
- Gợi ý đồ uống phù hợp với sở thích khách hàng.
- Giải thích cách tính giá.
- Trả lời bằng tiếng Việt.
- Trả lời thân thiện, ngắn gọn, dễ hiểu.
- Không tự bịa giá sản phẩm.
- Khi hỏi giá, chỉ sử dụng bảng giá được cung cấp dưới đây.
- Nếu câu hỏi không liên quan đến quán trà sữa, hãy nói rằng
  bạn chuyên hỗ trợ các câu hỏi liên quan đến quán.

MENU:

{menu_text}

TOPPING:

{topping_text}

SIZE:

{size_text}

QUY TẮC GỢI Ý TOPPING:

{TOPPING_RECOMMENDATIONS}

QUY TẮC VỊ:

Nhóm vị ngọt nổi bật:
{SWEET_DRINKS}

Nhóm vị ngọt vừa:
{MEDIUM_SWEET_DRINKS}

Nhóm vị nhẹ/thanh:
{LIGHT_DRINKS}

Lưu ý:
Các phân loại "ngọt", "ngọt vừa", "nhẹ/thanh"
là quy tắc tư vấn của quán, không phải kết quả phân tích
dinh dưỡng hoặc xét nghiệm hàm lượng đường.
"""


    # --------------------------------------------------------
    # LỊCH SỬ CHAT GỬI CHO AI
    # --------------------------------------------------------

    messages = [
        {
            "role": "system",
            "content": system_prompt
        }
    ]


    # Chỉ gửi một số tin nhắn gần nhất
    recent_messages = st.session_state.ai_messages[-10:]


    for message in recent_messages:

        messages.append(
            {
                "role": message["role"],
                "content": message["content"]
            }
        )


    # Thêm câu hỏi hiện tại

    messages.append(
        {
            "role": "user",
            "content": question
        }
    )


    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://streamlit.io",
        "X-Title": "Tra Sua Hoa Don AI Chatbot"
    }


    # --------------------------------------------------------
    # BODY
    # --------------------------------------------------------

    payload = {
        "model": AI_MODEL,
        "messages": messages,
        "temperature": 0.5,
        "max_tokens": 700
    }


    # --------------------------------------------------------
    # GỌI API
    # --------------------------------------------------------

    try:

        response = requests.post(
            OPENROUTER_URL,
            headers=headers,
            json=payload,
            timeout=60
        )


        # ----------------------------------------------------
        # KIỂM TRA HTTP
        # ----------------------------------------------------

        if response.status_code != 200:

            try:
                error_data = response.json()

                error_message = error_data.get(
                    "error",
                    {}
                ).get(
                    "message",
                    response.text
                )

            except Exception:

                error_message = response.text


            return (
                f"❌ OpenRouter trả về lỗi "
                f"{response.status_code}:\n\n"
                f"{error_message}"
            )


        # ----------------------------------------------------
        # ĐỌC JSON
        # ----------------------------------------------------

        data = response.json()


        # ----------------------------------------------------
        # LẤY CÂU TRẢ LỜI
        # ----------------------------------------------------

        answer = data["choices"][0]["message"]["content"]


        return answer


    except requests.exceptions.Timeout:

        return (
            "⏱️ Kết nối AI bị timeout. "
            "Vui lòng thử lại."
        )


    except requests.exceptions.ConnectionError:

        return (
            "🌐 Không thể kết nối đến OpenRouter. "
            "Hãy kiểm tra kết nối Internet."
        )


    except Exception as e:

        return (
            f"❌ Có lỗi khi gọi chatbot AI:\n\n"
            f"{str(e)}"
        )


# ============================================================
# TIÊU ĐỀ
# ============================================================

st.markdown(
    '<div class="main-title">'
    '🧋 TRÀ SỮA - HÓA ĐƠN & AI CHATBOT'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="sub-title">'
    'Tính hóa đơn • Thanh toán • AI tư vấn trà sữa'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# TABS
# ============================================================

tab1, tab2 = st.tabs(
    [
        "🧾 TÍNH HÓA ĐƠN",
        "🤖 AI CHATBOT"
    ]
)


# ============================================================
# TAB 1 - HÓA ĐƠN
# ============================================================

with tab1:

    st.subheader("👤 Thông tin khách hàng")

    customer_name = st.text_input(
        "Tên khách hàng",
        placeholder="Nhập tên khách hàng..."
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
        TOPPINGS[x]
        for x in toppings
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

    c1, c2, c3, c4 = st.columns(4)


    with c1:

        st.metric(
            "Giá cơ bản",
            f"{base_price:,} đ"
        )


    with c2:

        st.metric(
            f"Size {size}",
            f"+{size_price:,} đ"
        )


    with c3:

        st.metric(
            "Topping",
            f"+{topping_price:,} đ"
        )


    with c4:

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
                "⚠️ Vui lòng nhập tên khách hàng."
            )

        else:

            item = {
                "product": product,
                "size": size,
                "quantity": quantity,
                "sugar": sugar,
                "ice": ice,
                "toppings": toppings.copy(),
                "unit_price": unit_price,
                "total": item_total
            }

            st.session_state.cart.append(item)

            st.session_state.payment_done = False

            st.success(
                f"✅ Đã thêm {quantity} ly "
                f"{product}."
            )


    st.divider()


    # ========================================================
    # GIỎ HÀNG
    # ========================================================

    st.subheader("🛒 Danh sách món")

    if not st.session_state.cart:

        st.info(
            "Chưa có món nào. "
            "Hãy chọn món và nhấn Thêm món."
        )

    else:

        grand_total = 0


        for i, item in enumerate(
            st.session_state.cart
        ):

            grand_total += item["total"]


            with st.container(border=True):

                ca, cb, cc, cd = st.columns(
                    [3, 1, 2, 1]
                )


                with ca:

                    st.markdown(
                        f"**{i + 1}. "
                        f"{item['product']}**"
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


                with cb:

                    st.write(
                        f"SL: **{item['quantity']}**"
                    )


                with cc:

                    st.write(
                        f"{item['unit_price']:,} đ/ly"
                    )


                with cd:

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
        # TỔNG
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
        # NÚT
        # ----------------------------------------------------

        clear_col, pay_col = st.columns(2)


        with clear_col:

            if st.button(
                "🗑️ Xóa toàn bộ hóa đơn",
                use_container_width=True
            ):

                st.session_state.cart = []

                st.session_state.payment_done = False

                st.rerun()


        with pay_col:

            if st.button(
                "💳 THANH TOÁN",
                type="primary",
                use_container_width=True
            ):

                st.session_state.payment_done = True

                st.rerun()


    # ========================================================
    # HÓA ĐƠN
    # ========================================================

    if (
        st.session_state.payment_done
        and st.session_state.cart
    ):

        st.divider()

        st.subheader("🧾 HÓA ĐƠN THANH TOÁN")

        now = datetime.now()

        bill_time = now.strftime(
            "%d/%m/%Y %H:%M:%S"
        )

        grand_total = sum(
            x["total"]
            for x in st.session_state.cart
        )


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
        # FILE TEXT
        # ----------------------------------------------------

        bill_text = ""

        bill_text += (
            "================================\n"
        )

        bill_text += (
            "          QUÁN TRÀ SỮA\n"
        )

        bill_text += (
            "        HÓA ĐƠN THANH TOÁN\n"
        )

        bill_text += (
            "================================\n"
        )

        bill_text += (
            f"Khách hàng: {customer_name}\n"
        )

        bill_text += (
            f"Thời gian: {bill_time}\n"
        )

        bill_text += (
            "--------------------------------\n"
        )


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


        st.download_button(
            "🖨️ Tải hóa đơn",
            data=bill_text,
            file_name=(
                f"hoa_don_"
                f"{now.strftime('%Y%m%d_%H%M%S')}.txt"
            ),
            mime="text/plain",
            use_container_width=True
        )


# ============================================================
# TAB 2 - AI CHATBOT
# ============================================================

with tab2:

    st.subheader("🤖 AI Chatbot tư vấn trà sữa")

    st.markdown(
        """
        <div class="ai-box">

        🤖 Chatbot này sử dụng <b>trí tuệ nhân tạo</b> thông qua
        OpenRouter API.

        <br><br>

        Bạn có thể hỏi tự nhiên như:

        <br>

        • Trà sữa nào đắt nhất?

        <br>

        • Tôi thích uống ngọt thì nên chọn gì?

        <br>

        • Matcha nên kết hợp với topping nào?

        <br>

        • Tôi có 50.000 đồng thì nên gọi gì?

        <br>

        • Hai người uống thì nên gọi thế nào?

        </div>
        """,
        unsafe_allow_html=True
    )


    st.divider()


    # ========================================================
    # CÂU HỎI GỢI Ý
    # ========================================================

    st.markdown("### 💡 Câu hỏi gợi ý")

    suggestions = [
        "Trà sữa nào có giá cao nhất?",
        "Tôi thích uống ngọt thì nên chọn gì?",
        "Trà sữa matcha hợp topping nào?",
        "Tôi có 50.000 đồng thì nên gọi gì?",
        "Hãy giới thiệu menu cho tôi.",
        "Size L thêm bao nhiêu tiền?"
    ]


    cols = st.columns(3)


    for i, suggestion in enumerate(
        suggestions
    ):

        with cols[i % 3]:

            if st.button(
                suggestion,
                key=f"ai_suggestion_{i}",
                use_container_width=True
            ):

                # Lưu câu hỏi

                st.session_state.ai_messages.append(
                    {
                        "role": "user",
                        "content": suggestion
                    }
                )


                # Gọi AI

                with st.spinner(
                    "🤖 AI đang suy nghĩ..."
                ):

                    answer = ask_ai(
                        suggestion
                    )


                # Lưu câu trả lời

                st.session_state.ai_messages.append(
                    {
                        "role": "assistant",
                        "content": answer
                    }
                )


                st.rerun()


    st.divider()


    # ========================================================
    # HIỂN THỊ CHAT
    # ========================================================

    for message in st.session_state.ai_messages:

        with st.chat_message(
            message["role"]
        ):

            st.markdown(
                message["content"]
            )


    # ========================================================
    # CHAT INPUT
    # ========================================================

    user_question = st.chat_input(
        "Nhập câu hỏi cho AI..."
    )


    if user_question:

        # -----------------------------------------------
        # HIỂN THỊ USER
        # -----------------------------------------------

        st.session_state.ai_messages.append(
            {
                "role": "user",
                "content": user_question
            }
        )


        # -----------------------------------------------
        # GỌI AI
        # -----------------------------------------------

        with st.spinner(
            "🤖 AI đang trả lời..."
        ):

            answer = ask_ai(
                user_question
            )


        # -----------------------------------------------
        # LƯU ANSWER
        # -----------------------------------------------

        st.session_state.ai_messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )


        st.rerun()


    # ========================================================
    # XÓA LỊCH SỬ
    # ========================================================

    if st.session_state.ai_messages:

        if st.button(
            "🗑️ Xóa lịch sử trò chuyện",
            key="clear_ai_chat"
        ):

            st.session_state.ai_messages = []

            st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        🧋 Hệ thống hóa đơn & AI Chatbot trà sữa
    </div>
    """,
    unsafe_allow_html=True
)
