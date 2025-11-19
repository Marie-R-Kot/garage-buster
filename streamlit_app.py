import folium
from folium import Element
import streamlit as st
from streamlit_folium import st_folium

from clients.map_manager import get_coords_by_address, get_url
from table_processing import render_garage_data
from model.ml_process import get_coords_from_model
from clients.rosreestr import return_results_from_reestr

# константы для изначальной карты
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
        zoom_control=False,
        scrollWheelZoom=False,
        dragging=True,
    )

    # убираем надписи в виджете
    css_hide_attribution = """
    <style>
    .leaflet-control-attribution {
        display: none !important;
    }
    </style>
    """
    m.get_root().header.add_child(Element(css_hide_attribution))

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
    # свойста текущего участка карты для провери 
    st.session_state.lat, st.session_state.lon = st.session_state.map_center
    st.session_state.coords_str = f"{round(st.session_state.lat, 6)},{round(st.session_state.lon, 6)}"
    st.session_state.image_url = get_url([st.session_state.lat, st.session_state.lon])
    # запрос в модель
    st.session_state.garage_coords = get_coords_from_model([st.session_state.lat, st.session_state.lon])

    left, right = st.columns(2)

    with left:
        st.image(
            st.session_state.image_url,
            caption=f"Центр области поиска объектов ({st.session_state.lat:.6f}, {st.session_state.lon:.6f})",
            width="stretch",
        )

    with right:
        # отображаем таблицу найденных объектов
        if st.session_state.garage_coords:
            table_data = render_garage_data("found", st.session_state.garage_coords)
            st.write("##### Найденные объекты")
            st.table(table_data)
            
            st.button(
                "Проверить объекты в Росреестре",
                width="stretch",
                type="primary",
                on_click=check_in_registry,
            )
        else:
            st.info("Подозрительные объекты не обнаружены. Выберите другую область :)")

        # Кнопки
        st.button("← Назад", width="stretch", on_click=reset)

# шаг 3: проверка в Росреестре
elif st.session_state.step == "checked":
    # запрос в росеестр
    property_states = return_results_from_reestr(st.session_state.garage_coords)

    left, right = st.columns(2)

    with left:
            st.image(
                st.session_state.image_url,
                caption=f"Центр области поиска объектов ({st.session_state.lat:.6f}, {st.session_state.lon:.6f})",
                width="stretch",
            )

    with right:
        # отображаем уже обогащённую Росреестром таблицу
        table_data = render_garage_data("checked", st.session_state.garage_coords, property_states)
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
