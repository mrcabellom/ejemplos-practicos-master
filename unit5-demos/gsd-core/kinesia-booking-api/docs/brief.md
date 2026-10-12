# Brief: agenda online de Kinesia

*De: Marta Gil (gerente de Kinesia) · Para: equipo de desarrollo · 2 de octubre de 2026*

Hola. Ahora mismo llevamos las citas en una hoja de cálculo compartida y cada semana pasa algo:
dos pacientes a la misma hora con Ana, alguien que reserva para "mañana a las 9" a las 8:55, o una
cita metida el 12 de octubre con la clínica cerrada.

Queremos una **API sencilla para recepción** (más adelante haremos la web para pacientes) que permita:

1. Ver los huecos libres de cada fisioterapeuta para un día.
2. Reservar una cita para un paciente (nombre y teléfono).

Cómo trabajamos:

- Somos dos fisios: **Ana** (`ANA`) y **Luis** (`LUIS`).
- Las sesiones duran **45 minutos**.
- Abrimos **de lunes a viernes, de 9 a 14 y de 16 a 20**. Fines de semana y festivos nacionales, cerrado.
- Las citas tienen que pedirse **con al menos 2 horas de antelación**.
- Una sola clínica, en Madrid.

Ahora mismo **no** necesitamos: cancelaciones (las seguimos gestionando por teléfono), recordatorios
por SMS, pagos online ni que los pacientes reserven solos.

Gracias,
Marta
