from datetime import datetime
import streamlit as st

# ============================================================
# CẤU HÌNH TRANG
# ============================================================

st.set_page_config(
    page_title="Trà Sữa - Hóa Đơn & Chatbot Tư Vấn", page_icon="🧋", layout="wide"
)


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

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []


# ============================================================
# HELPER FUNCTIONS & CHATBOT LOGIC
# ============================================================


def format_money(value):
    return f"{value:,} VNĐ"


def ask_chatbot(question):
    """Xử lý trả lời tự động dựa trên từ khóa và dữ liệu của quán."""
    q = question.lower().strip()

    # Chào hỏi
    if any(x in q for x in ["xin chào", "chào", "hello", "hi"]):
        return "Xin chào 👋 Tôi là trợ lý ảo của quán trà sữa! Tôi có thể giúp bạn xem menu, tra cứu giá, chọn size, topping hoặc gợi ý món theo sở thích."

    # Hỏi món đắt nhất
    if any(x in q for x in ["cao nhất", "đắt nhất", "mắc nhất"]):
        max_price = max(MENU.values())
        products = [name for name, price in MENU.items() if price == max_price]
        return f"🏆 Loại có giá cao nhất là: **{', '.join(products)}** - {format_money(max_price)}."

    # Hỏi món rẻ nhất
    if any(x in q for x in ["rẻ nhất", "thấp nhất"]):
        min_price = min(MENU.values())
        products = [name for name, price in MENU.items() if price == min_price]
        return f"🏷️ Loại có giá thấp nhất là: **{', '.join(products)}** - {format_money(min_price)}."

    # Topping đắt/rẻ
    if "topping" in q and any(x in q for x in ["đắt nhất", "cao nhất"]):
        max_price = max(TOPPINGS.values())
        toppings = [
            name for name, price in TOPPINGS.items() if price == max_price
        ]
        return f"✨ Topping có giá cao nhất: **{', '.join(toppings)}** - {format_money(max_price)}."

    if "topping" in q and any(x in q for x in ["rẻ nhất", "thấp nhất"]):
        min_price = min(TOPPINGS.values())
        toppings = [
            name for name, price in TOPPINGS.items() if price == min_price
        ]
        return f"✨ Topping có giá thấp nhất: **{', '.join(toppings)}** - {format_money(min_price)}."

    # Hỏi về Size
    if "size" in q:
        return "🥤 **Giá phụ thu Size:**\n\n• Size S: không phụ thu (giá gốc)\n• Size M: +5.000 VNĐ\n• Size L: +10.000 VNĐ"

    # Gợi ý theo vị ngọt/thanh
    if any(x in q for x in ["ngọt", "uống ngọt"]):
        return (
            f"🍫 **Nhóm trà sữa vị đậm đà & ngọt thơm:** {', '.join(SWEET_DRINKS)}.\n\n"
            "💡 *Mẹo:* Bạn có thể chọn 70% hoặc 100% đường để cảm nhận trọn vẹn vị ngọt nhé!"
        )

    if any(
        x in q for x in ["ít ngọt", "không ngọt", "ít đường", "thanh", "chua", "mát"]
    ):
        return (
            f"🍋 **Nhóm trà trái cây thanh nhẹ & giải nhiệt:** {', '.join(LIGHT_DRINKS)}.\n\n"
            "💡 *Mẹo:* Bạn có thể chọn 30% hoặc 0% đường nếu muốn uống ít ngọt."
        )

    # Tư vấn theo ngân sách (Ví dụ: "có 50k", "50000", "40k")
    import re
    numbers = re.findall(r"\d+", q)
    if numbers and any(k in q for k in ["đồng", "k", "tiền", "ngân sách", "có"]):
        budget = int(numbers[0])
        if budget < 1000:
            budget *= 1000  # Ví dụ "50k" -> 50000

        suitable = []
        for name, price in MENU.items():
            if price <= budget:
                rem = budget - price
                suitable.append(f"• **{name}** ({format_money(price)}) - còn thừa {format_money(rem)} để thêm topping!")
        
        if suitable:
            return f"💰 Với **{format_money(budget)}**, bạn có thể gọi các món sau:\n\n" + "\n".join(suitable[:5])
        else:
            return f"😅 Với **{format_money(budget)}**, hiện chưa có món nào vừa ngân sách (món thấp nhất là {format_money(min(MENU.values()))})."

    # Tìm sản phẩm cụ thể
    selected_product = next(
        (prod for prod in MENU if prod.lower() in q), None
    )
    if selected_product:
        price = MENU[selected_product]
        recs = TOPPING_RECOMMENDATIONS.get(selected_product, [])
        rec_str = ", ".join(recs) if recs else "Không có gợi ý riêng"

        return (
            f"🧋 **Thông tin món: {selected_product}**\n\n"
            f"• **Giá niêm yết (Size S):** {format_money(price)}\n"
            f"• **Size M:** {format_money(price + 5000)} | **Size L:** {format_money(price + 10000)}\n"
            f"• **Topping khuyên dùng:** {rec_str}"
        )

    # Hỏi Menu / Topping chung
    if any(x in q for x in ["menu", "danh sách", "có những loại", "món gì"]):
        text = "🧋 **MENU QUÁN TRÀ SỮA:**\n\n"
        for name, price in MENU.items():
            text += f"• {name}: **{format_money(price)}**\n"
        text += "\n🍡 **TOPPING:**\n"
        for name, price in TOPPINGS.items():
            text += f"• {name}: +{format_money(price)}\n"
        return text

    # Câu trả lời mặc định khi không khớp từ khóa
    return (
        "🤖 Cảm ơn bạn đã đặt câu hỏi! Tôi có thể tư vấn các thông tin sau:\n"
        "- **Menu & Giá cả** (VD: *Cho xem menu*, *Trà sữa matcha giá bao nhiêu?*)\n"
        "- **Gợi ý món** (VD: *Món nào đắt nhất?*, *Tôi thích uống ít ngọt*)\n"
        "- **Tư vấn ngân sách** (VD: *Tôi có 50k nên uống gì?*)"
    )


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="main-title">🧋 TRÀ SỮA - HÓA ĐƠN & CHATBOT TƯ VẤN</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="sub-title">Tính hóa đơn • Thanh toán • Trợ lý tư vấn đặt món</div>',
    unsafe_allow_html=True,
)

