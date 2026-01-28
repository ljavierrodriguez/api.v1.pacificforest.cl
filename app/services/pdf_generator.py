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
    Image as RLImage,
    Flowable,
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.utils import ImageReader

from sqlalchemy.orm import Session

from app.models.proforma import Proforma
from app.models.detalle_proforma import DetalleProforma
from app.models.contacto_proforma import ContactoProforma


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
    def _get_cliente_y_contactos(self, proforma: Proforma, db: Session):
        cliente_name = (
            proforma.empresa_razon_social
            or proforma.empresa_nombre_fantasia
            or "-"
        )
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

            if c.ClienteProveedor is not None:
                cliente_name = (
                    c.ClienteProveedor.razon_social
                    or c.ClienteProveedor.nombre_fantasia
                    or cliente_name
                )

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
        return cliente_name, contactos_html, contacto_phone

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

            if self.language == "es":
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

        cliente_name, contactos_html, contacto_phone = self._get_cliente_y_contactos(proforma, db)

        facturar_country_city = f"{proforma.direccion_facturar_pais or '-'} / {proforma.direccion_facturar_ciudad or '-'}"
        consignar_country_city = f"{proforma.direccion_consignar_pais or '-'} / {proforma.direccion_consignar_ciudad or '-'}"
        notificar_country_city = f"{proforma.direccion_notificar_pais or '-'} / {proforma.direccion_notificar_ciudad or '-'}"

        fono_fact = proforma.direccion_facturar_fono_1 or contacto_phone or "-"
        fono_cons = proforma.direccion_consignar_fono_1 or contacto_phone or "-"
        fono_not = proforma.direccion_notificar_fono_1 or contacto_phone or "-"

        # ===== PAGE 1 =====
        elements.append(
            self._address_block(
                self.t("BILL_TO"),
                cliente_name,
                proforma.direccion_facturar_texto,
                fono_fact,
                facturar_country_city,
                contactos_html=contactos_html,
            )
        )
        elements.append(Spacer(1, 0.03 * inch))
        elements.append(
            self._address_block(
                self.t("SHIP_TO"),
                cliente_name,
                proforma.direccion_consignar_texto,
                fono_cons,
                consignar_country_city,
                contactos_html=None,
            )
        )
        elements.append(Spacer(1, 0.03 * inch))
        elements.append(
            self._address_block(
                self.t("NOTIFY"),
                cliente_name,
                proforma.direccion_notificar_texto,
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
