--
-- PostgreSQL database dump
--

\restrict 90G68rgrFMb9c8EU1crCnDSevA8cDYQzWg6jeNr1BmhgbCbr3miI7dklL73mryC

-- Dumped from database version 18.0 (Debian 18.0-1.pgdg13+3)
-- Dumped by pg_dump version 18.0 (Debian 18.0-1.pgdg13+3)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: agente; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.agente (
    id_agente integer NOT NULL,
    id_pais integer NOT NULL,
    nombre character varying(100) NOT NULL,
    correo character varying(100),
    telefono character varying(50),
    por_defecto boolean NOT NULL
);


--
-- Name: agente_id_agente_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.agente_id_agente_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: agente_id_agente_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.agente_id_agente_seq OWNED BY public.agente.id_agente;


--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


--
-- Name: bodega; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.bodega (
    id_bodega integer NOT NULL,
    nombre character varying(200) NOT NULL,
    direccion character varying(200)
);


--
-- Name: bodega_id_bodega_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.bodega_id_bodega_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: bodega_id_bodega_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.bodega_id_bodega_seq OWNED BY public.bodega.id_bodega;


--
-- Name: ciudad; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ciudad (
    id_ciudad integer NOT NULL,
    id_pais integer NOT NULL,
    nombre character varying(200) NOT NULL
);


--
-- Name: ciudad_id_ciudad_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.ciudad_id_ciudad_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ciudad_id_ciudad_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.ciudad_id_ciudad_seq OWNED BY public.ciudad.id_ciudad;


--
-- Name: clase; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.clase (
    id_clase integer NOT NULL,
    nombre character varying(100) NOT NULL,
    descripcion character varying(100)
);


--
-- Name: clase_id_clase_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.clase_id_clase_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: clase_id_clase_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.clase_id_clase_seq OWNED BY public.clase.id_clase;


--
-- Name: clausula_venta; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.clausula_venta (
    id_clausula_venta character varying(10) NOT NULL
);


--
-- Name: cliente_proveedor; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.cliente_proveedor (
    id_cliente_proveedor integer NOT NULL,
    rut character varying(15),
    nombre_fantasia character varying(200) NOT NULL,
    razon_social character varying(200) NOT NULL,
    es_nacional boolean NOT NULL,
    giro character varying(200),
    es_cliente boolean NOT NULL,
    es_proveedor boolean NOT NULL
);


--
-- Name: cliente_proveedor_id_cliente_proveedor_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.cliente_proveedor_id_cliente_proveedor_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: cliente_proveedor_id_cliente_proveedor_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.cliente_proveedor_id_cliente_proveedor_seq OWNED BY public.cliente_proveedor.id_cliente_proveedor;


--
-- Name: contacto; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.contacto (
    id_contacto integer NOT NULL,
    nombre character varying(100) NOT NULL,
    correo character varying(100),
    telefono character varying(50),
    id_cliente_proveedor integer NOT NULL
);


--
-- Name: contacto_id_contacto_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.contacto_id_contacto_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: contacto_id_contacto_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.contacto_id_contacto_seq OWNED BY public.contacto.id_contacto;


--
-- Name: contacto_orden_compra; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.contacto_orden_compra (
    id_contacto_orden_compra integer NOT NULL,
    id_orden_compra integer,
    id_contacto integer
);


--
-- Name: contacto_orden_compra_id_contacto_orden_compra_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.contacto_orden_compra_id_contacto_orden_compra_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: contacto_orden_compra_id_contacto_orden_compra_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.contacto_orden_compra_id_contacto_orden_compra_seq OWNED BY public.contacto_orden_compra.id_contacto_orden_compra;


--
-- Name: contacto_proforma; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.contacto_proforma (
    id_contacto_proforma integer NOT NULL,
    id_contacto integer,
    id_proforma integer
);


--
-- Name: contacto_proforma_id_contacto_proforma_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.contacto_proforma_id_contacto_proforma_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: contacto_proforma_id_contacto_proforma_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.contacto_proforma_id_contacto_proforma_seq OWNED BY public.contacto_proforma.id_contacto_proforma;


--
-- Name: contenedor; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.contenedor (
    id_contenedor integer NOT NULL,
    nombre character varying(50) NOT NULL,
    tara numeric(12,3),
    peso_maximo numeric(12,3)
);


--
-- Name: contenedor_id_contenedor_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.contenedor_id_contenedor_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: contenedor_id_contenedor_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.contenedor_id_contenedor_seq OWNED BY public.contenedor.id_contenedor;


--
-- Name: detalle_factura; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.detalle_factura (
    id_detalle_factura integer NOT NULL,
    id_factura integer NOT NULL,
    cantidad character varying(12) NOT NULL,
    especificaciones character varying(300) NOT NULL,
    precio_unitario character varying(12) NOT NULL,
    total character varying(12) NOT NULL
);


--
-- Name: detalle_factura_id_detalle_factura_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.detalle_factura_id_detalle_factura_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: detalle_factura_id_detalle_factura_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.detalle_factura_id_detalle_factura_seq OWNED BY public.detalle_factura.id_detalle_factura;


--
-- Name: detalle_gasto; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.detalle_gasto (
    id_detalle_gasto integer NOT NULL,
    id_gasto integer,
    valor character varying(12) NOT NULL,
    nro_documento character varying(50),
    pagado boolean NOT NULL
);


--
-- Name: detalle_gasto_id_detalle_gasto_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.detalle_gasto_id_detalle_gasto_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: detalle_gasto_id_detalle_gasto_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.detalle_gasto_id_detalle_gasto_seq OWNED BY public.detalle_gasto.id_detalle_gasto;


--
-- Name: detalle_ide; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.detalle_ide (
    id_detalle_ide integer NOT NULL,
    id_ide integer NOT NULL,
    id_plc integer NOT NULL,
    fob character varying(12) NOT NULL,
    identificador_contenedor character varying(50),
    sello character varying(50),
    peso_neto character varying(12),
    peso_bruto character varying(12),
    nro_linea integer NOT NULL
);


--
-- Name: detalle_ide_id_detalle_ide_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.detalle_ide_id_detalle_ide_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: detalle_ide_id_detalle_ide_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.detalle_ide_id_detalle_ide_seq OWNED BY public.detalle_ide.id_detalle_ide;


--
-- Name: detalle_orden_compra; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.detalle_orden_compra (
    id_detalle_odc integer NOT NULL,
    id_orden_compra integer NOT NULL,
    id_producto integer,
    id_unidad_venta integer,
    texto_abierto character varying(200),
    espesor character varying(20),
    id_unidad_medida_espesor integer,
    ancho character varying(20),
    id_unidad_medida_ancho integer,
    largo character varying(20),
    id_unidad_medida_largo integer,
    cantidad numeric(12,3),
    precio_unitario numeric(12,3),
    subtotal numeric(12,3),
    volumen numeric(12,3),
    volumen_eq numeric(12,3),
    precio_eq numeric(12,3),
    odc_salida integer
);


--
-- Name: detalle_orden_compra_id_detalle_odc_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.detalle_orden_compra_id_detalle_odc_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: detalle_orden_compra_id_detalle_odc_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.detalle_orden_compra_id_detalle_odc_seq OWNED BY public.detalle_orden_compra.id_detalle_odc;


--
-- Name: detalle_pl; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.detalle_pl (
    id_detalle_pl integer NOT NULL,
    id_ple integer,
    id_plc integer,
    etiqueta character varying(20) NOT NULL,
    descripcion character varying(100) NOT NULL,
    id_unidad_venta integer NOT NULL,
    cantidad integer,
    espesor_ple character varying(20) NOT NULL,
    id_unidad_medida_espesor_ple integer NOT NULL,
    ancho_ple character varying(20) NOT NULL,
    id_unidad_medida_ancho_ple integer NOT NULL,
    largo_ple character varying(20) NOT NULL,
    id_unidad_medida_largo_ple integer NOT NULL,
    piezas integer NOT NULL,
    volumen_ple numeric(12,3) NOT NULL,
    costo_eq_m3 numeric(12,3),
    costo_paquete numeric(12,3),
    id_estado_detalle_ple integer NOT NULL,
    venta_eq_m3 numeric(12,3),
    venta_unitario numeric(12,3),
    venta_paquete numeric(12,3) NOT NULL,
    operacion_exportacion integer,
    odc integer,
    id_unidad_medida_espesor_plc integer,
    id_unidad_medida_ancho_plc integer,
    id_unidad_medida_largo_plc integer,
    espesor_plc character varying(20),
    ancho_plc character varying(20),
    largo_plc character varying(20),
    volumen_plc numeric(12,3),
    costo_unitario numeric(12,3),
    pulgada_cubica numeric(12,3),
    metro_lineal numeric(12,3),
    pie numeric(12,3)
);


--
-- Name: detalle_pl_id_detalle_pl_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.detalle_pl_id_detalle_pl_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: detalle_pl_id_detalle_pl_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.detalle_pl_id_detalle_pl_seq OWNED BY public.detalle_pl.id_detalle_pl;


--
-- Name: detalle_proforma; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.detalle_proforma (
    id_detalle_proforma integer NOT NULL,
    id_proforma integer NOT NULL,
    id_producto integer,
    id_unidad_venta integer NOT NULL,
    texto_libre character varying(200),
    espesor character varying(20),
    id_unidad_medida_espesor integer,
    ancho character varying(20),
    id_unidad_medida_ancho integer,
    largo character varying(20),
    id_unidad_medida_largo integer,
    piezas integer,
    cantidad character varying(12) NOT NULL,
    precio_unitario character varying(12) NOT NULL,
    subtotal character varying(12) NOT NULL,
    volumen character varying(12),
    volumen_eq character varying(12) NOT NULL,
    precio_eq character varying(12) NOT NULL,
    producto_nombre_esp character varying(100),
    producto_nombre_ing character varying(100),
    producto_obs_calidad character varying(2000),
    producto_especie character varying(100)
);


--
-- Name: detalle_proforma_id_detalle_proforma_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.detalle_proforma_id_detalle_proforma_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: detalle_proforma_id_detalle_proforma_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.detalle_proforma_id_detalle_proforma_seq OWNED BY public.detalle_proforma.id_detalle_proforma;


--
-- Name: direccion; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.direccion (
    id_direccion integer NOT NULL,
    direccion character varying(200) NOT NULL,
    id_ciudad integer NOT NULL,
    continente character varying(15),
    fono_1 character varying(15),
    fono_2 character varying(15),
    id_cliente_proveedor integer NOT NULL,
    por_defecto boolean NOT NULL
);


--
-- Name: direccion_id_direccion_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.direccion_id_direccion_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: direccion_id_direccion_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.direccion_id_direccion_seq OWNED BY public.direccion.id_direccion;


--
-- Name: documento_ide; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.documento_ide (
    id_documento_ide integer NOT NULL,
    id_ide integer,
    descripcion character varying(100) NOT NULL,
    nombre_original character varying(200),
    nombre_archivo character varying(200),
    enviado boolean
);


