import os
import time

import httpx
import pytest


BASE_URL = os.getenv("TEST_API_BASE_URL", "http://localhost:8000/api/v1")
TEST_OC_ID = os.getenv("TEST_OC_ID")


@pytest.mark.skipif(not TEST_OC_ID, reason="Define TEST_OC_ID para ejecutar la prueba de integración")
def test_packinglist_multi_guia_flow():
    oc_id = int(TEST_OC_ID)
    now = int(time.time())

    create_payload = {
        "origen": "Bodega Central",
        "producto": "Madera Aserrada",
        "destino": "Puerto San Antonio",
        "guias": [
            {
                "guia_despacho": f"GD-{now}-01",
                "fecha_despacho": "2026-06-11",
                "orden": 0,
                "detalles": [
                    {
                        "oc": "OC-001",
                        "etiqueta": "A-1",
                        "numero_pqts": 10,
                        "espesor": 25.5,
                        "ancho": 120.0,
                        "largo": 2400.0,
                        "piezas": 40,
                        "origen_detalle": "Patio 1",
                    }
                ],
            },
            {
                "guia_despacho": f"GD-{now}-02",
                "fecha_despacho": "2026-06-12",
                "orden": 1,
                "detalles": [
                    {
                        "oc": "OC-001",
                        "etiqueta": "B-1",
                        "numero_pqts": 12,
                        "espesor": 30.0,
                        "ancho": 100.0,
                        "largo": 2200.0,
                        "piezas": 35,
                        "origen_detalle": "Patio 2",
                    }
                ],
            },
        ],
    }

    with httpx.Client(timeout=30.0) as client:
        create_resp = client.post(
            f"{BASE_URL}/orden-compra/{oc_id}/packing-list",
            json=create_payload,
        )
        assert create_resp.status_code in (200, 201), create_resp.text

        created = create_resp.json()
        assert created["orden_compra_id"] == oc_id
        assert len(created["guias"]) == 2

        packing_id = created["id_packing_list"]

        get_resp = client.get(f"{BASE_URL}/orden-compra/{oc_id}/packing-list")
        assert get_resp.status_code == 200, get_resp.text
        fetched = get_resp.json()
        assert fetched["id_packing_list"] == packing_id
        assert len(fetched["guias"]) == 2

        update_payload = {
            "origen": "Bodega Norte",
            "producto": "Madera Cepillada",
            "destino": "Puerto Coronel",
            "guias": [
                {
                    "guia_despacho": f"GD-{now}-03",
                    "fecha_despacho": "2026-06-13",
                    "orden": 0,
                    "detalles": [
                        {
                            "oc": "OC-001",
                            "etiqueta": "C-1",
                            "numero_pqts": 20,
                            "espesor": 20.0,
                            "ancho": 90.0,
                            "largo": 2100.0,
                            "piezas": 60,
                            "origen_detalle": "Patio 3",
                        }
                    ],
                }
            ],
        }

        update_resp = client.put(
            f"{BASE_URL}/orden-compra/{oc_id}/packing-list/{packing_id}",
            json=update_payload,
        )
        assert update_resp.status_code == 200, update_resp.text
        updated = update_resp.json()
        assert updated["origen"] == "Bodega Norte"
        assert len(updated["guias"]) == 1
        assert updated["guias"][0]["guia_despacho"] == f"GD-{now}-03"

        excel_resp = client.get(
            f"{BASE_URL}/orden-compra/{oc_id}/packing-list/{packing_id}/excel"
        )
        assert excel_resp.status_code == 200, excel_resp.text
        assert (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            in excel_resp.headers.get("content-type", "")
        )
        assert len(excel_resp.content) > 0

        delete_resp = client.delete(
            f"{BASE_URL}/orden-compra/{oc_id}/packing-list/{packing_id}"
        )
        assert delete_resp.status_code == 200, delete_resp.text

        after_delete = client.get(f"{BASE_URL}/orden-compra/{oc_id}/packing-list")
        assert after_delete.status_code == 404
