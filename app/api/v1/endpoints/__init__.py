from fastapi import APIRouter

from .auth import router as auth_router
from .agente import router as agente_router
from .pais import router as pais_router
from .especie import router as especie_router
from .estado_detalle_ple import router as estado_detalle_ple_router
from .direccion import router as direccion_router
from .parametro import router as parametro_router
from .factura import router as factura_router
from .cliente_proveedor import router as cliente_proveedor_router
from .detalle_factura import router as detalle_factura_router
from .detalle_gasto import router as detalle_gasto_router
from .detalle_ide import router as detalle_ide_router
from .detalle_orden_compra import router as detalle_orden_compra_router
from .detalle_pl import router as detalle_pl_router
from .contacto import router as contacto_router
from .contacto_proforma import router as contacto_proforma_router
from .contacto_orden_compra import router as contacto_orden_compra_router
from .contenedor import router as contenedor_router
from .estado_proforma import router as estado_proforma_router
from .documento_ide import router as documento_ide_router
from .clase import router as clase_router
from .clausula_venta import router as clausula_venta_router
from .empresa import router as empresa_router
from .ide import router as ide_router
from .ciudad import router as ciudad_router
from .operacion_exportacion import router as operacion_exportacion_router
from .puerto import router as puerto_router
from .ple import router as ple_router
from .gasto import router as gasto_router
from .proforma import router as proforma_router
from .estado_pl import router as estado_pl_router
from .tipo_envase import router as tipo_envase_router
from .plc import router as plc_router
from .producto import router as producto_router
from .moneda import router as moneda_router
from .detalle_proforma import router as detalle_proforma_router
from .unidad_venta import router as unidad_venta_router
from .estado_odc import router as estado_odc_router
from .estado_oe import router as estado_oe_router
from .usuario import router as usuario_router
from .seguridad import router as seguridad_router
from .forma_pago import router as forma_pago_router
from .unidad_medida import router as unidad_medida_router
from .bodega import router as bodega_router
from .naviera import router as naviera_router
from .tipo_comision import router as tipo_comision_router
from .orden_compra import router as orden_compra_router

router = APIRouter()

router.include_router(auth_router)
router.include_router(agente_router)
router.include_router(pais_router)
router.include_router(especie_router)
router.include_router(estado_detalle_ple_router)
router.include_router(direccion_router)
router.include_router(parametro_router)
router.include_router(factura_router)
router.include_router(cliente_proveedor_router)
router.include_router(detalle_factura_router)
router.include_router(detalle_gasto_router)
router.include_router(detalle_ide_router)
router.include_router(detalle_orden_compra_router)
router.include_router(detalle_pl_router)
router.include_router(contacto_router)
router.include_router(contacto_proforma_router)
router.include_router(contacto_orden_compra_router)
router.include_router(contenedor_router)
router.include_router(estado_proforma_router)
router.include_router(documento_ide_router)
router.include_router(clase_router)
router.include_router(clausula_venta_router)
router.include_router(empresa_router)
router.include_router(ide_router)
router.include_router(ciudad_router)
router.include_router(operacion_exportacion_router)
router.include_router(puerto_router)
router.include_router(ple_router)
router.include_router(gasto_router)
router.include_router(proforma_router)
router.include_router(estado_pl_router)
router.include_router(tipo_envase_router)
router.include_router(plc_router)
router.include_router(producto_router)
router.include_router(moneda_router)
router.include_router(detalle_proforma_router)
router.include_router(unidad_venta_router)
router.include_router(estado_odc_router)
router.include_router(estado_oe_router)
router.include_router(usuario_router)
router.include_router(seguridad_router)
router.include_router(forma_pago_router)
router.include_router(unidad_medida_router)
router.include_router(bodega_router)
router.include_router(naviera_router)
router.include_router(tipo_comision_router)
router.include_router(orden_compra_router)

