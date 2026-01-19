#!/usr/bin/env python3
"""
Test completo para crear una proforma con detalle_proforma y verificar
que los nuevos campos de especie y clase se incluyen correctamente.
"""

import json
from datetime import date
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.empresa import Empresa
from app.models.pais import Pais
from app.models.ciudad import Ciudad
from app.models.cliente_proveedor import ClienteProveedor
from app.models.direccion import Direccion
from app.models.especie import Especie
from app.models.clase import Clase
from app.models.producto import Producto
from app.models.unidad_venta import UnidadVenta
from app.models.proforma import Proforma
from app.models.detalle_proforma import DetalleProforma

def create_test_data(db: Session):
    """Crear todos los datos necesarios para el test"""
    
    # 1. Crear País
    pais = Pais(
        id_pais=999,
        nombre="CHILE TEST"
    )
    db.add(pais)
    db.flush()
    
    # 2. Crear Ciudad
    ciudad = Ciudad(
        id_ciudad=999,
        nombre="SANTIAGO TEST",
        id_pais=pais.id_pais
    )
    db.add(ciudad)
    db.flush()
    
    # 3. Crear Empresa
    empresa = Empresa(
        id_empresa=999,
        nombre_fantasia="EMPRESA TEST",
        razon_social="EMPRESA TEST LTDA",
        rut="12345678-9",
        direccion="DIRECCION TEST 123",
        giro="COMERCIO",
        id_ciudad=ciudad.id_ciudad
    )
    db.add(empresa)
    db.flush()
    
    # 4. Crear Cliente/Proveedor
    cliente = ClienteProveedor(
        id_cliente_proveedor=999,
        nombre_fantasia="CLIENTE TEST",
        razon_social="CLIENTE TEST LTDA",
        rut="87654321-0",
        es_nacional=True,
        es_cliente=True,
        es_proveedor=False
    )
    db.add(cliente)
    db.flush()
    
    # 5. Crear Direcciones
    direccion = Direccion(
        id_direccion=999,
        direccion="DIRECCION TEST 456",
        id_ciudad=ciudad.id_ciudad,
        id_cliente_proveedor=cliente.id_cliente_proveedor,
        por_defecto=True,
        fono_1="+56912345678"
    )
    db.add(direccion)
    db.flush()
    
    # 6. Crear Especie
    especie = Especie(
        id_especie=999,
        nombre_esp="PINO TEST",
        nombre_ing="PINE TEST",
        descripcion="Especie de prueba"
    )
    db.add(especie)
    db.flush()
    
    # 7. Crear Clase
    clase = Clase(
        id_clase=999,
        nombre="MADERA TEST",
        descripcion="Clase de prueba"
    )
    db.add(clase)
    db.flush()
    
    # 8. Crear Producto
    producto = Producto(
        id_producto=999,
        nombre_producto_esp="PRODUCTO TEST",
        nombre_producto_ing="TEST PRODUCT",
        obs_calidad="Calidad premium",
        id_especie=especie.id_especie,
        id_clase=clase.id_clase
    )
    db.add(producto)
    db.flush()
    
    # 9. Crear Unidad de Venta
    unidad_venta = UnidadVenta(
        id_unidad_venta=999,
        nombre="M3 TEST",
        cubicacion="Metro cúbico",
        descripcion="Unidad de prueba",
        por_defecto=False
    )
    db.add(unidad_venta)
    db.flush()
    
    db.commit()
    
    return {
        'empresa': empresa,
        'direccion': direccion,
        'producto': producto,
        'unidad_venta': unidad_venta,
        'especie': especie,
        'clase': clase
    }

def cleanup_test_data(db: Session):
    """Limpiar datos de prueba"""
    try:
        # Eliminar en orden inverso para evitar problemas de FK
        db.query(DetalleProforma).filter(DetalleProforma.id_producto == 999).delete()
        db.query(Proforma).filter(Proforma.id_empresa == 999).delete()
        db.query(UnidadVenta).filter(UnidadVenta.id_unidad_venta == 999).delete()
        db.query(Producto).filter(Producto.id_producto == 999).delete()
        db.query(Clase).filter(Clase.id_clase == 999).delete()
        db.query(Especie).filter(Especie.id_especie == 999).delete()
        db.query(Direccion).filter(Direccion.id_direccion == 999).delete()
        db.query(ClienteProveedor).filter(ClienteProveedor.id_cliente_proveedor == 999).delete()
        db.query(Empresa).filter(Empresa.id_empresa == 999).delete()
        db.query(Ciudad).filter(Ciudad.id_ciudad == 999).delete()
        db.query(Pais).filter(Pais.id_pais == 999).delete()
        db.commit()
        print("✓ Test data cleaned up")
    except Exception as e:
        print(f"Warning: Error cleaning up test data: {e}")
        db.rollback()

