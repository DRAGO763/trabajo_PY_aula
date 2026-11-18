package simulador;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/** Valida los datos capturados (texto) contra el catalogo de parametros del tema. */
public class Validador {

    /** Un problema de validacion; clave es null si afecta a varios parametros a la vez. */
    public static class Error {
        public final String clave;
        public final String mensaje;

        public Error(String clave, String mensaje) {
            this.clave = clave;
            this.mensaje = mensaje;
        }

        @Override
        public String toString() {
            return mensaje;
        }
    }

    /** Resultado: valores ya convertidos (Double o Boolean) y la lista de errores. */
    public static class Resultado {
        public final Map<String, Object> valores = new LinkedHashMap<>();
        public final List<Error> errores = new ArrayList<>();

        public boolean esValido() {
            return errores.isEmpty();
        }
    }

    public static Resultado validar(Tema tema, Map<String, String> entradas) {
        Resultado r = new Resultado();
        for (Parametro p : tema.parametros) {
            String txt = entradas.get(p.clave);
            if (p.tipo == Parametro.Tipo.BOOLEANO) {
                r.valores.put(p.clave, "true".equalsIgnoreCase(txt));
                continue;
            }
            // Los datos inactivos (p. ej. Cd sin arrastre) no se exigen, se usa el valor por defecto.
            if (!aplica(tema, p, entradas) && (txt == null || txt.trim().isEmpty())) {
                r.valores.put(p.clave, p.defecto);
                continue;
            }
            Double v = convertir(p, txt, r);
            if (v != null) r.valores.put(p.clave, v);
        }
        if (r.esValido()) reglasCruzadas(tema, r);
        return r;
    }

    private static boolean aplica(Tema tema, Parametro p, Map<String, String> entradas) {
        if (tema.id.equals(Tema.TIRO) && (p.clave.equals("cd") || p.clave.equals("area"))) {
            return "true".equalsIgnoreCase(entradas.get("usar_arrastre"));
        }
        return true;
    }

    private static Double convertir(Parametro p, String txt, Resultado r) {
        String nombre = p.etiqueta;
        if (txt == null || txt.trim().isEmpty()) {
            r.errores.add(new Error(p.clave, nombre + ": es obligatorio."));
            return null;
        }
        double v;
        try {
            v = Double.parseDouble(txt.trim().replace(',', '.'));
        } catch (NumberFormatException ex) {
            r.errores.add(new Error(p.clave, nombre + ": '" + txt.trim() + "' no es un número válido."));
            return null;
        }
        if (Double.isNaN(v) || Double.isInfinite(v)) {
            r.errores.add(new Error(p.clave, nombre + ": debe ser un número finito."));
            return null;
        }
        if (p.tipo == Parametro.Tipo.ENTERO && v != Math.rint(v)) {
            r.errores.add(new Error(p.clave, nombre + ": debe ser un número entero."));
            return null;
        }
        if (v < p.min || v > p.max) {
            r.errores.add(new Error(p.clave, nombre + ": debe estar entre " + Tema.num(p.min)
                + " y " + Tema.num(p.max) + (p.unidad.isEmpty() ? "" : " " + p.unidad) + "."));
            return null;
        }
        return v;
    }

    private static void reglasCruzadas(Tema tema, Resultado r) {
        if (tema.id.equals(Tema.TIRO)) {
            double h0 = (Double) r.valores.get("h0");
            double ang = (Double) r.valores.get("angulo");
            if (h0 == 0 && ang == 0) {
                r.errores.add(new Error("angulo", "Con altura 0 y ángulo 0° el proyectil no se mueve: "
                    + "aumente el ángulo o la altura."));
            }
            if ((Boolean) r.valores.get("usar_arrastre")
                && ((Double) r.valores.get("cd") <= 0 || (Double) r.valores.get("area") <= 0)) {
                r.errores.add(new Error("cd", "Con resistencia del aire, Cd y el área deben ser mayores que 0."));
            }
        } else {
            double h0 = (Double) r.valores.get("h0");
            double v0 = (Double) r.valores.get("v0");
            if (h0 == 0 && v0 <= 0) {
                r.errores.add(new Error("h0", "Con altura 0 y sin velocidad hacia arriba no hay movimiento: "
                    + "suba la altura o dé una velocidad positiva."));
            }
        }
    }
}
