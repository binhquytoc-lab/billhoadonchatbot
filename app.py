import streamlit as st
from datetime import datetime
import io
import requests

# =========================================================
# CẤU HÌNH TRANG
# =========================================================

st.set_page_config(
    page_title="Quán Trà Sữa",
    page_icon="🧋",
    layout="centered"
)

# =========================================================
# API CHATBOT GROK (xAI)
# =========================================================

GROK_API_KEY = "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"
GROK_URL = "https://api.x.ai/v1/chat/completions"

# Model chuẩn của xAI cho Grok
MODEL_NAME = "grok-beta"

# =========================================================
# ẢNH QUÁN
# =========================================================

try:
    st.image("TRASUA.jpg", use_container_width=True)
except Exception:
    pass

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

# =========================================================
# GIÁ TOPPING
# =========================================================

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
# SESSION STATE
# =========================================================

if "cart" not in st.session_state:
    st.session_state.cart = []

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = [
        {
            "role": "assistant",
            "content": (
                "Xin chào! 🧋 Tôi là chatbot của Quán Trà Sữa. "
                "Tôi có thể giúp bạn xem menu, giá đồ uống, giá topping "
                "và tư vấn lựa chọn trà sữa."
            )
        }
    ]

# =========================================================
# HÀM GỌI CHATBOT AI (GROK)
# =========================================================

def ask_chatbot(user_message):
    menu_text = ""
    for drink_name, price in MENU.items():
        menu_text += f"- {drink_name}: {price:,} VNĐ\n"

    topping_text = ""
    for topping_name, price in TOPPINGS.items():
        topping_text += f"- {topping_name}: {price:,} VNĐ\n"

    cart_text = ""
    if len(st.session_state.cart) == 0:
        cart_text = "Hiện tại khách chưa có món nào trong giỏ hàng."
    else:
        cart_text = "Các món hiện đang có trong giỏ hàng:\n"
        for index, item in enumerate(st.session_state.cart):
            cart_text += (
                f"{index + 1}. {item['drink']} - "
                f"{item['quantity']} ly - "
                f"Topping: {item['topping']} - "
                f"Đường: {item['sugar']} - "
                f"Đá: {item['ice']} - "
                f"Thành tiền: {item['total']:,} VNĐ\n"
            )

    system_prompt = f"""
Bạn là chatbot tư vấn khách hàng cho một quán trà sữa.

Tên quán: QUÁN TRÀ SỮA
Địa chỉ: Số 504 Đại lộ Bình Dương

Bạn chỉ nên tư vấn dựa trên thông tin menu được cung cấp bên dưới.

MENU:
{menu_text}

TOPPING:
{topping_text}

MỨC ĐỘ ĐƯỜNG: 100%, 70%, 0%
MỨC ĐỘ ĐÁ: 100%, 70%, 0%

{cart_text}

QUY TẮC:
1. Trả lời bằng tiếng Việt thân thiện, ngắn gọn, dễ hiểu.
2. Tư vấn khách chọn món dựa vào menu.
3. Khi khách hỏi giá, trả lời đúng theo MENU và TOPPING.
4. Không tự bịa thêm món hoặc giá ngoài menu.
5. Nếu khách hỏi ngoài phạm vi quán trà sữa, hãy trả lời lịch sự rằng bạn chủ yếu hỗ trợ thông tin về quán.
"""

    messages = [{"role": "system", "content": system_prompt}]
    
    for message in st.session_state.chat_messages[-10:]:
        messages.append({
            "role": message["role"],
            "content": message["content"]
        })

    messages.append({"role": "user", "content": user_message})

    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": MODEL_NAME,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 500
    }

    try:
        response = requests.post(GROK_URL, headers=headers, json=data, timeout=60)
        
        if response.status_code != 200:
            try:
                error_data = response.json()
                error_message = error_data.get("error", {}).get("message", "Không xác định")
            except Exception:
                error_message = response.text
            return f"❌ Chatbot gặp lỗi API (Mã {response.status_code}): {error_message}"

        result = response.json()
        answer = result["choices"][0]["message"]["content"]
        return answer

    except requests.exceptions.Timeout:
        return "❌ Kết nối chatbot quá thời gian chờ. Vui lòng thử lại."
    except requests.exceptions.RequestException as e:
        return f"❌ Không thể kết nối đến chatbot. Chi tiết: {str(e)}"
    except Exception as e:
        return f"❌ Có lỗi xảy ra: {str(e)}"

# =========================================================
# TIÊU ĐỀ
# =========================================================

st.markdown('<div class="main-title">❤️ QUÁN TRÀ SỮA</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">📍 Số 504 Đại lộ Bình Dương</div>', unsafe_allow_html=True)

# =========================================================
# CHATBOT
# =========================================================

st.divider()
st.subheader("🤖 Chatbot tư vấn khách hàng")
st.caption("Bạn có thể hỏi chatbot về menu, giá, topping, đường, đá hoặc nhờ tư vấn đồ uống.")

for message in st.session_state.chat_messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_message = st.chat_input("Ví dụ: Trà sữa nào giá 35.000?")

