import folium
import streamlit as st
from streamlit_folium import st_folium

from clients.maps import get_coords_by_address, get_static_map_url
from model.ml_process import render_garage_data

# константы
ZOOM = 16
DEFAULT_CENTER = [60.0020, 30.3976]

# контроль состояний приложения
if "map_center" not in st.session_state:
    st.session_state.map_center = DEFAULT_CENTER

if "step" not in st.session_state:
    st.session_state.step = "start"  # ["start", "found", "checked"]


# управление приложением
def start_search():
    st.session_state.step = "found"


def check_in_registry():
    st.session_state.step = "checked"


def reset():
    st.session_state.map_center = DEFAULT_CENTER
    st.session_state.step = "start"
    st.rerun()


# UI
st.subheader("Детектор незаконных гаражей (и не только 😊)")
st.write(
    "Укажите область на карте — мы найдём подозрительные объекты "
    "и проверим их в Росреестре."
)

# шаг 1: ввод адреса
if st.session_state.step == "start":
    address = st.text_input(
        "Введите адрес для центровки карты",
        placeholder="Например: Санкт-Петербург, улица Бутлерова",
    )

    if address:
        try:
            coords = get_coords_by_address(address)
            lat, lon = map(float, coords.split(","))
            st.session_state.map_center = [lat, lon]
        except Exception:
            st.warning("Не удалось найти адрес. Проверьте, что в нём нет опечаток.")

    # карта
    st.write("...или просто переместите карту, чтобы выбрать нужную область:")
    m = folium.Map(
        location=st.session_state.map_center,
        zoom_start=ZOOM,
        tiles="OpenStreetMap",
        zoom_control=False,
        scrollWheelZoom=False,
        dragging=True,
    )
    output = st_folium(
        m,
        width="100%",
        height=400,
        key="map",
        returned_objects=["center"],
    )

    # обновляем центр, если карта двигалась
    if output and "center" in output:
        st.session_state.map_center = [
            output["center"]["lat"],
            output["center"]["lng"],
        ]

    st.button("Найти объекты", width="stretch", on_click=start_search)

# шаг 2: передача карты в модель
elif st.session_state.step == "found":
    lat, lon = st.session_state.map_center
    coords_str = f"{lat},{lon}"
    image_url = get_static_map_url(lat, lon)

    left, right = st.columns(2)

    with left:
        st.image(
            image_url,
            caption=f"Область поиска объектов ({lat:.5f}, {lon:.5f})",
            width="stretch",
        )

    with right:
        # Получаем и отображаем таблицу найденных объектов
        table_data = render_garage_data("found", coords_str)
        if table_data:
            st.write("##### Найденные объекты")
            st.table(table_data)
        else:
            st.info("Подозрительные объекты не обнаружены. Выберите другую область :)")

        # Кнопки
        st.button(
            "Проверить объекты в Росреестре",
            width="stretch",
            type="primary",
            on_click=check_in_registry,
        )
        st.button("← Назад", width="stretch", on_click=reset)

# шаг 3: проверка в Росреестре
elif st.session_state.step == "checked":
    lat, lon = st.session_state.map_center
    coords_str = f"{lat},{lon}"
    image_url = get_static_map_url(lat, lon)

    left, right = st.columns(2)

    with left:
        st.image(image_url, caption="Область поиска", width="stretch")

    with right:
        # Получаем и отображаем ОБОГАЩЁННУЮ таблицу
        table_data = render_garage_data("checked", coords_str)
        if table_data:
            st.write("##### Найденные объекты")
            st.table(table_data)
        else:
            st.info("Нет данных для отображения")

        st.button("Начать новый поиск", width="stretch", on_click=reset)

# README.md внизу страницы
with st.expander("Как это работает"):
    with open("README.md", "r", encoding="utf-8") as f:
        st.markdown(f.read())
