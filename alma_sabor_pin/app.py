import streamlit as st
from dataclasses import dataclass, field
from typing import Dict, List, Any


# ============================================================
#  CONFIGURACIÓN GENERAL
# ============================================================
st.set_page_config(
    page_title="Ordify - Sistema de Gestión",
    page_icon="",
    layout="wide"
)


# ============================================================
#  ESTILOS GLOBALES (CSS – etapas 2 y 3)
# ============================================================

def aplicar_css_global():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;700&display=swap');

        html, body, [class*="css"] {
            font-family: 'Montserrat', sans-serif;
        }

        /* Fondo general oscuro elegante */
        body {
            background: #020617;
        }
        .main .block-container {
            padding-top: 1.5rem;
            padding-bottom: 2rem;
            max-width: 1100px;
        }

        /* NAVBAR SUPERIOR */
        .ordify-topbar {
            background: #020617;
            border-bottom: 1px solid #1f2933;
            padding: 0.6rem 1.2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
            position: sticky;
            top: 0;
            z-index: 999;
        }
        .ordify-brand {
            display: flex;
            flex-direction: column;
        }
        .ordify-logo {
            font-weight: 700;
            font-size: 1.1rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: #f97316;
        }
        .ordify-subtitle {
            font-size: 0.8rem;
            color: #9ca3af;
        }
        .ordify-right {
            display: flex;
            align-items: center;
            gap: 0.75rem;
        }
        .ordify-role {
            font-size: 0.9rem;
            color: #e5e7eb;
        }
        .ordify-logout button {
            background: #ef4444 !important;
            color: #f9fafb !important;
            border-radius: 999px !important;
            padding: 0.35rem 1.1rem !important;
            border: none !important;
            font-size: 0.85rem !important;
        }
        .ordify-logout button:hover {
            background: #b91c1c !important;
        }

        /* TABS EN CARD CON SOMBRA */
        div[data-testid="stTabs"] {
            background: #0b1120;
            border-radius: 1rem;
            padding: 0.8rem 1.2rem 1.2rem 1.2rem;
            box-shadow: 0 18px 35px rgba(0,0,0,0.55);
            border: 1px solid #1f2937;
        }

        /* Secciones tipo card */
        .ordify-section {
            background: #020617;
            border-radius: 1rem;
            padding: 1rem 1.3rem;
            margin-bottom: 1rem;
            box-shadow: 0 12px 30px rgba(0,0,0,0.55);
            border: 1px solid #111827;
        }

        /* Títulos */
        h1, h2, h3, h4 {
            color: #f9fafb !important;
        }
        .ordify-section h3 {
            margin-top: 0.2rem;
        }

        /* Tablas */
        table {
            font-size: 0.85rem;
        }

        /* Botones principales */
        .stButton button {
            border-radius: 999px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
#  CLASES BASE (pensadas para futura integración con SQL)
# ============================================================

@dataclass
class Usuario:
    pin: str
    rol: str
    nombre: str


@dataclass
class Mesa:
    numero: int
    comensales: int
    estado: str = "activa"  # activa, cerrada, etc.


@dataclass
class Pedido:
    id: int
    mesa_numero: int
    items: List[Dict[str, Any]]          # [{nombre, cantidad, tipo}]
    estado: str = "pendiente"            # pendiente, entregado, cancelado
    creado_por: str = ""
    produccion_estados: Dict[str, str] = field(default_factory=dict)
    # produccion_estados: {"comida_italiana": "pendiente"|"enviado", ...}


# ============================================================
#  DATOS INICIALES (USUARIOS + INVENTARIO)
# ============================================================

def get_usuarios_predefinidos() -> Dict[str, Usuario]:
    """Base de usuarios predefinida, indexada por PIN."""
    return {
        "000000": Usuario(pin="000000", rol="admin",          nombre="Administrador"),
        "111111": Usuario(pin="111111", rol="mesero",         nombre="Mesero"),
        "222222": Usuario(pin="222222", rol="chef_italiano",  nombre="Chef Italiano"),
        "333333": Usuario(pin="333333", rol="chef_mexicano",  nombre="Chef Mexicano"),
        "444444": Usuario(pin="444444", rol="barista",        nombre="Barista"),
    }


def get_inventario_inicial() -> Dict[str, Dict[str, Dict[str, float]]]:
    """Inventario hardcodeado (simulación, luego se migrará a SQL Server)."""
    return {
        "comida_italiana": {
            "Pizza Margherita": {"stock": 15, "precio": 12.99},
            "Lasagna": {"stock": 8, "precio": 14.50},
        },
        "comida_mexicana": {
            "Tacos": {"stock": 20, "precio": 10.99},
            "Burrito": {"stock": 12, "precio": 11.50},
        },
        "bebidas": {
            "Café": {"stock": 50, "precio": 3.99},
            "Jugo Natural": {"stock": 25, "precio": 4.50},
        },
    }


# ============================================================
#  INICIALIZACIÓN DE ESTADO
# ============================================================

def inicializar_session_state():
    if "usuarios" not in st.session_state:
        st.session_state.usuarios = get_usuarios_predefinidos()

    if "inventario" not in st.session_state:
        st.session_state.inventario = get_inventario_inicial()

    if "mesas" not in st.session_state:
        st.session_state.mesas: List[Mesa] = []

    if "pedidos" not in st.session_state:
        st.session_state.pedidos: List[Pedido] = []

    if "usuario_actual" not in st.session_state:
        st.session_state.usuario_actual = None


# ============================================================
#  FUNCIONES DE NEGOCIO
# ============================================================

def autenticar_pin(pin: str):
    usuarios = st.session_state.usuarios
    return usuarios.get(pin)


def crear_mesa(numero: int, comensales: int) -> bool:
    for mesa in st.session_state.mesas:
        if mesa.numero == numero:
            return False
    st.session_state.mesas.append(Mesa(numero=numero, comensales=comensales))
    return True


def generar_nuevo_id_pedido() -> int:
    if not st.session_state.pedidos:
        return 1
    return max(p.id for p in st.session_state.pedidos) + 1


def crear_pedido(mesa_num: int, items_list: List[Dict[str, Any]], creador: str) -> Pedido:
    """Registra un nuevo pedido con items de varias categorías."""
    inventario = st.session_state.inventario
    produccion_estados: Dict[str, str] = {}

    # Descontar stock y detectar qué estaciones participan
    for item in items_list:
        tipo = item["tipo"]
        nombre = item["nombre"]
        cantidad = item["cantidad"]
        inv_item = inventario[tipo][nombre]
        inv_item["stock"] -= cantidad
        if tipo not in produccion_estados:
            produccion_estados[tipo] = "pendiente"

    nuevo_pedido = Pedido(
        id=generar_nuevo_id_pedido(),
        mesa_numero=mesa_num,
        items=items_list,
        estado="pendiente",
        creado_por=creador,
        produccion_estados=produccion_estados,
    )
    st.session_state.pedidos.append(nuevo_pedido)
    return nuevo_pedido


def filtrar_pedidos_por_estacion(tipo: str) -> List[Pedido]:
    """Pedidos pendientes para una estación (chef/barista)."""
    res = []
    for p in st.session_state.pedidos:
        if p.produccion_estados.get(tipo) == "pendiente":
            # Debe haber al menos un item de ese tipo
            if any(it["tipo"] == tipo for it in p.items):
                res.append(p)
    return res


def obtener_pedidos_por_mesa(mesa_num: int) -> List[Pedido]:
    """Obtiene todos los pedidos (no cancelados) de una mesa."""
    return [
        p for p in st.session_state.pedidos
        if p.mesa_numero == mesa_num and p.estado != "cancelado"
    ]


def calcular_total_pedido(p: Pedido) -> float:
    total = 0.0
    inventario = st.session_state.inventario
    for it in p.items:
        tipo = it["tipo"]
        nombre = it["nombre"]
        cant = it["cantidad"]
        precio = inventario[tipo][nombre]["precio"]
        total += precio * cant
    return total


def eliminar_pedido_por_id(pedido_id: int):
    st.session_state.pedidos = [p for p in st.session_state.pedidos if p.id != pedido_id]


def eliminar_mesa_por_numero(mesa_num: int):
    st.session_state.mesas = [m for m in st.session_state.mesas if m.numero != mesa_num]


# ============================================================
#  NAVBAR
# ============================================================

def render_topbar():
    usuario = st.session_state.usuario_actual
    rol_str = "Sin sesión" if usuario is None else usuario.rol.replace("_", " ").title()

    st.markdown(
        """
        <div class="ordify-topbar">
            <div class="ordify-brand">
                <span class="ordify-logo">ORDIFY</span>
                <span class="ordify-subtitle">Panel de gestión · Restaurante Alma & Sabor</span>
            </div>
            <div class="ordify-right">
                <span class="ordify-role">Rol: """ + rol_str + """</span>
        """,
        unsafe_allow_html=True,
    )

    col1, col2, col3 = st.columns([6, 1, 1])
    with col2:
        st.empty()
    with col3:
        if usuario is not None:
            # botón de logout arriba a la derecha
            with st.container():
                st.markdown('<div class="ordify-logout">', unsafe_allow_html=True)
                if st.button("Cerrar sesión", key="logout_btn"):
                    st.session_state.usuario_actual = None
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)  # cierra ordify-topbar


