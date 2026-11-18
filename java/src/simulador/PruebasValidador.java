package simulador;

import java.util.LinkedHashMap;
import java.util.Map;

/** Pruebas simples del validador y del JSON (sin librerias externas). Ejecutar: java -cp out simulador.PruebasValidador */
public class PruebasValidador {
    private static int ok = 0, fallos = 0;

    private static Map<String, String> base(Tema t) {
        Map<String, String> m = new LinkedHashMap<>();
        for (Parametro p : t.parametros) m.put(p.clave, Tema.num(p.defecto));
        m.put("usar_arrastre", "false");
        return m;
    }

    private static void verificar(String nombre, boolean cond) {
        if (cond) ok++;
        else fallos++;
        System.out.println((cond ? "  [OK]    " : "  [FALLO] ") + nombre);
    }

    private static boolean invalido(Tema t, String clave, String valor) {
        Map<String, String> m = base(t);
        m.put(clave, valor);
        Validador.Resultado r = Validador.validar(t, m);
        return !r.esValido();
    }

    public static void main(String[] args) {
        Tema T = Tema.TIRO_PARABOLICO, C = Tema.CAIDA_ENERGIA;
        System.out.println("== Validador ==");
        verificar("valores por defecto de tiro son válidos", Validador.validar(T, base(T)).esValido());
        verificar("valores por defecto de caída son válidos", Validador.validar(C, base(C)).esValido());
        verificar("coma decimal 9,81 se acepta", !invalido(T, "g", "9,81"));
        verificar("texto no numérico se rechaza", invalido(T, "v0", "abc"));
        verificar("campo vacío se rechaza", invalido(T, "v0", ""));
        verificar("NaN se rechaza", invalido(T, "v0", "NaN"));
        verificar("Infinity se rechaza", invalido(T, "v0", "Infinity"));
        verificar("velocidad negativa en tiro se rechaza", invalido(T, "v0", "-5"));
        verificar("ángulo 91° se rechaza", invalido(T, "angulo", "91"));
        verificar("ángulo 90° se acepta", !invalido(T, "angulo", "90"));
        verificar("gravedad 0 se rechaza", invalido(T, "g", "0"));
        verificar("masa 0 se rechaza", invalido(T, "masa", "0"));
        verificar("altura 0 y ángulo 0 se rechaza (sin movimiento)", invalidoVarios(T, "h0", "0", "angulo", "0"));
        verificar("arrastre activo con Cd = 0 se rechaza", invalidoVarios(T, "usar_arrastre", "true", "cd", "0"));
        verificar("arrastre inactivo ignora Cd vacío", !invalidoVarios(T, "usar_arrastre", "false", "cd", ""));
        verificar("e = 1.5 se rechaza", invalido(C, "e", "1.5"));
        verificar("e = 1 se acepta", !invalido(C, "e", "1"));
        verificar("rebotes decimales (2.5) se rechazan", invalido(C, "rebotes", "2.5"));
        verificar("rebotes = 21 se rechaza", invalido(C, "rebotes", "21"));
        verificar("caída con h = 0 y v = 0 se rechaza", invalidoVarios(C, "h0", "0", "v0", "0"));
        verificar("caída con h = 0 y v = 10 se acepta", !invalidoVarios(C, "h0", "0", "v0", "10"));
        System.out.println("== JSON ==");
        Map<String, Object> vals = Validador.validar(T, base(T)).valores;
        String json = EjecutorPython.jsonEntrada(T, "Prueba \"citas\"", "Equipo A", vals);
        verificar("JSON contiene el tema", json.contains("\"tema\": \"tiro_parabolico\""));
        verificar("JSON escapa comillas", json.contains("Prueba \\\"citas\\\""));
        verificar("JSON escribe booleano sin comillas", json.contains("\"usar_arrastre\": false"));
        verificar("JSON escribe números con punto", json.contains("\"g\": 9.81"));
        verificar("leerCadena recupera ruta con barras", "C:\\x\\y.pdf".equals(
            JsonUtil.leerCadena("{\"pdf\": \"C:\\\\x\\\\y.pdf\"}", "pdf")));
        verificar("leerListaCadenas lee 2 elementos",
            JsonUtil.leerListaCadenas("{\"graficas\": [\"a.png\", \"b.png\"]}", "graficas").size() == 2);
        System.out.println("\nResultado: " + ok + " correctas, " + fallos + " fallidas.");
        System.exit(fallos == 0 ? 0 : 1);
    }

    private static boolean invalidoVarios(Tema t, String... kv) {
        Map<String, String> m = base(t);
        for (int i = 0; i < kv.length; i += 2) m.put(kv[i], kv[i + 1]);
        return !Validador.validar(t, m).esValido();
    }
}