if user_message:
    st.session_state.chat_messages.append({"role": "user", "content": user_message})
    with st.chat_message("user"):
        st.markdown(user_message)

    with st.chat_message("assistant"):
        with st.spinner("🤖 Chatbot đang trả lời..."):
            answer = ask_chatbot(user_message)
            st.markdown(answer)

    st.session_state.chat_messages.append({"role": "assistant", "content": answer})

if st.button("🗑️ Xóa lịch sử chatbot", key="clear_chat"):
    st.session_state.chat_messages = [
        {
            "role": "assistant",
            "content": (
                "Xin chào! 🧋 Tôi là chatbot của Quán Trà Sữa. "
                "Tôi có thể giúp bạn xem menu, giá đồ uống, "
                "giá topping và tư vấn lựa chọn trà sữa."
            )
        }
    ]
    st.rerun()

# =========================================================
# THÔNG TIN KHÁCH HÀNG & CHỌN MÓN
# =========================================================

st.divider()
st.subheader("👤 Thông tin khách hàng")
customer_name = st.text_input("Tên khách hàng", placeholder="Nhập tên khách hàng...")

st.subheader("🧋 Chọn món")
col1, col2 = st.columns(2)

with col1:
    drink = st.selectbox("Loại trà sữa / đồ uống", list(MENU.keys()))
    quantity = st.number_input("Số lượng", min_value=1, max_value=20, value=1, step=1)
    sugar = st.selectbox("Mức độ đường", ["100%", "70%", "0%"])

with col2:
    topping = st.selectbox("Topping", list(TOPPINGS.keys()))
    ice = st.selectbox("Mức độ đá", ["100%", "70%", "0%"])

drink_price = MENU[drink]
topping_price = TOPPINGS[topping]
unit_price = drink_price + topping_price
item_total = unit_price * quantity

st.markdown("### 💰 Thông tin món")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Giá đồ uống", f"{drink_price:,} VNĐ")
with col2:
    st.metric("Giá topping", f"{topping_price:,} VNĐ")
with col3:
    st.metric("Thành tiền", f"{item_total:,} VNĐ")

if st.button("➕ THÊM MÓN VÀO HÓA ĐƠN", use_container_width=True):
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
        st.success(f"✅ Đã thêm {quantity} ly {drink} vào hóa đơn.")

# =========================================================
# HÓA ĐƠN
# =========================================================

st.divider()
st.subheader("🧾 HÓA ĐƠN HIỆN TẠI")

if len(st.session_state.cart) == 0:
    st.info("Chưa có món nào trong hóa đơn. Hãy chọn món và bấm 'THÊM MÓN VÀO HÓA ĐƠN'.")
else:
    total_bill = 0
    for index, item in enumerate(st.session_state.cart):
        total_bill += item["total"]
        st.markdown(
            f"""
            <div class="bill-box">
            <b>{index + 1}. {item['drink']}</b><br>
            Số lượng: {item['quantity']} ly<br>
            Topping: {item['topping']}<br>
            Đường: {item['sugar']}<br>
            Đá: {item['ice']}<br>
            Đơn giá: {item['unit_price']:,} VNĐ<br>
            <b>Thành tiền: {item['total']:,} VNĐ</b>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown(
        f"""
        <div class="total-box">
        <div>TỔNG TIỀN THANH TOÁN</div>
        <div class="total-money">{total_bill:,} VNĐ</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ XÓA HÓA ĐƠN", use_container_width=True):
            st.session_state.cart = []
            st.rerun()

    with col2:
        if st.button("💳 THANH TOÁN & XUẤT HÓA ĐƠN", use_container_width=True):
            payment_time = datetime.now()
            bill_text = "========================================\n"
            bill_text += "             QUÁN TRÀ SỮA\n"
            bill_text += "          HÓA ĐƠN THANH TOÁN\n"
            bill_text += "========================================\n\n"
            bill_text += f"Khách hàng: {customer_name}\n"
            bill_text += f"Thời gian: {payment_time.strftime('%d/%m/%Y %H:%M:%S')}\n\n"
            bill_text += "----------------------------------------\n"

            for index, item in enumerate(st.session_state.cart):
                bill_text += f"{index + 1}. {item['drink']}\n"
                bill_text += f"   Số lượng: {item['quantity']} ly\n"
                bill_text += f"   Topping: {item['topping']}\n"
                bill_text += f"   Đường: {item['sugar']}\n"
                bill_text += f"   Đá: {item['ice']}\n"
                bill_text += f"   Đơn giá: {item['unit_price']:,} VNĐ\n"
                bill_text += f"   Thành tiền: {item['total']:,} VNĐ\n"
                bill_text += "----------------------------------------\n"

            bill_text += f"\nTỔNG THANH TOÁN: {total_bill:,} VNĐ\n\n"
            bill_text += "Cảm ơn quý khách đã sử dụng dịch vụ!\n"
            bill_text += "Hẹn gặp lại quý khách!\n"
            bill_text += "========================================\n"

            st.success(f"✅ THANH TOÁN THÀNH CÔNG! Tổng tiền: {total_bill:,} VNĐ")

            file_data = io.BytesIO(bill_text.encode("utf-8"))
            filename = "hoa_don_" + payment_time.strftime("%Y%m%d_%H%M%S") + ".txt"

            st.download_button(
                label="📥 TẢI HÓA ĐƠN",
                data=file_data,
                file_name=filename,
                mime="text/plain",
                use_container_width=True
            )
