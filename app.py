import os
from datetime import datetime
import requests
import streamlit as st

# ============================================================
# CẤU HÌNH TRANG
# ============================================================

st.set_page_config(
    page_title="Trà Sữa - Hóa Đơn & AI Chatbot", page_icon="🧋", layout="wide"
)


# ============================================================
# OPENROUTER & API CONFIG
# ============================================================

# API Key công khai trực tiếp
OPENROUTER_API_KEY = "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"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Model miễn phí chất lượng cao trên OpenRouter
AI_MODEL = "meta-llama/llama-3.3-70b-instruct:free"


# ============================================================
# CSS CUSTOM
# ============================================================

st.markdown(
    """
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
    color: #d9534f;
}

.bill-box {
    background-color: white;
    padding: 25px;
    border-radius: 12px;
    border: 1px solid #ddd;
    box-shadow: 0px 2px 8px rgba(0,0,0,0.08);
    color: #333;
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
    margin-top: 50px;
    padding: 20px;
    border-top: 1px solid #eee;
}

.ai-box {
    background-color: #f5f7ff;
    padding: 15px;
    border-radius: 10px;
    border: 1px solid #d9ddff;
}
</style>
""",
    unsafe_allow_html=True,
)


# ============================================================
# DỮ LIỆU QUÁN
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
    "Trà xoài": 32000,
}

TOPPINGS = {
    "Trân châu đen": 5000,
    "Trân châu trắng": 6000,
    "Thạch rau câu": 5000,
    "Thạch dừa": 5000,
    "Pudding trứng": 7000,
    "Kem cheese": 10000,
    "Đậu đỏ": 6000,
    "Khoai môn": 7000,
}

SIZE_PRICE = {"S": 0, "M": 5000, "L": 10000}

TOPPING_RECOMMENDATIONS = {
    "Trà sữa truyền thống": [
        "Trân châu đen",
        "Trân châu trắng",
        "Pudding trứng",
    ],
    "Trà sữa trân châu": ["Trân châu đen", "Trân châu trắng", "Pudding trứng"],
    "Trà sữa matcha": ["Trân châu trắng", "Pudding trứng", "Kem cheese"],
    "Trà sữa socola": ["Pudding trứng", "Kem cheese", "Trân châu đen"],
    "Trà sữa khoai môn": ["Khoai môn", "Trân châu trắng", "Pudding trứng"],
    "Trà sữa dâu": ["Trân châu trắng", "Thạch dừa", "Kem cheese"],
    "Trà đào": ["Thạch dừa", "Thạch rau câu"],
    "Trà vải": ["Thạch dừa", "Thạch rau câu"],
    "Trà chanh": ["Thạch rau câu", "Thạch dừa"],
    "Trà xoài": ["Thạch dừa", "Thạch rau câu"],
}

SWEET_DRINKS = ["Trà sữa socola", "Trà sữa khoai môn", "Trà sữa dâu"]
MEDIUM_SWEET_DRINKS = [
    "Trà sữa truyền thống",
    "Trà sữa trân châu",
    "Trà sữa matcha",
]
LIGHT_DRINKS = ["Trà đào", "Trà vải", "Trà chanh", "Trà xoài"]


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
# HELPER FUNCTIONS
# ============================================================


def format_money(value):
    return f"{value:,} VNĐ"


