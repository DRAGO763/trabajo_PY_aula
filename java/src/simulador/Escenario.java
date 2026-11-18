package simulador;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/** Escenarios preconfigurados (equivalen a los archivos de la carpeta escenarios/). */
public class Escenario {
    public final String nombre;
    public final String descripcion;
    public final Map<String, String> valores;

    private Escenario(String nombre, String descripcion, String... kv) {
        this.nombre = nombre;
        this.descripcion = descripcion;
        this.valores = new LinkedHashMap<>();
        for (int i = 0; i < kv.length; i += 2) valores.put(kv[i], kv[i + 1]);
    }

    public static List<Escenario> de(Tema tema) {
        List<Escenario> l = new ArrayList<>();
        if (tema.id.equals(Tema.TIRO)) {
            l.add(new Escenario("Lanzamiento ideal a 45°", "Desde el suelo, sin aire: alcance máximo de referencia.",
                "v0", "25", "angulo", "45", "h0", "0", "g", "9.81", "masa", "0.5", "usar_arrastre", "false", "cd", "0.47", "area", "0.04"));
            l.add(new Escenario("Desde un acantilado", "Lanzamiento desde 40 m: el ángulo óptimo baja de 45°.",
                "v0", "20", "angulo", "20", "h0", "40", "g", "9.81", "masa", "0.5", "usar_arrastre", "false", "cd", "0.47", "area", "0.04"));
            l.add(new Escenario("Balón con resistencia del aire", "Compara la trayectoria real con la ideal.",
                "v0", "30", "angulo", "40", "h0", "1", "g", "9.81", "masa", "0.45", "usar_arrastre", "true", "cd", "0.47", "area", "0.038"));
            l.add(new Escenario("El mismo tiro en la Luna", "Misma rapidez y ángulo, con g = 1.62 m/s².",
                "v0", "25", "angulo", "45", "h0", "0", "g", "1.62", "masa", "0.5", "usar_arrastre", "false", "cd", "0.47", "area", "0.04"));
        } else {
            l.add(new Escenario("Caída libre desde 20 m", "Se suelta desde el reposo: la energía potencial se vuelve cinética.",
                "h0", "20", "v0", "0", "masa", "1.5", "g", "9.81", "e", "0.7", "rebotes", "0"));
            l.add(new Escenario("Lanzamiento hacia arriba", "Se lanza a 12 m/s desde 5 m: sube, se detiene y cae.",
                "h0", "5", "v0", "12", "masa", "1", "g", "9.81", "e", "0.7", "rebotes", "0"));
            l.add(new Escenario("Pelota con rebotes (e = 0.7)", "Cinco rebotes: cada uno conserva e² de la energía.",
                "h0", "10", "v0", "0", "masa", "0.2", "g", "9.81", "e", "0.7", "rebotes", "5"));
            l.add(new Escenario("Caída en Marte", "Misma caída desde 20 m con g = 3.71 m/s².",
                "h0", "20", "v0", "0", "masa", "1.5", "g", "3.71", "e", "0.7", "rebotes", "0"));
        }
        return l;
    }

    @Override
    public String toString() {
        return nombre;
    }
}
