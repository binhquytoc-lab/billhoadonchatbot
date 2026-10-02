import os
from datetime import datetime

import pandas as pd
import streamlit as st
from openai import OpenAI

# ----------------------------------------------------------------------------
# CẤU HÌNH TRANG
# ----------------------------------------------------------------------------
st.set_page_config(page_title="Quán Trà Sữa - Tính Hoá Đơn", page_icon="🧋", layout="wide")

SHOP_NAME = "TRÀ SỮA HANOI VIBES"
SHOP_ADDRESS = "123 Phố Huế, Hai Bà Trưng, Hà Nội"
SHOP_PHONE = "0123 456 789"

# ----------------------------------------------------------------------------
# DỮ LIỆU MENU (có thể sửa tuỳ ý)
# ----------------------------------------------------------------------------
MENU = {
    "Trà sữa trân châu đen": {"M": 35000, "L": 42000},
    "Trà sữa matcha": {"M": 40000, "L": 48000},
    "Trà sữa khoai môn": {"M": 38000, "L": 45000},
    "Trà sữa Thái xanh": {"M": 36000, "L": 43000},
    "Hồng trà sữa": {"M": 32000, "L": 39000},
    "Trà đào cam sả": {"M": 38000, "L": 45000},
    "Trà vải hoa hồng": {"M": 38000, "L": 45000},
    "Trà chanh giã tay": {"M": 25000, "L": 30000},
    "Sữa tươi trân châu đường đen": {"M": 42000, "L": 50000},
    "Cà phê muối": {"M": 30000, "L": 36000},
}

TOPPINGS = {
    "Trân châu đen": 7000,
    "Trân châu trắng": 8000,
    "Thạch dừa": 6000,
    "Thạch trái cây": 6000,
    "Pudding trứng": 8000,
    "Kem cheese": 12000,
    "Sương sáo": 6000,
}

SUGAR_LEVELS = ["100%", "70%", "50%", "30%", "0%"]
ICE_LEVELS = ["Bình thường", "Ít đá", "Không đá", "Nóng"]


# ----------------------------------------------------------------------------
# HÀM TIỆN ÍCH
# ----------------------------------------------------------------------------
def vnd(amount: float) -> str:
    return f"{amount:,.0f}".replace(",", ".") + "đ"