def rule_based_answer(question):
    """Xử lý trả lời nhanh dựa trên từ khóa luật cứng."""
    q = question.lower().strip()

    if any(x in q for x in ["xin chào", "chào", "hello", "hi"]):
        return "Xin chào 👋 Tôi có thể tư vấn về menu, giá, topping và size cho bạn!"

    if any(x in q for x in ["cao nhất", "đắt nhất", "mắc nhất"]):
        max_price = max(MENU.values())
        products = [name for name, price in MENU.items() if price == max_price]
        return f"Loại có giá cao nhất: {', '.join(products)} - {format_money(max_price)}."

    if any(x in q for x in ["rẻ nhất", "thấp nhất"]):
        min_price = min(MENU.values())
        products = [name for name, price in MENU.items() if price == min_price]
        return f"Loại có giá thấp nhất: {', '.join(products)} - {format_money(min_price)}."

    if "topping" in q and any(x in q for x in ["đắt nhất", "cao nhất"]):
        max_price = max(TOPPINGS.values())
        toppings = [
            name for name, price in TOPPINGS.items() if price == max_price
        ]
        return f"Topping có giá cao nhất: {', '.join(toppings)} - {format_money(max_price)}."

    if "topping" in q and any(x in q for x in ["rẻ nhất", "thấp nhất"]):
        min_price = min(TOPPINGS.values())
        toppings = [
            name for name, price in TOPPINGS.items() if price == min_price
        ]
        return f"Topping có giá thấp nhất: {', '.join(toppings)} - {format_money(min_price)}."

    if "size" in q:
        return "🥤 Giá phụ thu Size:\n\n• Size S: không phụ thu\n• Size M: +5.000 VNĐ\n• Size L: +10.000 VNĐ"

    if any(x in q for x in ["ngọt", "uống ngọt"]):
        return (
            f"🍫 Nhóm vị ngọt nổi bật gồm: {', '.join(SWEET_DRINKS)}.\n\n"
            "Bạn có thể chọn 70% hoặc 100% đường để tận hưởng trọn vị ngọt nhé!"
        )

    if any(
        x in q for x in ["ít ngọt", "không ngọt", "ít đường", "thanh", "chua"]
    ):
        return (
            f"🍋 Nhóm trà vị nhẹ & thanh gồm: {', '.join(LIGHT_DRINKS)}.\n\n"
            "Bạn có thể chọn 30% hoặc 0% đường nhé!"
        )

    # Tìm sản phẩm cụ thể
    selected_product = next(
        (prod for prod in MENU if prod.lower() in q), None
    )
    if selected_product:
        price = MENU[selected_product]
        if any(x in q for x in ["giá", "bao nhiêu", "tiền"]):
            return (
                f"🧋 **{selected_product}**:\n\n"
                f"• Size S: {format_money(price)}\n"
                f"• Size M: {format_money(price + 5000)}\n"
                f"• Size L: {format_money(price + 10000)}"
            )
        if any(x in q for x in ["topping", "ăn kèm", "dùng kèm", "hợp"]):
            recs = TOPPING_RECOMMENDATIONS.get(selected_product, [])
            rec_str = "\n".join([f"• {x}" for x in recs])
            return f"🧋 Với **{selected_product}**, quán gợi ý nên dùng kèm:\n\n{rec_str}"

    if any(x in q for x in ["menu", "danh sách", "có những loại"]):
        text = "🧋 **Menu quán hiện tại:**\n\n"
        for name, price in MENU.items():
            text += f"• {name}: {format_money(price)}\n"
        return text

    return None


