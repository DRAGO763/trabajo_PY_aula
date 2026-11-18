package simulador;

import java.awt.BorderLayout;
import java.awt.Color;
import java.awt.Desktop;
import java.awt.Dimension;
import java.awt.FlowLayout;
import java.awt.Font;
import java.awt.GridBagConstraints;
import java.awt.GridBagLayout;
import java.awt.Image;
import java.awt.Insets;
import java.awt.image.BufferedImage;
import java.io.IOException;
import java.nio.file.Path;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import javax.imageio.ImageIO;
import javax.swing.BorderFactory;
import javax.swing.ImageIcon;
import javax.swing.JButton;
import javax.swing.JCheckBox;
import javax.swing.JComboBox;
import javax.swing.JComponent;
import javax.swing.JFrame;
import javax.swing.JLabel;
import javax.swing.JOptionPane;
import javax.swing.JPanel;
import javax.swing.JScrollPane;
import javax.swing.JSplitPane;
import javax.swing.JTextArea;
import javax.swing.JTextField;
import javax.swing.SwingWorker;

/** Interfaz grafica (Java Swing): captura de parametros, validacion y ejecucion de la simulacion. */
public class VentanaPrincipal extends JFrame {
    private static final Color ERROR = new Color(255, 214, 214);

    private final Path raiz;
    private final JComboBox<Tema> cbTema = new JComboBox<>();
    private final JComboBox<Escenario> cbEscenario = new JComboBox<>();
    private final JLabel lblTema = new JLabel();
    private final JLabel lblEscenario = new JLabel(" ");
    private final JTextField tfEquipo = new JTextField(22);
    private final JPanel panelCampos = new JPanel(new GridBagLayout());
    private final Map<String, JComponent> campos = new LinkedHashMap<>();
    private final JTextArea log = new JTextArea(7, 40);
    private final JLabel lblImagen = new JLabel("La gráfica aparecerá aquí al simular.", JLabel.CENTER);
    private final JComboBox<String> cbGraficas = new JComboBox<>();
    private final JButton btnSimular = new JButton("Validar y simular");
    private final JButton btnPdf = new JButton("Abrir PDF");
    private final JButton btnCarpeta = new JButton("Abrir carpeta de resultados");
    private final JScrollPane scrollImagen = new JScrollPane(lblImagen);
    private EjecutorPython.Salida ultima;
    private boolean cargando;

    public VentanaPrincipal(Path raiz) {
        super("Simulador educativo de Física — Tiro parabólico y Caída libre / Energía");
        this.raiz = raiz;
        setDefaultCloseOperation(EXIT_ON_CLOSE);
        setLayout(new BorderLayout(8, 8));
        ((JPanel) getContentPane()).setBorder(BorderFactory.createEmptyBorder(8, 8, 8, 8));
        add(construirEncabezado(), BorderLayout.NORTH);

        JPanel izq = new JPanel(new BorderLayout(4, 4));
        izq.setBorder(BorderFactory.createTitledBorder("Parámetros de la simulación"));
        izq.add(new JScrollPane(panelCampos), BorderLayout.CENTER);
        izq.setMinimumSize(new Dimension(380, 300));

        JPanel der = new JPanel(new BorderLayout(4, 4));
        der.setBorder(BorderFactory.createTitledBorder("Resultados gráficos"));
        JPanel barraGraf = new JPanel(new FlowLayout(FlowLayout.LEFT));
        barraGraf.add(new JLabel("Gráfica:"));
        barraGraf.add(cbGraficas);
        der.add(barraGraf, BorderLayout.NORTH);
        der.add(scrollImagen, BorderLayout.CENTER);

        JSplitPane split = new JSplitPane(JSplitPane.HORIZONTAL_SPLIT, izq, der);
        split.setResizeWeight(0.35);
        add(split, BorderLayout.CENTER);
        add(construirPie(), BorderLayout.SOUTH);

        for (Tema t : Tema.todos()) cbTema.addItem(t);
        cbTema.addActionListener(e -> cambiarTema());
        cbEscenario.addActionListener(e -> cargarEscenario());
        cbGraficas.addActionListener(e -> mostrarGraficaSeleccionada());
        btnSimular.addActionListener(e -> simular());
        btnPdf.addActionListener(e -> abrir(ultima == null ? null : ultima.pdf));
        btnCarpeta.addActionListener(e -> abrir(ultima == null ? null : ultima.directorio));
        btnPdf.setEnabled(false);
        btnCarpeta.setEnabled(false);
        cambiarTema();
        setSize(1180, 760);
        setLocationRelativeTo(null);
    }

