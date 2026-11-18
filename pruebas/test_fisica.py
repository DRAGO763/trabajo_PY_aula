"""Pruebas automaticas de la parte Python. Ejecutar:  python3 -m unittest discover -s pruebas -v"""
import json, math, os, subprocess, sys, tempfile, unittest
RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "python"))
import fisica_tiro as T
import fisica_caida as C

BASE_T = {"v0": 20, "angulo": 45, "h0": 0, "g": 9.81, "masa": 1.0,
          "usar_arrastre": False, "cd": 0.47, "area": 0.04}
BASE_C = {"h0": 20, "v0": 0, "masa": 1.0, "g": 9.81, "e": 0.7, "rebotes": 0}


class TiroParabolico(unittest.TestCase):
    def test_alcance_formula_clasica(self):
        s = T.simular_ideal(BASE_T)
        esperado = 20 ** 2 * math.sin(math.radians(90)) / 9.81
        self.assertAlmostEqual(s["x"][-1], esperado, places=6)

    def test_altura_maxima_y_tiempo(self):
        s = T.simular_ideal(BASE_T)
        vy = 20 * math.sin(math.radians(45))
        self.assertAlmostEqual(max(s["y"]), vy ** 2 / (2 * 9.81), places=3)
        self.assertAlmostEqual(s["t"][-1], 2 * vy / 9.81, places=6)

    def test_angulos_complementarios_mismo_alcance(self):
        a = T.simular_ideal(dict(BASE_T, angulo=30))["x"][-1]
        b = T.simular_ideal(dict(BASE_T, angulo=60))["x"][-1]
        self.assertAlmostEqual(a, b, places=6)

    def test_energia_se_conserva_sin_aire(self):
        em = T.simular_ideal(dict(BASE_T, h0=10))["em"]
        self.assertLess(max(em) - min(em), 1e-6 * em[0])

    def test_arrastre_reduce_alcance_y_energia(self):
        p = dict(BASE_T, v0=30, usar_arrastre=True)
        con = T.simular_arrastre(p)
        sin = T.simular_ideal(p)
        self.assertLess(con["x"][-1], sin["x"][-1])
        self.assertLess(con["em"][-1], con["em"][0])

    def test_arrastre_casi_cero_tiende_al_ideal(self):
        p = dict(BASE_T, usar_arrastre=True, cd=1e-9, area=1e-9)
        self.assertAlmostEqual(T.simular_arrastre(p)["x"][-1], T.simular_ideal(p)["x"][-1], delta=0.01)

    def test_luna_alcanza_mas_lejos(self):
        luna = T.simular_ideal(dict(BASE_T, g=1.62))["x"][-1]
        self.assertGreater(luna, T.simular_ideal(BASE_T)["x"][-1] * 5)

    def test_sin_movimiento_lanza_error(self):
        with self.assertRaises(ValueError):
            T.simular_ideal(dict(BASE_T, angulo=0, h0=0))

    def test_angulo_optimo_45_desde_el_suelo(self):
        self.assertEqual(T.barrido_angulos(BASE_T, False)[2], 45.0)


class CaidaEnergia(unittest.TestCase):
    def test_rapidez_impacto_por_energia(self):
        s = C.simular(BASE_C)
        self.assertAlmostEqual(s["tramos"][0]["v_impacto"], math.sqrt(2 * 9.81 * 20), places=6)

    def test_tiempo_de_caida(self):
        s = C.simular(BASE_C)
        self.assertAlmostEqual(s["tramos"][0]["t_impacto"], math.sqrt(2 * 20 / 9.81), places=6)

    def test_energia_mecanica_constante_en_vuelo(self):
        em = C.simular(BASE_C)["em"]
        self.assertLess(max(em) - min(em), 1e-9 * em[0])

    def test_masa_no_afecta_tiempo(self):
        a = C.simular(dict(BASE_C, masa=1))["tramos"][0]["t_impacto"]
        b = C.simular(dict(BASE_C, masa=50))["tramos"][0]["t_impacto"]
        self.assertAlmostEqual(a, b, places=9)

    def test_rebotes_pierden_e2_de_energia(self):
        s = C.simular(dict(BASE_C, rebotes=3))
        self.assertAlmostEqual(s["em"][-1] / s["em"][0], 0.7 ** 6, places=6)
        self.assertAlmostEqual(s["tramos"][1]["h_pico"], 20 * 0.49, places=6)

    def test_choque_elastico_conserva_energia(self):
        s = C.simular(dict(BASE_C, e=1.0, rebotes=3))
        self.assertAlmostEqual(s["em"][-1], s["em"][0], places=6)

    def test_lanzamiento_hacia_arriba(self):
        s = C.simular(dict(BASE_C, h0=5, v0=12))
        self.assertAlmostEqual(max(s["y"]), 5 + 12 ** 2 / (2 * 9.81), places=3)

    def test_sin_movimiento_lanza_error(self):
        with self.assertRaises(ValueError):
            C.simular(dict(BASE_C, h0=0, v0=0))


class IntegracionJsonPdf(unittest.TestCase):
    def _correr(self, datos):
        with tempfile.TemporaryDirectory() as d:
            ent = os.path.join(d, "entrada.json")
            with open(ent, "w") as f:
                json.dump(datos, f)
            r = subprocess.run([sys.executable, os.path.join(RAIZ, "python", "simulador.py"),
                                "--entrada", ent, "--salida", os.path.join(d, "out")],
                               capture_output=True, text=True)
            est = json.loads(r.stdout.strip().splitlines()[-1])
            if est["estado"] == "ok":
                self.assertTrue(os.path.getsize(est["pdf"]) > 5000)
                with open(est["pdf"], "rb") as f:
                    self.assertEqual(f.read(5), b"%PDF-")
            return r.returncode, est

    def test_genera_pdf_tiro(self):
        rc, est = self._correr({"tema": "tiro_parabolico", "parametros": BASE_T})
        self.assertEqual((rc, est["estado"]), (0, "ok"))

    def test_genera_pdf_caida(self):
        rc, est = self._correr({"tema": "caida_energia", "parametros": dict(BASE_C, rebotes=2)})
        self.assertEqual((rc, est["estado"]), (0, "ok"))

    def test_json_invalido_da_error_controlado(self):
        rc, est = self._correr({"tema": "caida_energia", "parametros": dict(BASE_C, e=2)})
        self.assertEqual((rc, est["estado"]), (2, "error"))

    def test_tema_desconocido(self):
        rc, est = self._correr({"tema": "otro", "parametros": {}})
        self.assertEqual(est["estado"], "error")


if __name__ == "__main__":
    unittest.main()