def ask_ai(question):
    """Gọi OpenRouter AI API. Nếu gặp lỗi sẽ tự động fallback về Rule-based."""
    rule_ans = rule_based_answer(question)

    menu_text = "\n".join(f"- {k}: {v:,} VNĐ" for k, v in MENU.items())
    topping_text = "\n".join(f"- {k}: {v:,} VNĐ" for k, v in TOPPINGS.items())
    size_text = "\n".join(
        f"- Size {k}: +{v:,} VNĐ" for k, v in SIZE_PRICE.items()
    )

    system_prompt = f"""
Bạn là AI chatbot tư vấn bán hàng cho quán trà sữa tại Việt Nam.

Nhiệm vụ:
- Tư vấn menu, giá cả, topping, size.
- Gợi ý đồ uống phù hợp với sở thích khách hàng.
- Trả lời thân thiện, ngắn gọn, lịch sự, đúng sự thật.
- Chỉ sử dụng bảng giá chính xác dưới đây:

MENU:
{menu_text}

TOPPING:
{topping_text}

SIZE PHỤ THU:
{size_text}

GỢI Ý TOPPING:
{TOPPING_RECOMMENDATIONS}

NHÓM VỊ:
- Ngọt nổi bật: {SWEET_DRINKS}
- Ngọt vừa: {MEDIUM_SWEET_DRINKS}
- Thanh nhẹ: {LIGHT_DRINKS}
"""

    messages = [{"role": "system", "content": system_prompt}]
    for msg in st.session_state.ai_messages[-8:]:
        messages.append({"role": msg["role"], "content": msg["content"]})
    messages.append({"role": "user", "content": question})

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://streamlit.io",
        "X-Title": "Tra Sua App",
    }

    payload = {
        "model": AI_MODEL,
        "messages": messages,
        "temperature": 0.5,
        "max_tokens": 500,
    }

    try:
        response = requests.post(
            OPENROUTER_URL, headers=headers, json=payload, timeout=15
        )
        if response.status_code == 200:
            data = response.json()
            return data["choices"][0]["message"]["content"]
        else:
            if rule_ans:
                return rule_ans
            return f"❌ Lỗi API OpenRouter ({response.status_code}): Vui lòng kiểm tra lại Key hoặc Model."
    except Exception as e:
        if rule_ans:
            return rule_ans
        return f"❌ Không thể kết nối AI: {str(e)}"


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🧋 TRÀ SỮA - HÓA ĐƠN & AI CHATBOT</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="sub-title">Tính hóa đơn • Thanh toán • AI tư vấn đặt món</div>',
    unsafe_allow_html=True,
)

tab1, tab2 = st.tabs(["🧾 TÍNH HÓA ĐƠN", "🤖 AI CHATBOT"])


# ============================================================
# TAB 1 - HÓA ĐƠN
# ============================================================