--
-- Name: documento_ide_id_documento_ide_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.documento_ide_id_documento_ide_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: documento_ide_id_documento_ide_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.documento_ide_id_documento_ide_seq OWNED BY public.documento_ide.id_documento_ide;


--
-- Name: empresa; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.empresa (
    id_empresa integer NOT NULL,
    rut character varying(15) NOT NULL,
    nombre_fantasia character varying(200) NOT NULL,
    razon_social character varying(200) NOT NULL,
    direccion character varying(200) NOT NULL,
    telefono_1 character varying(50),
    telefono_2 character varying(50),
    giro character varying(200),
    id_ciudad integer NOT NULL,
    es_vigente boolean NOT NULL,
    en_proforma boolean NOT NULL,
    en_odc boolean NOT NULL,
    por_defecto boolean NOT NULL,
    url_logo text
);


--
-- Name: empresa_id_empresa_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.empresa_id_empresa_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: empresa_id_empresa_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.empresa_id_empresa_seq OWNED BY public.empresa.id_empresa;


--
-- Name: especie; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.especie (
    id_especie integer NOT NULL,
    nombre_esp character varying(100) NOT NULL,
    nombre_ing character varying(100) NOT NULL,
    descripcion character varying(200),
    por_defecto boolean,
    url_imagen character varying(100)
);


--
-- Name: especie_id_especie_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.especie_id_especie_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: especie_id_especie_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.especie_id_especie_seq OWNED BY public.especie.id_especie;


--
-- Name: estado_detalle_ple; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.estado_detalle_ple (
    id_estado_detalle_ple integer NOT NULL,
    nombre character varying(15) NOT NULL
);


--
-- Name: estado_detalle_ple_id_estado_detalle_ple_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.estado_detalle_ple_id_estado_detalle_ple_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: estado_detalle_ple_id_estado_detalle_ple_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.estado_detalle_ple_id_estado_detalle_ple_seq OWNED BY public.estado_detalle_ple.id_estado_detalle_ple;


--
-- Name: estado_odc; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.estado_odc (
    id_estado_odc integer NOT NULL,
    nombre character varying(15) NOT NULL
);


--
-- Name: estado_odc_id_estado_odc_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.estado_odc_id_estado_odc_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: estado_odc_id_estado_odc_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.estado_odc_id_estado_odc_seq OWNED BY public.estado_odc.id_estado_odc;


--
-- Name: estado_oe; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.estado_oe (
    id_estado_oe integer NOT NULL,
    nombre character varying(50) NOT NULL
);


--
-- Name: estado_oe_id_estado_oe_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.estado_oe_id_estado_oe_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: estado_oe_id_estado_oe_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.estado_oe_id_estado_oe_seq OWNED BY public.estado_oe.id_estado_oe;


--
-- Name: estado_pl; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.estado_pl (
    id_estado_pl integer NOT NULL,
    nombre character varying(15) NOT NULL,
    es_ple boolean,
    es_plc boolean
);


--
-- Name: estado_pl_id_estado_pl_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.estado_pl_id_estado_pl_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: estado_pl_id_estado_pl_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.estado_pl_id_estado_pl_seq OWNED BY public.estado_pl.id_estado_pl;


--
-- Name: estado_proforma; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.estado_proforma (
    id_estado_proforma integer NOT NULL,
    nombre character varying(20) NOT NULL
);


--
-- Name: estado_proforma_id_estado_proforma_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.estado_proforma_id_estado_proforma_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: estado_proforma_id_estado_proforma_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.estado_proforma_id_estado_proforma_seq OWNED BY public.estado_proforma.id_estado_proforma;


--
-- Name: factura; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.factura (
    id_factura integer NOT NULL,
    fecha_creacion date NOT NULL,
    fecha_emision date NOT NULL,
    folio_sii integer NOT NULL,
    terms character varying(200) NOT NULL,
    carta_credito character varying(50),
    fecha_carta_credito character varying(50),
    id_ide integer NOT NULL,
    subtotal character varying(13),
    total character varying(13),
    descuento character varying(13),
    contract character varying(200),
    nota character varying(3000),
    nota_al_pie character varying(1000)
);


--
-- Name: factura_id_factura_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.factura_id_factura_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: factura_id_factura_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.factura_id_factura_seq OWNED BY public.factura.id_factura;


--
-- Name: forma_pago; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.forma_pago (
    id_forma_pago integer NOT NULL,
    nombre character varying(50) NOT NULL,
    por_defecto boolean
);


--
-- Name: forma_pago_id_forma_pago_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.forma_pago_id_forma_pago_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: forma_pago_id_forma_pago_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.forma_pago_id_forma_pago_seq OWNED BY public.forma_pago.id_forma_pago;


--
-- Name: gasto; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.gasto (
    id_gasto integer NOT NULL,
    nombre character varying(100) NOT NULL,
    es_gasto boolean NOT NULL,
    es_costo boolean NOT NULL
);


--
-- Name: gasto_id_gasto_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.gasto_id_gasto_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: gasto_id_gasto_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.gasto_id_gasto_seq OWNED BY public.gasto.id_gasto;


--
-- Name: ide; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ide (
    id_ide integer NOT NULL,
    id_naviera integer,
    id_cliente_consignar_a integer NOT NULL,
    direccion_consignar_a character varying(500) NOT NULL,
    id_cliente_notificar_a integer NOT NULL,
    direccion_notificar_a character varying(500) NOT NULL,
    id_bodega integer NOT NULL,
    id_cliente_notificar_tambien integer,
    direccion_tambien_notificar character varying(500),
    id_tipo_envase integer NOT NULL,
    id_usuario_responsable integer NOT NULL,
    fecha_creacion date NOT NULL,
    fecha_emision date NOT NULL,
    nave character varying(100) NOT NULL,
    comision character varying(100),
    retiro_unidades character varying(100),
    codigo_reserva character varying(100),
    medio_transporte character varying(15),
    etd date NOT NULL,
    tiempo_transito integer NOT NULL,
    eta date NOT NULL,
    flete character varying(13),
    confirma_zarpe boolean,
    fob character varying(13),
    stacking date,
    seguro_app character varying(13),
    total_flete character varying(13),
    total character varying(13),
    id_cliente_facturar_a integer NOT NULL,
    id_puerto_origen integer NOT NULL,
    id_puerto_destino integer NOT NULL,
    id_clausula_venta character varying(10) NOT NULL,
    id_forma_pago integer NOT NULL,
    id_tipo_comision integer,
    id_moneda integer NOT NULL,
    carta_credito character varying(60),
    fecha_carta_credito character varying(60),
    modalidad_venta character varying(100) NOT NULL,
    tipo_flete character varying(60)
);


--
-- Name: ide_id_ide_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.ide_id_ide_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ide_id_ide_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.ide_id_ide_seq OWNED BY public.ide.id_ide;


--
-- Name: moneda; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.moneda (
    id_moneda integer NOT NULL,
    etiqueta character varying(10) NOT NULL,
    nombre_moneda character varying(200),
    por_defecto boolean
);


--
-- Name: moneda_id_moneda_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.moneda_id_moneda_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: moneda_id_moneda_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.moneda_id_moneda_seq OWNED BY public.moneda.id_moneda;


--
-- Name: naviera; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.naviera (
    id_naviera integer NOT NULL,
    nombre character varying(100) NOT NULL
);


--
-- Name: naviera_id_naviera_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.naviera_id_naviera_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: naviera_id_naviera_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.naviera_id_naviera_seq OWNED BY public.naviera.id_naviera;


--
-- Name: operacion_exportacion; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.operacion_exportacion (
    id_operacion_exportacion integer NOT NULL,
    facturar_a integer NOT NULL,
    consignar_a integer NOT NULL,
    notificar_a integer NOT NULL,
    id_puerto_origen integer NOT NULL,
    id_puerto_destino integer NOT NULL,
    id_forma_pago integer NOT NULL,
    id_estado_oe integer NOT NULL,
    fecha date NOT NULL
);


--
-- Name: orden_compra; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.orden_compra (
    id_orden_compra integer NOT NULL,
    id_proforma integer,
    id_proforma_anterior integer,
    fecha_emision date NOT NULL,
    id_cliente_proveedor integer NOT NULL,
    id_usuario_encargado integer NOT NULL,
    fecha_entrega date NOT NULL,
    id_bodega integer NOT NULL,
    destino character varying(15),
    id_moneda integer NOT NULL,
    id_empresa integer,
    ajustar_volumen boolean,
    observacion character varying(1000),
    id_usuario integer NOT NULL,
    nota_1 character varying(1000),
    otras_especificaciones character varying(1000),
    url_imagen character varying(100),
    valor_neto numeric(13,3) NOT NULL,
    iva numeric(12,3) NOT NULL,
    tasa_iva numeric(6,3),
    valor_total numeric(12,3) NOT NULL,
    id_estado_odc integer NOT NULL,
    id_direccion_proveedor integer NOT NULL,
    vinculado integer
);


--
-- Name: orden_compra_id_orden_compra_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.orden_compra_id_orden_compra_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: orden_compra_id_orden_compra_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.orden_compra_id_orden_compra_seq OWNED BY public.orden_compra.id_orden_compra;


--
-- Name: pais; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.pais (
    id_pais integer NOT NULL,
    nombre character varying(50) NOT NULL
);


--
-- Name: pais_id_pais_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.pais_id_pais_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: pais_id_pais_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.pais_id_pais_seq OWNED BY public.pais.id_pais;


--
-- Name: parametro; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.parametro (
    id_parametro integer NOT NULL,
    nota_1 character varying(1000) NOT NULL
);


--
-- Name: parametro_id_parametro_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.parametro_id_parametro_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: parametro_id_parametro_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.parametro_id_parametro_seq OWNED BY public.parametro.id_parametro;


--
-- Name: plc; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.plc (
    id_plc integer NOT NULL,
    id_operacion_exportacion integer,
    id_estado_pl integer NOT NULL,
    fecha_creacion date NOT NULL,
    volumen_m3 character varying(12),
    paquetes integer NOT NULL,
    peso_bruto character varying(12) NOT NULL,
    piezas integer NOT NULL,
    rw boolean,
    rl boolean,
    descripcion character varying(200) NOT NULL,
    categoria_fsc character varying(20)
);


--
-- Name: plc_id_plc_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.plc_id_plc_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: plc_id_plc_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.plc_id_plc_seq OWNED BY public.plc.id_plc;


--
-- Name: ple; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.ple (
    id_ple integer NOT NULL,
    id_orden_compra integer NOT NULL,
    id_estado_pl integer,
    fecha_creacion date NOT NULL,
    nro_guia integer,
    despacho date,
    volumen_m3 numeric(12,3) NOT NULL,
    paquetes integer NOT NULL,
    piezas integer NOT NULL,
    costo_total_pesos numeric(12,3) NOT NULL,
    tc numeric(12,3),
    factura integer,
    monto_factura numeric(12,3),
    factura_pagada boolean,
    id_usuario_encargado integer
);