# ============================================================
#  VISTAS / UI
# ============================================================

def vista_login():
    st.markdown('<div class="ordify-section">', unsafe_allow_html=True)
    st.title("Ordify")
    st.subheader("Acceso al sistema de gestión")
    st.markdown("### Inicio de sesión por PIN (6 dígitos)")

    with st.form("form_login"):
        pin = st.text_input("PIN", max_chars=6, type="password", help="Ingresa tu PIN de 6 dígitos")
        submitted = st.form_submit_button("Ingresar")

    if submitted:
        if len(pin) != 6 or not pin.isdigit():
            st.error("El PIN debe tener exactamente 6 dígitos numéricos.")
        else:
            usuario = autenticar_pin(pin)
            if usuario is None:
                st.error("PIN inválido. Verifica tus datos.")
            else:
                st.session_state.usuario_actual = usuario
                st.success(f"Bienvenido, {usuario.nombre} ({usuario.rol}).")
                st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)


def vista_admin_mesero():
    usuario: Usuario = st.session_state.usuario_actual

    st.sidebar.markdown(f"**Usuario:** {usuario.nombre}")
    st.sidebar.markdown(f"**Rol:** {usuario.rol.capitalize()}")

    # Tabs dentro de card
    st.markdown('<div class="ordify-section">', unsafe_allow_html=True)
    tabs = st.tabs(["Mesas", "Pedidos", "Inventario", "Cuentas"])
    st.markdown('</div>', unsafe_allow_html=True)

    # ----------------------- TAB MESAS -----------------------
    with tabs[0]:
        st.markdown('<div class="ordify-section">', unsafe_allow_html=True)
        st.subheader("Gestión de mesas")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Crear nueva mesa")
            with st.form("form_mesa"):
                num_mesa = st.number_input("Número de mesa", min_value=1, step=1)
                comensales = st.number_input("Número de comensales", min_value=1, step=1)
                crear = st.form_submit_button("Crear mesa")

            if crear:
                if crear_mesa(int(num_mesa), int(comensales)):
                    st.success("Mesa creada correctamente.")
                else:
                    st.error("Ya existe una mesa con ese número.")

        with col2:
            st.markdown("#### Mesas registradas")
            if st.session_state.mesas:
                data = [
                    {"Mesa": m.numero, "Comensales": m.comensales, "Estado": m.estado}
                    for m in st.session_state.mesas
                ]
                st.table(data)
            else:
                st.info("No hay mesas registradas.")
        st.markdown('</div>', unsafe_allow_html=True)

    # ----------------------- TAB PEDIDOS -----------------------
    with tabs[1]:
        st.markdown('<div class="ordify-section">', unsafe_allow_html=True)
        st.subheader("Gestión de pedidos")

        if not st.session_state.mesas:
            st.warning("Primero debes registrar al menos una mesa.")
        else:
            col1, col2 = st.columns([2, 1])

            # FORM NUEVO PEDIDO (mezcla de categorías, AHORA CON LISTAS DESPLEGABLES)
            with col1:
                st.markdown("### Crear nuevo pedido")

                mesa_opciones = [m.numero for m in st.session_state.mesas]
                mesa_seleccionada = st.selectbox("Mesa", mesa_opciones)

                inventario = st.session_state.inventario
                items_seleccionados: List[Dict[str, Any]] = []

                st.markdown("#### Selecciona platillos por categoría")

                # CAMBIO: selects por categoría en lugar de un campo por producto
                for tipo, items_cat in inventario.items():
                    st.markdown(f"##### {tipo.replace('_', ' ').title()}")

                    # Construimos labels bonitos para el select
                    opciones = ["-- Ninguno --"]
                    label_to_name: Dict[str, str] = {}
                    for nombre_item, info in items_cat.items():
                        label = f"{nombre_item} (stock: {info['stock']}, precio: ${info['precio']})"
                        opciones.append(label)
                        label_to_name[label] = nombre_item

                    seleccion = st.selectbox(
                        "Producto",
                        opciones,
                        key=f"select_{tipo}"
                    )

                    if seleccion != "-- Ninguno --":
                        nombre_elegido = label_to_name[seleccion]
                        stock_disp = items_cat[nombre_elegido]["stock"]
                        cantidad = st.number_input(
                            f"Cantidad para {nombre_elegido}",
                            min_value=1,
                            max_value=stock_disp,
                            value=1,
                            step=1,
                            key=f"qty_{tipo}"
                        )
                        items_seleccionados.append({
                            "nombre": nombre_elegido,
                            "cantidad": int(cantidad),
                            "tipo": tipo,
                        })
                # FIN CAMBIO

                if st.button("Confirmar pedido"):
                    if not items_seleccionados:
                        st.error("Debes seleccionar al menos un producto.")
                    else:
                        pedido = crear_pedido(
                            mesa_num=int(mesa_seleccionada),
                            items_list=items_seleccionados,
                            creador=usuario.nombre
                        )
                        st.success(f"Pedido {pedido.id} creado correctamente.")
                        st.balloons()

            # LISTADO Y ACCIONES SOBRE PEDIDOS
            with col2:
                st.markdown("### Pedidos activos")
                pedidos_visibles = [p for p in st.session_state.pedidos if p.estado != "entregado"]

                if pedidos_visibles:
                    data_ped = []
                    for p in pedidos_visibles:
                        total = calcular_total_pedido(p)
                        tipos = sorted(set(it["tipo"] for it in p.items))
                        tipos_str = " / ".join(t.replace("_", " ").title() for t in tipos)
                        data_ped.append({
                            "ID": p.id,
                            "Mesa": p.mesa_numero,
                            "Tipos": tipos_str,
                            "Estado": p.estado,
                            "Total aprox": round(total, 2),
                        })
                    st.table(data_ped)

                    ids = [p.id for p in pedidos_visibles]
                    ped_sel = st.selectbox("Selecciona ID de pedido", ids)

                    pedido_obj = next(p for p in st.session_state.pedidos if p.id == ped_sel)
                    st.write(f"Pedido #{pedido_obj.id} - Mesa {pedido_obj.mesa_numero}")
                    st.write(f"Estado actual: **{pedido_obj.estado}**")

                    detalle_rows = []
                    inventario = st.session_state.inventario
                    for it in pedido_obj.items:
                        tipo = it["tipo"]
                        nombre = it["nombre"]
                        cant = it["cantidad"]
                        precio = inventario[tipo][nombre]["precio"]
                        subtotal = precio * cant
                        detalle_rows.append({
                            "Tipo": tipo.replace("_", " ").title(),
                            "Producto": nombre,
                            "Cantidad": cant,
                            "Precio": precio,
                            "Subtotal": round(subtotal, 2),
                        })
                    st.table(detalle_rows)

                    if st.button("Marcar como ENTREGADO"):
                        pedido_obj.estado = "entregado"
                        st.success("Estado actualizado a ENTREGADO. El pedido ya no aparecerá en esta lista.")
                        st.rerun()

                    if usuario.rol == "admin":
                        if st.button("Eliminar pedido"):
                            eliminar_pedido_por_id(pedido_obj.id)
                            st.warning("Pedido eliminado.")
                            st.rerun()
                else:
                    st.info("No hay pedidos activos (todos entregados o sin pedidos).")
        st.markdown('</div>', unsafe_allow_html=True)

    # ----------------------- TAB INVENTARIO -----------------------
    with tabs[2]:
        st.markdown('<div class="ordify-section">', unsafe_allow_html=True)
        st.subheader("Inventario (solo lectura)")

        inventario = st.session_state.inventario
        for categoria, items in inventario.items():
            st.markdown(f"#### {categoria.replace('_', ' ').title()}")
            data_inv = []
            for nombre_item, info in items.items():
                data_inv.append({
                    "Producto": nombre_item,
                    "Stock": info["stock"],
                    "Precio": info["precio"],
                })
            st.table(data_inv)
        st.markdown('</div>', unsafe_allow_html=True)

    # ----------------------- TAB CUENTAS -----------------------
    with tabs[3]:
        st.markdown('<div class="ordify-section">', unsafe_allow_html=True)
        st.subheader("Cuentas por mesa")

        if not st.session_state.mesas:
            st.info("No hay mesas activas para cobrar.")
        else:
            mesas_nums = [m.numero for m in st.session_state.mesas]
            mesa_sel = st.selectbox("Selecciona la mesa para cobrar", mesas_nums, key="mesa_cobro")

            mesa_obj = next(m for m in st.session_state.mesas if m.numero == mesa_sel)
            pedidos_mesa = obtener_pedidos_por_mesa(mesa_sel)

            if not pedidos_mesa:
                st.warning("Esta mesa no tiene pedidos registrados (o todos fueron cancelados).")
            else:
                if st.button("Calcular cuenta"):
                    st.markdown("### Resumen de cuenta")
                    st.write(f"**Mesa:** {mesa_obj.numero}")
                    st.write(f"**Comensales:** {mesa_obj.comensales}")

                    consumo_rows = []
                    total_general = 0.0
                    inventario = st.session_state.inventario

                    for p in pedidos_mesa:
                        for it in p.items:
                            tipo = it["tipo"]
                            nombre = it["nombre"]
                            cant = it["cantidad"]
                            precio = inventario[tipo][nombre]["precio"]
                            subtotal = precio * cant
                            total_general += subtotal
                            consumo_rows.append({
                                "Pedido ID": p.id,
                                "Tipo": tipo.replace("_", " ").title(),
                                "Producto": nombre,
                                "Cantidad": cant,
                                "Precio": precio,
                                "Subtotal": round(subtotal, 2),
                            })

                    st.table(consumo_rows)
                    st.write(f"### Total a pagar: **${round(total_general, 2)}**")

                    if st.button("Confirmar pago y cerrar mesa"):
                        eliminar_mesa_por_numero(mesa_obj.numero)
                        st.success(f"La mesa {mesa_obj.numero} ha sido cobrada y eliminada del sistema.")
                        st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)