def init_state():
    defaults = {
        "cart": [],
        "history": [],
        "invoice_no": 1,
        "last_invoice": None,
        "messages": [],
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def cart_subtotal() -> int:
    return sum(item["Thành tiền"] for item in st.session_state.cart)


def build_invoice_text(order: dict) -> str:
    width = 46
    lines = [
        SHOP_NAME.center(width),
        SHOP_ADDRESS.center(width),
        f"ĐT: {SHOP_PHONE}".center(width),
        "=" * width,
        "HOÁ ĐƠN THANH TOÁN".center(width),
        f"Số HĐ : {order['invoice_no']:05d}",
        f"Ngày  : {order['time']}",
        f"Khách : {order['customer']}",
        "-" * width,
    ]
    for i, item in enumerate(order["items"], 1):
        lines.append(f"{i}. {item['Tên món']} ({item['Size']}) x{item['SL']}")
        detail = f"   Đường {item['Đường']}, {item['Đá']}"
        if item["Topping"]:
            detail += f", +{item['Topping']}"
        lines.append(detail)
        if item["Ghi chú"]:
            lines.append(f"   Ghi chú: {item['Ghi chú']}")
        lines.append(f"{vnd(item['Đơn giá'])} x {item['SL']}".ljust(width - 14) + vnd(item["Thành tiền"]).rjust(14))
    lines.append("-" * width)
    lines.append("Tạm tính".ljust(width - 14) + vnd(order["subtotal"]).rjust(14))
    lines.append(f"Giảm giá ({order['discount_pct']}%)".ljust(width - 14) + ("-" + vnd(order["discount"])).rjust(14))
    lines.append(f"VAT ({order['vat_pct']}%)".ljust(width - 14) + vnd(order["vat"]).rjust(14))
    lines.append("=" * width)
    lines.append("TỔNG CỘNG".ljust(width - 16) + vnd(order["total"]).rjust(16))
    lines.append(f"Thanh toán: {order['payment']}")
    if order["payment"] == "Tiền mặt":
        lines.append("Khách đưa".ljust(width - 14) + vnd(order["paid"]).rjust(14))
        lines.append("Tiền thừa".ljust(width - 14) + vnd(order["change"]).rjust(14))
    lines.append("=" * width)
    lines.append("Cảm ơn quý khách - Hẹn gặp lại!".center(width))
    return "\n".join(lines)


def get_api_key() -> str:
    """Ưu tiên: ô nhập ở sidebar -> st.secrets -> biến môi trường."""
    key = st.session_state.get("api_key_input", "").strip()
    if key:
        return key
    try:
        if "OPENROUTER_API_KEY" in st.secrets:
            return st.secrets["OPENROUTER_API_KEY"]
    except Exception:
        pass
    return os.getenv("OPENROUTER_API_KEY", "")


def build_system_prompt() -> str:
    menu_text = "\n".join(
        f"- {name}: size M {vnd(p['M'])}, size L {vnd(p['L'])}" for name, p in MENU.items()
    )
    topping_text = "\n".join(f"- {name}: +{vnd(price)}" for name, price in TOPPINGS.items())
    if st.session_state.cart:
        cart_text = "\n".join(
            f"- {it['Tên món']} ({it['Size']}) x{it['SL']}"
            + (f", topping: {it['Topping']}" if it["Topping"] else "")
            + f" = {vnd(it['Thành tiền'])}"
            for it in st.session_state.cart
        )
        cart_text += f"\nTạm tính: {vnd(cart_subtotal())}"
    else:
        cart_text = "(giỏ hàng đang trống)"
    return f"""Bạn là trợ lý AI thân thiện của quán trà sữa "{SHOP_NAME}".
Nhiệm vụ: tư vấn món, gợi ý topping, giải thích cách tính tiền, hỗ trợ nhân viên thu ngân.
Luôn trả lời bằng tiếng Việt, ngắn gọn, lịch sự. Chỉ dùng thông tin menu bên dưới, không bịa món hoặc giá.

MENU:
{menu_text}

TOPPING:
{topping_text}

GIỎ HÀNG HIỆN TẠI:
{cart_text}
"""


def stream_ai_reply(api_key: str, model: str):
    client = OpenAI(base_url="https://openrouter.ai/api/v1", api_key=api_key)
    messages = [{"role": "system", "content": build_system_prompt()}] + st.session_state.messages
    stream = client.chat.completions.create(model=model, messages=messages, stream=True)
    for chunk in stream:
        if chunk.choices and chunk.choices[0].delta.content:
            yield chunk.choices[0].delta.content


# ----------------------------------------------------------------------------
# GIAO DIỆN
# ----------------------------------------------------------------------------
init_state()

with st.sidebar:
    st.title("⚙️ Cài đặt")
    st.text_input(
        "OpenRouter API Key",
        type="password",
        key="api_key_input",
        help="Hoặc đặt OPENROUTER_API_KEY trong .streamlit/secrets.toml / biến môi trường.",
    )
    model = st.text_input("Model AI", value="openai/gpt-4o-mini")
    st.caption("Xem danh sách model tại openrouter.ai/models")
    st.divider()
    st.metric("Số hoá đơn đã xuất", len(st.session_state.history))
    st.metric("Doanh thu", vnd(sum(o["total"] for o in st.session_state.history)))

st.title("🧋 " + SHOP_NAME)

tab_order, tab_history, tab_chat = st.tabs(["🛒 Tạo đơn & Hoá đơn", "📜 Lịch sử", "🤖 Chatbot AI"])

# ---------------------------- TAB 1: TẠO ĐƠN --------------------------------
with tab_order:
    left, right = st.columns([1, 1.2], gap="large")

    with left:
        st.subheader("Thêm món")
        drink = st.selectbox("Món", list(MENU.keys()))
        c1, c2, c3 = st.columns(3)
        size = c1.radio("Size", ["M", "L"], horizontal=True)
        sugar = c2.selectbox("Đường", SUGAR_LEVELS)
        ice = c3.selectbox("Đá", ICE_LEVELS)
        toppings = st.multiselect("Topping", list(TOPPINGS.keys()), format_func=lambda t: f"{t} (+{vnd(TOPPINGS[t])})")
        qty = st.number_input("Số lượng", min_value=1, max_value=50, value=1, step=1)
        note = st.text_input("Ghi chú (tuỳ chọn)")

        unit_price = MENU[drink][size] + sum(TOPPINGS[t] for t in toppings)
        st.info(f"Đơn giá: **{vnd(unit_price)}** → Thành tiền: **{vnd(unit_price * qty)}**")

        if st.button("➕ Thêm vào giỏ", use_container_width=True, type="primary"):
            st.session_state.cart.append(
                {
                    "Tên món": drink,
                    "Size": size,
                    "Đường": sugar,
                    "Đá": ice,
                    "Topping": ", ".join(toppings),
                    "Ghi chú": note,
                    "SL": int(qty),
                    "Đơn giá": unit_price,
                    "Thành tiền": unit_price * int(qty),
                }
            )
            st.rerun()

    with right:
        st.subheader("Giỏ hàng")
        if st.session_state.cart:
            df = pd.DataFrame(st.session_state.cart)
            st.dataframe(
                df[["Tên món", "Size", "SL", "Topping", "Đơn giá", "Thành tiền"]],
                use_container_width=True,
                hide_index=True,
            )
            rc1, rc2 = st.columns([2, 1])
            remove_idx = rc1.selectbox(
                "Xoá món",
                range(len(st.session_state.cart)),
                format_func=lambda i: f"{i + 1}. {st.session_state.cart[i]['Tên món']} x{st.session_state.cart[i]['SL']}",
            )
            rc2.write("")
            rc2.write("")
            if rc2.button("🗑️ Xoá", use_container_width=True):
                st.session_state.cart.pop(remove_idx)
                st.rerun()
            if st.button("Xoá toàn bộ giỏ"):
                st.session_state.cart = []
                st.rerun()

            st.divider()
            st.subheader("Thanh toán")
            customer = st.text_input("Tên khách hàng", value="Khách lẻ")
            p1, p2 = st.columns(2)
            discount_pct = p1.slider("Giảm giá (%)", 0, 50, 0, step=5)
            vat_pct = p2.selectbox("VAT (%)", [0, 8, 10], index=0)
            payment = st.radio("Hình thức", ["Tiền mặt", "Chuyển khoản", "Thẻ"], horizontal=True)

            subtotal = cart_subtotal()
            discount = round(subtotal * discount_pct / 100)
            vat = round((subtotal - discount) * vat_pct / 100)
            total = subtotal - discount + vat

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Tạm tính", vnd(subtotal))
            m2.metric("Giảm giá", "-" + vnd(discount))
            m3.metric("VAT", vnd(vat))
            m4.metric("Tổng cộng", vnd(total))

            paid = total
            if payment == "Tiền mặt":
                paid = st.number_input("Khách đưa (VNĐ)", min_value=0, value=int(total), step=1000)
                if paid >= total:
                    st.success(f"Tiền thừa: {vnd(paid - total)}")
                else:
                    st.error(f"Còn thiếu: {vnd(total - paid)}")

            can_checkout = not (payment == "Tiền mặt" and paid < total)
            if st.button("🧾 Xuất hoá đơn", type="primary", use_container_width=True, disabled=not can_checkout):
                order = {
                    "invoice_no": st.session_state.invoice_no,
                    "time": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                    "customer": customer.strip() or "Khách lẻ",
                    "items": list(st.session_state.cart),
                    "subtotal": subtotal,
                    "discount_pct": discount_pct,
                    "discount": discount,
                    "vat_pct": vat_pct,
                    "vat": vat,
                    "total": total,
                    "payment": payment,
                    "paid": paid,
                    "change": max(paid - total, 0),
                }
                st.session_state.history.append(order)
                st.session_state.last_invoice = order
                st.session_state.invoice_no += 1
                st.session_state.cart = []
                st.rerun()
        else:
            st.write("Giỏ hàng đang trống. Hãy thêm món ở bên trái.")

    if st.session_state.last_invoice:
        st.divider()
        st.subheader("Hoá đơn vừa xuất")
        invoice_text = build_invoice_text(st.session_state.last_invoice)
        st.code(invoice_text, language=None)
        st.download_button(
            "⬇️ Tải hoá đơn (.txt)",
            data=invoice_text,
            file_name=f"hoadon_{st.session_state.last_invoice['invoice_no']:05d}.txt",
            mime="text/plain",
        )

# ---------------------------- TAB 2: LỊCH SỬ --------------------------------
with tab_history:
    st.subheader("Lịch sử hoá đơn (phiên làm việc hiện tại)")
    if st.session_state.history:
        summary = pd.DataFrame(
            [
                {
                    "Số HĐ": f"{o['invoice_no']:05d}",
                    "Thời gian": o["time"],
                    "Khách": o["customer"],
                    "Số món": sum(i["SL"] for i in o["items"]),
                    "Tổng tiền": o["total"],
                    "Thanh toán": o["payment"],
                }
                for o in st.session_state.history
            ]
        )
        st.dataframe(summary, use_container_width=True, hide_index=True)
        st.download_button(
            "⬇️ Tải báo cáo (.csv)",
            data=summary.to_csv(index=False).encode("utf-8-sig"),
            file_name="lich_su_hoa_don.csv",
            mime="text/csv",
        )
        pick = st.selectbox(
            "Xem lại hoá đơn",
            range(len(st.session_state.history)),
            format_func=lambda i: f"HĐ {st.session_state.history[i]['invoice_no']:05d} - {st.session_state.history[i]['customer']}",
        )
        st.code(build_invoice_text(st.session_state.history[pick]), language=None)
    else:
        st.write("Chưa có hoá đơn nào.")

# ---------------------------- TAB 3: CHATBOT --------------------------------
with tab_chat:
    st.subheader("Trợ lý AI của quán")
    st.caption("Hỏi về menu, gợi ý món, topping, cách tính tiền... Chatbot biết cả giỏ hàng hiện tại.")

    if st.button("🧹 Xoá cuộc trò chuyện"):
        st.session_state.messages = []
        st.rerun()

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    user_input = st.chat_input("Nhập câu hỏi, ví dụ: Gợi ý món ít ngọt cho người mới thử?")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        api_key = get_api_key()
        with st.chat_message("assistant"):
            if not api_key:
                reply = "⚠️ Chưa có API key. Hãy nhập OpenRouter API Key ở thanh bên trái."
                st.markdown(reply)
            else:
                try:
                    reply = st.write_stream(stream_ai_reply(api_key, model))
                except Exception as e:
                    reply = f"⚠️ Lỗi khi gọi AI: {e}"
                    st.markdown(reply)
        st.session_state.messages.append({"role": "assistant", "content": reply})