--
-- Name: ple_id_ple_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.ple_id_ple_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: ple_id_ple_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.ple_id_ple_seq OWNED BY public.ple.id_ple;


--
-- Name: producto; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.producto (
    id_producto integer NOT NULL,
    id_clase integer,
    id_especie integer,
    nombre_producto_esp character varying(100) NOT NULL,
    nombre_producto_ing character varying(100) NOT NULL,
    obs_calidad character varying(2000)
);


--
-- Name: producto_id_producto_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.producto_id_producto_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: producto_id_producto_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.producto_id_producto_seq OWNED BY public.producto.id_producto;


--
-- Name: proforma; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.proforma (
    id_proforma integer NOT NULL,
    id_operacion_exportacion integer,
    id_contenedor integer,
    id_usuario_encargado integer,
    id_estado_proforma integer,
    id_moneda integer,
    id_agente integer,
    id_tipo_comision integer,
    id_clausula_venta character varying(10),
    cantidad_contenedor integer,
    fecha_emision date NOT NULL,
    fecha_aceptacion date,
    fecha_entrega date,
    valor_flete numeric,
    especificaciones character varying(2000),
    nota character varying(2000),
    nota_1 character varying(2000),
    nota_2 character varying(2000),
    url_imagen character varying(100),
    id_empresa integer NOT NULL,
    id_direccion_facturar integer NOT NULL,
    id_direccion_consignar integer NOT NULL,
    id_direccion_notificar integer NOT NULL,
    empresa_nombre_fantasia character varying(200),
    empresa_razon_social character varying(200),
    empresa_rut character varying(15),
    empresa_direccion character varying(200),
    empresa_giro character varying(200),
    direccion_facturar_texto character varying(200),
    direccion_facturar_ciudad character varying(100),
    direccion_facturar_pais character varying(100),
    direccion_facturar_fono_1 character varying(15),
    direccion_consignar_texto character varying(200),
    direccion_consignar_ciudad character varying(100),
    direccion_consignar_pais character varying(100),
    direccion_consignar_fono_1 character varying(15),
    direccion_notificar_texto character varying(200),
    direccion_notificar_ciudad character varying(100),
    direccion_notificar_pais character varying(100),
    direccion_notificar_fono_1 character varying(15)
);


--
-- Name: puerto; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.puerto (
    id_puerto integer NOT NULL,
    nombre character varying(200) NOT NULL,
    descripcion character varying(200),
    id_ciudad integer NOT NULL
);


--
-- Name: puerto_id_puerto_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.puerto_id_puerto_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: puerto_id_puerto_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.puerto_id_puerto_seq OWNED BY public.puerto.id_puerto;


--
-- Name: seguridad; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.seguridad (
    id_seguridad integer NOT NULL,
    id_usuario integer NOT NULL,
    modulo character varying(15) NOT NULL,
    crear boolean NOT NULL,
    ver boolean NOT NULL,
    editar boolean NOT NULL,
    eliminar boolean NOT NULL
);


--
-- Name: seguridad_id_seguridad_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.seguridad_id_seguridad_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: seguridad_id_seguridad_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.seguridad_id_seguridad_seq OWNED BY public.seguridad.id_seguridad;


--
-- Name: tipo_comision; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tipo_comision (
    id_tipo_comision integer NOT NULL,
    nombre character varying(20) NOT NULL,
    por_defecto boolean
);


--
-- Name: tipo_comision_id_tipo_comision_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.tipo_comision_id_tipo_comision_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: tipo_comision_id_tipo_comision_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.tipo_comision_id_tipo_comision_seq OWNED BY public.tipo_comision.id_tipo_comision;


--
-- Name: tipo_envase; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.tipo_envase (
    id_tipo_envase integer NOT NULL,
    nombre character varying(50) NOT NULL
);


--
-- Name: tipo_envase_id_tipo_envase_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.tipo_envase_id_tipo_envase_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: tipo_envase_id_tipo_envase_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.tipo_envase_id_tipo_envase_seq OWNED BY public.tipo_envase.id_tipo_envase;


--
-- Name: unidad_medida; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.unidad_medida (
    id_unidad_medida integer NOT NULL,
    nombre character varying(10) NOT NULL,
    equivalencia_mm character varying(12) NOT NULL,
    descripcion character varying(100) NOT NULL,
    por_defecto boolean
);


--
-- Name: unidad_medida_id_unidad_medida_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.unidad_medida_id_unidad_medida_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: unidad_medida_id_unidad_medida_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.unidad_medida_id_unidad_medida_seq OWNED BY public.unidad_medida.id_unidad_medida;


--
-- Name: unidad_venta; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.unidad_venta (
    id_unidad_venta integer NOT NULL,
    nombre character varying(20) NOT NULL,
    cubicacion character varying(200) NOT NULL,
    descripcion character varying(200) NOT NULL,
    por_defecto boolean
);


--
-- Name: unidad_venta_id_unidad_venta_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.unidad_venta_id_unidad_venta_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: unidad_venta_id_unidad_venta_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.unidad_venta_id_unidad_venta_seq OWNED BY public.unidad_venta.id_unidad_venta;


--
-- Name: usuario; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.usuario (
    id_usuario integer NOT NULL,
    rut character varying(20),
    nombre character varying(120) NOT NULL,
    login character varying(80) NOT NULL,
    pass character varying(255) NOT NULL,
    correo character varying(200) NOT NULL,
    telefono character varying(50),
    url_firma character varying(255),
    activo boolean NOT NULL
);


--
-- Name: usuario_id_usuario_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.usuario_id_usuario_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: usuario_id_usuario_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.usuario_id_usuario_seq OWNED BY public.usuario.id_usuario;


--
-- Name: agente id_agente; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agente ALTER COLUMN id_agente SET DEFAULT nextval('public.agente_id_agente_seq'::regclass);


--
-- Name: bodega id_bodega; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bodega ALTER COLUMN id_bodega SET DEFAULT nextval('public.bodega_id_bodega_seq'::regclass);


--
-- Name: ciudad id_ciudad; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ciudad ALTER COLUMN id_ciudad SET DEFAULT nextval('public.ciudad_id_ciudad_seq'::regclass);


--
-- Name: clase id_clase; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.clase ALTER COLUMN id_clase SET DEFAULT nextval('public.clase_id_clase_seq'::regclass);


--
-- Name: cliente_proveedor id_cliente_proveedor; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cliente_proveedor ALTER COLUMN id_cliente_proveedor SET DEFAULT nextval('public.cliente_proveedor_id_cliente_proveedor_seq'::regclass);


--
-- Name: contacto id_contacto; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.contacto ALTER COLUMN id_contacto SET DEFAULT nextval('public.contacto_id_contacto_seq'::regclass);


--
-- Name: contacto_orden_compra id_contacto_orden_compra; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.contacto_orden_compra ALTER COLUMN id_contacto_orden_compra SET DEFAULT nextval('public.contacto_orden_compra_id_contacto_orden_compra_seq'::regclass);


--
-- Name: contacto_proforma id_contacto_proforma; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.contacto_proforma ALTER COLUMN id_contacto_proforma SET DEFAULT nextval('public.contacto_proforma_id_contacto_proforma_seq'::regclass);


--
-- Name: contenedor id_contenedor; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.contenedor ALTER COLUMN id_contenedor SET DEFAULT nextval('public.contenedor_id_contenedor_seq'::regclass);


--
-- Name: detalle_factura id_detalle_factura; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.detalle_factura ALTER COLUMN id_detalle_factura SET DEFAULT nextval('public.detalle_factura_id_detalle_factura_seq'::regclass);


--
-- Name: detalle_gasto id_detalle_gasto; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.detalle_gasto ALTER COLUMN id_detalle_gasto SET DEFAULT nextval('public.detalle_gasto_id_detalle_gasto_seq'::regclass);


--
-- Name: detalle_ide id_detalle_ide; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.detalle_ide ALTER COLUMN id_detalle_ide SET DEFAULT nextval('public.detalle_ide_id_detalle_ide_seq'::regclass);


--
-- Name: detalle_orden_compra id_detalle_odc; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.detalle_orden_compra ALTER COLUMN id_detalle_odc SET DEFAULT nextval('public.detalle_orden_compra_id_detalle_odc_seq'::regclass);


--
-- Name: detalle_pl id_detalle_pl; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.detalle_pl ALTER COLUMN id_detalle_pl SET DEFAULT nextval('public.detalle_pl_id_detalle_pl_seq'::regclass);


--
-- Name: detalle_proforma id_detalle_proforma; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.detalle_proforma ALTER COLUMN id_detalle_proforma SET DEFAULT nextval('public.detalle_proforma_id_detalle_proforma_seq'::regclass);


--
-- Name: direccion id_direccion; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.direccion ALTER COLUMN id_direccion SET DEFAULT nextval('public.direccion_id_direccion_seq'::regclass);


--
-- Name: documento_ide id_documento_ide; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.documento_ide ALTER COLUMN id_documento_ide SET DEFAULT nextval('public.documento_ide_id_documento_ide_seq'::regclass);


--
-- Name: empresa id_empresa; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.empresa ALTER COLUMN id_empresa SET DEFAULT nextval('public.empresa_id_empresa_seq'::regclass);


--
-- Name: especie id_especie; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.especie ALTER COLUMN id_especie SET DEFAULT nextval('public.especie_id_especie_seq'::regclass);


--
-- Name: estado_detalle_ple id_estado_detalle_ple; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.estado_detalle_ple ALTER COLUMN id_estado_detalle_ple SET DEFAULT nextval('public.estado_detalle_ple_id_estado_detalle_ple_seq'::regclass);


--
-- Name: estado_odc id_estado_odc; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.estado_odc ALTER COLUMN id_estado_odc SET DEFAULT nextval('public.estado_odc_id_estado_odc_seq'::regclass);


--
-- Name: estado_oe id_estado_oe; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.estado_oe ALTER COLUMN id_estado_oe SET DEFAULT nextval('public.estado_oe_id_estado_oe_seq'::regclass);


--
-- Name: estado_pl id_estado_pl; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.estado_pl ALTER COLUMN id_estado_pl SET DEFAULT nextval('public.estado_pl_id_estado_pl_seq'::regclass);


--
-- Name: estado_proforma id_estado_proforma; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.estado_proforma ALTER COLUMN id_estado_proforma SET DEFAULT nextval('public.estado_proforma_id_estado_proforma_seq'::regclass);


--
-- Name: factura id_factura; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.factura ALTER COLUMN id_factura SET DEFAULT nextval('public.factura_id_factura_seq'::regclass);


--
-- Name: forma_pago id_forma_pago; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.forma_pago ALTER COLUMN id_forma_pago SET DEFAULT nextval('public.forma_pago_id_forma_pago_seq'::regclass);


