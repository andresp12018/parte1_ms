# Configuración de Secretos en GitHub Actions

Este documento explica cómo configurar los secretos necesarios para el workflow de CI/CD.

## Secretos requeridos

El workflow necesita los siguientes secretos configurados en el repositorio:

### Para DockerHub (build-and-push job)
- **DOCKER_USER**: Tu usuario de DockerHub
- **DOCKER_PASSWORD**: Tu contraseña o token de acceso de DockerHub

### Para OpenShift (deploy-openshift job)
- **OPENSHIFT_SERVER**: URL del servidor OpenShift (ej: https://api.openshift.ejemplo.com:6443)
- **OPENSHIFT_TOKEN**: Token de autenticación de OpenShift
- **OPENSHIFT_NAMESPACE**: Nombre del namespace/proyecto en OpenShift (ej: default, production, etc)

## Pasos para configurar los secretos

1. Ve a tu repositorio en GitHub
2. Haz clic en **Settings** (Configuración)
3. En el menú izquierdo, ve a **Secrets and variables** → **Actions**
4. Haz clic en **New repository secret** para cada secreto
5. Ingresa el nombre del secreto (exactamente como se muestra arriba) y su valor
6. Haz clic en **Add secret**

## Obtener las credenciales

### DockerHub
1. Ve a https://hub.docker.com/
2. Inicia sesión con tu cuenta
3. Ve a **Account Settings** → **Security**
4. En la sección **Access Tokens**, crea un nuevo token
5. Usa tu usuario como DOCKER_USER y el token como DOCKER_PASSWORD

### OpenShift
1. Accede a tu consola de OpenShift (ej: https://console-openshift-console.apps.ejemplo.com)
2. En la esquina superior derecha, haz clic en tu usuario → **Copy login command**
3. En la terminal, ejecuta el comando copiado (te autenticas)
4. Luego ejecuta:
   ```bash
   oc whoami --show-token
   ```
5. Ese es tu OPENSHIFT_TOKEN
6. Obtén la URL del servidor con:
   ```bash
   oc config view --minify -o jsonpath='{.clusters[*].cluster.server}'
   ```
7. Tu OPENSHIFT_NAMESPACE es el proyecto donde quieres desplegar

## Cómo funciona el workflow

1. **Trigger**: Se activa cuando haces un push a `main` o creas un PR
2. **Build & Push**: 
   - Construye la imagen Docker
   - La sube a DockerHub con tags basados en la rama y el SHA del commit
   - Solo en push a main usa el tag `latest`
3. **Deploy OpenShift** (solo en push a main):
   - Se autentica en OpenShift
   - Reemplaza la imagen en k8s.yaml con la nueva imagen de DockerHub
   - Aplica el manifiesto
   - Espera a que los pods estén listos
   - Muestra los logs para verificación

## Resultado esperado

Después de un push a main:
- La imagen aparecerá en DockerHub: `docker.io/TU_USUARIO/parte1-ms:latest`
- El microservicio se desplegará automáticamente en OpenShift
- El workflow mostrará logs y estado de los pods

## Troubleshooting

Si el workflow falla:
1. Verifica que los secretos estén correctamente configurados
2. Revisa los logs del workflow en GitHub Actions
3. Asegúrate de que el namespace en OpenShift existe
4. Verifica que el token de OpenShift tiene permisos suficientes
5. Comprueba que DockerHub tiene espacio para la imagen
