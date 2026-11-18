package simulador;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.concurrent.TimeUnit;

/** Arma el JSON de entrada, lo guarda y ejecuta el procesamiento en Python. */
public class EjecutorPython {

    public static class Salida {
        public boolean ok;
        public String mensaje;
        public Path directorio;
        public Path pdf;
        public Path entradaJson;
        public List<Path> graficas = new ArrayList<>();
    }

    private final Path raiz;

    public EjecutorPython(Path raiz) {
        this.raiz = raiz;
    }

    /** Busca la carpeta del proyecto (la que contiene python/simulador.py) desde el directorio actual. */
    public static Path buscarRaiz() {
        Path p = Paths.get("").toAbsolutePath();
        for (int i = 0; i < 4 && p != null; i++, p = p.getParent()) {
            if (Files.exists(p.resolve("python").resolve("simulador.py"))) return p;
        }
        return Paths.get("").toAbsolutePath();
    }

    public static String jsonEntrada(Tema tema, String escenario, String equipo, Map<String, Object> valores) {
        Map<String, Object> meta = new LinkedHashMap<>();
        meta.put("origen", "Java");
        meta.put("fecha", LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss")));
        if (equipo != null && !equipo.trim().isEmpty()) meta.put("equipo", equipo.trim());
        Map<String, Object> raizJson = new LinkedHashMap<>();
        raizJson.put("version", 1);
        raizJson.put("tema", tema.id);
        raizJson.put("escenario", escenario == null || escenario.isEmpty() ? "Personalizado" : escenario);
        raizJson.put("meta", meta);
        raizJson.put("parametros", valores);
        return JsonUtil.escribir(raizJson);
    }

    public Salida ejecutar(Tema tema, String escenario, String equipo, Map<String, Object> valores) {
        Salida s = new Salida();
        try {
            String marca = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd_HHmmss"));
            s.directorio = raiz.resolve("salidas").resolve(marca + "_" + tema.id);
            Files.createDirectories(s.directorio);
            s.entradaJson = s.directorio.resolve("entrada.json");
            Files.write(s.entradaJson, jsonEntrada(tema, escenario, equipo, valores).getBytes(StandardCharsets.UTF_8));

            Path script = raiz.resolve("python").resolve("simulador.py");
            if (!Files.exists(script)) {
                s.mensaje = "No se encontró " + script + ". Ejecute el programa desde la carpeta del proyecto.";
                return s;
            }
            String py = buscarPython();
            if (py == null) {
                s.mensaje = "No se encontró Python (probé python3, python y py). Instálelo y agréguelo al PATH.";
                return s;
            }
            ProcessBuilder pb = new ProcessBuilder(py, script.toString(),
                "--entrada", s.entradaJson.toString(), "--salida", s.directorio.toString());
            pb.environment().put("PYTHONIOENCODING", "utf-8");
            pb.redirectErrorStream(true);
            Process proc = pb.start();
            String salida = leer(proc);
            if (!proc.waitFor(180, TimeUnit.SECONDS)) {
                proc.destroyForcibly();
                s.mensaje = "Python tardó demasiado (más de 180 s) y fue detenido.";
                return s;
            }
            String ultima = ultimaLineaJson(salida);
            if (ultima == null) {
                s.mensaje = "Python no devolvió un resultado válido:\n" + salida.trim();
                return s;
            }
            if (!"ok".equals(JsonUtil.leerCadena(ultima, "estado"))) {
                s.mensaje = String.valueOf(JsonUtil.leerCadena(ultima, "mensaje"));
                return s;
            }
            s.ok = true;
            s.pdf = Paths.get(JsonUtil.leerCadena(ultima, "pdf"));
            for (String g : JsonUtil.leerListaCadenas(ultima, "graficas")) s.graficas.add(Paths.get(g));
            s.mensaje = "Simulación completada.";
        } catch (IOException | InterruptedException ex) {
            s.mensaje = "Error al ejecutar Python: " + ex.getMessage();
        }
        return s;
    }

    private static String leer(Process proc) throws IOException {
        StringBuilder sb = new StringBuilder();
        try (BufferedReader br = new BufferedReader(new InputStreamReader(proc.getInputStream(), StandardCharsets.UTF_8))) {
            String linea;
            while ((linea = br.readLine()) != null) sb.append(linea).append('\n');
        }
        return sb.toString();
    }

    private static String ultimaLineaJson(String salida) {
        String res = null;
        for (String l : salida.split("\n")) {
            if (l.trim().startsWith("{\"estado\"")) res = l.trim();
        }
        return res;
    }

    static String buscarPython() {
        for (String c : new String[] {"python3", "python", "py"}) {
            try {
                Process p = new ProcessBuilder(c, "--version").redirectErrorStream(true).start();
                leer(p);
                if (p.waitFor(10, TimeUnit.SECONDS) && p.exitValue() == 0) return c;
            } catch (IOException | InterruptedException ex) {
                // probar el siguiente candidato
            }
        }
        return null;
    }
}
