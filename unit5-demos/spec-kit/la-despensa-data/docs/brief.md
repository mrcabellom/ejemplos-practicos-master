# Brief: ventas diarias por tienda

*De: Lucía Herrero (responsable de Operaciones de La Despensa) · Para: equipo de datos · 5 de octubre de 2026*

Hola. Cada mañana, alguien de mi equipo abre el fichero de pedidos del día anterior en una hoja de
cálculo y suma manualmente las ventas de cada tienda. Tarda media hora y casi nunca coinciden las cifras
de dos personas distintas.

Queremos una **tabla con las ventas de cada tienda por día** que podamos consultar a primera hora para
comparar las dos tiendas. Para cada tienda y día necesitamos:

1. El número de pedidos.
2. Las unidades vendidas.
3. El importe bruto (precio por cantidad, tal como viene en el fichero).

Lo que sabemos del fichero:

- Lo exporta cada noche el sistema de caja a `data/raw/orders.csv`, con una línea por producto de cada pedido.
- Las líneas con cantidad cero o negativa no son ventas.

Ahora mismo **no** necesitamos: importes sin IVA, previsiones, un cuadro de mando ni cargar más de un
fichero a la vez.

Gracias,
Lucía
