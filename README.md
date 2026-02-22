**Al hacer cambios en el código, recuerda reconstruir la imagen de Docker para que los cambios se reflejen en el contenedor:**

```shell
docker-compose up -d --build
```

**Para probar el moltbot dockerizado, puedes usar el siguiente comando:**

```shell
docker logs -f moltbot_app
```