def test_proforma_with_detalle():
    """Test principal que crea proforma con detalle y verifica los nuevos campos"""
    
    # Obtener sesión de base de datos
    db = next(get_db())
    
    try:
        print("🔧 Creating test data...")
        cleanup_test_data(db)
        test_data = create_test_data(db)
        
        print("📝 Creating proforma...")
        # Crear proforma directamente en la base de datos
        proforma = Proforma(
            fecha_emision=date.today(),
            id_empresa=test_data['empresa'].id_empresa,
            id_direccion_facturar=test_data['direccion'].id_direccion,
            id_direccion_consignar=test_data['direccion'].id_direccion,
            id_direccion_notificar=test_data['direccion'].id_direccion,
            especificaciones="Proforma de prueba"
        )
        db.add(proforma)
        db.commit()
        db.refresh(proforma)
        
        print(f"✓ Proforma created with ID: {proforma.id_proforma}")
        
        print("📋 Creating detalle_proforma...")
        # Crear detalle de proforma
        detalle = DetalleProforma(
            id_proforma=proforma.id_proforma,
            id_producto=test_data['producto'].id_producto,
            id_unidad_venta=test_data['unidad_venta'].id_unidad_venta,
            texto_libre="Detalle de prueba",
            cantidad="100",
            precio_unitario="50.00",
            subtotal="5000.00",
            volumen_eq="10.000",
            precio_eq="50.00"
        )
        db.add(detalle)
        db.commit()
        db.refresh(detalle)
        
        print(f"✓ DetalleProforma created with ID: {detalle.id_detalle_proforma}")
        
        print("🔍 Testing direct function call...")
        # Test directo con la función _build_detalle_response
        from app.api.v1.endpoints.detalle_proforma import _build_detalle_response
        from sqlalchemy.orm import joinedload
        
        # Cargar detalle con eager loading
        from app.models.producto import Producto
        detalle_loaded = (db.query(DetalleProforma)
                        .options(
                            joinedload(DetalleProforma.Producto)
                            .joinedload(Producto.especie)
                        )
                        .options(
                            joinedload(DetalleProforma.Producto)
                            .joinedload(Producto.clase)
                        )
                        .filter(DetalleProforma.id_detalle_proforma == detalle.id_detalle_proforma)
                        .first())
        
        if detalle_loaded:
            response_data = _build_detalle_response(detalle_loaded)
            
            print("✓ Direct function call successful")
            print("\n📊 Checking new fields in response:")
            
            required_fields = [
                'id_especie', 'nombre_especie_esp', 'nombre_especie_ing',
                'id_clase', 'nombre_clase'
            ]
            
            all_fields_present = True
            for field in required_fields:
                if field in response_data:
                    value = response_data[field]
                    print(f"  ✓ {field}: {value}")
                else:
                    print(f"  ✗ {field}: MISSING")
                    all_fields_present = False
            
            # Verificar valores específicos
            print("\n🎯 Validating field values:")
            values_correct = True
            
            if response_data.get('id_especie') == test_data['especie'].id_especie:
                print(f"  ✓ id_especie matches: {response_data['id_especie']}")
            else:
                print(f"  ✗ id_especie mismatch: expected {test_data['especie'].id_especie}, got {response_data.get('id_especie')}")
                values_correct = False
            
            if response_data.get('nombre_especie_esp') == test_data['especie'].nombre_esp:
                print(f"  ✓ nombre_especie_esp matches: {response_data['nombre_especie_esp']}")
            else:
                print(f"  ✗ nombre_especie_esp mismatch: expected {test_data['especie'].nombre_esp}, got {response_data.get('nombre_especie_esp')}")
                values_correct = False
            
            if response_data.get('id_clase') == test_data['clase'].id_clase:
                print(f"  ✓ id_clase matches: {response_data['id_clase']}")
            else:
                print(f"  ✗ id_clase mismatch: expected {test_data['clase'].id_clase}, got {response_data.get('id_clase')}")
                values_correct = False
            
            if response_data.get('nombre_clase') == test_data['clase'].nombre:
                print(f"  ✓ nombre_clase matches: {response_data['nombre_clase']}")
            else:
                print(f"  ✗ nombre_clase mismatch: expected {test_data['clase'].nombre}, got {response_data.get('nombre_clase')}")
                values_correct = False
            
            # Verificar compatibilidad hacia atrás
            print("\n🔄 Checking backward compatibility:")
            legacy_fields = ['id_detalle_proforma', 'id_proforma', 'id_producto', 'cantidad', 'precio_unitario', 'producto']
            backward_compatible = True
            for field in legacy_fields:
                if field in response_data:
                    print(f"  ✓ {field}: present")
                else:
                    print(f"  ✗ {field}: MISSING")
                    backward_compatible = False
            
            print(f"\n📄 Full response:")
            print(json.dumps(response_data, indent=2, ensure_ascii=False))
            
            # Determinar si el test fue exitoso
            if all_fields_present and values_correct and backward_compatible:
                print("\n🎉 All tests passed!")
                return True
            else:
                print("\n❌ Some tests failed!")
                return False
            
        else:
            print("✗ Could not load detalle from database")
            return False
        
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False
        
    finally:
        print("\n🧹 Cleaning up test data...")
        cleanup_test_data(db)
        db.close()

if __name__ == "__main__":
    print("🚀 Starting complete proforma + detalle test...")
    print("=" * 60)
    
    success = test_proforma_with_detalle()
    
    print("=" * 60)
    if success:
        print("✅ Test completed successfully!")
    else:
        print("❌ Test failed!")
        exit(1)