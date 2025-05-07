# -*- coding: utf-8 -*-
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
from agent.agent import create_agent
from agent.config import get_admin_password
from agent.db_utils import (
    add_product, get_all_products,
    update_product, delete_product
)

st.set_page_config(page_title="LLM SQL Агент", layout="centered")

def manage_products():
    st.header("📜 Управление товарами")

    products = get_all_products()
    if not products:
        st.info("Товары отсутствуют.")
        return

    for product in products:
        pid, name, price, category, description, image_blob = product
        with st.expander(f"🔹 {name} (ID: {pid})"):
            col1, col2 = st.columns([3, 1])
            with col1:
                new_name = st.text_input(f"Название {pid}", value=name, key=f"name_{pid}")
                new_price = st.number_input(f"Цена {pid}", value=price, key=f"price_{pid}")
                new_category = st.text_input(f"Категория {pid}", value=category, key=f"cat_{pid}")
                new_description = st.text_area(f"Описание {pid}", value=description or "", key=f"desc_{pid}")
                new_image = st.file_uploader(f"Загрузите новое изображение {pid}", type=["png", "jpg", "jpeg"], key=f"upload_{pid}")

                image_to_save = new_image.read() if new_image else image_blob

                if st.button("📏 Обновить", key=f"update_{pid}"):
                    update_product(pid, new_name, new_price, new_category, new_description, image_to_save)
                    st.success("✅ Товар обновлён.")

            with col2:
                if image_blob:
                    from PIL import Image
                    import io
                    try:
                        image = Image.open(io.BytesIO(image_blob))
                        st.image(image, caption="Фото товара", width=150)
                    except Exception:
                        st.warning("⚠️ Невозможно отобразить изображение.")

                if st.button("🗑️ Удалить", key=f"delete_{pid}"):
                    delete_product(pid)
                    st.warning(f"🗑️ Товар '{name}' удалён.")
                    st.experimental_rerun()

def admin_login():
    with st.expander("🔐 Вход для администратора"):
        password = st.text_input("Введите пароль:", type="password")
        if st.button("Войти"):
            if password == get_admin_password():
                st.session_state.is_admin = True
                st.success("✅ Успешный вход. Вы суперпользователь.")
            else:
                st.error("❌ Неверный пароль")

def handle_query():
    query = st.text_input("Введите запрос к базе данных:")
    if query:
        try:
            with st.spinner("Обрабатываю..."):
                response = st.session_state.agent.run(query)
            st.success("Ответ:")
            st.write(response)
        except Exception as e:
            st.error(f"❌ Ошибка: {e}")

def admin_panel():
    st.header("➕ Добавить новый товар")
    with st.form("add_product_form"):
        name = st.text_input("Название")
        price = st.number_input("Цена", min_value=0.0, step=0.01, format="%.2f")
        category = st.text_input("Категория")
        description = st.text_area("Описание")
        image_file = st.file_uploader("Загрузите изображение", type=["png", "jpg", "jpeg"])

        submitted = st.form_submit_button("Добавить товар")
        if submitted:
            if name.strip() and category.strip():
                try:
                    image_data = image_file.read() if image_file else None
                    add_product(name, price, category, description, image_data)
                    st.success(f"✅ Товар '{name}' добавлен в базу данных.")
                except Exception as e:
                    st.error(str(e))
            else:
                st.warning("⚠️ Название и категория обязательны для заполнения.")

if "agent" not in st.session_state:
    st.session_state.agent = create_agent()

if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

st.title("🤖 LLM SQL Агент")

admin_login()
handle_query()

if st.session_state.is_admin:
    admin_panel()
    manage_products()
else:
    st.info("ℹ️ Для администрирования войдите как администратор выше.")

