package simulador;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Locale;

/** Catalogo de los dos temas de Fisica del simulador y sus parametros. */
public class Tema {
    public static final String TIRO = "tiro_parabolico";
    public static final String CAIDA = "caida_energia";

    public final String id;
    public final String nombre;
    public final String descripcion;
    public final List<Parametro> parametros;

    private Tema(String id, String nombre, String descripcion, List<Parametro> parametros) {
        this.id = id;
        this.nombre = nombre;
        this.descripcion = descripcion;
        this.parametros = parametros;
    }

    public static final Tema TIRO_PARABOLICO = new Tema(TIRO, "Tiro parabólico",
        "Lanzamiento de un proyectil con ángulo, rapidez, altura y gravedad; opcionalmente "
        + "con resistencia del aire. Analiza alcance, altura máxima y energías.",
        Arrays.asList(
            Parametro.numero("v0", "Rapidez inicial", "m/s", 0.1, 300, 25, "Rapidez con que sale el proyectil"),
            Parametro.numero("angulo", "Ángulo de lanzamiento", "°", 0, 90, 45, "Medido desde la horizontal"),
            Parametro.numero("h0", "Altura inicial", "m", 0, 2000, 0, "Altura desde donde se lanza"),
            Parametro.numero("g", "Gravedad", "m/s²", 0.1, 30, 9.81, "Tierra 9.81, Luna 1.62, Marte 3.71"),
            Parametro.numero("masa", "Masa", "kg", 0.001, 10000, 0.5, "Afecta energías y el arrastre"),
            Parametro.booleano("usar_arrastre", "Considerar resistencia del aire", false,
                "Activa el modelo con arrastre cuadrático"),
            Parametro.numero("cd", "Coeficiente de arrastre Cd", "", 0, 3, 0.47, "Esfera ≈ 0.47"),
            Parametro.numero("area", "Área frontal", "m²", 0.00001, 100, 0.04, "Sección transversal del objeto"))
    );

    public static final Tema CAIDA_ENERGIA = new Tema(CAIDA, "Caída libre y conservación de la energía",
        "Objeto que cae (o se lanza verticalmente) y puede rebotar. Muestra la transformación "
        + "entre energía potencial y cinética y la pérdida de energía en cada rebote.",
        Arrays.asList(
            Parametro.numero("h0", "Altura inicial", "m", 0, 2000, 20, "Altura desde donde se suelta"),
            Parametro.numero("v0", "Velocidad inicial (+ hacia arriba)", "m/s", -300, 300, 0, "0 = se suelta"),
            Parametro.numero("masa", "Masa", "kg", 0.001, 10000, 1.5, "No afecta el tiempo de caída"),
            Parametro.numero("g", "Gravedad", "m/s²", 0.1, 30, 9.81, "Tierra 9.81, Luna 1.62, Marte 3.71"),
            Parametro.numero("e", "Coeficiente de restitución e", "", 0, 1, 0.7, "1 = choque elástico, 0 = no rebota"),
            Parametro.entero("rebotes", "Rebotes a simular", 0, 20, 0, "Número entero de rebotes"))
    );

    public static List<Tema> todos() {
        List<Tema> l = new ArrayList<>();
        l.add(TIRO_PARABOLICO);
        l.add(CAIDA_ENERGIA);
        return l;
    }

    public static Tema porId(String id) {
        for (Tema t : todos()) {
            if (t.id.equals(id)) return t;
        }
        throw new IllegalArgumentException("Tema desconocido: " + id);
    }

    public Parametro parametro(String clave) {
        for (Parametro p : parametros) {
            if (p.clave.equals(clave)) return p;
        }
        throw new IllegalArgumentException("Parámetro desconocido: " + clave);
    }

    /** Texto con el rango, p. ej. "[0 – 300]". */
    public static String rango(Parametro p) {
        if (p.tipo == Parametro.Tipo.BOOLEANO) return "";
        return String.format(Locale.ROOT, "[%s – %s]", num(p.min), num(p.max));
    }

    public static String num(double v) {
        return v == Math.rint(v) ? String.valueOf((long) v) : java.math.BigDecimal.valueOf(v).stripTrailingZeros().toPlainString();
    }

    @Override
    public String toString() {
        return nombre;
    }
}
