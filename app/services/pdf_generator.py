from io import BytesIO
from decimal import Decimal, InvalidOperation
from datetime import date
import os

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    PageBreak,
    CondPageBreak,
    KeepTogether,
    Image as RLImage,
    Flowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.utils import ImageReader

from sqlalchemy.orm import Session

from app.models.proforma import Proforma
from app.models.detalle_proforma import DetalleProforma
from app.models.contacto_proforma import ContactoProforma
from app.models.orden_compra import OrdenCompra
from app.models.detalle_orden_compra import DetalleOrdenCompra
from app.models.contacto_orden_compra import ContactoOrdenCompra
from app.models.contacto import Contacto


# ---------------- Rounded container (reusable) ----------------
class RoundedContainer(Flowable):
    """
    Dibuja un rectángulo con bordes redondeados y pone un Flowable adentro.
    Soporta split() para que, si el contenido es muy alto, pueda pasar a otra página.
    """
    def __init__(
        self,
        inner,
        padding=6,
        radius=10,
        stroke_color=colors.Color(0.70, 0.70, 0.70),  # gris suave
        stroke_width=1,
        fill=0,
    ):
        super().__init__()
        self.inner = inner
        self.padding = padding
        self.radius = radius
        self.stroke_color = stroke_color
        self.stroke_width = stroke_width
        self.fill = fill
        self.width = 0
        self.height = 0
        self.inner_w = 0
        self.inner_h = 0

    def wrap(self, availWidth, availHeight):
        inner_w = max(1, availWidth - 2 * self.padding)
        usable_h = max(1, availHeight - 2 * self.padding)
        w, h = self.inner.wrap(inner_w, usable_h)
        self.inner_w = inner_w
        self.inner_h = h
        self.width = availWidth
        self.height = h + 2 * self.padding
        return self.width, self.height

    def split(self, availWidth, availHeight):
        inner_w = max(1, availWidth - 2 * self.padding)
        usable_h = max(1, availHeight - 2 * self.padding)

        if not hasattr(self.inner, "split"):
            return []

        self.inner.wrap(inner_w, usable_h)
        parts = self.inner.split(inner_w, usable_h)
        if not parts:
            return []

        return [
            RoundedContainer(
                p,
                padding=self.padding,
                radius=self.radius,
                stroke_color=self.stroke_color,
                stroke_width=self.stroke_width,
                fill=self.fill,
            )
            for p in parts
        ]

    def draw(self):
        c = self.canv
        c.saveState()
        c.setStrokeColor(self.stroke_color)
        c.setLineWidth(self.stroke_width)

        try:
            c.roundRect(0, 0, self.width, self.height, self.radius, stroke=1, fill=self.fill)
        except Exception:
            c.rect(0, 0, self.width, self.height, stroke=1, fill=self.fill)

        self.inner.drawOn(c, self.padding, self.padding)
        c.restoreState()