    private JPanel construirEncabezado() {
        JPanel p = new JPanel(new GridBagLayout());
        GridBagConstraints c = new GridBagConstraints();
        c.insets = new Insets(2, 4, 2, 4);
        c.anchor = GridBagConstraints.WEST;
        c.gridx = 0; c.gridy = 0; p.add(new JLabel("Tema:"), c);
        c.gridx = 1; p.add(cbTema, c);
        c.gridx = 2; p.add(new JLabel("Escenario:"), c);
        c.gridx = 3; p.add(cbEscenario, c);
        c.gridx = 4; p.add(new JLabel("Equipo:"), c);
        c.gridx = 5; p.add(tfEquipo, c);
        c.gridx = 0; c.gridy = 1; c.gridwidth = 6; c.fill = GridBagConstraints.HORIZONTAL;
        lblTema.setFont(lblTema.getFont().deriveFont(Font.PLAIN, 12f));
        p.add(lblTema, c);
        c.gridy = 2;
        lblEscenario.setFont(lblEscenario.getFont().deriveFont(Font.ITALIC, 12f));
        p.add(lblEscenario, c);
        return p;
    }

    private JPanel construirPie() {
        JPanel p = new JPanel(new BorderLayout(4, 4));
        log.setEditable(false);
        log.setFont(new Font(Font.MONOSPACED, Font.PLAIN, 12));
        JScrollPane sp = new JScrollPane(log);
        sp.setBorder(BorderFactory.createTitledBorder("Mensajes"));
        p.add(sp, BorderLayout.CENTER);
        JPanel botones = new JPanel(new FlowLayout(FlowLayout.RIGHT));
        btnSimular.setFont(btnSimular.getFont().deriveFont(Font.BOLD));
        botones.add(btnSimular);
        botones.add(btnPdf);
        botones.add(btnCarpeta);
        p.add(botones, BorderLayout.SOUTH);
        return p;
    }

    private Tema temaActual() {
        return (Tema) cbTema.getSelectedItem();
    }

    private void cambiarTema() {
        Tema t = temaActual();
        lblTema.setText("<html>" + t.descripcion + "</html>");
        cargando = true;
        cbEscenario.removeAllItems();
        for (Escenario e : Escenario.de(t)) cbEscenario.addItem(e);
        cargando = false;
        construirCampos(t);
        cargarEscenario();
    }

    private void construirCampos(Tema t) {
        panelCampos.removeAll();
        campos.clear();
        GridBagConstraints c = new GridBagConstraints();
        c.insets = new Insets(4, 6, 4, 6);
        c.anchor = GridBagConstraints.WEST;
        int fila = 0;
        for (Parametro p : t.parametros) {
            String unidad = p.unidad.isEmpty() ? "" : " (" + p.unidad + ")";
            c.gridx = 0; c.gridy = fila; c.fill = GridBagConstraints.NONE; c.weightx = 0;
            JLabel etq = new JLabel(p.etiqueta + unidad);
            etq.setToolTipText(p.ayuda);
            panelCampos.add(etq, c);
            JComponent comp;
            if (p.tipo == Parametro.Tipo.BOOLEANO) {
                JCheckBox cb = new JCheckBox();
                cb.setToolTipText(p.ayuda);
                cb.addActionListener(e -> actualizarDependientes());
                comp = cb;
            } else {
                JTextField tf = new JTextField(8);
                tf.setToolTipText(p.ayuda + "  " + Tema.rango(p));
                comp = tf;
            }
            c.gridx = 1; panelCampos.add(comp, c);
            c.gridx = 2;
            panelCampos.add(new JLabel("<html><font color='gray'>" + Tema.rango(p) + "</font></html>"), c);
            campos.put(p.clave, comp);
            fila++;
        }
        c.gridx = 0; c.gridy = fila; c.weighty = 1; c.gridwidth = 3; c.fill = GridBagConstraints.VERTICAL;
        panelCampos.add(new JLabel(), c);
        panelCampos.revalidate();
        panelCampos.repaint();
    }

    private void actualizarDependientes() {
        if (temaActual().id.equals(Tema.TIRO)) {
            boolean on = ((JCheckBox) campos.get("usar_arrastre")).isSelected();
            campos.get("cd").setEnabled(on);
            campos.get("area").setEnabled(on);
        }
    }

    private void cargarEscenario() {
        if (cargando) return;
        Escenario e = (Escenario) cbEscenario.getSelectedItem();
        if (e == null) return;
        lblEscenario.setText("<html>" + e.descripcion + "</html>");
        for (Map.Entry<String, String> kv : e.valores.entrySet()) {
            JComponent comp = campos.get(kv.getKey());
            if (comp instanceof JCheckBox) ((JCheckBox) comp).setSelected("true".equals(kv.getValue()));
            else if (comp instanceof JTextField) ((JTextField) comp).setText(kv.getValue());
        }
        limpiarErrores();
        actualizarDependientes();
    }