--
-- Name: gasto id_gasto; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.gasto ALTER COLUMN id_gasto SET DEFAULT nextval('public.gasto_id_gasto_seq'::regclass);


--
-- Name: ide id_ide; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ide ALTER COLUMN id_ide SET DEFAULT nextval('public.ide_id_ide_seq'::regclass);


--
-- Name: moneda id_moneda; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.moneda ALTER COLUMN id_moneda SET DEFAULT nextval('public.moneda_id_moneda_seq'::regclass);


--
-- Name: naviera id_naviera; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.naviera ALTER COLUMN id_naviera SET DEFAULT nextval('public.naviera_id_naviera_seq'::regclass);


--
-- Name: orden_compra id_orden_compra; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.orden_compra ALTER COLUMN id_orden_compra SET DEFAULT nextval('public.orden_compra_id_orden_compra_seq'::regclass);


--
-- Name: pais id_pais; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pais ALTER COLUMN id_pais SET DEFAULT nextval('public.pais_id_pais_seq'::regclass);


--
-- Name: parametro id_parametro; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.parametro ALTER COLUMN id_parametro SET DEFAULT nextval('public.parametro_id_parametro_seq'::regclass);


--
-- Name: plc id_plc; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.plc ALTER COLUMN id_plc SET DEFAULT nextval('public.plc_id_plc_seq'::regclass);


--
-- Name: ple id_ple; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ple ALTER COLUMN id_ple SET DEFAULT nextval('public.ple_id_ple_seq'::regclass);


--
-- Name: producto id_producto; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.producto ALTER COLUMN id_producto SET DEFAULT nextval('public.producto_id_producto_seq'::regclass);


--
-- Name: puerto id_puerto; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.puerto ALTER COLUMN id_puerto SET DEFAULT nextval('public.puerto_id_puerto_seq'::regclass);


--
-- Name: seguridad id_seguridad; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.seguridad ALTER COLUMN id_seguridad SET DEFAULT nextval('public.seguridad_id_seguridad_seq'::regclass);


--
-- Name: tipo_comision id_tipo_comision; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tipo_comision ALTER COLUMN id_tipo_comision SET DEFAULT nextval('public.tipo_comision_id_tipo_comision_seq'::regclass);


--
-- Name: tipo_envase id_tipo_envase; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tipo_envase ALTER COLUMN id_tipo_envase SET DEFAULT nextval('public.tipo_envase_id_tipo_envase_seq'::regclass);


--
-- Name: unidad_medida id_unidad_medida; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.unidad_medida ALTER COLUMN id_unidad_medida SET DEFAULT nextval('public.unidad_medida_id_unidad_medida_seq'::regclass);


--
-- Name: unidad_venta id_unidad_venta; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.unidad_venta ALTER COLUMN id_unidad_venta SET DEFAULT nextval('public.unidad_venta_id_unidad_venta_seq'::regclass);


--
-- Name: usuario id_usuario; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuario ALTER COLUMN id_usuario SET DEFAULT nextval('public.usuario_id_usuario_seq'::regclass);


--
-- Data for Name: agente; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.agente (id_agente, id_pais, nombre, correo, telefono, por_defecto) FROM stdin;
\.


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.alembic_version (version_num) FROM stdin;
002
\.


--
-- Data for Name: bodega; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.bodega (id_bodega, nombre, direccion) FROM stdin;
\.


--
-- Data for Name: ciudad; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.ciudad (id_ciudad, id_pais, nombre) FROM stdin;
1	1	SANTIAGO
\.


--
-- Data for Name: clase; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.clase (id_clase, nombre, descripcion) FROM stdin;
\.


--
-- Data for Name: clausula_venta; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.clausula_venta (id_clausula_venta) FROM stdin;
\.


--
-- Data for Name: cliente_proveedor; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.cliente_proveedor (id_cliente_proveedor, rut, nombre_fantasia, razon_social, es_nacional, giro, es_cliente, es_proveedor) FROM stdin;
\.


--
-- Data for Name: contacto; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.contacto (id_contacto, nombre, correo, telefono, id_cliente_proveedor) FROM stdin;
\.


--
-- Data for Name: contacto_orden_compra; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.contacto_orden_compra (id_contacto_orden_compra, id_orden_compra, id_contacto) FROM stdin;
\.


--
-- Data for Name: contacto_proforma; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.contacto_proforma (id_contacto_proforma, id_contacto, id_proforma) FROM stdin;
\.


--
-- Data for Name: contenedor; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.contenedor (id_contenedor, nombre, tara, peso_maximo) FROM stdin;
\.


--
-- Data for Name: detalle_factura; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.detalle_factura (id_detalle_factura, id_factura, cantidad, especificaciones, precio_unitario, total) FROM stdin;
\.


--
-- Data for Name: detalle_gasto; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.detalle_gasto (id_detalle_gasto, id_gasto, valor, nro_documento, pagado) FROM stdin;
\.


--
-- Data for Name: detalle_ide; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.detalle_ide (id_detalle_ide, id_ide, id_plc, fob, identificador_contenedor, sello, peso_neto, peso_bruto, nro_linea) FROM stdin;
\.


--
-- Data for Name: detalle_orden_compra; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.detalle_orden_compra (id_detalle_odc, id_orden_compra, id_producto, id_unidad_venta, texto_abierto, espesor, id_unidad_medida_espesor, ancho, id_unidad_medida_ancho, largo, id_unidad_medida_largo, cantidad, precio_unitario, subtotal, volumen, volumen_eq, precio_eq, odc_salida) FROM stdin;
\.


--
-- Data for Name: detalle_pl; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.detalle_pl (id_detalle_pl, id_ple, id_plc, etiqueta, descripcion, id_unidad_venta, cantidad, espesor_ple, id_unidad_medida_espesor_ple, ancho_ple, id_unidad_medida_ancho_ple, largo_ple, id_unidad_medida_largo_ple, piezas, volumen_ple, costo_eq_m3, costo_paquete, id_estado_detalle_ple, venta_eq_m3, venta_unitario, venta_paquete, operacion_exportacion, odc, id_unidad_medida_espesor_plc, id_unidad_medida_ancho_plc, id_unidad_medida_largo_plc, espesor_plc, ancho_plc, largo_plc, volumen_plc, costo_unitario, pulgada_cubica, metro_lineal, pie) FROM stdin;
\.


--
-- Data for Name: detalle_proforma; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.detalle_proforma (id_detalle_proforma, id_proforma, id_producto, id_unidad_venta, texto_libre, espesor, id_unidad_medida_espesor, ancho, id_unidad_medida_ancho, largo, id_unidad_medida_largo, piezas, cantidad, precio_unitario, subtotal, volumen, volumen_eq, precio_eq, producto_nombre_esp, producto_nombre_ing, producto_obs_calidad, producto_especie) FROM stdin;
\.


--
-- Data for Name: direccion; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.direccion (id_direccion, direccion, id_ciudad, continente, fono_1, fono_2, id_cliente_proveedor, por_defecto) FROM stdin;
\.


--
-- Data for Name: documento_ide; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.documento_ide (id_documento_ide, id_ide, descripcion, nombre_original, nombre_archivo, enviado) FROM stdin;
\.


--
-- Data for Name: empresa; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.empresa (id_empresa, rut, nombre_fantasia, razon_social, direccion, telefono_1, telefono_2, giro, id_ciudad, es_vigente, en_proforma, en_odc, por_defecto, url_logo) FROM stdin;
\.


--
-- Data for Name: especie; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.especie (id_especie, nombre_esp, nombre_ing, descripcion, por_defecto, url_imagen) FROM stdin;
\.


--
-- Data for Name: estado_detalle_ple; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.estado_detalle_ple (id_estado_detalle_ple, nombre) FROM stdin;
\.


--
-- Data for Name: estado_odc; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.estado_odc (id_estado_odc, nombre) FROM stdin;
\.


--
-- Data for Name: estado_oe; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.estado_oe (id_estado_oe, nombre) FROM stdin;
\.


--
-- Data for Name: estado_pl; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.estado_pl (id_estado_pl, nombre, es_ple, es_plc) FROM stdin;
\.


--
-- Data for Name: estado_proforma; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.estado_proforma (id_estado_proforma, nombre) FROM stdin;
\.


--
-- Data for Name: factura; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.factura (id_factura, fecha_creacion, fecha_emision, folio_sii, terms, carta_credito, fecha_carta_credito, id_ide, subtotal, total, descuento, contract, nota, nota_al_pie) FROM stdin;
\.


--
-- Data for Name: forma_pago; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.forma_pago (id_forma_pago, nombre, por_defecto) FROM stdin;
\.


--
-- Data for Name: gasto; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.gasto (id_gasto, nombre, es_gasto, es_costo) FROM stdin;
\.


--
-- Data for Name: ide; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.ide (id_ide, id_naviera, id_cliente_consignar_a, direccion_consignar_a, id_cliente_notificar_a, direccion_notificar_a, id_bodega, id_cliente_notificar_tambien, direccion_tambien_notificar, id_tipo_envase, id_usuario_responsable, fecha_creacion, fecha_emision, nave, comision, retiro_unidades, codigo_reserva, medio_transporte, etd, tiempo_transito, eta, flete, confirma_zarpe, fob, stacking, seguro_app, total_flete, total, id_cliente_facturar_a, id_puerto_origen, id_puerto_destino, id_clausula_venta, id_forma_pago, id_tipo_comision, id_moneda, carta_credito, fecha_carta_credito, modalidad_venta, tipo_flete) FROM stdin;
\.


--
-- Data for Name: moneda; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.moneda (id_moneda, etiqueta, nombre_moneda, por_defecto) FROM stdin;
1	CLP	Peso Chileno	t
\.


--
-- Data for Name: naviera; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.naviera (id_naviera, nombre) FROM stdin;
\.


--
-- Data for Name: operacion_exportacion; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.operacion_exportacion (id_operacion_exportacion, facturar_a, consignar_a, notificar_a, id_puerto_origen, id_puerto_destino, id_forma_pago, id_estado_oe, fecha) FROM stdin;
\.


--
-- Data for Name: orden_compra; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.orden_compra (id_orden_compra, id_proforma, id_proforma_anterior, fecha_emision, id_cliente_proveedor, id_usuario_encargado, fecha_entrega, id_bodega, destino, id_moneda, id_empresa, ajustar_volumen, observacion, id_usuario, nota_1, otras_especificaciones, url_imagen, valor_neto, iva, tasa_iva, valor_total, id_estado_odc, id_direccion_proveedor, vinculado) FROM stdin;
\.


--
-- Data for Name: pais; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.pais (id_pais, nombre) FROM stdin;
1	CHILE
3	ARGENTINA
\.


--
-- Data for Name: parametro; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.parametro (id_parametro, nota_1) FROM stdin;
\.