class ProformaPDFGenerator:
    def __init__(self, language: str = "es"):
        self.language = (language or "es").lower()
        self.styles = getSampleStyleSheet()

        # Diccionario de traducciones
        self.translations = {
            "es": {
                "PROFORMA": "PROFORMA",
                "ISSUE_DATE": "Fecha Emisión",
                "BILL_TO": "FACTURAR A",
                "SHIP_TO": "CONSIGNAR A",
                "NOTIFY": "NOTIFICAR A",
                "ADDRESS": "Dirección",
                "CONTACTS": "Contactos",
                "PHONE": "Teléfono",
                "COUNTRY_CITY": "País/Ciudad",
                "SPECIFICATIONS": "ESPECIFICACIONES",
                "NOTE": "NOTA",
                "NOTE_1": "NOTA 1",
                "NOTE_2": "NOTA 2",
                "BUYER": "COMPRADOR",
                "SUPPLIER": "PROVEEDOR",
                "AUTHORIZED_BY": "Autorizado por",
                "PRODUCT": "Producto",
                "QTY": "Cant.",
                "UNIT": "Unidad",
                "THICKNESS": "Espesor",
                "WIDTH": "Ancho",
                "LENGTH": "Largo",
                "UNIT_PRICE": "Precio Unit.",
                "TOTAL": "Total",
            },
            "en": {
                "PROFORMA": "PROFORM",
                "ISSUE_DATE": "Issue Date",
                "BILL_TO": "INVOICE TO",
                "SHIP_TO": "CONSIGN TO",
                "NOTIFY": "NOTIFY TO",
                "ADDRESS": "Address",
                "CONTACTS": "Contacts",
                "PHONE": "Phone",
                "COUNTRY_CITY": "Country/City",
                "SPECIFICATIONS": "SPECIFICATIONS",
                "NOTE": "NOTE",
                "NOTE_1": "NOTE 1",
                "NOTE_2": "NOTE 2",
                "BUYER": "BUYER",
                "SUPPLIER": "SUPPLIER",
                "AUTHORIZED_BY": "Authorized by",
                "PRODUCT": "Product",
                "QTY": "Qty.",
                "UNIT": "Unit",
                "THICKNESS": "Thickness",
                "WIDTH": "Width",
                "LENGTH": "Length",
                "UNIT_PRICE": "Unit Price",
                "TOTAL": "Total",
            }
        }

        # Paleta "gris suave"
        self.border_grey = colors.Color(0.70, 0.70, 0.70)
        self.grid_grey = colors.Color(0.75, 0.75, 0.75)
        self.subtotal_bg = colors.Color(0.93, 0.93, 0.93)

        # Verde bosque para membrete (#143832)
        self.forest_green = colors.Color(0.0784, 0.2196, 0.1961)

        self._setup_styles()
    
    def t(self, key: str) -> str:
        """Helper para obtener traducción"""
        return self.translations.get(self.language, {}).get(key, key)

    # ---------------- Styles ----------------
    def _setup_styles(self):
        self.styles.add(
            ParagraphStyle(
                name="Small",
                fontName="Helvetica",
                fontSize=8,
                leading=10,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="SmallBold",
                fontName="Helvetica-Bold",
                fontSize=8,
                leading=10,
            )
        )

        # MÁS COMPACTO para cajas de dirección (FACT/CONS/NOTIF)
        self.styles.add(
            ParagraphStyle(
                name="SmallBox",
                fontName="Helvetica",
                fontSize=7.2,
                leading=8.6,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="SmallBoxBold",
                fontName="Helvetica-Bold",
                fontSize=7.2,
                leading=8.6,
            )
        )

        # Tabla productos compacta
        self.styles.add(
            ParagraphStyle(
                name="SmallTable",
                fontName="Helvetica",
                fontSize=7,
                leading=8,
            )
        )

        self.styles.add(
            ParagraphStyle(
                name="LineTitle",
                fontName="Helvetica-Bold",
                fontSize=10,
                leading=12,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="CompanyInfo",
                fontName="Helvetica",
                fontSize=8.5,
                leading=11,
                alignment=TA_CENTER,
                textColor=self.forest_green,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="BoxTitle",
                fontName="Helvetica-Bold",
                fontSize=9,
                leading=11,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="BoxBody",
                fontName="Helvetica",
                fontSize=9,
                leading=12,
            )
        )

    # ---------------- Helpers ----------------
    def _format_date(self, d: date) -> str:
        return d.strftime("%d-%m-%Y") if d else "-"

    def _to_decimal(self, v) -> Decimal:
        if v is None:
            return Decimal("0")
        s = str(v).strip()
        if s == "":
            return Decimal("0")
        s = s.replace(" ", "")
        if "," in s and "." in s:
            s = s.replace(".", "").replace(",", ".")
        elif "," in s and "." not in s:
            s = s.replace(",", ".")
        try:
            return Decimal(s)
        except InvalidOperation:
            return Decimal("0")

    def _fmt_money_cl(self, v: Decimal) -> str:
        v = Decimal(v or 0)
        s = f"{v:,.2f}"
        return s.replace(",", "X").replace(".", ",").replace("X", ".")

    def _fmt_qty(self, v: Decimal) -> str:
        v = Decimal(v or 0)
        s = f"{v:,.3f}"
        return s.replace(",", "X").replace(".", ",").replace("X", ".")

    def _get_logo_path(self):
        possible = [
            os.path.join(os.getcwd(), "app", "static", "logo_pacific_forest.png"),
            os.path.join(os.getcwd(), "app", "static", "logo.png"),
            os.path.join(os.getcwd(), "static", "logo_pacific_forest.png"),
            os.path.join(os.getcwd(), "static", "logo.png"),
        ]
        for p in possible:
            if os.path.exists(p):
                return p
        return None

    def _set_canvas_alpha(self, canv: canvas.Canvas, alpha: float):
        """
        Transparencia en ReportLab (si el backend/versión lo soporta).
        """
        try:
            canv.setFillAlpha(alpha)
            canv.setStrokeAlpha(alpha)
        except Exception:
            pass

    def _draw_right_watermark(self, canv: canvas.Canvas, doc: SimpleDocTemplate):
        """
        Imagen de fondo (NO el logo principal):
        - archivo: 'logo con transparencia.png'
        - pegada al borde derecho
        - comienza en esquina superior derechas
        - altura aprox mitad de página
        """
        watermark_path = os.path.join(
            os.getcwd(), "app", "static", "logo con transparencia.png"
        )

        if not os.path.exists(watermark_path):
            return

        page_w, page_h = doc.pagesize

        img = ImageReader(watermark_path)
        iw, ih = img.getSize()
        if not iw or not ih:
            return

        # Altura ~ mitad de página
        target_h = page_h * 0.50
        scale = target_h / float(ih)

        draw_w = float(iw) * scale
        draw_h = float(ih) * scale

        # Pegado al borde derecho, esquina superior
        x = page_w - draw_w
        y = page_h - draw_h

        canv.saveState()

        # Transparencia
        self._set_canvas_alpha(canv, 0.45)

        canv.drawImage(
            img,
            x,
            y,
            width=draw_w,
            height=draw_h,
            mask="auto",
        )

        canv.restoreState()



    # ---------------- Data Extraction ----------------
    def _get_cliente_nombre(self, cliente_proveedor):
        """Obtiene el nombre de un ClienteProveedor (razon_social o nombre_fantasia)"""
        if not cliente_proveedor:
            return "-"
        return (
            cliente_proveedor.razon_social
            or cliente_proveedor.nombre_fantasia
            or "-"
        )

    def _get_contactos(self, proforma: Proforma, db: Session):
        """Obtiene los contactos asociados a la proforma"""
        contacto_phone = None
        contactos = []

        cps = (
            db.query(ContactoProforma)
            .filter(ContactoProforma.id_proforma == proforma.id_proforma)
            .all()
        )

        for cp in cps:
            c = cp.Contacto
            if not c:
                continue

            parts = []
            if c.nombre:
                parts.append(c.nombre)
            if c.telefono:
                parts.append(c.telefono)
                if not contacto_phone:
                    contacto_phone = c.telefono
            if c.correo:
                parts.append(c.correo)

            if parts:
                contactos.append(" - ".join(parts))

        contactos_html = "<br/>".join(contactos) if contactos else None
        return contactos_html, contacto_phone

    # ---------------- Header blocks (flowables) ----------------
    def _header_flowable(self):
        logo_path = self._get_logo_path()
        if logo_path:
            logo = RLImage(logo_path, width=1.8 * inch, height=1.3 * inch)
        else:
            logo = Paragraph("PACIFIC FOREST", self.styles["LineTitle"])

        company = Paragraph(
            "<b>COMERCIALIZADORA FORESTAL SPA.</b><br/>"
            "Av. Bernardo O'Higgins 77, Depto.1205., Concepción, Región del Bio Bio, CHILE<br/>"
            "+56-412185630  +56-412185631<br/>"
            "CONCEPCIÓN, CHILE",
            self.styles["CompanyInfo"],
        )

        company_tbl = Table([[company]], colWidths=[5.25 * inch])
        company_tbl.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )
        company_box = RoundedContainer(
            company_tbl,
            padding=0,
            radius=12,
            stroke_color=self.border_grey,
            stroke_width=1,
        )

        t = Table([[logo, company_box]], colWidths=[1.85 * inch, 5.1 * inch])
        t.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ALIGN", (0, 0), (0, 0), "CENTER"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ]
            )
        )
        return t

    def _proforma_line_flowable(self, proforma: Proforma):
        proforma_code = f"{proforma.OperacionExportacion.id_operacion_exportacion}-{proforma.id_proforma}"
        left = Paragraph(f"<b>{self.t('PROFORMA')}:</b> {proforma_code}", self.styles["LineTitle"])
        right = Paragraph(
            f"<b>{self.t('ISSUE_DATE')}:</b> {self._format_date(proforma.fecha_emision)}",
            self.styles["LineTitle"],
        )
        t = Table([[left, right]], colWidths=[3.5 * inch, 3.5 * inch])
        t.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (0, 0), "LEFT"),
                    ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                ]
            )
        )
        return t

    def _draw_page_header(self, canv: canvas.Canvas, doc: SimpleDocTemplate, proforma: Proforma):
        canv.saveState()

        # 1) watermark (fondo)
        self._draw_right_watermark(canv, doc)

        page_w, page_h = doc.pagesize
        x = doc.leftMargin
        y_top = page_h - 0.35 * inch

        header_flow = self._header_flowable()
        w1, h1 = header_flow.wrap(doc.width, doc.topMargin)
        y_header = y_top - h1
        header_flow.drawOn(canv, x, y_header)

        line_flow = self._proforma_line_flowable(proforma)
        w2, h2 = line_flow.wrap(doc.width, doc.topMargin)
        y_line = y_header - 0.10 * inch - h2
        line_flow.drawOn(canv, x, y_line)

        canv.restoreState()

    # ---------------- Layout blocks ----------------
    def _address_block(
        self,
        title: str,
        name: str,
        address: str,
        phone: str,
        country_city: str,
        contactos_html: str | None = None,
    ):
        data = [
            [Paragraph(title, self.styles["SmallBoxBold"]), Paragraph(f"<b>{name or '-'}</b>", self.styles["SmallBox"])],
            [Paragraph(self.t("ADDRESS"), self.styles["SmallBoxBold"]), Paragraph(address or "-", self.styles["SmallBox"])],
        ]

        if contactos_html:
            data.append([Paragraph(self.t("CONTACTS"), self.styles["SmallBoxBold"]), Paragraph(contactos_html, self.styles["SmallBox"])])

        data += [
            [Paragraph(self.t("PHONE"), self.styles["SmallBoxBold"]), Paragraph(phone or "-", self.styles["SmallBox"])],
            [Paragraph(self.t("COUNTRY_CITY"), self.styles["SmallBoxBold"]), Paragraph(country_city or "-", self.styles["SmallBox"])],
        ]

        t = Table(data, colWidths=[1.15 * inch, 5.80 * inch])
        t.setStyle(
            TableStyle(
                [
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, self.grid_grey),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 2),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ]
            )
        )

        return RoundedContainer(
            t,
            padding=4,
            radius=10,
            stroke_color=self.border_grey,
            stroke_width=1,
        )

    def _products_table(self, proforma: Proforma, db: Session):
        details = (
            db.query(DetalleProforma)
            .filter(DetalleProforma.id_proforma == proforma.id_proforma)
            .all()
        )

        header = [
            "#", 
            self.t("PRODUCT"), 
            self.t("QTY"), 
            self.t("UNIT"), 
            self.t("THICKNESS"), 
            self.t("WIDTH"), 
            self.t("LENGTH"), 
            self.t("UNIT_PRICE"), 
            self.t("TOTAL")
        ]
        rows = [header]

        subtotal = Decimal("0")

        for i, d in enumerate(details, start=1):
            qty = self._to_decimal(d.cantidad)
            unit_price = self._to_decimal(d.precio_unitario)
            line_total = qty * unit_price
            subtotal += line_total

            # Usar texto_libre si existe, sino usar el nombre del producto
            if d.texto_libre:
                producto = d.texto_libre
            elif self.language == "es":
                producto = d.producto_nombre_esp or d.producto_nombre_ing or "-"
            else:
                producto = d.producto_nombre_ing or d.producto_nombre_esp or "-"

            unidad = "M3"
            if d.UnidadVenta is not None:
                unidad = (
                    getattr(d.UnidadVenta, "abreviatura", None)
                    or getattr(d.UnidadVenta, "nombre", None)
                    or getattr(d.UnidadVenta, "codigo", None)
                    or "M3"
                )

            um_e = getattr(d.UnidadMedidaEspesor, "abreviatura", None) or getattr(d.UnidadMedidaEspesor, "nombre", None) or ""
            um_a = getattr(d.UnidadMedidaAncho, "abreviatura", None) or getattr(d.UnidadMedidaAncho, "nombre", None) or ""
            um_l = getattr(d.UnidadMedidaLargo, "abreviatura", None) or getattr(d.UnidadMedidaLargo, "nombre", None) or ""

            espesor = f"{d.espesor} {um_e}".strip() if d.espesor else "-"
            ancho = f"{d.ancho} {um_a}".strip() if d.ancho else "-"
            largo = f"{d.largo} {um_l}".strip() if d.largo else "-"

            rows.append(
                [
                    str(i),
                    Paragraph(str(producto), self.styles["SmallTable"]),
                    self._fmt_qty(qty),
                    str(unidad),
                    espesor,
                    ancho,
                    largo,
                    self._fmt_money_cl(unit_price),
                    self._fmt_money_cl(line_total),
                ]
            )

        moneda_code = (getattr(proforma.Moneda, "etiqueta", None) or "").strip()

        # En vez de usar id_clausula_venta (que suele ser un número), intenta sacar un texto tipo "CIF"
        cv = getattr(proforma, "ClausulaVenta", None)
        clausula_venta = (str(getattr(proforma, "id_clausula_venta", "") or "").strip())
        label = f"<nobr>{moneda_code} SUBTOTAL {clausula_venta}</nobr>"




      

        rows.append([
        "",  # 0
        "",  # 1
        "",  # 2
        "",  # 3
        "",  # 4
        "",  # 5
        "",  # 6
        Paragraph(f"<b>{label}</b>", self.styles["SmallBold"]),  # 7 (label)
        Paragraph(f"<b>{self._fmt_money_cl(subtotal)}</b>", self.styles["SmallBold"]),  # 8 (total)
        ])


        col_widths = [
            0.30 * inch,
            2.10 * inch,
            0.70 * inch,
            0.50 * inch,
            0.60 * inch,
            0.60 * inch,
            0.70 * inch,
            1.30 * inch,
            0.95 * inch,
        ]

        t = Table(rows, colWidths=col_widths, repeatRows=1)
        last = len(rows) - 1

        t.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.5, self.grid_grey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 7.2),
                    ("FONTSIZE", (0, 1), (-1, -1), 7.0),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ALIGN", (0, 0), (0, -1), "CENTER"),
                    ("ALIGN", (1, 1), (1, last - 1), "LEFT"),
                    ("ALIGN", (2, 1), (6, last - 1), "CENTER"),
                    ("ALIGN", (7, 1), (8, -1), "RIGHT"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 2),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                    ("TOPPADDING", (0, 0), (-1, -1), 1),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                    
                    # Evitar que se parta el texto en la columna del label
                    ("WORDWRAP", (7, last), (7, last), "OFF"),

                    # --- Subtotal: sombrear SOLO las 2 celdas finales ---

                    ("BACKGROUND", (7, last), (8, last), self.subtotal_bg),
                    ("FONTNAME", (7, last), (8, last), "Helvetica-Bold"),

                    # Alineaciones del bloque subtotal
                    ("ALIGN", (7, last), (7, last), "RIGHT"),
                    ("ALIGN", (8, last), (8, last), "RIGHT"),

                    # Si quieres que se vea como "bloque" (opcional pero queda muy parecido al Yii)
                    ("BOX", (7, last), (8, last), 0.8, self.grid_grey),

                    # Quitar líneas (grid) del resto de la fila subtotal para que no parezca fila completa
                    ("GRID", (0, last), (6, last), 0, colors.white),
                    ("LINEABOVE", (0, last), (6, last), 0, colors.white),
                    ("LINEBELOW", (0, last), (6, last), 0, colors.white),
                    ("LINEBEFORE", (0, last), (6, last), 0, colors.white),
                    ("LINEAFTER", (0, last), (6, last), 0, colors.white),

                ]
            )
        )
        return t

    def _note_box(self, title: str, body: str | None):
        if not body or not str(body).strip():
            return None

        title_p = Paragraph(title, self.styles["BoxTitle"])
        body_html = "<br/>".join([ln.strip() for ln in str(body).splitlines() if ln.strip()])
        body_p = Paragraph(body_html, self.styles["BoxBody"])

        inner = Table([[title_p], [body_p]], colWidths=[6.9 * inch])
        inner.setStyle(
            TableStyle(
                [
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )

        return RoundedContainer(
            inner,
            padding=0,
            radius=10,
            stroke_color=self.border_grey,
            stroke_width=1,
        )

    def _signatures(self, proforma: Proforma):
        # Altura de espacio antes de la línea de firma
        sign_gap = 0.75 * inch

        left = Table(
            [
                [Paragraph(self.t("BUYER"), self.styles["SmallBold"])],
                [Spacer(1, sign_gap)],
                [Paragraph("______________________________", self.styles["Small"])],
                [Paragraph(self.t("AUTHORIZED_BY"), self.styles["Small"])],
            ],
            colWidths=[3.4 * inch],
        )

        usuario_nombre = "-"
        usuario_telefono = "-"
        firma_img = None
        
        if getattr(proforma, "UsuarioEncargado", None):
            nombre_raw = getattr(proforma.UsuarioEncargado, "nombre", None) or "-"
            usuario_nombre = nombre_raw.title() if nombre_raw != "-" else "-"
            usuario_telefono = getattr(proforma.UsuarioEncargado, "telefono", None) or "-"
            url_firma = getattr(proforma.UsuarioEncargado, "url_firma", None)
            
            # Cargar imagen de firma si existe
            if url_firma:
                # Convertir la URL relativa a ruta absoluta
                if url_firma.startswith("/static/"):
                    firma_path = os.path.join(os.getcwd(), "app", url_firma.replace("/static/", "static/"))
                else:
                    firma_path = url_firma
                
                if os.path.exists(firma_path):
                    try:
                        # Crear imagen con tamaño controlado, manteniendo aspecto
                        from reportlab.platypus import Image as RLImage
                        firma_img = RLImage(firma_path, width=2*inch, height=0.7*inch, kind='proportional')
                    except Exception as e:
                        pass

        # Construir la tabla derecha con la firma sobre la línea (sin espacio entre firma y línea)
        if firma_img:
            # Con firma: título, espacio pequeño, firma pegada a línea, nombre, teléfono
            right_rows = [
                [Paragraph(self.t("SUPPLIER"), self.styles["SmallBold"])],
                [Spacer(1, 0.05*inch)],  # Espacio mínimo
                [firma_img],
                [Paragraph("______________________________", self.styles["Small"])],
                [Paragraph(usuario_nombre, self.styles["Small"])],
                [Paragraph(usuario_telefono, self.styles["Small"])],
            ]
        else:
            # Sin firma: mantener el layout original
            right_rows = [
                [Paragraph(self.t("SUPPLIER"), self.styles["SmallBold"])],
                [Spacer(1, sign_gap)],
                [Paragraph("______________________________", self.styles["Small"])],
                [Paragraph(usuario_nombre, self.styles["Small"])],
                [Paragraph(usuario_telefono, self.styles["Small"])],
            ]

        right = Table(right_rows, colWidths=[3.4 * inch])

        t = Table([[left, right]], colWidths=[3.45 * inch, 3.45 * inch])
        t.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ]
            )
        )
        return t

    def _image_page(self, url_imagen: str):
        """
        Crea una página con una imagen centrada.
        """
        if not url_imagen:
            return None
        
        # Convertir URL relativa a ruta absoluta
        if url_imagen.startswith("/static/"):
            img_path = os.path.join(os.getcwd(), "app", url_imagen.replace("/static/", "static/"))
        else:
            img_path = url_imagen
        
        if not os.path.exists(img_path):
            return None
        
        try:
            # Crear imagen con ancho máximo de página, manteniendo proporción
            img = RLImage(img_path, width=7*inch, height=9*inch, kind='proportional')
            return img
        except Exception as e:
            return None

    # ---------------- Public API ----------------
    def generate_pdf(self, proforma: Proforma, db: Session) -> BytesIO:
        buffer = BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            topMargin=2.25 * inch,
            bottomMargin=0.45 * inch,
            leftMargin=0.55 * inch,
            rightMargin=0.55 * inch,
        )

        elements = []

        # Obtener contactos para mostrar en la sección de facturar
        contactos_html, contacto_phone = self._get_contactos(proforma, db)

        # Obtener nombres de clientes desde OperacionExportacion
        facturar_name = "-"
        consignar_name = "-"
        notificar_name = "-"
        
        if proforma.OperacionExportacion:
            oe = proforma.OperacionExportacion
            facturar_name = self._get_cliente_nombre(oe.FacturarA)
            consignar_name = self._get_cliente_nombre(oe.ConsignarA)
            notificar_name = self._get_cliente_nombre(oe.NotificarA)

        def _direccion_info(direccion):
            if not direccion:
                return {"texto": None, "ciudad": None, "pais": None, "fono_1": None}
            ciudad = direccion.Ciudad.nombre if direccion.Ciudad else None
            pais = direccion.Ciudad.Pais.nombre if direccion.Ciudad and direccion.Ciudad.Pais else None
            return {
                "texto": direccion.direccion,
                "ciudad": ciudad,
                "pais": pais,
                "fono_1": direccion.fono_1,
            }

        dir_fact = _direccion_info(proforma.DireccionFacturar)
        dir_cons = _direccion_info(proforma.DireccionConsignar)
        dir_not = _direccion_info(proforma.DireccionNotificar)

        facturar_country_city = f"{dir_fact['pais'] or '-'} / {dir_fact['ciudad'] or '-'}"
        consignar_country_city = f"{dir_cons['pais'] or '-'} / {dir_cons['ciudad'] or '-'}"
        notificar_country_city = f"{dir_not['pais'] or '-'} / {dir_not['ciudad'] or '-'}"

        fono_fact = dir_fact["fono_1"] or contacto_phone or "-"
        fono_cons = dir_cons["fono_1"] or contacto_phone or "-"
        fono_not = dir_not["fono_1"] or contacto_phone or "-"

        # ===== PAGE 1 =====
        elements.append(
            self._address_block(
                self.t("BILL_TO"),
                facturar_name,
                dir_fact["texto"],
                fono_fact,
                facturar_country_city,
                contactos_html=contactos_html,
            )
        )
        elements.append(Spacer(1, 0.03 * inch))
        elements.append(
            self._address_block(
                self.t("SHIP_TO"),
                consignar_name,
                dir_cons["texto"],
                fono_cons,
                consignar_country_city,
                contactos_html=None,
            )
        )
        elements.append(Spacer(1, 0.03 * inch))
        elements.append(
            self._address_block(
                self.t("NOTIFY"),
                notificar_name,
                dir_not["texto"],
                fono_not,
                notificar_country_city,
                contactos_html=None,
            )
        )

        elements.append(Spacer(1, 0.08 * inch))
        elements.append(self._products_table(proforma, db))

        if getattr(proforma, "especificaciones", None):
            spec_box = self._note_box(self.t("SPECIFICATIONS"), proforma.especificaciones)
            if spec_box:
                elements.append(Spacer(1, 0.12 * inch))
                elements.append(spec_box)

        # ===== PAGE 2 =====
        elements.append(PageBreak())

        b0 = self._note_box(self.t("NOTE"), getattr(proforma, "nota", None))
        if b0:
            elements.append(b0)
            elements.append(Spacer(1, 0.15 * inch))

        b1 = self._note_box(self.t("NOTE_1"), getattr(proforma, "nota_1", None))
        if b1:
            elements.append(b1)
            elements.append(Spacer(1, 0.15 * inch))

        b2 = self._note_box(self.t("NOTE_2"), getattr(proforma, "nota_2", None))
        if b2:
            elements.append(b2)

        # ===== PAGE 3 =====
        elements.append(PageBreak())
        elements.append(Spacer(1, 0.7 * inch))
        elements.append(self._signatures(proforma))

        # ===== PAGE 4 (si hay imagen) =====
        if getattr(proforma, "url_imagen", None):
            img = self._image_page(proforma.url_imagen)
            if img:
                elements.append(PageBreak())
                elements.append(Spacer(1, 0.5 * inch))
                elements.append(img)

        def on_page(canv, d):
            self._draw_page_header(canv, d, proforma)

        doc.build(
            elements,
            onFirstPage=on_page,
            onLaterPages=on_page,
            canvasmaker=NumberedCanvas,
        )

        buffer.seek(0)
        return buffer