with tab1:
    st.subheader("👤 Thông tin khách hàng")
    customer_name = st.text_input(
        "Tên khách hàng", placeholder="Nhập tên khách hàng..."
    )

    st.subheader("🧋 Chọn món")
    col1, col2 = st.columns(2)

    with col1:
        product = st.selectbox("Loại trà sữa / đồ uống", list(MENU.keys()))
        size = st.selectbox("Size ly", ["S", "M", "L"])
        quantity = st.number_input(
            "Số lượng", min_value=1, max_value=50, value=1, step=1
        )

    with col2:
        sugar = st.selectbox(
            "Mức độ đường",
            [
                "100% đường",
                "70% đường",
                "50% đường",
                "30% đường",
                "0% đường",
            ],
        )
        ice = st.selectbox(
            "Mức độ đá",
            ["100% đá", "70% đá", "50% đá", "30% đá", "Không đá"],
        )
        toppings = st.multiselect("Topping", list(TOPPINGS.keys()))

    # Tính toán đơn giá
    base_price = MENU[product]
    size_price = SIZE_PRICE[size]
    topping_price = sum(TOPPINGS[x] for x in toppings)
    unit_price = base_price + size_price + topping_price
    item_total = unit_price * quantity

    st.markdown("### 💰 Tạm tính món này")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Giá cơ bản", f"{base_price:,} đ")
    c2.metric(f"Size {size}", f"+{size_price:,} đ")
    c3.metric("Topping", f"+{topping_price:,} đ")
    c4.metric("Thành tiền", f"{item_total:,} đ")

    if st.button("➕ Thêm món vào giỏ", use_container_width=True):
        if not customer_name.strip():
            st.warning("⚠️ Vui lòng nhập tên khách hàng trước khi thêm món.")
        else:
            item = {
                "product": product,
                "size": size,
                "quantity": quantity,
                "sugar": sugar,
                "ice": ice,
                "toppings": toppings.copy(),
                "unit_price": unit_price,
                "total": item_total,
            }
            st.session_state.cart.append(item)
            st.session_state.payment_done = False
            st.success(f"✅ Đã thêm {quantity} ly {product} vào giỏ hàng!")

    st.divider()

    # GIỎ HÀNG
    st.subheader("🛒 Danh sách món đã chọn")
    if not st.session_state.cart:
        st.info("Giỏ hàng đang trống. Hãy chọn món và bấm 'Thêm món vào giỏ'.")
    else:
        grand_total = sum(item["total"] for item in st.session_state.cart)

        for i, item in enumerate(st.session_state.cart):
            with st.container(border=True):
                ca, cb, cc, cd = st.columns([3, 1, 2, 1])
                with ca:
                    st.markdown(f"**{i + 1}. {item['product']}**")
                    top_str = (
                        ", ".join(item["toppings"])
                        if item["toppings"]
                        else "Không topping"
                    )
                    st.caption(
                        f"Size: {item['size']} | Đường: {item['sugar']} | Đá: {item['ice']}"
                    )
                    st.caption(f"Topping: {top_str}")

                with cb:
                    st.write(f"SL: **{item['quantity']}**")

                with cc:
                    st.write(f"{item['unit_price']:,} đ/ly")

                with cd:
                    st.write(f"**{item['total']:,} đ**")
                    if st.button("🗑️ Xóa", key=f"delete_{i}"):
                        st.session_state.cart.pop(i)
                        st.rerun()

        st.markdown(
            f"""
            <div class="total-box">
                <div>TỔNG THANH TOÁN</div>
                <div class="total-money">{grand_total:,} VNĐ</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        clear_col, pay_col = st.columns(2)
        with clear_col:
            if st.button("🗑️ Xóa giỏ hàng", use_container_width=True):
                st.session_state.cart = []
                st.session_state.payment_done = False
                st.rerun()

        with pay_col:
            if st.button(
                "💳 XÁC NHẬN THANH TOÁN",
                type="primary",
                use_container_width=True,
            ):
                st.session_state.payment_done = True
                st.rerun()

    # HÓA ĐƠN
    if st.session_state.payment_done and st.session_state.cart:
        st.divider()
        st.subheader("🧾 HÓA ĐƠN THANH TOÁN")

        now = datetime.now()
        bill_time = now.strftime("%d/%m/%Y %H:%M:%S")
        grand_total = sum(x["total"] for x in st.session_state.cart)

        bill_html = f"""
        <div class="bill-box">
            <div class="bill-title">🧋 QUÁN TRÀ SỮA</div>
            <div class="bill-center"><p>HÓA ĐƠN THANH TOÁN</p></div>
            <hr>
            <p><b>Khách hàng:</b> {customer_name}</p>
            <p><b>Thời gian:</b> {bill_time}</p>
            <hr>
        """

        for i, item in enumerate(st.session_state.cart):
            top_str = (
                ", ".join(item["toppings"])
                if item["toppings"]
                else "Không topping"
            )
            bill_html += f"""
            <div class="item-row">
                <b>{i + 1}. {item['product']}</b><br>
                Size: {item['size']} &nbsp;|&nbsp; SL: {item['quantity']}<br>
                Đường: {item['sugar']} &nbsp;|&nbsp; Đá: {item['ice']}<br>
                Topping: {top_str}<br>
                Đơn giá: {item['unit_price']:,} đ<br>
                <b>Thành tiền: {item['total']:,} đ</b>
            </div>
            """

        bill_html += f"""
            <hr>
            <div style="text-align:right;">
                <h2>TỔNG CỘNG: {grand_total:,} VNĐ</h2>
            </div>
            <hr>
            <div class="bill-center">
                <b>Cảm ơn quý khách!</b><br>
                Hẹn gặp lại quý khách lần sau ❤️
            </div>
        </div>
        """

        st.markdown(bill_html, unsafe_allow_html=True)

        # FILE TEXT DOWNLOAD
        bill_text = f"================================\n"
        bill_text += f"         QUÁN TRÀ SỮA\n"
        bill_text += f"      HÓA ĐƠN THANH TOÁN\n"
        bill_text += f"================================\n"
        bill_text += f"Khách hàng: {customer_name}\n"
        bill_text += f"Thời gian: {bill_time}\n"
        bill_text += f"--------------------------------\n"

        for i, item in enumerate(st.session_state.cart):
            top_str = (
                ", ".join(item["toppings"])
                if item["toppings"]
                else "Không topping"
            )
            bill_text += f"{i + 1}. {item['product']}\n"
            bill_text += f"   Size: {item['size']} | SL: {item['quantity']}\n"
            bill_text += f"   Đường: {item['sugar']} | Đá: {item['ice']}\n"
            bill_text += f"   Topping: {top_str}\n"
            bill_text += f"   Thành tiền: {item['total']:,} VNĐ\n"
            bill_text += f"--------------------------------\n"

        bill_text += f"TỔNG THANH TOÁN: {grand_total:,} VNĐ\n"
        bill_text += f"================================\n"

        st.download_button(
            "🖨️ Tải file Hóa Đơn (.txt)",
            data=bill_text,
            file_name=f"hoa_don_{now.strftime('%Y%m%d_%H%M%S')}.txt",
            mime="text/plain",
            use_container_width=True,
        )


# ============================================================
# TAB 2 - AI CHATBOT
# ============================================================

with tab2:
    st.subheader("🤖 AI Chatbot tư vấn trà sữa")

    st.markdown(
        """
        <div class="ai-box">
            🤖 Chatbot hỗ trợ tư vấn menu, gợi ý vị trà sữa và cách chọn topping phù hợp theo sở thích của bạn!
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # GỢI Ý CÂU HỎI
    st.markdown("### 💡 Gợi ý câu hỏi")
    suggestions = [
        "Trà sữa nào đắt nhất?",
        "Tôi thích uống ngọt thì nên chọn gì?",
        "Trà sữa matcha hợp topping nào?",
        "Tôi có 50.000 đồng thì nên gọi gì?",
        "Hãy giới thiệu menu cho tôi.",
        "Size L thêm bao nhiêu tiền?",
    ]

    cols = st.columns(3)
    for i, suggestion in enumerate(suggestions):
        with cols[i % 3]:
            if st.button(
                suggestion,
                key=f"ai_suggestion_{i}",
                use_container_width=True,
            ):
                st.session_state.ai_messages.append(
                    {"role": "user", "content": suggestion}
                )
                with st.spinner("🤖 AI đang suy nghĩ..."):
                    answer = ask_ai(suggestion)
                st.session_state.ai_messages.append(
                    {"role": "assistant", "content": answer}
                )
                st.rerun()

    st.divider()

    # LỊCH SỬ CHAT
    for message in st.session_state.ai_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # INPUT CHAT
    if user_question := st.chat_input("Nhập câu hỏi cho AI..."):
        st.session_state.ai_messages.append(
            {"role": "user", "content": user_question}
        )
        with st.chat_message("user"):
            st.markdown(user_question)

        with st.chat_message("assistant"):
            with st.spinner("🤖 AI đang trả lời..."):
                answer = ask_ai(user_question)
                st.markdown(answer)

        st.session_state.ai_messages.append(
            {"role": "assistant", "content": answer}
        )

    # XÓA LỊCH SỬ CHAT
    if st.session_state.ai_messages:
        st.write("")
        if st.button(
            "🗑️️ Xóa lịch sử trò chuyện", key="clear_ai_chat_btn"
        ):
            st.session_state.ai_messages = []
            st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        🧋 Hệ thống Quản lý Hóa đơn & AI Chatbot Trà Sữa
    </div>
    """,
    unsafe_allow_html=True,
)