--
-- Data for Name: plc; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.plc (id_plc, id_operacion_exportacion, id_estado_pl, fecha_creacion, volumen_m3, paquetes, peso_bruto, piezas, rw, rl, descripcion, categoria_fsc) FROM stdin;
\.


--
-- Data for Name: ple; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.ple (id_ple, id_orden_compra, id_estado_pl, fecha_creacion, nro_guia, despacho, volumen_m3, paquetes, piezas, costo_total_pesos, tc, factura, monto_factura, factura_pagada, id_usuario_encargado) FROM stdin;
\.


--
-- Data for Name: producto; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.producto (id_producto, id_clase, id_especie, nombre_producto_esp, nombre_producto_ing, obs_calidad) FROM stdin;
\.


--
-- Data for Name: proforma; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.proforma (id_proforma, id_operacion_exportacion, id_contenedor, id_usuario_encargado, id_estado_proforma, id_moneda, id_agente, id_tipo_comision, id_clausula_venta, cantidad_contenedor, fecha_emision, fecha_aceptacion, fecha_entrega, valor_flete, especificaciones, nota, nota_1, nota_2, url_imagen, id_empresa, id_direccion_facturar, id_direccion_consignar, id_direccion_notificar, empresa_nombre_fantasia, empresa_razon_social, empresa_rut, empresa_direccion, empresa_giro, direccion_facturar_texto, direccion_facturar_ciudad, direccion_facturar_pais, direccion_facturar_fono_1, direccion_consignar_texto, direccion_consignar_ciudad, direccion_consignar_pais, direccion_consignar_fono_1, direccion_notificar_texto, direccion_notificar_ciudad, direccion_notificar_pais, direccion_notificar_fono_1) FROM stdin;
\.


--
-- Data for Name: puerto; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.puerto (id_puerto, nombre, descripcion, id_ciudad) FROM stdin;
\.


--
-- Data for Name: seguridad; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.seguridad (id_seguridad, id_usuario, modulo, crear, ver, editar, eliminar) FROM stdin;
1	2	Proforma	t	t	t	t
2	2	Inventario	t	t	t	t
3	2	Comex	t	t	t	t
4	2	Seguridad	t	t	t	t
5	2	Informes	t	t	t	t
\.


--
-- Data for Name: tipo_comision; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.tipo_comision (id_tipo_comision, nombre, por_defecto) FROM stdin;
\.


--
-- Data for Name: tipo_envase; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.tipo_envase (id_tipo_envase, nombre) FROM stdin;
\.


--
-- Data for Name: unidad_medida; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.unidad_medida (id_unidad_medida, nombre, equivalencia_mm, descripcion, por_defecto) FROM stdin;
\.


--
-- Data for Name: unidad_venta; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.unidad_venta (id_unidad_venta, nombre, cubicacion, descripcion, por_defecto) FROM stdin;
\.


--
-- Data for Name: usuario; Type: TABLE DATA; Schema: public; Owner: -
--

COPY public.usuario (id_usuario, rut, nombre, login, pass, correo, telefono, url_firma, activo) FROM stdin;
1	\N	Test User	testuser_longpwd	$bcrypt-sha256$v=2,t=2b,r=12$1Q7LEB5FcuGiW.5SJLGpw.$fF1cvaWJtJ6jBY4BbwfkvveeeaBRiFK	testuser_longpwd@example.com	\N	\N	t
2	\N	Luis Rodriguez	lrodriguez	$bcrypt-sha256$v=2,t=2b,r=12$M4eQKzcN.AOAPnR6NoRRGe$0sPFPdcCmFbHSEFS2JE4mVmGEdvwo8y	lrodriguez@gmail.com	\N	\N	t
\.


--
-- Name: agente_id_agente_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.agente_id_agente_seq', 1, false);


--
-- Name: bodega_id_bodega_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.bodega_id_bodega_seq', 1, false);


--
-- Name: ciudad_id_ciudad_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.ciudad_id_ciudad_seq', 1, true);


--
-- Name: clase_id_clase_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.clase_id_clase_seq', 1, false);


--
-- Name: cliente_proveedor_id_cliente_proveedor_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.cliente_proveedor_id_cliente_proveedor_seq', 1, false);


--
-- Name: contacto_id_contacto_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.contacto_id_contacto_seq', 1, false);


--
-- Name: contacto_orden_compra_id_contacto_orden_compra_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.contacto_orden_compra_id_contacto_orden_compra_seq', 1, false);


--
-- Name: contacto_proforma_id_contacto_proforma_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.contacto_proforma_id_contacto_proforma_seq', 1, false);


--
-- Name: contenedor_id_contenedor_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.contenedor_id_contenedor_seq', 1, false);


--
-- Name: detalle_factura_id_detalle_factura_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.detalle_factura_id_detalle_factura_seq', 1, false);


--
-- Name: detalle_gasto_id_detalle_gasto_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.detalle_gasto_id_detalle_gasto_seq', 1, false);


--
-- Name: detalle_ide_id_detalle_ide_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.detalle_ide_id_detalle_ide_seq', 1, false);


--
-- Name: detalle_orden_compra_id_detalle_odc_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.detalle_orden_compra_id_detalle_odc_seq', 1, false);


--
-- Name: detalle_pl_id_detalle_pl_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.detalle_pl_id_detalle_pl_seq', 1, false);


--
-- Name: detalle_proforma_id_detalle_proforma_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.detalle_proforma_id_detalle_proforma_seq', 1, false);


--
-- Name: direccion_id_direccion_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.direccion_id_direccion_seq', 2, true);


--
-- Name: documento_ide_id_documento_ide_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.documento_ide_id_documento_ide_seq', 1, false);


--
-- Name: empresa_id_empresa_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.empresa_id_empresa_seq', 1, false);


--
-- Name: especie_id_especie_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.especie_id_especie_seq', 1, false);


--
-- Name: estado_detalle_ple_id_estado_detalle_ple_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.estado_detalle_ple_id_estado_detalle_ple_seq', 1, false);


--
-- Name: estado_odc_id_estado_odc_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.estado_odc_id_estado_odc_seq', 1, false);


--
-- Name: estado_oe_id_estado_oe_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.estado_oe_id_estado_oe_seq', 1, false);


--
-- Name: estado_pl_id_estado_pl_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.estado_pl_id_estado_pl_seq', 1, false);


--
-- Name: estado_proforma_id_estado_proforma_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.estado_proforma_id_estado_proforma_seq', 1, false);


--
-- Name: factura_id_factura_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.factura_id_factura_seq', 1, false);


--
-- Name: forma_pago_id_forma_pago_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.forma_pago_id_forma_pago_seq', 1, false);


--
-- Name: gasto_id_gasto_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.gasto_id_gasto_seq', 1, false);


--
-- Name: ide_id_ide_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.ide_id_ide_seq', 1, false);


--
-- Name: moneda_id_moneda_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.moneda_id_moneda_seq', 1, true);


--
-- Name: naviera_id_naviera_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.naviera_id_naviera_seq', 1, false);


--
-- Name: orden_compra_id_orden_compra_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.orden_compra_id_orden_compra_seq', 1, false);


--
-- Name: pais_id_pais_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.pais_id_pais_seq', 3, true);


--
-- Name: parametro_id_parametro_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.parametro_id_parametro_seq', 1, false);


--
-- Name: plc_id_plc_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.plc_id_plc_seq', 1, false);


--
-- Name: ple_id_ple_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.ple_id_ple_seq', 1, false);


--
-- Name: producto_id_producto_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.producto_id_producto_seq', 1, false);


--
-- Name: puerto_id_puerto_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.puerto_id_puerto_seq', 1, false);


--
-- Name: seguridad_id_seguridad_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.seguridad_id_seguridad_seq', 5, true);


--
-- Name: tipo_comision_id_tipo_comision_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.tipo_comision_id_tipo_comision_seq', 1, false);


--
-- Name: tipo_envase_id_tipo_envase_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.tipo_envase_id_tipo_envase_seq', 1, false);


--
-- Name: unidad_medida_id_unidad_medida_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.unidad_medida_id_unidad_medida_seq', 1, false);


--
-- Name: unidad_venta_id_unidad_venta_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.unidad_venta_id_unidad_venta_seq', 1, false);


--
-- Name: usuario_id_usuario_seq; Type: SEQUENCE SET; Schema: public; Owner: -
--

SELECT pg_catalog.setval('public.usuario_id_usuario_seq', 2, true);


--
-- Name: agente agente_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agente
    ADD CONSTRAINT agente_pkey PRIMARY KEY (id_agente);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: bodega bodega_nombre_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bodega
    ADD CONSTRAINT bodega_nombre_key UNIQUE (nombre);


--
-- Name: bodega bodega_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.bodega
    ADD CONSTRAINT bodega_pkey PRIMARY KEY (id_bodega);


--
-- Name: ciudad ciudad_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ciudad
    ADD CONSTRAINT ciudad_pkey PRIMARY KEY (id_ciudad);


--
-- Name: clase clase_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.clase
    ADD CONSTRAINT clase_pkey PRIMARY KEY (id_clase);


--
-- Name: clausula_venta clausula_venta_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.clausula_venta
    ADD CONSTRAINT clausula_venta_pkey PRIMARY KEY (id_clausula_venta);


--
-- Name: cliente_proveedor cliente_proveedor_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.cliente_proveedor
    ADD CONSTRAINT cliente_proveedor_pkey PRIMARY KEY (id_cliente_proveedor);


--
-- Name: contacto_orden_compra contacto_orden_compra_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.contacto_orden_compra
    ADD CONSTRAINT contacto_orden_compra_pkey PRIMARY KEY (id_contacto_orden_compra);


--
-- Name: contacto contacto_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.contacto
    ADD CONSTRAINT contacto_pkey PRIMARY KEY (id_contacto);


--
-- Name: contacto_proforma contacto_proforma_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.contacto_proforma
    ADD CONSTRAINT contacto_proforma_pkey PRIMARY KEY (id_contacto_proforma);


--
-- Name: contenedor contenedor_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.contenedor
    ADD CONSTRAINT contenedor_pkey PRIMARY KEY (id_contenedor);


--
-- Name: detalle_factura detalle_factura_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.detalle_factura
    ADD CONSTRAINT detalle_factura_pkey PRIMARY KEY (id_detalle_factura);


--
-- Name: detalle_gasto detalle_gasto_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.detalle_gasto
    ADD CONSTRAINT detalle_gasto_pkey PRIMARY KEY (id_detalle_gasto);


--
-- Name: detalle_ide detalle_ide_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.detalle_ide
    ADD CONSTRAINT detalle_ide_pkey PRIMARY KEY (id_detalle_ide);


--
-- Name: detalle_orden_compra detalle_orden_compra_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.detalle_orden_compra
    ADD CONSTRAINT detalle_orden_compra_pkey PRIMARY KEY (id_detalle_odc);


