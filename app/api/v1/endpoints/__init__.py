from fastapi import APIRouter, Depends
from app.dependencies.permissions import require_module_access

from .agente import router as agente_router
from .auth import router as auth_router
from .bodega import router as bodega_router
from .ciudad import router as ciudad_router
from .clase import router as clase_router
from .clausula_venta import router as clausula_venta_router
from .cliente_proveedor import router as cliente_proveedor_router
from .contacto import router as contacto_router
from .contacto_orden_compra import router as contacto_orden_compra_router
from .contacto_proforma import router as contacto_proforma_router
from .contenedor import router as contenedor_router
from .detalle_factura import router as detalle_factura_router
from .detalle_gasto import router as detalle_gasto_router
from .detalle_ide import router as detalle_ide_router
from .detalle_orden_compra import router as detalle_orden_compra_router
from .detalle_pl import router as detalle_pl_router
from .detalle_proforma import router as detalle_proforma_router
from .direccion import router as direccion_router
from .documento_ide import router as documento_ide_router
from .empresa import router as empresa_router
from .especie import router as especie_router
from .estado_detalle_ple import router as estado_detalle_ple_router
from .estado_odc import router as estado_odc_router
from .estado_oe import router as estado_oe_router
from .estado_pl import router as estado_pl_router
from .estado_proforma import router as estado_proforma_router
from .factura import router as factura_router
from .forma_pago import router as forma_pago_router
from .gasto import router as gasto_router
from .ide import router as ide_router
from .moneda import router as moneda_router
from .naviera import router as naviera_router
from .operacion_exportacion import router as operacion_exportacion_router
from .orden_compra import router as orden_compra_router
from .pais import router as pais_router
from .parametro import router as parametro_router
from .plc import router as plc_router
from .ple import router as ple_router
from .producto import router as producto_router
from .proforma import router as proforma_router
from .puerto import router as puerto_router
from .seguridad import router as seguridad_router
from .tipo_comision import router as tipo_comision_router
from .tipo_envase import router as tipo_envase_router
from .unidad_medida import router as unidad_medida_router
from .unidad_venta import router as unidad_venta_router
from .usuario import router as usuario_router

router = APIRouter()

router.include_router(agente_router, dependencies=[Depends(require_module_access("agente"))])
router.include_router(auth_router)
router.include_router(bodega_router, dependencies=[Depends(require_module_access("bodega"))])
router.include_router(ciudad_router, dependencies=[Depends(require_module_access("ciudad"))])
router.include_router(clase_router, dependencies=[Depends(require_module_access("clase"))])
router.include_router(clausula_venta_router, dependencies=[Depends(require_module_access("clausula_venta"))])
router.include_router(cliente_proveedor_router, dependencies=[Depends(require_module_access("cliente_prov"))])
router.include_router(contacto_router, dependencies=[Depends(require_module_access("contacto"))])
router.include_router(contacto_orden_compra_router, dependencies=[Depends(require_module_access("contacto_odc"))])
router.include_router(contacto_proforma_router, dependencies=[Depends(require_module_access("contacto_prof"))])
router.include_router(contenedor_router, dependencies=[Depends(require_module_access("contenedor"))])
router.include_router(detalle_factura_router, dependencies=[Depends(require_module_access("detalle_factura"))])
router.include_router(detalle_gasto_router, dependencies=[Depends(require_module_access("detalle_gasto"))])
router.include_router(detalle_ide_router, dependencies=[Depends(require_module_access("detalle_ide"))])
router.include_router(detalle_orden_compra_router, dependencies=[Depends(require_module_access("orden_compra"))])
router.include_router(detalle_pl_router, dependencies=[Depends(require_module_access("detalle_pl"))])
router.include_router(detalle_proforma_router, dependencies=[Depends(require_module_access("proforma"))])
router.include_router(direccion_router, dependencies=[Depends(require_module_access("direccion"))])
router.include_router(documento_ide_router, dependencies=[Depends(require_module_access("documento_ide"))])
router.include_router(empresa_router, dependencies=[Depends(require_module_access("empresa"))])
router.include_router(especie_router, dependencies=[Depends(require_module_access("especie"))])
router.include_router(estado_detalle_ple_router, dependencies=[Depends(require_module_access("estado_det_ple"))])
router.include_router(estado_odc_router, dependencies=[Depends(require_module_access("estado_odc"))])
router.include_router(estado_oe_router, dependencies=[Depends(require_module_access("estado_oe"))])
router.include_router(estado_pl_router, dependencies=[Depends(require_module_access("estado_pl"))])
router.include_router(estado_proforma_router, dependencies=[Depends(require_module_access("estado_proforma"))])
router.include_router(factura_router, dependencies=[Depends(require_module_access("factura"))])
router.include_router(forma_pago_router, dependencies=[Depends(require_module_access("forma_pago"))])
router.include_router(gasto_router, dependencies=[Depends(require_module_access("gasto"))])
router.include_router(ide_router, dependencies=[Depends(require_module_access("ide"))])
router.include_router(moneda_router, dependencies=[Depends(require_module_access("moneda"))])
router.include_router(naviera_router, dependencies=[Depends(require_module_access("naviera"))])
router.include_router(operacion_exportacion_router, dependencies=[Depends(require_module_access("oper_export"))])
router.include_router(orden_compra_router, dependencies=[Depends(require_module_access("orden_compra"))])
router.include_router(pais_router, dependencies=[Depends(require_module_access("pais"))])
router.include_router(parametro_router, dependencies=[Depends(require_module_access("parametro"))])
router.include_router(plc_router, dependencies=[Depends(require_module_access("plc"))])
router.include_router(ple_router, dependencies=[Depends(require_module_access("ple"))])
router.include_router(producto_router, dependencies=[Depends(require_module_access("producto"))])
router.include_router(proforma_router, dependencies=[Depends(require_module_access("proforma"))])
router.include_router(puerto_router, dependencies=[Depends(require_module_access("puerto"))])
router.include_router(seguridad_router, dependencies=[Depends(require_module_access("seguridad"))])
router.include_router(tipo_comision_router, dependencies=[Depends(require_module_access("tipo_comision"))])
router.include_router(tipo_envase_router, dependencies=[Depends(require_module_access("tipo_envase"))])
router.include_router(unidad_medida_router, dependencies=[Depends(require_module_access("unidad_medida"))])
router.include_router(unidad_venta_router, dependencies=[Depends(require_module_access("unidad_venta"))])
router.include_router(usuario_router, dependencies=[Depends(require_module_access("usuario"))])