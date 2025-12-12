# Guía: Consumir endpoints de parte1_ms desde otro microservicio

## URLs internas en OpenShift

Si tienes otro microservicio (`parte3_ms`) que quiere consumir los endpoints de `parte1_ms`, usa estas URLs:

### Desde dentro del mismo namespace:
```
http://parte1-ms-service:8000/health
http://parte1-ms-service:8000/get
http://parte1-ms-service:8000/post
```

### Desde otro namespace:
```
http://parte1-ms-service.nombre-namespace.svc.cluster.local:8000/health
```

## Verificar conectividad desde otro pod

Si tienes problemas de conectividad, ejecuta esto desde el pod de `parte3_ms`:

```bash
# Ver si puede resolver el nombre del servicio
nslookup parte1-ms-service

# Probar conectividad HTTP
curl http://parte1-ms-service:8000/health
```

## Ejemplo de código Python para consumir los endpoints

```python
import requests

# URL base del servicio parte1_ms
BASE_URL = "http://parte1-ms-service:8000"

# GET - obtener todos los empleados
response = requests.get(f"{BASE_URL}/get")
empleados = response.json()
print(empleados)

# POST - crear un empleado
data = {
    "nombres": "Juan Pérez",
    "telefono": "1234567890"
}
response = requests.post(f"{BASE_URL}/post", json=data)
nuevo_empleado = response.json()
print(nuevo_empleado)

# Health check
response = requests.get(f"{BASE_URL}/health")
print(response.json())
```

## Variables de entorno útiles

Si quieres que `parte3_ms` obtenga la URL del servicio dinámicamente, puedes pasar como variable de entorno:

```yaml
env:
  - name: PARTE1_MS_URL
    value: "http://parte1-ms-service:8000"
```

Luego usarla en el código:
```python
import os
PARTE1_MS_URL = os.getenv("PARTE1_MS_URL", "http://parte1-ms-service:8000")
```

## Verificar que parte1_ms está funcionando

Ejecuta estos comandos en OpenShift:

```bash
# Ver logs del servicio
oc logs -l app=parte1-ms --tail=50

# Probar endpoint desde dentro del cluster
oc exec -it <pod-name> -- curl http://parte1-ms-service:8000/health

# Ver detalles del servicio
oc describe svc parte1-ms-service
```