--
-- Name: detalle_pl detalle_pl_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.detalle_pl
    ADD CONSTRAINT detalle_pl_pkey PRIMARY KEY (id_detalle_pl);


--
-- Name: detalle_proforma detalle_proforma_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.detalle_proforma
    ADD CONSTRAINT detalle_proforma_pkey PRIMARY KEY (id_detalle_proforma);


--
-- Name: direccion direccion_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.direccion
    ADD CONSTRAINT direccion_pkey PRIMARY KEY (id_direccion);


--
-- Name: documento_ide documento_ide_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.documento_ide
    ADD CONSTRAINT documento_ide_pkey PRIMARY KEY (id_documento_ide);


--
-- Name: empresa empresa_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.empresa
    ADD CONSTRAINT empresa_pkey PRIMARY KEY (id_empresa);


--
-- Name: especie especie_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.especie
    ADD CONSTRAINT especie_pkey PRIMARY KEY (id_especie);


--
-- Name: estado_detalle_ple estado_detalle_ple_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.estado_detalle_ple
    ADD CONSTRAINT estado_detalle_ple_pkey PRIMARY KEY (id_estado_detalle_ple);


--
-- Name: estado_odc estado_odc_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.estado_odc
    ADD CONSTRAINT estado_odc_pkey PRIMARY KEY (id_estado_odc);


--
-- Name: estado_oe estado_oe_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.estado_oe
    ADD CONSTRAINT estado_oe_pkey PRIMARY KEY (id_estado_oe);


--
-- Name: estado_pl estado_pl_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.estado_pl
    ADD CONSTRAINT estado_pl_pkey PRIMARY KEY (id_estado_pl);


--
-- Name: estado_proforma estado_proforma_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.estado_proforma
    ADD CONSTRAINT estado_proforma_pkey PRIMARY KEY (id_estado_proforma);


--
-- Name: factura factura_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.factura
    ADD CONSTRAINT factura_pkey PRIMARY KEY (id_factura);


--
-- Name: forma_pago forma_pago_nombre_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.forma_pago
    ADD CONSTRAINT forma_pago_nombre_key UNIQUE (nombre);


--
-- Name: forma_pago forma_pago_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.forma_pago
    ADD CONSTRAINT forma_pago_pkey PRIMARY KEY (id_forma_pago);


--
-- Name: gasto gasto_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.gasto
    ADD CONSTRAINT gasto_pkey PRIMARY KEY (id_gasto);


--
-- Name: ide ide_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ide
    ADD CONSTRAINT ide_pkey PRIMARY KEY (id_ide);


--
-- Name: moneda moneda_etiqueta_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.moneda
    ADD CONSTRAINT moneda_etiqueta_key UNIQUE (etiqueta);


--
-- Name: moneda moneda_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.moneda
    ADD CONSTRAINT moneda_pkey PRIMARY KEY (id_moneda);


--
-- Name: naviera naviera_nombre_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.naviera
    ADD CONSTRAINT naviera_nombre_key UNIQUE (nombre);


--
-- Name: naviera naviera_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.naviera
    ADD CONSTRAINT naviera_pkey PRIMARY KEY (id_naviera);


--
-- Name: operacion_exportacion operacion_exportacion_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.operacion_exportacion
    ADD CONSTRAINT operacion_exportacion_pkey PRIMARY KEY (id_operacion_exportacion);


--
-- Name: orden_compra orden_compra_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.orden_compra
    ADD CONSTRAINT orden_compra_pkey PRIMARY KEY (id_orden_compra);


--
-- Name: pais pais_nombre_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pais
    ADD CONSTRAINT pais_nombre_key UNIQUE (nombre);


--
-- Name: pais pais_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.pais
    ADD CONSTRAINT pais_pkey PRIMARY KEY (id_pais);


--
-- Name: parametro parametro_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.parametro
    ADD CONSTRAINT parametro_pkey PRIMARY KEY (id_parametro);


--
-- Name: plc plc_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.plc
    ADD CONSTRAINT plc_pkey PRIMARY KEY (id_plc);


--
-- Name: ple ple_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ple
    ADD CONSTRAINT ple_pkey PRIMARY KEY (id_ple);


--
-- Name: producto producto_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.producto
    ADD CONSTRAINT producto_pkey PRIMARY KEY (id_producto);


--
-- Name: proforma proforma_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.proforma
    ADD CONSTRAINT proforma_pkey PRIMARY KEY (id_proforma);


--
-- Name: puerto puerto_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.puerto
    ADD CONSTRAINT puerto_pkey PRIMARY KEY (id_puerto);


--
-- Name: seguridad seguridad_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.seguridad
    ADD CONSTRAINT seguridad_pkey PRIMARY KEY (id_seguridad);


--
-- Name: tipo_comision tipo_comision_nombre_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tipo_comision
    ADD CONSTRAINT tipo_comision_nombre_key UNIQUE (nombre);


--
-- Name: tipo_comision tipo_comision_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tipo_comision
    ADD CONSTRAINT tipo_comision_pkey PRIMARY KEY (id_tipo_comision);


--
-- Name: tipo_envase tipo_envase_nombre_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tipo_envase
    ADD CONSTRAINT tipo_envase_nombre_key UNIQUE (nombre);


--
-- Name: tipo_envase tipo_envase_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.tipo_envase
    ADD CONSTRAINT tipo_envase_pkey PRIMARY KEY (id_tipo_envase);


--
-- Name: unidad_medida unidad_medida_nombre_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.unidad_medida
    ADD CONSTRAINT unidad_medida_nombre_key UNIQUE (nombre);


--
-- Name: unidad_medida unidad_medida_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.unidad_medida
    ADD CONSTRAINT unidad_medida_pkey PRIMARY KEY (id_unidad_medida);


--
-- Name: unidad_venta unidad_venta_nombre_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.unidad_venta
    ADD CONSTRAINT unidad_venta_nombre_key UNIQUE (nombre);


--
-- Name: unidad_venta unidad_venta_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.unidad_venta
    ADD CONSTRAINT unidad_venta_pkey PRIMARY KEY (id_unidad_venta);


--
-- Name: empresa uq_empresa_rut; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.empresa
    ADD CONSTRAINT uq_empresa_rut UNIQUE (rut);


--
-- Name: puerto uq_puerto_nombre; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.puerto
    ADD CONSTRAINT uq_puerto_nombre UNIQUE (nombre);


--
-- Name: seguridad uq_seguridad_usuario_modulo; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.seguridad
    ADD CONSTRAINT uq_seguridad_usuario_modulo UNIQUE (id_usuario, modulo);


--
-- Name: usuario uq_usuario_login; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT uq_usuario_login UNIQUE (login);


--
-- Name: usuario usuario_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_pkey PRIMARY KEY (id_usuario);


--
-- Name: usuario usuario_rut_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.usuario
    ADD CONSTRAINT usuario_rut_key UNIQUE (rut);


--
-- Name: ix_agente_id_agente; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_agente_id_agente ON public.agente USING btree (id_agente);


--
-- Name: ix_bodega_id_bodega; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_bodega_id_bodega ON public.bodega USING btree (id_bodega);


--
-- Name: ix_ciudad_id_ciudad; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_ciudad_id_ciudad ON public.ciudad USING btree (id_ciudad);


--
-- Name: ix_ciudad_nombre; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_ciudad_nombre ON public.ciudad USING btree (nombre);


--
-- Name: ix_clase_id_clase; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_clase_id_clase ON public.clase USING btree (id_clase);


--
-- Name: ix_clase_nombre; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_clase_nombre ON public.clase USING btree (nombre);


--
-- Name: ix_cliente_proveedor_id_cliente_proveedor; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_cliente_proveedor_id_cliente_proveedor ON public.cliente_proveedor USING btree (id_cliente_proveedor);


--
-- Name: ix_contacto_id_contacto; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_contacto_id_contacto ON public.contacto USING btree (id_contacto);


--
-- Name: ix_contacto_orden_compra_id_contacto; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_contacto_orden_compra_id_contacto ON public.contacto_orden_compra USING btree (id_contacto);


--
-- Name: ix_contacto_orden_compra_id_contacto_orden_compra; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_contacto_orden_compra_id_contacto_orden_compra ON public.contacto_orden_compra USING btree (id_contacto_orden_compra);


--
-- Name: ix_contacto_orden_compra_id_orden_compra; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_contacto_orden_compra_id_orden_compra ON public.contacto_orden_compra USING btree (id_orden_compra);


--
-- Name: ix_contacto_proforma_id_contacto_proforma; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_contacto_proforma_id_contacto_proforma ON public.contacto_proforma USING btree (id_contacto_proforma);


--
-- Name: ix_contenedor_id_contenedor; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_contenedor_id_contenedor ON public.contenedor USING btree (id_contenedor);


--
-- Name: ix_detalle_pl_id_ple; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_detalle_pl_id_ple ON public.detalle_pl USING btree (id_ple);


--
-- Name: ix_direccion_id_direccion; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_direccion_id_direccion ON public.direccion USING btree (id_direccion);


--
-- Name: ix_especie_id_especie; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_especie_id_especie ON public.especie USING btree (id_especie);


--
-- Name: ix_estado_detalle_ple_id_estado_detalle_ple; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_estado_detalle_ple_id_estado_detalle_ple ON public.estado_detalle_ple USING btree (id_estado_detalle_ple);


--
-- Name: ix_factura_id_factura; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_factura_id_factura ON public.factura USING btree (id_factura);


--
-- Name: ix_pais_id_pais; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_pais_id_pais ON public.pais USING btree (id_pais);


--
-- Name: ix_parametro_id_parametro; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_parametro_id_parametro ON public.parametro USING btree (id_parametro);


--
-- Name: ix_ple_id_estado_pl; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_ple_id_estado_pl ON public.ple USING btree (id_estado_pl);


--
-- Name: ix_ple_id_orden_compra; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_ple_id_orden_compra ON public.ple USING btree (id_orden_compra);


--
-- Name: ix_ple_id_usuario_encargado; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_ple_id_usuario_encargado ON public.ple USING btree (id_usuario_encargado);


--
-- Name: ix_seguridad_id_seguridad; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_seguridad_id_seguridad ON public.seguridad USING btree (id_seguridad);


--
-- Name: ix_usuario_correo; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_usuario_correo ON public.usuario USING btree (correo);


--
-- Name: ix_usuario_id_usuario; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_usuario_id_usuario ON public.usuario USING btree (id_usuario);


--
-- Name: ix_usuario_login; Type: INDEX; Schema: public; Owner: -
--

CREATE UNIQUE INDEX ix_usuario_login ON public.usuario USING btree (login);


--
-- Name: agente agente_id_pais_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.agente
    ADD CONSTRAINT agente_id_pais_fkey FOREIGN KEY (id_pais) REFERENCES public.pais(id_pais);


--
-- Name: ciudad ciudad_id_pais_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ciudad
    ADD CONSTRAINT ciudad_id_pais_fkey FOREIGN KEY (id_pais) REFERENCES public.pais(id_pais);


