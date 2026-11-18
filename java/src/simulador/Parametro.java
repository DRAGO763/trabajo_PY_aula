package simulador;

/** Describe un parametro de entrada del simulador (nombre, unidad, rango y valor por defecto). */
public class Parametro {
    public enum Tipo { NUMERO, ENTERO, BOOLEANO }

    public final String clave;
    public final String etiqueta;
    public final String unidad;
    public final Tipo tipo;
    public final double min;
    public final double max;
    public final double defecto;
    public final String ayuda;

    public Parametro(String clave, String etiqueta, String unidad, Tipo tipo,
                     double min, double max, double defecto, String ayuda) {
        this.clave = clave;
        this.etiqueta = etiqueta;
        this.unidad = unidad;
        this.tipo = tipo;
        this.min = min;
        this.max = max;
        this.defecto = defecto;
        this.ayuda = ayuda;
    }

    public static Parametro numero(String clave, String etiqueta, String unidad,
                                   double min, double max, double defecto, String ayuda) {
        return new Parametro(clave, etiqueta, unidad, Tipo.NUMERO, min, max, defecto, ayuda);
    }

    public static Parametro entero(String clave, String etiqueta, double min, double max,
                                   double defecto, String ayuda) {
        return new Parametro(clave, etiqueta, "", Tipo.ENTERO, min, max, defecto, ayuda);
    }

    public static Parametro booleano(String clave, String etiqueta, boolean defecto, String ayuda) {
        return new Parametro(clave, etiqueta, "", Tipo.BOOLEANO, 0, 1, defecto ? 1 : 0, ayuda);
    }
}