class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total_pages = len(self._saved_page_states)
        for page_num, state in enumerate(self._saved_page_states, start=1):
            self.__dict__.update(state)
            self.draw_page_number(page_num, total_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_num, total_pages):
        self.setFont("Helvetica", 8)
        self.setFillColorRGB(0.4, 0.4, 0.4)
        self.drawRightString(7.75 * inch, 0.35 * inch, f"Página {page_num} de {total_pages}")


# ============================================================
#  OrdenCompraPDFGenerator
# ============================================================
class OrdenCompraPDFGenerator(ProformaPDFGenerator):
    """Genera PDFs de Orden de Compra con el mismo diseño que la Proforma."""

    def __init__(self, language: str = "es"):
        super().__init__(language)
        # Extend translations with ODC-specific keys
        self.translations["es"].update({
            "PURCHASE_ORDER": "ORDEN DE COMPRA",
            "CLIENT": "SEÑORES",
            "REQUEST_ITEMS": "Solicitamos producción de los siguientes ítems :",
            "ASSIGN_TO": "Asignar a:",
            "RUT": "RUT",
            "DELIVERY_DATE": "Fecha Entrega",
            "STORE": "Bodega",
            "DESTINATION": "Destino",
            "QUALITY_OBS": "OBSERVACIONES DE CALIDAD",
            "OTHER_SPECS": "OTRAS ESPECIFICACIONES",
            "NOTE_ODC": "NOTAS",
            "AUTHORIZED_BY_ODC": "Autorizado por",
            "RESPONSIBLE": "ENCARGADO",
        })
        self.translations["en"].update({
            "PURCHASE_ORDER": "PURCHASE ORDER",
            "CLIENT": "Company",
            "REQUEST_ITEMS": "We request production of the following items :",
            "ASSIGN_TO": "Assign to:",
            "RUT": "RUT",
            "DELIVERY_DATE": "Delivery Date",
            "STORE": "Store",
            "DESTINATION": "Destination",
            "QUALITY_OBS": "QUALITY OBSERVATIONS",
            "OTHER_SPECS": "OTHER SPECIFICATIONS",
            "NOTE_ODC": "NOTES",
            "AUTHORIZED_BY_ODC": "Authorized by",
            "RESPONSIBLE": "RESPONSIBLE",
        })

    # ------------------------------------------------------------------ #
    #  Dynamic company header (uses Empresa from OrdenCompra)             #
    # ------------------------------------------------------------------ #
    def _header_flowable_empresa(self, empresa=None):
        logo_path = self._get_logo_path()
        if logo_path:
            logo = RLImage(logo_path, width=1.8 * inch, height=1.3 * inch)
        else:
            logo = Paragraph("PACIFIC FOREST", self.styles["LineTitle"])

        if empresa:
            nombre = empresa.razon_social or empresa.nombre_fantasia or "PACIFIC FOREST"
            direccion = empresa.direccion or ""
            tel1 = empresa.telefono_1 or ""
            tel2 = empresa.telefono_2 or ""
            telefonos = "  ".join(filter(None, [tel1, tel2]))
            # Try to get city/country from empresa
            ciudad_txt = ""
            if getattr(empresa, "Ciudad", None):
                ciudad_txt = empresa.Ciudad.nombre or ""
            company_text = (
                f"<b>{nombre}</b><br/>"
                f"{direccion}<br/>"
                f"{telefonos}<br/>"
                f"{ciudad_txt}"
            )
        else:
            company_text = (
                "<b>COMERCIALIZADORA FORESTAL SPA.</b><br/>"
                "Av. Bernardo O'Higgins 77, Depto.1205., Concepción, Región del Bio Bio, CHILE<br/>"
                "+56-412185630  +56-412185631<br/>"
                "CONCEPCIÓN, CHILE"
            )

        company = Paragraph(company_text, self.styles["CompanyInfo"])

        company_tbl = Table([[company]], colWidths=[5.25 * inch])
        company_tbl.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 10),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                    ("TOPPADDING", (0, 0), (-1, -1), 8),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ]
            )
        )
        company_box = RoundedContainer(
            company_tbl,
            padding=0,
            radius=12,
            stroke_color=self.border_grey,
            stroke_width=1,
        )

        t = Table([[logo, company_box]], colWidths=[1.85 * inch, 5.1 * inch])
        t.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ALIGN", (0, 0), (0, 0), "CENTER"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                ]
            )
        )
        return t

    def _odc_line_flowable(self, orden_compra: OrdenCompra):
        """Returns only the left part (ODC code) as a flowable.
        The date is drawn directly on the canvas in _draw_odc_page_header."""
        oe_id = None
        if orden_compra.Proforma and getattr(orden_compra.Proforma, "OperacionExportacion", None):
            oe_id = orden_compra.Proforma.OperacionExportacion.id_operacion_exportacion
        if oe_id:
            odc_code = f"{oe_id}-{orden_compra.id_orden_compra}"
        else:
            odc_code = str(orden_compra.id_orden_compra)

        left = Paragraph(
            f"<b>{self.t('PURCHASE_ORDER')}:</b> {odc_code}",
            self.styles["LineTitle"],
        )
        return left

    def _odc_date_label(self, orden_compra: OrdenCompra) -> str:
        """Returns the formatted issue date label for direct canvas drawing."""
        return f"{self.t('ISSUE_DATE')}: {self._format_date(orden_compra.fecha_emision)}"

    def _draw_odc_page_header(
        self,
        canv: canvas.Canvas,
        doc: SimpleDocTemplate,
        orden_compra: OrdenCompra,
    ):
        canv.saveState()
        self._draw_right_watermark(canv, doc)

        page_w, page_h = doc.pagesize
        x = doc.leftMargin
        y_top = page_h - 0.35 * inch

        header_flow = self._header_flowable_empresa(getattr(orden_compra, "Empresa", None))
        w1, h1 = header_flow.wrap(doc.width, doc.topMargin)
        y_header = y_top - h1
        header_flow.drawOn(canv, x, y_header)

        line_flow = self._odc_line_flowable(orden_compra)
        w2, h2 = line_flow.wrap(doc.width, doc.topMargin)
        y_line = y_header - 0.10 * inch - h2
        line_flow.drawOn(canv, x, y_line)

        # Draw issue date at the exact right margin, same vertical position
        date_label = self._odc_date_label(orden_compra)
        canv.setFont("Helvetica-Bold", 10)
        canv.setFillColor(colors.black)
        canv.drawRightString(page_w - doc.rightMargin, y_line, date_label)

        # Draw "Asignar a: X" centered between left and right, only if vinculado exists
        vinculado = getattr(orden_compra, "vinculado", None)
        if vinculado:
            assign_label = f"{self.t('ASSIGN_TO')} {vinculado}"
            canv.setFont("Helvetica-Bold", 10)
            canv.drawCentredString(page_w / 2, y_line, assign_label)

        canv.restoreState()

    # ------------------------------------------------------------------ #
    #  Client block                                                        #
    # ------------------------------------------------------------------ #
    def _client_block(
        self,
        orden_compra: OrdenCompra,
        contactos_html: str | None,
    ):
        cp = orden_compra.ClienteProveedor
        nombre = "-"
        rut = "-"
        if cp:
            nombre = cp.razon_social or cp.nombre_fantasia or "-"
            rut = cp.rut or "-"

        direccion_txt = "-"
        pais_ciudad = "-"
        if getattr(orden_compra, "DireccionProveedor", None):
            d = orden_compra.DireccionProveedor
            direccion_txt = d.direccion or "-"
            ciudad = d.Ciudad.nombre if d.Ciudad else None
            pais = d.Ciudad.Pais.nombre if d.Ciudad and d.Ciudad.Pais else None
            pais_ciudad = f"{pais or '-'} / {ciudad or '-'}"

        bodega_nombre = "-"
        if getattr(orden_compra, "Bodega", None):
            bodega_nombre = orden_compra.Bodega.nombre or "-"

        fecha_entrega = self._format_date(orden_compra.fecha_entrega)
        destino = orden_compra.destino or "-"

        data = [
            [
                Paragraph(self.t("CLIENT"), self.styles["SmallBoxBold"]),
                Paragraph(f"<b>{nombre}</b>", self.styles["SmallBox"]),
            ],
            [
                Paragraph(self.t("RUT"), self.styles["SmallBoxBold"]),
                Paragraph(rut, self.styles["SmallBox"]),
            ],
            [
                Paragraph(self.t("ADDRESS"), self.styles["SmallBoxBold"]),
                Paragraph(direccion_txt, self.styles["SmallBox"]),
            ],
        ]

        if contactos_html:
            data.append([
                Paragraph(self.t("CONTACTS"), self.styles["SmallBoxBold"]),
                Paragraph(contactos_html, self.styles["SmallBox"]),
            ])

        data += [
            [
                Paragraph(self.t("DELIVERY_DATE"), self.styles["SmallBoxBold"]),
                Paragraph(fecha_entrega, self.styles["SmallBox"]),
            ],
            [
                Paragraph(self.t("STORE"), self.styles["SmallBoxBold"]),
                Paragraph(bodega_nombre, self.styles["SmallBox"]),
            ],
            [
                Paragraph(self.t("COUNTRY_CITY"), self.styles["SmallBoxBold"]),
                Paragraph(pais_ciudad, self.styles["SmallBox"]),
            ],
            [
                Paragraph(self.t("DESTINATION"), self.styles["SmallBoxBold"]),
                Paragraph(destino, self.styles["SmallBox"]),
            ],
        ]

        t = Table(data, colWidths=[1.15 * inch, 5.80 * inch])
        t.setStyle(
            TableStyle(
                [
                    ("INNERGRID", (0, 0), (-1, -1), 0.5, self.grid_grey),
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 4),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                    ("TOPPADDING", (0, 0), (-1, -1), 2),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ]
            )
        )

        return RoundedContainer(
            t,
            padding=4,
            radius=10,
            stroke_color=self.border_grey,
            stroke_width=1,
        )

    # ------------------------------------------------------------------ #
    #  Contacts helper                                                     #
    # ------------------------------------------------------------------ #
    def _get_odc_contactos(self, orden_compra: OrdenCompra, db: Session):
        contacto_phone = None
        contactos = []

        # Only contacts explicitly linked to the purchase order
        odc_contacts = (
            db.query(Contacto)
            .join(
                ContactoOrdenCompra,
                ContactoOrdenCompra.id_contacto == Contacto.id_contacto,
            )
            .filter(ContactoOrdenCompra.id_orden_compra == orden_compra.id_orden_compra)
            .all()
        )

        for c in odc_contacts:
            if not c:
                continue
            parts = []
            if c.nombre:
                parts.append(c.nombre)
            if c.telefono:
                parts.append(c.telefono)
                if not contacto_phone:
                    contacto_phone = c.telefono
            if c.correo:
                parts.append(c.correo)
            if parts:
                contactos.append(" - ".join(parts))

        contactos_html = "<br/>".join(contactos) if contactos else None
        return contactos_html, contacto_phone

    # ------------------------------------------------------------------ #
    #  Products table                                                      #
    # ------------------------------------------------------------------ #
    def _odc_products_table(self, orden_compra: OrdenCompra, db: Session):
        details = (
            db.query(DetalleOrdenCompra)
            .filter(DetalleOrdenCompra.id_orden_compra == orden_compra.id_orden_compra)
            .all()
        )

        header = [
            "#",
            self.t("PRODUCT"),
            self.t("QTY"),
            self.t("UNIT"),
            self.t("THICKNESS"),
            self.t("WIDTH"),
            self.t("LENGTH"),
            self.t("UNIT_PRICE"),
            self.t("TOTAL"),
        ]
        rows = [header]

        subtotal = Decimal("0")

        for i, d in enumerate(details, start=1):
            qty = self._to_decimal(d.cantidad)
            unit_price = self._to_decimal(d.precio_unitario)
            line_total = qty * unit_price
            subtotal += line_total

            if d.texto_abierto:
                producto = d.texto_abierto
            elif d.Producto:
                if self.language == "es":
                    producto = d.Producto.nombre_producto_esp or d.Producto.nombre_producto_ing or "-"
                else:
                    producto = d.Producto.nombre_producto_ing or d.Producto.nombre_producto_esp or "-"
            else:
                producto = "-"

            unidad = "M3"
            if d.UnidadVenta is not None:
                unidad = (
                    getattr(d.UnidadVenta, "abreviatura", None)
                    or getattr(d.UnidadVenta, "nombre", None)
                    or getattr(d.UnidadVenta, "codigo", None)
                    or "M3"
                )

            um_e = getattr(d.UnidadMedidaEspesor, "abreviatura", None) or getattr(d.UnidadMedidaEspesor, "nombre", None) or ""
            um_a = getattr(d.UnidadMedidaAncho, "abreviatura", None) or getattr(d.UnidadMedidaAncho, "nombre", None) or ""
            um_l = getattr(d.UnidadMedidaLargo, "abreviatura", None) or getattr(d.UnidadMedidaLargo, "nombre", None) or ""

            espesor = f"{d.espesor} {um_e}".strip() if d.espesor else "-"
            ancho = f"{d.ancho} {um_a}".strip() if d.ancho else "-"
            largo = f"{d.largo} {um_l}".strip() if d.largo else "-"

            rows.append(
                [
                    str(i),
                    Paragraph(str(producto), self.styles["SmallTable"]),
                    self._fmt_qty(qty),
                    str(unidad),
                    espesor,
                    ancho,
                    largo,
                    self._fmt_money_cl(unit_price),
                    self._fmt_money_cl(line_total),
                ]
            )

        moneda_code = (getattr(getattr(orden_compra, "Moneda", None), "etiqueta", None) or "").strip()
        label = f"<nobr>{moneda_code} SUBTOTAL</nobr>"

        rows.append([
            "", "", "", "", "", "",
            "",
            Paragraph(f"<b>{label}</b>", self.styles["SmallBold"]),
            Paragraph(f"<b>{self._fmt_money_cl(subtotal)}</b>", self.styles["SmallBold"]),
        ])

        col_widths = [
            0.30 * inch,
            2.10 * inch,
            0.70 * inch,
            0.50 * inch,
            0.60 * inch,
            0.60 * inch,
            0.70 * inch,
            1.30 * inch,
            0.95 * inch,
        ]

        t = Table(rows, colWidths=col_widths, repeatRows=1)
        last = len(rows) - 1

        t.setStyle(
            TableStyle(
                [
                    ("GRID", (0, 0), (-1, -1), 0.5, self.grid_grey),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 7.2),
                    ("FONTSIZE", (0, 1), (-1, -1), 7.0),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                    ("ALIGN", (0, 0), (0, -1), "CENTER"),
                    ("ALIGN", (1, 1), (1, last - 1), "LEFT"),
                    ("ALIGN", (2, 1), (6, last - 1), "CENTER"),
                    ("ALIGN", (7, 1), (8, -1), "RIGHT"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 2),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                    ("TOPPADDING", (0, 0), (-1, -1), 1),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
                    ("WORDWRAP", (7, last), (7, last), "OFF"),
                    ("BACKGROUND", (7, last), (8, last), self.subtotal_bg),
                    ("FONTNAME", (7, last), (8, last), "Helvetica-Bold"),
                    ("ALIGN", (7, last), (7, last), "RIGHT"),
                    ("ALIGN", (8, last), (8, last), "RIGHT"),
                    ("BOX", (7, last), (8, last), 0.8, self.grid_grey),
                    ("GRID", (0, last), (6, last), 0, colors.white),
                    ("LINEABOVE", (0, last), (6, last), 0, colors.white),
                    ("LINEBELOW", (0, last), (6, last), 0, colors.white),
                    ("LINEBEFORE", (0, last), (6, last), 0, colors.white),
                    ("LINEAFTER", (0, last), (6, last), 0, colors.white),
                ]
            )
        )
        return t

    # ------------------------------------------------------------------ #
    #  Quality obs section                                                 #
    # ------------------------------------------------------------------ #
    def _quality_obs_section(self, orden_compra: OrdenCompra, db: Session):
        details = (
            db.query(DetalleOrdenCompra)
            .filter(DetalleOrdenCompra.id_orden_compra == orden_compra.id_orden_compra)
            .all()
        )

        obs_parts = []
        seen_products = set()
        for d in details:
            if d.Producto and d.id_producto not in seen_products:
                obs = d.Producto.obs_calidad
                if obs and str(obs).strip():
                    prod_name = (
                        d.Producto.nombre_producto_esp
                        if self.language == "es"
                        else d.Producto.nombre_producto_ing
                    ) or d.Producto.nombre_producto_esp or "-"
                    obs_parts.append(f"<b>{prod_name}:</b> {obs.strip()}")
                    seen_products.add(d.id_producto)

        if not obs_parts:
            return None

        combined = "<br/>".join(obs_parts)
        return self._note_box(self.t("QUALITY_OBS"), combined)

    # ------------------------------------------------------------------ #
    #  Signature (single: usuario encargado)                              #
    # ------------------------------------------------------------------ #
    def _odc_signature(self, orden_compra: OrdenCompra):
        sign_gap = 0.75 * inch

        centered_small = ParagraphStyle(
            "CenteredSmallODC",
            parent=self.styles["Small"],
            alignment=TA_CENTER,
        )

        usuario_nombre = "-"
        usuario_telefono = "-"
        firma_img = None

        if getattr(orden_compra, "UsuarioEncargado", None):
            nombre_raw = getattr(orden_compra.UsuarioEncargado, "nombre", None) or "-"
            usuario_nombre = nombre_raw.title() if nombre_raw != "-" else "-"
            usuario_telefono = getattr(orden_compra.UsuarioEncargado, "telefono", None) or "-"
            url_firma = getattr(orden_compra.UsuarioEncargado, "url_firma", None)

            if url_firma:
                if url_firma.startswith("/static/"):
                    firma_path = os.path.join(
                        os.getcwd(), "app", url_firma.replace("/static/", "static/")
                    )
                else:
                    firma_path = url_firma

                if os.path.exists(firma_path):
                    try:
                        firma_img = RLImage(firma_path, width=2 * inch, height=0.7 * inch, kind="proportional")
                    except Exception:
                        pass

        if firma_img:
            rows = [
                [Spacer(1, 0.05 * inch)],
                [firma_img],
                [Paragraph("______________________________", centered_small)],
                [Paragraph(usuario_nombre, centered_small)],
                [Paragraph(usuario_telefono, centered_small)],
            ]
        else:
            rows = [
                [Spacer(1, sign_gap)],
                [Paragraph("______________________________", centered_small)],
                [Paragraph(usuario_nombre, centered_small)],
                [Paragraph(usuario_telefono, centered_small)],
            ]

        sign_tbl = Table(rows, colWidths=[3.4 * inch])
        sign_tbl.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )

        # Center the signature block on the page
        wrapper = Table([[sign_tbl]], colWidths=[6.9 * inch])
        wrapper.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ]
            )
        )
        return wrapper

    # ------------------------------------------------------------------ #
    #  Public API                                                          #
    # ------------------------------------------------------------------ #
    def generate_pdf(self, orden_compra: OrdenCompra, db: Session) -> BytesIO:  # type: ignore[override]
        buffer = BytesIO()

        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            topMargin=2.25 * inch,
            bottomMargin=0.45 * inch,
            leftMargin=0.55 * inch,
            rightMargin=0.55 * inch,
        )

        elements = []

        contactos_html, _ = self._get_odc_contactos(orden_compra, db)

        # ===== PAGE 1: client block + products =====
        elements.append(self._client_block(orden_compra, contactos_html))
        elements.append(Spacer(1, 0.32 * inch))
        elements.append(Paragraph(self.t("REQUEST_ITEMS"), self.styles["SmallBold"]))
        elements.append(Spacer(1, 0.06 * inch))
        elements.append(self._odc_products_table(orden_compra, db))

        # Quality observations
        qual_box = self._quality_obs_section(orden_compra, db)
        if qual_box:
            elements.append(Spacer(1, 0.12 * inch))
            elements.append(qual_box)

        # Other specifications on page 1 (uses remaining space)
        spec_parts = []
        observacion_txt = getattr(orden_compra, "observacion", None)
        otras_txt = getattr(orden_compra, "otras_especificaciones", None)
        if observacion_txt and str(observacion_txt).strip():
            spec_parts.append(str(observacion_txt).strip())
        if otras_txt and str(otras_txt).strip():
            spec_parts.append(str(otras_txt).strip())

        if spec_parts:
            other_specs_box = self._note_box(self.t("OTHER_SPECS"), "\n\n".join(spec_parts))
            if other_specs_box:
                elements.append(Spacer(1, 0.12 * inch))
                elements.append(other_specs_box)

        # ===== Notes: only break if less than 2 inches remain on current page =====
        elements.append(CondPageBreak(2 * inch))
        elements.append(Spacer(1, 0.4 * inch))

        nota_box = self._note_box(
            self.t("NOTE_ODC"), getattr(orden_compra, "nota_1", None)
        )
        if nota_box:
            elements.append(nota_box)
            elements.append(Spacer(1, 0.15 * inch))

        # ===== Image (optional): before signature, break only if needed =====
        if getattr(orden_compra, "url_imagen", None):
            img = self._image_page(orden_compra.url_imagen)
            if img:
                elements.append(CondPageBreak(3 * inch))
                elements.append(Spacer(1, 0.3 * inch))
                elements.append(img)

        # ===== Signature: keep together with a minimum space check =====
        elements.append(CondPageBreak(2 * inch))
        elements.append(Spacer(1, 0.5 * inch))
        elements.append(self._odc_signature(orden_compra))

        def on_page(canv, d):
            self._draw_odc_page_header(canv, d, orden_compra)

        doc.build(
            elements,
            onFirstPage=on_page,
            onLaterPages=on_page,
            canvasmaker=NumberedCanvas,
        )

        buffer.seek(0)
        return buffer