--
-- Name: contacto contacto_id_cliente_proveedor_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.contacto
    ADD CONSTRAINT contacto_id_cliente_proveedor_fkey FOREIGN KEY (id_cliente_proveedor) REFERENCES public.cliente_proveedor(id_cliente_proveedor);


--
-- Name: contacto_orden_compra contacto_orden_compra_id_contacto_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.contacto_orden_compra
    ADD CONSTRAINT contacto_orden_compra_id_contacto_fkey FOREIGN KEY (id_contacto) REFERENCES public.contacto(id_contacto) ON DELETE CASCADE;


--
-- Name: contacto_orden_compra contacto_orden_compra_id_orden_compra_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.contacto_orden_compra
    ADD CONSTRAINT contacto_orden_compra_id_orden_compra_fkey FOREIGN KEY (id_orden_compra) REFERENCES public.orden_compra(id_orden_compra) ON DELETE CASCADE;


--
-- Name: contacto_proforma contacto_proforma_id_contacto_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.contacto_proforma
    ADD CONSTRAINT contacto_proforma_id_contacto_fkey FOREIGN KEY (id_contacto) REFERENCES public.contacto(id_contacto);


--
-- Name: contacto_proforma contacto_proforma_id_proforma_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.contacto_proforma
    ADD CONSTRAINT contacto_proforma_id_proforma_fkey FOREIGN KEY (id_proforma) REFERENCES public.proforma(id_proforma);


--
-- Name: detalle_factura detalle_factura_id_factura_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.detalle_factura
    ADD CONSTRAINT detalle_factura_id_factura_fkey FOREIGN KEY (id_factura) REFERENCES public.factura(id_factura);


--
-- Name: detalle_gasto detalle_gasto_id_gasto_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.detalle_gasto
    ADD CONSTRAINT detalle_gasto_id_gasto_fkey FOREIGN KEY (id_gasto) REFERENCES public.gasto(id_gasto);


--
-- Name: detalle_ide detalle_ide_id_ide_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.detalle_ide
    ADD CONSTRAINT detalle_ide_id_ide_fkey FOREIGN KEY (id_ide) REFERENCES public.ide(id_ide);


--
-- Name: detalle_ide detalle_ide_id_plc_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.detalle_ide
    ADD CONSTRAINT detalle_ide_id_plc_fkey FOREIGN KEY (id_plc) REFERENCES public.plc(id_plc);


--
-- Name: detalle_orden_compra detalle_orden_compra_id_orden_compra_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.detalle_orden_compra
    ADD CONSTRAINT detalle_orden_compra_id_orden_compra_fkey FOREIGN KEY (id_orden_compra) REFERENCES public.orden_compra(id_orden_compra);


--
-- Name: detalle_orden_compra detalle_orden_compra_id_producto_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.detalle_orden_compra
    ADD CONSTRAINT detalle_orden_compra_id_producto_fkey FOREIGN KEY (id_producto) REFERENCES public.producto(id_producto);


--
-- Name: detalle_orden_compra detalle_orden_compra_id_unidad_medida_ancho_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.detalle_orden_compra
    ADD CONSTRAINT detalle_orden_compra_id_unidad_medida_ancho_fkey FOREIGN KEY (id_unidad_medida_ancho) REFERENCES public.unidad_medida(id_unidad_medida);


--
-- Name: detalle_orden_compra detalle_orden_compra_id_unidad_medida_espesor_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.detalle_orden_compra
    ADD CONSTRAINT detalle_orden_compra_id_unidad_medida_espesor_fkey FOREIGN KEY (id_unidad_medida_espesor) REFERENCES public.unidad_medida(id_unidad_medida);


--
-- Name: detalle_orden_compra detalle_orden_compra_id_unidad_medida_largo_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.detalle_orden_compra
    ADD CONSTRAINT detalle_orden_compra_id_unidad_medida_largo_fkey FOREIGN KEY (id_unidad_medida_largo) REFERENCES public.unidad_medida(id_unidad_medida);


--
-- Name: detalle_orden_compra detalle_orden_compra_id_unidad_venta_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.detalle_orden_compra
    ADD CONSTRAINT detalle_orden_compra_id_unidad_venta_fkey FOREIGN KEY (id_unidad_venta) REFERENCES public.unidad_venta(id_unidad_venta);


--
-- Name: detalle_pl detalle_pl_id_estado_detalle_ple_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.detalle_pl
    ADD CONSTRAINT detalle_pl_id_estado_detalle_ple_fkey FOREIGN KEY (id_estado_detalle_ple) REFERENCES public.estado_detalle_ple(id_estado_detalle_ple);


--
-- Name: detalle_pl detalle_pl_id_plc_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.detalle_pl
    ADD CONSTRAINT detalle_pl_id_plc_fkey FOREIGN KEY (id_plc) REFERENCES public.plc(id_plc);


--
-- Name: detalle_pl detalle_pl_id_ple_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.detalle_pl
    ADD CONSTRAINT detalle_pl_id_ple_fkey FOREIGN KEY (id_ple) REFERENCES public.ple(id_ple);


--
-- Name: detalle_pl detalle_pl_id_unidad_medida_ancho_plc_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.detalle_pl
    ADD CONSTRAINT detalle_pl_id_unidad_medida_ancho_plc_fkey FOREIGN KEY (id_unidad_medida_ancho_plc) REFERENCES public.unidad_medida(id_unidad_medida);


--
-- Name: detalle_pl detalle_pl_id_unidad_medida_ancho_ple_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.detalle_pl
    ADD CONSTRAINT detalle_pl_id_unidad_medida_ancho_ple_fkey FOREIGN KEY (id_unidad_medida_ancho_ple) REFERENCES public.unidad_medida(id_unidad_medida);


--
-- Name: detalle_pl detalle_pl_id_unidad_medida_espesor_plc_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.detalle_pl
    ADD CONSTRAINT detalle_pl_id_unidad_medida_espesor_plc_fkey FOREIGN KEY (id_unidad_medida_espesor_plc) REFERENCES public.unidad_medida(id_unidad_medida);


--
-- Name: detalle_pl detalle_pl_id_unidad_medida_espesor_ple_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.detalle_pl
    ADD CONSTRAINT detalle_pl_id_unidad_medida_espesor_ple_fkey FOREIGN KEY (id_unidad_medida_espesor_ple) REFERENCES public.unidad_medida(id_unidad_medida);


--
-- Name: detalle_pl detalle_pl_id_unidad_medida_largo_plc_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.detalle_pl
    ADD CONSTRAINT detalle_pl_id_unidad_medida_largo_plc_fkey FOREIGN KEY (id_unidad_medida_largo_plc) REFERENCES public.unidad_medida(id_unidad_medida);


--
-- Name: detalle_pl detalle_pl_id_unidad_medida_largo_ple_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.detalle_pl
    ADD CONSTRAINT detalle_pl_id_unidad_medida_largo_ple_fkey FOREIGN KEY (id_unidad_medida_largo_ple) REFERENCES public.unidad_medida(id_unidad_medida);


--
-- Name: detalle_pl detalle_pl_id_unidad_venta_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.detalle_pl
    ADD CONSTRAINT detalle_pl_id_unidad_venta_fkey FOREIGN KEY (id_unidad_venta) REFERENCES public.unidad_venta(id_unidad_venta);


--
-- Name: detalle_proforma detalle_proforma_id_producto_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.detalle_proforma
    ADD CONSTRAINT detalle_proforma_id_producto_fkey FOREIGN KEY (id_producto) REFERENCES public.producto(id_producto);


--
-- Name: detalle_proforma detalle_proforma_id_proforma_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.detalle_proforma
    ADD CONSTRAINT detalle_proforma_id_proforma_fkey FOREIGN KEY (id_proforma) REFERENCES public.proforma(id_proforma);


--
-- Name: detalle_proforma detalle_proforma_id_unidad_medida_ancho_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.detalle_proforma
    ADD CONSTRAINT detalle_proforma_id_unidad_medida_ancho_fkey FOREIGN KEY (id_unidad_medida_ancho) REFERENCES public.unidad_medida(id_unidad_medida);


--
-- Name: detalle_proforma detalle_proforma_id_unidad_medida_espesor_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.detalle_proforma
    ADD CONSTRAINT detalle_proforma_id_unidad_medida_espesor_fkey FOREIGN KEY (id_unidad_medida_espesor) REFERENCES public.unidad_medida(id_unidad_medida);


--
-- Name: detalle_proforma detalle_proforma_id_unidad_medida_largo_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.detalle_proforma
    ADD CONSTRAINT detalle_proforma_id_unidad_medida_largo_fkey FOREIGN KEY (id_unidad_medida_largo) REFERENCES public.unidad_medida(id_unidad_medida);


--
-- Name: detalle_proforma detalle_proforma_id_unidad_venta_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.detalle_proforma
    ADD CONSTRAINT detalle_proforma_id_unidad_venta_fkey FOREIGN KEY (id_unidad_venta) REFERENCES public.unidad_venta(id_unidad_venta);


--
-- Name: direccion direccion_id_ciudad_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.direccion
    ADD CONSTRAINT direccion_id_ciudad_fkey FOREIGN KEY (id_ciudad) REFERENCES public.ciudad(id_ciudad);


--
-- Name: direccion direccion_id_cliente_proveedor_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.direccion
    ADD CONSTRAINT direccion_id_cliente_proveedor_fkey FOREIGN KEY (id_cliente_proveedor) REFERENCES public.cliente_proveedor(id_cliente_proveedor);


--
-- Name: documento_ide documento_ide_id_ide_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.documento_ide
    ADD CONSTRAINT documento_ide_id_ide_fkey FOREIGN KEY (id_ide) REFERENCES public.ide(id_ide);


--
-- Name: empresa empresa_id_ciudad_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.empresa
    ADD CONSTRAINT empresa_id_ciudad_fkey FOREIGN KEY (id_ciudad) REFERENCES public.ciudad(id_ciudad);


--
-- Name: factura factura_id_ide_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.factura
    ADD CONSTRAINT factura_id_ide_fkey FOREIGN KEY (id_ide) REFERENCES public.ide(id_ide);


--
-- Name: ide ide_id_bodega_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ide
    ADD CONSTRAINT ide_id_bodega_fkey FOREIGN KEY (id_bodega) REFERENCES public.bodega(id_bodega);


--
-- Name: ide ide_id_clausula_venta_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ide
    ADD CONSTRAINT ide_id_clausula_venta_fkey FOREIGN KEY (id_clausula_venta) REFERENCES public.clausula_venta(id_clausula_venta);


--
-- Name: ide ide_id_cliente_consignar_a_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ide
    ADD CONSTRAINT ide_id_cliente_consignar_a_fkey FOREIGN KEY (id_cliente_consignar_a) REFERENCES public.cliente_proveedor(id_cliente_proveedor);