tab1, tab2 = st.tabs(["🧾 TÍNH HÓA ĐƠN", "💬 TRỢ LÝ TƯ VẤN"])


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
        bill_text += f"          QUÁN TRÀ SỮA\n"
        bill_text += f"       HÓA ĐƠN THANH TOÁN\n"
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
# TAB 2 - CHATBOT TƯ VẤN
# ============================================================

with tab2:
    st.subheader("💬 Trợ lý Chatbot tư vấn chọn món")

    st.markdown(
        """
        <div class="ai-box">
            🤖 Chatbot tự động tư vấn menu, giá cả, gợi ý món theo sở thích và ngân sách của bạn mà không cần kết nối mạng bên ngoài!
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # GỢI Ý CÂU HỎI
    st.markdown("### 💡 Gợi ý câu hỏi nhanh")
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
                key=f"suggestion_{i}",
                use_container_width=True,
            ):
                st.session_state.chat_messages.append(
                    {"role": "user", "content": suggestion}
                )
                answer = ask_chatbot(suggestion)
                st.session_state.chat_messages.append(
                    {"role": "assistant", "content": answer}
                )
                st.rerun()

    st.divider()

    # LỊCH SỬ CHAT
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # INPUT CHAT
    if user_question := st.chat_input("Nhập câu hỏi cho Chatbot..."):
        st.session_state.chat_messages.append(
            {"role": "user", "content": user_question}
        )
        answer = ask_chatbot(user_question)
        st.session_state.chat_messages.append(
            {"role": "assistant", "content": answer}
        )
        st.rerun()

    # XÓA LỊCH SỬ CHAT
    if st.session_state.chat_messages:
        st.write("")
        if st.button(
            "🗑 Xóa lịch sử trò chuyện", key="clear_chat_btn"
        ):
            st.session_state.chat_messages = []
            st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        🧋 Hệ thống Quản lý Hóa đơn & Chatbot Tư Vấn Trà Sữa
    </div>
    """,
    unsafe_allow_html=True,
)