def vista_chef_barista():
    usuario: Usuario = st.session_state.usuario_actual

    st.sidebar.markdown(f"**Usuario:** {usuario.nombre}")
    st.sidebar.markdown(f"**Rol:** {usuario.rol.replace('_', ' ').title()}")

    st.markdown('<div class="ordify-section">', unsafe_allow_html=True)
    st.subheader("Pedidos pendientes por estación")

    mapa_rol_tipo = {
        "chef_italiano": "comida_italiana",
        "chef_mexicano": "comida_mexicana",
        "barista": "bebidas",
    }
    tipo = mapa_rol_tipo.get(usuario.rol)

    if not tipo:
        st.error("Rol no reconocido para vista de cocina/bar.")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    pedidos = filtrar_pedidos_por_estacion(tipo)

    if not pedidos:
        st.info("No hay pedidos pendientes para tu estación.")
    else:
        for p in sorted(pedidos, key=lambda x: x.id):
            with st.expander(f"Pedido #{p.id} - Mesa {p.mesa_numero}"):
                st.write(f"Estado general del pedido: {p.estado}")
                st.write(f"Creado por: {p.creado_por}")
                st.write("Detalle de productos para tu estación:")

                rows = []
                total = 0.0
                inventario = st.session_state.inventario
                for it in p.items:
                    if it["tipo"] != tipo:
                        continue
                    nombre = it["nombre"]
                    cant = it["cantidad"]
                    precio = inventario[tipo][nombre]["precio"]
                    subtotal = precio * cant
                    total += subtotal
                    rows.append({
                        "Producto": nombre,
                        "Cantidad": cant,
                        "Precio": precio,
                        "Subtotal": round(subtotal, 2),
                    })
                st.table(rows)
                st.write(f"**Total aprox para esta estación:** ${round(total, 2)}")

                if st.button("Pedido enviado", key=f"enviado_{tipo}_{p.id}"):
                    p.produccion_estados[tipo] = "enviado"
                    st.success("Pedido marcado como enviado para esta estación.")
                    st.rerun()

    st.caption("Vista de solo lectura sobre el pedido. Solo se marca como enviado para sacar de la lista.")
    st.markdown('</div>', unsafe_allow_html=True)


# ============================================================
#  CONTROL PRINCIPAL
# ============================================================

def main():
    aplicar_css_global()
    inicializar_session_state()

    usuario = st.session_state.usuario_actual
    render_topbar()

    if usuario is None:
        vista_login()
    else:
        if usuario.rol in ("admin", "mesero"):
            vista_admin_mesero()
        elif usuario.rol in ("chef_italiano", "chef_mexicano", "barista"):
            vista_chef_barista()
        else:
            st.error("Rol no soportado en esta versión.")


if __name__ == "__main__":
    main()