--
-- Name: ide ide_id_cliente_facturar_a_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ide
    ADD CONSTRAINT ide_id_cliente_facturar_a_fkey FOREIGN KEY (id_cliente_facturar_a) REFERENCES public.cliente_proveedor(id_cliente_proveedor);


--
-- Name: ide ide_id_cliente_notificar_a_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ide
    ADD CONSTRAINT ide_id_cliente_notificar_a_fkey FOREIGN KEY (id_cliente_notificar_a) REFERENCES public.cliente_proveedor(id_cliente_proveedor);


--
-- Name: ide ide_id_cliente_notificar_tambien_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ide
    ADD CONSTRAINT ide_id_cliente_notificar_tambien_fkey FOREIGN KEY (id_cliente_notificar_tambien) REFERENCES public.cliente_proveedor(id_cliente_proveedor);


--
-- Name: ide ide_id_naviera_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ide
    ADD CONSTRAINT ide_id_naviera_fkey FOREIGN KEY (id_naviera) REFERENCES public.naviera(id_naviera);


--
-- Name: ide ide_id_tipo_envase_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ide
    ADD CONSTRAINT ide_id_tipo_envase_fkey FOREIGN KEY (id_tipo_envase) REFERENCES public.tipo_envase(id_tipo_envase);


--
-- Name: operacion_exportacion operacion_exportacion_consignar_a_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.operacion_exportacion
    ADD CONSTRAINT operacion_exportacion_consignar_a_fkey FOREIGN KEY (consignar_a) REFERENCES public.cliente_proveedor(id_cliente_proveedor);


--
-- Name: operacion_exportacion operacion_exportacion_facturar_a_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.operacion_exportacion
    ADD CONSTRAINT operacion_exportacion_facturar_a_fkey FOREIGN KEY (facturar_a) REFERENCES public.cliente_proveedor(id_cliente_proveedor);


--
-- Name: operacion_exportacion operacion_exportacion_id_estado_oe_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.operacion_exportacion
    ADD CONSTRAINT operacion_exportacion_id_estado_oe_fkey FOREIGN KEY (id_estado_oe) REFERENCES public.estado_oe(id_estado_oe);


--
-- Name: operacion_exportacion operacion_exportacion_id_forma_pago_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.operacion_exportacion
    ADD CONSTRAINT operacion_exportacion_id_forma_pago_fkey FOREIGN KEY (id_forma_pago) REFERENCES public.forma_pago(id_forma_pago);


--
-- Name: operacion_exportacion operacion_exportacion_id_puerto_destino_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.operacion_exportacion
    ADD CONSTRAINT operacion_exportacion_id_puerto_destino_fkey FOREIGN KEY (id_puerto_destino) REFERENCES public.puerto(id_puerto);


--
-- Name: operacion_exportacion operacion_exportacion_id_puerto_origen_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.operacion_exportacion
    ADD CONSTRAINT operacion_exportacion_id_puerto_origen_fkey FOREIGN KEY (id_puerto_origen) REFERENCES public.puerto(id_puerto);


--
-- Name: operacion_exportacion operacion_exportacion_notificar_a_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.operacion_exportacion
    ADD CONSTRAINT operacion_exportacion_notificar_a_fkey FOREIGN KEY (notificar_a) REFERENCES public.cliente_proveedor(id_cliente_proveedor);


--
-- Name: orden_compra orden_compra_id_bodega_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.orden_compra
    ADD CONSTRAINT orden_compra_id_bodega_fkey FOREIGN KEY (id_bodega) REFERENCES public.bodega(id_bodega);


--
-- Name: orden_compra orden_compra_id_cliente_proveedor_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.orden_compra
    ADD CONSTRAINT orden_compra_id_cliente_proveedor_fkey FOREIGN KEY (id_cliente_proveedor) REFERENCES public.cliente_proveedor(id_cliente_proveedor);


--
-- Name: orden_compra orden_compra_id_direccion_proveedor_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.orden_compra
    ADD CONSTRAINT orden_compra_id_direccion_proveedor_fkey FOREIGN KEY (id_direccion_proveedor) REFERENCES public.direccion(id_direccion);


--
-- Name: orden_compra orden_compra_id_empresa_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.orden_compra
    ADD CONSTRAINT orden_compra_id_empresa_fkey FOREIGN KEY (id_empresa) REFERENCES public.empresa(id_empresa);


--
-- Name: orden_compra orden_compra_id_estado_odc_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.orden_compra
    ADD CONSTRAINT orden_compra_id_estado_odc_fkey FOREIGN KEY (id_estado_odc) REFERENCES public.estado_odc(id_estado_odc);


--
-- Name: orden_compra orden_compra_id_moneda_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.orden_compra
    ADD CONSTRAINT orden_compra_id_moneda_fkey FOREIGN KEY (id_moneda) REFERENCES public.moneda(id_moneda);


--
-- Name: orden_compra orden_compra_id_proforma_anterior_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.orden_compra
    ADD CONSTRAINT orden_compra_id_proforma_anterior_fkey FOREIGN KEY (id_proforma_anterior) REFERENCES public.proforma(id_proforma);


--
-- Name: orden_compra orden_compra_id_proforma_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.orden_compra
    ADD CONSTRAINT orden_compra_id_proforma_fkey FOREIGN KEY (id_proforma) REFERENCES public.proforma(id_proforma);


--
-- Name: orden_compra orden_compra_id_usuario_encargado_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.orden_compra
    ADD CONSTRAINT orden_compra_id_usuario_encargado_fkey FOREIGN KEY (id_usuario_encargado) REFERENCES public.usuario(id_usuario);


--
-- Name: orden_compra orden_compra_id_usuario_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.orden_compra
    ADD CONSTRAINT orden_compra_id_usuario_fkey FOREIGN KEY (id_usuario) REFERENCES public.usuario(id_usuario);


--
-- Name: plc plc_id_estado_pl_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.plc
    ADD CONSTRAINT plc_id_estado_pl_fkey FOREIGN KEY (id_estado_pl) REFERENCES public.estado_pl(id_estado_pl);


--
-- Name: plc plc_id_operacion_exportacion_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.plc
    ADD CONSTRAINT plc_id_operacion_exportacion_fkey FOREIGN KEY (id_operacion_exportacion) REFERENCES public.operacion_exportacion(id_operacion_exportacion);


--
-- Name: ple ple_id_estado_pl_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ple
    ADD CONSTRAINT ple_id_estado_pl_fkey FOREIGN KEY (id_estado_pl) REFERENCES public.estado_pl(id_estado_pl) ON DELETE RESTRICT;


--
-- Name: ple ple_id_orden_compra_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ple
    ADD CONSTRAINT ple_id_orden_compra_fkey FOREIGN KEY (id_orden_compra) REFERENCES public.orden_compra(id_orden_compra) ON DELETE RESTRICT;


--
-- Name: ple ple_id_usuario_encargado_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.ple
    ADD CONSTRAINT ple_id_usuario_encargado_fkey FOREIGN KEY (id_usuario_encargado) REFERENCES public.usuario(id_usuario) ON DELETE RESTRICT;


--
-- Name: producto producto_id_clase_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.producto
    ADD CONSTRAINT producto_id_clase_fkey FOREIGN KEY (id_clase) REFERENCES public.clase(id_clase);


--
-- Name: producto producto_id_especie_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.producto
    ADD CONSTRAINT producto_id_especie_fkey FOREIGN KEY (id_especie) REFERENCES public.especie(id_especie);


--
-- Name: proforma proforma_id_agente_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.proforma
    ADD CONSTRAINT proforma_id_agente_fkey FOREIGN KEY (id_agente) REFERENCES public.agente(id_agente);


--
-- Name: proforma proforma_id_clausula_venta_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.proforma
    ADD CONSTRAINT proforma_id_clausula_venta_fkey FOREIGN KEY (id_clausula_venta) REFERENCES public.clausula_venta(id_clausula_venta);


--
-- Name: proforma proforma_id_contenedor_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.proforma
    ADD CONSTRAINT proforma_id_contenedor_fkey FOREIGN KEY (id_contenedor) REFERENCES public.contenedor(id_contenedor);


--
-- Name: proforma proforma_id_direccion_consignar_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.proforma
    ADD CONSTRAINT proforma_id_direccion_consignar_fkey FOREIGN KEY (id_direccion_consignar) REFERENCES public.direccion(id_direccion);


--
-- Name: proforma proforma_id_direccion_facturar_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.proforma
    ADD CONSTRAINT proforma_id_direccion_facturar_fkey FOREIGN KEY (id_direccion_facturar) REFERENCES public.direccion(id_direccion);


--
-- Name: proforma proforma_id_direccion_notificar_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.proforma
    ADD CONSTRAINT proforma_id_direccion_notificar_fkey FOREIGN KEY (id_direccion_notificar) REFERENCES public.direccion(id_direccion);


--
-- Name: proforma proforma_id_empresa_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.proforma
    ADD CONSTRAINT proforma_id_empresa_fkey FOREIGN KEY (id_empresa) REFERENCES public.empresa(id_empresa);


--
-- Name: proforma proforma_id_estado_proforma_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.proforma
    ADD CONSTRAINT proforma_id_estado_proforma_fkey FOREIGN KEY (id_estado_proforma) REFERENCES public.estado_proforma(id_estado_proforma);


--
-- Name: proforma proforma_id_moneda_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.proforma
    ADD CONSTRAINT proforma_id_moneda_fkey FOREIGN KEY (id_moneda) REFERENCES public.moneda(id_moneda);


--
-- Name: proforma proforma_id_operacion_exportacion_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.proforma
    ADD CONSTRAINT proforma_id_operacion_exportacion_fkey FOREIGN KEY (id_operacion_exportacion) REFERENCES public.operacion_exportacion(id_operacion_exportacion);


--
-- Name: proforma proforma_id_tipo_comision_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.proforma
    ADD CONSTRAINT proforma_id_tipo_comision_fkey FOREIGN KEY (id_tipo_comision) REFERENCES public.tipo_comision(id_tipo_comision);


--
-- Name: proforma proforma_id_usuario_encargado_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.proforma
    ADD CONSTRAINT proforma_id_usuario_encargado_fkey FOREIGN KEY (id_usuario_encargado) REFERENCES public.usuario(id_usuario);


--
-- Name: puerto puerto_id_ciudad_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.puerto
    ADD CONSTRAINT puerto_id_ciudad_fkey FOREIGN KEY (id_ciudad) REFERENCES public.ciudad(id_ciudad);


--
-- Name: seguridad seguridad_id_usuario_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.seguridad
    ADD CONSTRAINT seguridad_id_usuario_fkey FOREIGN KEY (id_usuario) REFERENCES public.usuario(id_usuario);


--
-- PostgreSQL database dump complete
--

\unrestrict 90G68rgrFMb9c8EU1crCnDSevA8cDYQzWg6jeNr1BmhgbCbr3miI7dklL73mryC