    private Map<String, String> leerEntradas() {
        Map<String, String> m = new LinkedHashMap<>();
        for (Map.Entry<String, JComponent> kv : campos.entrySet()) {
            JComponent c = kv.getValue();
            if (c instanceof JCheckBox) m.put(kv.getKey(), String.valueOf(((JCheckBox) c).isSelected()));
            else m.put(kv.getKey(), ((JTextField) c).getText());
        }
        return m;
    }

    private void limpiarErrores() {
        for (JComponent c : campos.values()) {
            if (c instanceof JTextField) c.setBackground(Color.WHITE);
        }
    }

    private void anotar(String texto) {
        log.append(texto + "\n");
        log.setCaretPosition(log.getDocument().getLength());
    }

    private void simular() {
        limpiarErrores();
        Tema tema = temaActual();
        Validador.Resultado r = Validador.validar(tema, leerEntradas());
        if (!r.esValido()) {
            StringBuilder sb = new StringBuilder("Corrija los siguientes datos:\n");
            for (Validador.Error e : r.errores) {
                sb.append(" • ").append(e.mensaje).append('\n');
                anotar("[ERROR] " + e.mensaje);
                if (e.clave != null && campos.get(e.clave) instanceof JTextField) campos.get(e.clave).setBackground(ERROR);
            }
            JOptionPane.showMessageDialog(this, sb.toString(), "Datos inválidos", JOptionPane.WARNING_MESSAGE);
            return;
        }
        Escenario esc = (Escenario) cbEscenario.getSelectedItem();
        String nombreEsc = esc == null ? "Personalizado" : esc.nombre;
        if (esc != null && !coincide(esc, leerEntradas())) nombreEsc = esc.nombre + " (modificado)";
        final String nombreFinal = nombreEsc;
        btnSimular.setEnabled(false);
        anotar("Datos válidos. Generando JSON y ejecutando Python...");
        new SwingWorker<EjecutorPython.Salida, Void>() {
            @Override
            protected EjecutorPython.Salida doInBackground() {
                return new EjecutorPython(raiz).ejecutar(tema, nombreFinal, tfEquipo.getText(), r.valores);
            }

            @Override
            protected void done() {
                btnSimular.setEnabled(true);
                try {
                    terminar(get());
                } catch (Exception ex) {
                    anotar("[ERROR] " + ex);
                }
            }
        }.execute();
    }

    private static boolean coincide(Escenario e, Map<String, String> actual) {
        for (Map.Entry<String, String> kv : e.valores.entrySet()) {
            String a = actual.get(kv.getKey());
            if (a == null) return false;
            try {
                if (Double.parseDouble(a.replace(',', '.')) != Double.parseDouble(kv.getValue())) return false;
            } catch (NumberFormatException ex) {
                if (!a.equals(kv.getValue())) return false;
            }
        }
        return true;
    }

    private void terminar(EjecutorPython.Salida s) {
        if (!s.ok) {
            anotar("[ERROR] " + s.mensaje);
            JOptionPane.showMessageDialog(this, s.mensaje, "No se pudo simular", JOptionPane.ERROR_MESSAGE);
            return;
        }
        ultima = s;
        anotar("[OK] JSON de entrada: " + s.entradaJson);
        anotar("[OK] Informe PDF:     " + s.pdf);
        btnPdf.setEnabled(true);
        btnCarpeta.setEnabled(true);
        cargando = true;
        cbGraficas.removeAllItems();
        for (Path g : s.graficas) cbGraficas.addItem(g.getFileName().toString());
        cargando = false;
        mostrarGraficaSeleccionada();
    }

    private void mostrarGraficaSeleccionada() {
        if (cargando || ultima == null) return;
        int i = cbGraficas.getSelectedIndex();
        if (i < 0 || i >= ultima.graficas.size()) return;
        try {
            BufferedImage img = ImageIO.read(ultima.graficas.get(i).toFile());
            int ancho = Math.max(scrollImagen.getViewport().getWidth() - 20, 480);
            int alto = img.getHeight() * ancho / img.getWidth();
            lblImagen.setText(null);
            lblImagen.setIcon(new ImageIcon(img.getScaledInstance(ancho, alto, Image.SCALE_SMOOTH)));
        } catch (IOException ex) {
            anotar("[ERROR] No se pudo mostrar la gráfica: " + ex.getMessage());
        }
    }

    private void abrir(Path p) {
        if (p == null) return;
        try {
            if (Desktop.isDesktopSupported()) Desktop.getDesktop().open(p.toFile());
            else anotar("Abra manualmente: " + p);
        } catch (IOException | UnsupportedOperationException ex) {
            anotar("No se pudo abrir automáticamente. Ruta: " + p);
        }
    }
}
