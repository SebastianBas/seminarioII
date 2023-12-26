// productos.js
document.addEventListener("DOMContentLoaded", function () {
    // Función para cargar productos en el contenedor
    function cargarProductos() {
        fetch("/miaplicacion/api/productos")  // Ajusta la URL según la estructura de tus rutas
            .then(response => response.json())
            .then(data => {
                const productosContainer = document.getElementById("productos-container");
                productosContainer.innerHTML = ""; // Limpiar el contenedor

                data.productos.forEach(producto => {
                    const card = `
                        <div class="col-sm-4 mb-4">
                            <div class="card" style="background-color: black; color: white;">
                                <img class="card-img-top" src="${producto.imagen}" style="width: 100%; height: 400px; object-fit: contain;" onmouseover="this.style.opacity=0.5;" onmouseout="this.style.opacity=1;">
                                <div class="card-body text-center">
                                    <h5 class="card-title" style="color: yellow;">${producto.nombre}</h5>
                                    <p class="card-text">Colores Disponibles: ${producto.colores.join(', ')} <br> Tallas: ${producto.tallas.join(', ')} <br> Precio: ${producto.precio}</p>
                                    <button class="btn btn-primary rounded-pill" onclick="editarProducto(${producto.id})" style="font-weight: bold; color: black; background-color: yellow; border-color: yellow;">Editar</button>
                                    <button class="btn btn-danger rounded-pill" onclick="eliminarProducto(${producto.id})" style="font-weight: bold; color: black; background-color: red; border-color: red;">Eliminar</button>
                                </div>
                            </div>
                        </div>
                    `;
                    productosContainer.innerHTML += card;
                });
            })
            .catch(error => console.error("Error al cargar productos:", error));
    }

    // Función para eliminar un producto
    window.eliminarProducto = function (productoId) {
        if (confirm("¿Estás seguro de eliminar este producto?")) {
            fetch(`/miaplicacion/api/productos/${productoId}`, {  // Ajusta la URL según la estructura de tus rutas
                method: "DELETE",
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    cargarProductos(); // Actualizar la lista de productos después de eliminar
                } else {
                    alert("Error al eliminar el producto.");
                }
            })
            .catch(error => console.error("Error al eliminar producto:", error));
        }
    };

    // Función para editar un producto (redirigir a la página de edición)
    window.editarProducto = function (productoId) {
        window.location.href = `/miaplicacion/admin/productos/editar/${productoId}`;  // Ajusta la URL según la estructura de tus rutas
    };

    // Cargar productos al cargar la página
    cargarProductos();

    // Función para agregar un nuevo producto
    window.agregarProducto = function () {
        const nombre = document.getElementById("nombre").value;
        const colores = document.getElementById("colores").value.split(', ');
        const tallas = document.getElementById("tallas").value.split(', ');
        const precio = document.getElementById("precio").value;

        fetch("/miaplicacion/api/productos", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                nombre: nombre,
                colores: colores,
                tallas: tallas,
                precio: precio
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                cargarProductos(); // Actualizar la lista de productos después de agregar
                // Limpiar el formulario después de agregar
                document.getElementById("formulario-producto").reset();
            } else {
                alert("Error al agregar el producto.");
            }
        })
        .catch(error => console.error("Error al agregar producto:", error));
    };
});

