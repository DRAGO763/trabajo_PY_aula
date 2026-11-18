package simulador;

import java.util.ArrayList;
import java.util.Collection;
import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/** Escritura de JSON (Map/List/String/Number/Boolean) y lectura minima de la respuesta de Python. */
public final class JsonUtil {
    private JsonUtil() { }

    public static String escribir(Object o) {
        StringBuilder sb = new StringBuilder();
        escribir(o, sb, 0);
        return sb.append('\n').toString();
    }

    private static void sangria(StringBuilder sb, int n) {
        for (int i = 0; i < n; i++) sb.append("  ");
    }

    @SuppressWarnings("unchecked")
    private static void escribir(Object o, StringBuilder sb, int nivel) {
        if (o == null) {
            sb.append("null");
        } else if (o instanceof Map) {
            Map<String, Object> m = (Map<String, Object>) o;
            if (m.isEmpty()) { sb.append("{}"); return; }
            sb.append("{\n");
            int i = 0;
            for (Map.Entry<String, Object> e : m.entrySet()) {
                sangria(sb, nivel + 1);
                cadena(e.getKey(), sb);
                sb.append(": ");
                escribir(e.getValue(), sb, nivel + 1);
                sb.append(++i < m.size() ? ",\n" : "\n");
            }
            sangria(sb, nivel);
            sb.append('}');
        } else if (o instanceof Collection) {
            Collection<Object> c = (Collection<Object>) o;
            sb.append('[');
            int i = 0;
            for (Object x : c) {
                if (i++ > 0) sb.append(", ");
                escribir(x, sb, nivel + 1);
            }
            sb.append(']');
        } else if (o instanceof Boolean) {
            sb.append(o.toString());
        } else if (o instanceof Number) {
            double d = ((Number) o).doubleValue();
            if (Double.isNaN(d) || Double.isInfinite(d)) throw new IllegalArgumentException("Número no finito");
            if (o instanceof Integer || o instanceof Long) sb.append(o.toString());
            else sb.append(d == Math.rint(d) && Math.abs(d) < 1e15 ? String.valueOf((long) d) + ".0" : String.valueOf(d));
        } else {
            cadena(o.toString(), sb);
        }
    }

    private static void cadena(String s, StringBuilder sb) {
        sb.append('"');
        for (char c : s.toCharArray()) {
            switch (c) {
                case '"': sb.append("\\\""); break;
                case '\\': sb.append("\\\\"); break;
                case '\n': sb.append("\\n"); break;
                case '\r': sb.append("\\r"); break;
                case '\t': sb.append("\\t"); break;
                default:
                    if (c < 0x20) sb.append(String.format("\\u%04x", (int) c));
                    else sb.append(c);
            }
        }
        sb.append('"');
    }

    /** Lee el valor de texto de una clave de primer nivel (con des-escape basico). */
    public static String leerCadena(String json, String clave) {
        Matcher m = Pattern.compile("\"" + Pattern.quote(clave) + "\"\\s*:\\s*\"((?:[^\"\\\\]|\\\\.)*)\"").matcher(json);
        return m.find() ? desescapar(m.group(1)) : null;
    }

    /** Lee una lista de cadenas, p. ej. "graficas": ["a.png", "b.png"]. */
    public static List<String> leerListaCadenas(String json, String clave) {
        List<String> out = new ArrayList<>();
        Matcher m = Pattern.compile("\"" + Pattern.quote(clave) + "\"\\s*:\\s*\\[(.*?)\\]", Pattern.DOTALL).matcher(json);
        if (m.find()) {
            Matcher s = Pattern.compile("\"((?:[^\"\\\\]|\\\\.)*)\"").matcher(m.group(1));
            while (s.find()) out.add(desescapar(s.group(1)));
        }
        return out;
    }

    private static String desescapar(String s) {
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < s.length(); i++) {
            char c = s.charAt(i);
            if (c == '\\' && i + 1 < s.length()) {
                char n = s.charAt(++i);
                switch (n) {
                    case 'n': sb.append('\n'); break;
                    case 't': sb.append('\t'); break;
                    case 'u':
                        if (i + 4 < s.length()) {
                            sb.append((char) Integer.parseInt(s.substring(i + 1, i + 5), 16));
                            i += 4;
                        }
                        break;
                    default: sb.append(n);
                }
            } else {
                sb.append(c);
            }
        }
        return sb.toString();
    }
}
