package simulador;

import java.awt.GraphicsEnvironment;
import java.nio.file.Path;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import javax.swing.SwingUtilities;
import javax.swing.UIManager;

/**
 * Punto de entrada.
 *   Sin argumentos:  abre la interfaz grafica.
 *   Modo consola:    --cli tiro|caida [numero_de_escenario | clave=valor ...]
 */
public class Main {
    public static void main(String[] args) {
        if (args.length > 0 && args[0].equals("--cli")) {
            System.exit(consola(args));
            return;
        }
        if (GraphicsEnvironment.isHeadless()) {
            System.err.println("No hay entorno gráfico. Use el modo consola: --cli tiro 1");
            System.exit(1);
        }
        SwingUtilities.invokeLater(() -> {
            try {
                UIManager.setLookAndFeel(UIManager.getSystemLookAndFeelClassName());
            } catch (Exception ex) {
                // se usa el aspecto por defecto
            }
            new VentanaPrincipal(EjecutorPython.buscarRaiz()).setVisible(true);
        });
    }

    private static int consola(String[] args) {
        if (args.length < 2) {
            System.err.println("Uso: --cli <tiro|caida> [N | clave=valor ...]");
            return 1;
        }
        Tema tema = args[1].startsWith("t") ? Tema.TIRO_PARABOLICO : Tema.CAIDA_ENERGIA;
        Map<String, String> entradas = new LinkedHashMap<>();
        for (Parametro p : tema.parametros) entradas.put(p.clave, Tema.num(p.defecto));
        entradas.put("usar_arrastre", "false");
        String nombreEsc = "Personalizado (consola)";
        List<Escenario> escs = Escenario.de(tema);
        for (int i = 2; i < args.length; i++) {
            String a = args[i];
            if (a.matches("\\d+")) {
                int n = Integer.parseInt(a);
                if (n < 1 || n > escs.size()) {
                    System.err.println("Escenario inexistente (1 a " + escs.size() + ").");
                    return 1;
                }
                entradas.putAll(escs.get(n - 1).valores);
                nombreEsc = escs.get(n - 1).nombre;
            } else if (a.contains("=")) {
                String[] kv = a.split("=", 2);
                entradas.put(kv[0], kv[1]);
            } else {
                System.err.println("Argumento no reconocido: " + a);
                return 1;
            }
        }
        Validador.Resultado v = Validador.validar(tema, entradas);
        if (!v.esValido()) {
            System.err.println("Datos inválidos:");
            for (Validador.Error e : v.errores) System.err.println("  - " + e.mensaje);
            return 3;
        }
        Path raiz = EjecutorPython.buscarRaiz();
        EjecutorPython.Salida s = new EjecutorPython(raiz).ejecutar(tema, nombreEsc, "", v.valores);
        if (!s.ok) {
            System.err.println("Error: " + s.mensaje);
            return 4;
        }
        System.out.println("JSON de entrada: " + s.entradaJson);
        System.out.println("PDF generado:    " + s.pdf);
        for (Path g : s.graficas) System.out.println("Gráfica:         " + g);
        return 0;
    }
}
