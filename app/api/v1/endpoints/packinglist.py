from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session, joinedload

from app.db.session import get_db
from app.models.orden_compra import OrdenCompra
from app.models.packinglist import PackingList
from app.models.packinglist_detalle import PackingListDetalle
from app.models.packinglist_guia import PackingListGuia
from app.schemas.packinglist import (
    PackingListCreate,
    PackingListOut,
    PackingListUpdate,
)
from app.services.packinglist_excel import PackingListExcelGenerator

router = APIRouter(
    prefix="/orden-compra",
    tags=["Packing List"],
)


def _get_packing_list_by_ids(db: Session, id_orden_compra: int, id_packing_list: int) -> PackingList | None:
    return (
        db.query(PackingList)
        .options(joinedload(PackingList.guias).joinedload(PackingListGuia.detalles))
        .filter(
            PackingList.id_packing_list == id_packing_list,
            PackingList.orden_compra_id == id_orden_compra,
        )
        .first()
    )


def _attach_guias_and_detalles(db: Session, packing_list: PackingList, payload_guias) -> None:
    for idx, guia in enumerate(payload_guias):
        guia_obj = PackingListGuia(
            id_packing_list=packing_list.id_packing_list,
            guia_despacho=guia.guia_despacho,
            fecha_despacho=guia.fecha_despacho,
            orden=guia.orden if guia.orden is not None else idx,
        )
        db.add(guia_obj)
        db.flush()

        for detalle in guia.detalles:
            db.add(
                PackingListDetalle(
                    packing_list_id=packing_list.id_packing_list,
                    id_packing_list_guia=guia_obj.id_packing_list_guia,
                    oc=detalle.oc,
                    etiqueta=detalle.etiqueta,
                    numero_pqts=detalle.numero_pqts,
                    espesor=detalle.espesor,
                    ancho=detalle.ancho,
                    largo=detalle.largo,
                    piezas=detalle.piezas,
                    origen_detalle=detalle.origen_detalle,
                )
            )


@router.get("/{id_orden_compra}/packing-list", response_model=PackingListOut)
def obtener_packing_list(
    id_orden_compra: int,
    db: Session = Depends(get_db),
):
    packing_list = (
        db.query(PackingList)
        .options(joinedload(PackingList.guias).joinedload(PackingListGuia.detalles))
        .filter(PackingList.orden_compra_id == id_orden_compra)
        .first()
    )

    if not packing_list:
        raise HTTPException(
            status_code=404,
            detail="Esta orden de compra no tiene Packing List",
        )

    return packing_list


@router.post("/{id_orden_compra}/packing-list", response_model=PackingListOut)
def crear_packing_list(
    id_orden_compra: int,
    payload: PackingListCreate,
    db: Session = Depends(get_db),
):
    orden_compra = (
        db.query(OrdenCompra)
        .filter(OrdenCompra.id_orden_compra == id_orden_compra)
        .first()
    )

    if not orden_compra:
        raise HTTPException(status_code=404, detail="Orden de compra no encontrada")

    existente = (
        db.query(PackingList)
        .filter(PackingList.orden_compra_id == id_orden_compra)
        .first()
    )

    if existente:
        raise HTTPException(
            status_code=400,
            detail="Esta orden de compra ya tiene Packing List",
        )

    if not payload.guias:
        raise HTTPException(status_code=400, detail="Debe incluir al menos 1 guia")

    packing_list = PackingList(
        orden_compra_id=id_orden_compra,
        origen=payload.origen,
        producto=payload.producto,
        destino=payload.destino,
    )

    db.add(packing_list)
    db.flush()

    _attach_guias_and_detalles(db, packing_list, payload.guias)

    db.commit()
    db.refresh(packing_list)

    return _get_packing_list_by_ids(db, id_orden_compra, packing_list.id_packing_list)


@router.put(
    "/{id_orden_compra}/packing-list/{id_packing_list}",
    response_model=PackingListOut,
)
def actualizar_packing_list(
    id_orden_compra: int,
    id_packing_list: int,
    payload: PackingListUpdate,
    db: Session = Depends(get_db),
):
    packing_list = _get_packing_list_by_ids(db, id_orden_compra, id_packing_list)

    if not packing_list:
        raise HTTPException(
            status_code=404,
            detail="Packing List no encontrado",
        )

    if not payload.guias:
        raise HTTPException(status_code=400, detail="Debe incluir al menos 1 guia")

    packing_list.origen = payload.origen
    packing_list.producto = payload.producto
    packing_list.destino = payload.destino

    db.query(PackingListDetalle).filter(
        PackingListDetalle.packing_list_id == id_packing_list
    ).delete(synchronize_session=False)

    db.query(PackingListGuia).filter(
        PackingListGuia.id_packing_list == id_packing_list
    ).delete(synchronize_session=False)

    db.flush()

    _attach_guias_and_detalles(db, packing_list, payload.guias)

    db.commit()

    return _get_packing_list_by_ids(db, id_orden_compra, id_packing_list)


@router.delete(
    "/{id_orden_compra}/packing-list/{id_packing_list}/detalle/{id_packing_list_detalle}"
)
def eliminar_packing_list_detalle(
    id_orden_compra: int,
    id_packing_list: int,
    id_packing_list_detalle: int,
    db: Session = Depends(get_db),
):
    detalle = (
        db.query(PackingListDetalle)
        .join(
            PackingListGuia,
            PackingListDetalle.id_packing_list_guia == PackingListGuia.id_packing_list_guia,
        )
        .join(
            PackingList,
            PackingListGuia.id_packing_list == PackingList.id_packing_list,
        )
        .filter(
            PackingListDetalle.id_packing_list_detalle == id_packing_list_detalle,
            PackingList.id_packing_list == id_packing_list,
            PackingList.orden_compra_id == id_orden_compra,
        )
        .first()
    )

    if not detalle:
        raise HTTPException(
            status_code=404,
            detail="Detalle de Packing List no encontrado",
        )

    db.delete(detalle)
    db.commit()

    return {"message": "Detalle de Packing List eliminado correctamente"}


@router.get("/{id_orden_compra}/packing-list/{id_packing_list}/excel")
def exportar_packing_list_excel(
    id_orden_compra: int,
    id_packing_list: int,
    db: Session = Depends(get_db),
):
    packing_list = _get_packing_list_by_ids(db, id_orden_compra, id_packing_list)

    if not packing_list:
        raise HTTPException(
            status_code=404,
            detail="Packing List no encontrado",
        )

    try:
        generator = PackingListExcelGenerator()
        excel_buffer = generator.generate_excel(packing_list)
        filename = f"PackingList_{id_packing_list}.xlsx"

        return StreamingResponse(
            iter([excel_buffer.getvalue()]),
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generando Excel: {str(e)}")


@router.delete("/{id_orden_compra}/packing-list/{id_packing_list}")
def eliminar_packing_list(
    id_orden_compra: int,
    id_packing_list: int,
    db: Session = Depends(get_db),
):
    packing_list = (
        db.query(PackingList)
        .filter(
            PackingList.id_packing_list == id_packing_list,
            PackingList.orden_compra_id == id_orden_compra,
        )
        .first()
    )

    if not packing_list:
        raise HTTPException(
            status_code=404,
            detail="Packing List no encontrado",
        )

    db.delete(packing_list)
    db.commit()

    return {"message": "Packing List eliminado correctamente"}
