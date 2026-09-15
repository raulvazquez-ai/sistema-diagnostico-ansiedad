import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from fpdf import FPDF

from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.factors.discrete import TabularCPD
from pgmpy.inference import VariableElimination


class GestorDatos:
    def validar_datos(self, datos):
        errores = []

        if datos.get('antecedentes') not in (0, 1):
            errores.append('Seleccione si tiene antecedentes familiares (Sí/No).')
        if datos.get('edad') not in ('Joven', 'Normal', 'Anciano'):
            errores.append('Seleccione un grupo de edad.')
        if datos.get('estres') not in (0, 1):
            errores.append('Seleccione si experimenta estrés laboral/academico (Sí/No).')
        
        return errores
    
    def validar_sintomas(self, sintomas):
        errores = []
        if not sintomas or len(sintomas) == 0:
            errores.append('Seleccione al menos un síntoma que haya experimentado.')
        return errores


class NormalizadorDatos:
    def normalizar(self, datos_brutos):
        mapping_edad = {'Joven': 0, 'Normal': 1, 'Anciano': 2}
        normal = {}
        normal['antecedentes'] = 1 if datos_brutos.get('antecedentes') == 1 else 0
        normal['edad'] = mapping_edad.get(datos_brutos.get('edad'), 1)
        normal['estres'] = 1 if datos_brutos.get('estres') == 1 else 0
        
        sintomas_list = datos_brutos.get('sintomas', [])
        all_sintomas = ['Nerviosismo', 'Fatiga', 'Concentracion', 'Irritabilidad', 'TensionMuscular', 'Sueño']
        sintomas = {s: (1 if s in sintomas_list else 0) for s in all_sintomas}
        normal['sintomas'] = sintomas
        
        return normal


class RedBayesiana:
    def __init__(self):
        self.model = DiscreteBayesianNetwork()

        nodes = ['Antecedentes', 'Edad', 'Estres', 'Ansiedad', 
                'Nerviosismo', 'Fatiga', 'Concentracion', 'Irritabilidad', 
                'TensionMuscular', 'Sueño']
        for node in nodes:
            self.model.add_node(node)
        
        edges = [
            ('Antecedentes', 'Ansiedad'),
            ('Edad', 'Ansiedad'),
            ('Estres', 'Ansiedad'),
            ('Ansiedad', 'Nerviosismo'),
            ('Ansiedad', 'Fatiga'),
            ('Ansiedad', 'Concentracion'),
            ('Ansiedad', 'Irritabilidad'),
            ('Ansiedad', 'TensionMuscular'),
            ('Ansiedad', 'Sueño')
        ]
        self.model.add_edges_from(edges)
        
        self._define_cpds()
        if not self.model.check_model():
            raise ValueError('Modelo Bayesiano inconsistente con las CPDs proporcionadas')
        self.infer = VariableElimination(self.model)

    def _define_cpds(self):
        cpd_antecedentes = TabularCPD('Antecedentes', 2, [[0.85], [0.15]]) 
        cpd_edad = TabularCPD('Edad', 3, [[0.35], [0.45], [0.20]]) 
        cpd_estres = TabularCPD('Estres', 2, [[0.7], [0.3]]) 

        cpd_ansiedad = TabularCPD(
            variable='Ansiedad', 
            variable_card=2,
            values=[
                # P(Ansiedad=False)
                [
                    0.99,  # A=0, E=Joven, S=0 
                    0.95,  # A=0, E=Joven, S=1
                    0.99,  # A=0, E=Normal, S=0
                    0.955,  # A=0, E=Normal, S=1
                    0.99,  # A=0, E=Anciano, S=0
                    0.96,  # A=0, E=Anciano, S=1
                    
                    0.935,  # A=1, E=Joven, S=0
                    0.89,  # A=1, E=Joven, S=1
                    0.95,  # A=1, E=Normal, S=0
                    0.9,  # A=1, E=Normal, S=1
                    0.955,  # A=1, E=Anciano, S=0
                    0.91   # A=1, E=Anciano, S=1
                ],
                # P(Ansiedad=True)
                [
                    0.01,  # A=0, E=Joven, S=0
                    0.05,  # A=0, E=Joven, S=1
                    0.01,  # A=0, E=Normal, S=0
                    0.045,  # A=0, E=Normal, S=1
                    0.01,  # A=0, E=Anciano, S=0
                    0.04,  # A=0, E=Anciano, S=1
                    
                    0.065,  # A=1, E=Joven, S=0
                    0.11,  # A=1, E=Joven, S=1
                    0.05,  # A=1, E=Normal, S=0
                    0.1,  # A=1, E=Normal, S=1
                    0.045,  # A=1, E=Anciano, S=0
                    0.09   # A=1, E=Anciano, S=1
                ]
            ],
            evidence=['Antecedentes', 'Edad', 'Estres'],
            evidence_card=[2, 3, 2]
        )

        cpd_nerviosismo = TabularCPD('Nerviosismo', 2, 
                                   [[0.9, 0.45], 
                                    [0.10, 0.55]], 
                                   evidence=['Ansiedad'], evidence_card=[2])

        cpd_fatiga = TabularCPD('Fatiga', 2, 
                              [[0.75, 0.40],   
                               [0.25, 0.6]], 
                              evidence=['Ansiedad'], evidence_card=[2])

        cpd_concentracion = TabularCPD('Concentracion', 2, 
                                     [[0.8, 0.45],   
                                      [0.2, 0.55]],  
                                     evidence=['Ansiedad'], evidence_card=[2])

        cpd_irritabilidad = TabularCPD('Irritabilidad', 2, 
                                     [[0.85, 0.4],   
                                      [0.15, 0.6]],
                                     evidence=['Ansiedad'], evidence_card=[2])

        cpd_tension = TabularCPD('TensionMuscular', 2, 
                               [[0.85, 0.50],  
                                [0.15, 0.50]], 
                               evidence=['Ansiedad'], evidence_card=[2])

        cpd_sueno = TabularCPD('Sueño', 2, 
                             [[0.70, 0.45], 
                              [0.30, 0.55]],  
                             evidence=['Ansiedad'], evidence_card=[2])

        self.model.add_cpds(cpd_antecedentes, cpd_edad, cpd_estres, cpd_ansiedad,
                           cpd_nerviosismo, cpd_fatiga, cpd_concentracion, 
                           cpd_irritabilidad, cpd_tension, cpd_sueno)

    def inferir(self, evidencia_normalizada):
        evidence = {
            'Antecedentes': int(evidencia_normalizada['antecedentes']),
            'Edad': int(evidencia_normalizada['edad']),
            'Estres': int(evidencia_normalizada['estres'])
        }

        for sintoma, valor in evidencia_normalizada['sintomas'].items():
            if valor == 1:
                evidence[sintoma] = 1  
            
        try:
            q_ans = self.infer.query(['Ansiedad'], evidence=evidence)

            probs_sintomas = {}
            sintomas_nodes = ['Nerviosismo', 'Fatiga', 'Concentracion', 'Irritabilidad', 'TensionMuscular', 'Sueño']
            
            for sintoma in sintomas_nodes:
                if evidencia_normalizada['sintomas'].get(sintoma, 0) == 1:
                    probs_sintomas[sintoma] = type('obj', (object,), {'values': [0.0, 1.0]})()  
                else:
                    probs_sintomas[sintoma] = type('obj', (object,), {'values': [1.0, 0.0]})() 
                    
        except Exception as e:
            print(f"Error en inferencia: {e}")
            raise Exception(f"No se pudo realizar la inferencia bayesiana: {e}")
        
        return q_ans, probs_sintomas


class InterpretadorResultados:
    def interpretar_resultados(self, q_ans, probs_sintomas, factores_usuario):
        try:
            prob_ans = float(q_ans.values[1])  
        except:
            prob_ans = 0.0
            
        if prob_ans >= 0.8:
            nivel, recomendacion, color = 'ALTO', 'Consulte con especialista', 'rojo'
        
        elif prob_ans >= 0.4:
            nivel, recomendacion, color = 'MODERADO', 'Monitorear sintomas', 'naranja'
        
        else:
            nivel, recomendacion, color = 'BAJO', 'Continuar prevencion', 'verde'
        
        sintomas_principales = []
        
        mapping_nombres = {
            'Nerviosismo': 'Sensacion de nerviosismo',
            'Fatiga': 'Facilidad para fatigarse', 
            'Concentracion': 'Dificultad para concentrarse',
            'Irritabilidad': 'Irritabilidad frecuente',
            'TensionMuscular': 'Tension muscular',
            'Sueño': 'Trastornos del sueño'
        }
        
        for sintoma, q in probs_sintomas.items():
            try:
                prob_sintoma = float(q.values[1])
                if prob_sintoma == 1.0:  
                    nombre_sintoma = mapping_nombres.get(sintoma, sintoma)
                    sintomas_principales.append(nombre_sintoma)
            except Exception as e:
                print(f"Error procesando síntoma {sintoma}: {e}")
                continue
        
        return {
            'probabilidad_ansiedad': prob_ans,
            'nivel_riesgo': nivel,
            'recomendacion': recomendacion,
            'color_alerta': color,
            'sintomas_principales': sintomas_principales,
            'factores_influyentes': self.identificar_factores(factores_usuario)
        }

    def identificar_factores(self, factores_usuario):
        res = []
        if factores_usuario.get('antecedentes') == 1:
            res.append('Antecedentes familiares')
        
        edad_text = factores_usuario.get('edad_text')
        if edad_text:
            res.append(f'Edad: {edad_text}')
            
        if factores_usuario.get('estres') == 1:
            res.append('Estres laboral/academico')
            
        return res

class ExportadorPDF:
    
    def generar_reporte(self, diagnostico):

        COLORES = {
            'rojo': (220, 53, 69),
            'naranja': (253, 126, 20),
            'verde': (40, 167, 69),
            'gris_fondo': (248, 249, 250),
            'gris_borde': (222, 226, 230),
            'texto_oscuro': (33, 37, 41),
            'texto_claro': (255, 255, 255)
        }
        color_tupla = COLORES.get(diagnostico['color_alerta'], (108, 117, 125))

        try:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_auto_page_break(auto=True, margin=15)
            pdf.set_left_margin(15)
            pdf.set_right_margin(15)
            pdf.set_text_color(*COLORES['texto_oscuro'])

            pdf.set_font("Arial", 'B', 18)

            pdf.cell(0, 10, "Reporte de Evaluacion de Ansiedad", 0, 1, 'C')
            
            pdf.set_font("Arial", '', 10)
            fecha = datetime.now().strftime('%d/%m/%Y %H:%M:%S')

            pdf.cell(0, 8, f'Fecha de generacion: {fecha}', 0, 1, 'C')
            pdf.ln(10)

            pdf.set_fill_color(*color_tupla)
            pdf.set_text_color(*COLORES['texto_claro'])
            pdf.set_font("Arial", 'B', 14)
            pdf.cell(0, 12, f"Nivel de Riesgo: {diagnostico['nivel_riesgo']}", 0, 1, 'C', fill=True)
            pdf.set_text_color(*COLORES['texto_oscuro'])
            pdf.ln(4)

            pdf.set_font("Arial", 'B', 12)
            prob_txt = f"Probabilidad de Ansiedad: {diagnostico['probabilidad_ansiedad']*100:.1f}%"
            pdf.cell(0, 10, prob_txt, 0, 1, 'C')
            
            pdf.set_font("Arial", 'I', 11)

            pdf.multi_cell(0, 7, f"Recomendacion: {diagnostico['recomendacion']}", 0, 'C')
            pdf.ln(5)

            pdf.set_draw_color(*COLORES['gris_borde'])
            pdf.cell(0, 5, '', 'T', 1)
            pdf.ln(5)

            pdf.set_font("Arial", 'B', 12)
            pdf.cell(0, 10, 'Factores de Riesgo Identificados', 0, 1, 'L')
            pdf.set_font("Arial", '', 11)

            if diagnostico['factores_influyentes']:
                for f in diagnostico['factores_influyentes']:
                    pdf.cell(0, 7, f' -  {f}', 0, 1, 'L')
            
            else:
                pdf.cell(0, 7, ' -  Ninguno identificado.', 0, 1, 'L')
            pdf.ln(5)

            pdf.set_font("Arial", 'B', 12)

            pdf.cell(0, 10, 'Sintomas Principales Detectados', 0, 1, 'L')
            pdf.set_font("Arial", '', 11)
            
            if diagnostico['sintomas_principales']:
                for s in diagnostico['sintomas_principales']:
                    pdf.cell(0, 7, f' -  {s}', 0, 1, 'L')
            
            else:
                pdf.cell(0, 7, ' -  Ninguno seleccionado.', 0, 1, 'L')
            pdf.ln(5)

            pdf.set_y(-25) 
            pdf.set_font("Arial", 'I', 8)
            pdf.set_text_color(120, 120, 120)
            
            pdf.multi_cell(0, 5, 
                           'Este reporte es generado automaticamente basado en sus respuestas y un modelo '
                           'probabilistico. No sustituye, bajo ninguna circunstancia, un diagnostico '
                           'clinico realizado por un profesional de la salud mental.', 0, 'C')

            filename = 'diagnostico_ansiedad_reporte.pdf'
            pdf.output(filename)
            return filename
        
        except Exception as e:
            print(f"Error generando PDF: {e}")
            raise Exception(f"No se pudo generar el PDF: {e}")


class InterfazUsuario:
    def __init__(self, root):
        self.root = root
        self.root.title('Sistema Diagnostico de Ansiedad')
        self.root.geometry('600x550')
        
        style = ttk.Style()
        style.configure('TButton', font=('Helvetica', 10), padding=5)
        style.configure('TRadiobutton', font=('Helvetica', 10), padding=5)
        style.configure('TCheckbutton', font=('Helvetica', 10), padding=5)

        self.gestor = GestorDatos()
        self.normalizador = NormalizadorDatos()
        try:
            self.red = RedBayesiana()
            print("Red bayesiana inicializada correctamente")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo inicializar la red bayesiana: {e}")
            return
        self.interpretador = InterpretadorResultados()
        self.exportador = ExportadorPDF()
        self.datos_brutos = {}
        self._build_welcome()

    def _clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def _build_welcome(self):
        self._clear()
        frm = ttk.Frame(self.root, padding=30)
        frm.pack(fill='both', expand=True)

        ttk.Label(frm, 
                 text='BIENVENIDO AL SISTEMA DE DIAGNOSTICO DE ANSIEDAD', 
                 font=('Helvetica', 14, 'bold'),
                 anchor='center',
                 justify='center',
                 wraplength=500).pack(pady=20, fill='x')
        
        ttk.Label(frm, 
                 text='De acuerdo con la Ley de Protección de Datos Personales, garantizados la confidencialidad y seguridad de la informacion' \
                 'proporcionada. Los datos serán tratados de forma lícita, transparente y únicamente para los fines autorizados.',
                 anchor='center',
                 justify='center',
                 wraplength=500).pack(pady=15, fill='x')

        ttk.Button(frm, 
                  text='Entendido, comenzar evaluacion', 
                  command=self._build_paso1).pack(pady=20)

    def _build_paso1(self):
        self._clear()
        frm = ttk.Frame(self.root, padding=20)
        frm.pack(fill='both', expand=True)
       
        ttk.Label(frm, 
                 text='PASO 1: EVALUACION GENERAL', 
                 font=('Helvetica', 13, 'bold'),
                 anchor='center',
                 justify='center').pack(pady=(10, 15), fill='x')

        content_frame = ttk.Frame(frm)
        content_frame.pack() 

        ttk.Label(content_frame, 
                 text='Antecedentes familiares de ansiedad:',
                 font=('Helvetica', 11)).pack(pady=(5, 8))
        
        ante_frame = ttk.Frame(content_frame)
        self.ante_var = tk.IntVar(value=-1)
        ttk.Radiobutton(ante_frame, text='Si', variable=self.ante_var, value=1).pack(side='left', padx=10)
        ttk.Radiobutton(ante_frame, text='No', variable=self.ante_var, value=0).pack(side='left', padx=10)
        ante_frame.pack()

        ttk.Label(content_frame, 
                 text='Grupo de edad:',
                 font=('Helvetica', 11)).pack(pady=(10, 8))
        
        edad_frame = ttk.Frame(content_frame)
        self.edad_var = tk.StringVar(value='')
        ttk.Radiobutton(edad_frame, text='Joven (18-35)', variable=self.edad_var, value='Joven').pack(side='left', padx=5)
        ttk.Radiobutton(edad_frame, text='Normal (36-60)', variable=self.edad_var, value='Normal').pack(side='left', padx=5)
        ttk.Radiobutton(edad_frame, text='Anciano (>60)', variable=self.edad_var, value='Anciano').pack(side='left', padx=5)
        edad_frame.pack()

        ttk.Label(content_frame, 
                 text='¿Experimenta estres laboral o academico?',
                 font=('Helvetica', 11)).pack(pady=(10, 8))
        
        estres_frame = ttk.Frame(content_frame)
        self.estres_var = tk.IntVar(value=-1)
        ttk.Radiobutton(estres_frame, text='Si', variable=self.estres_var, value=1).pack(side='left', padx=10)
        ttk.Radiobutton(estres_frame, text='No', variable=self.estres_var, value=0).pack(side='left', padx=10)
        estres_frame.pack()

        btn_frame = ttk.Frame(frm)
        btn_frame.pack(side='bottom', pady=20) 
        ttk.Button(btn_frame, text='← Atras', command=self._build_welcome).pack(side='left', padx=10)
        ttk.Button(btn_frame, text='Continuar →', command=self._paso1_continuar).pack(side='left', padx=10)

    def _paso1_continuar(self):
        datos = {
            'antecedentes': self.ante_var.get(),
            'edad': self.edad_var.get(),
            'estres': self.estres_var.get()
        }
        errores = self.gestor.validar_datos(datos)
        if errores:
            messagebox.showerror('Datos invalidos', '\n'.join(errores))
            return
        self.datos_brutos = datos
        self._build_paso2()

    def _build_paso2(self):
        self._clear()
        frm = ttk.Frame(self.root, padding=20)
        frm.pack(fill='both', expand=True)

        ttk.Label(frm, 
                 text='PASO 2: EVALUACION DE SINTOMAS', 
                 font=('Helvetica', 13, 'bold'),
                 anchor='center',
                 justify='center').pack(pady=(15, 10), fill='x')

        ttk.Label(frm, 
                 text='Marque al menos UN sintoma que haya experimentado durante las ultimas dos semanas:',
                 anchor='center',
                 justify='center',
                 wraplength=450).pack(pady=(5, 10), fill='x')

        center_frame = ttk.Frame(frm)
        center_frame.pack()
        
        self.s_vars = {}
        sintomas = [
            ('Nerviosismo', 'Sensacion constante de nerviosismo'),
            ('Fatiga', 'Facilidad para fatigarse'),
            ('Concentracion', 'Dificultad para concentrarse'),
            ('Irritabilidad', 'Irritabilidad frecuente'),
            ('TensionMuscular', 'Tension muscular'),
            ('Sueño', 'Trastornos del sueño')
        ]
        
        for i, (key, label) in enumerate(sintomas):
            var = tk.IntVar(value=0)
            ttk.Checkbutton(center_frame, text=label, variable=var).grid(row=i, column=0, pady=4, sticky='w')
            self.s_vars[key] = var

        btn_frame = ttk.Frame(frm)
        btn_frame.pack(side='bottom', pady=20)
        ttk.Button(btn_frame, text='← Atras', command=self._build_paso1).pack(side='left', padx=10)
        ttk.Button(btn_frame, text='Evaluar →', command=self._evaluar).pack(side='left', padx=10)

    def _evaluar(self):
        sintomas_seleccionados = [k for k, v in self.s_vars.items() if v.get() == 1]
        self.datos_brutos['sintomas'] = sintomas_seleccionados

        errores_sintomas = self.gestor.validar_sintomas(sintomas_seleccionados)
        if errores_sintomas:
            messagebox.showerror('Datos incompletos', '\n'.join(errores_sintomas))
            return

        errores_factores = self.gestor.validar_datos(self.datos_brutos)
        if errores_factores:
            messagebox.showerror('Datos invalidos', '\n'.join(errores_factores))
            return
        
        try:
            normal = self.normalizador.normalizar(self.datos_brutos)
            q_ans, probs_sintomas = self.red.inferir(normal)
            
            factores_usuario = {
                'antecedentes': normal['antecedentes'],
                'edad_text': self.datos_brutos.get('edad'),
                'estres': normal['estres']
            }
            
            self.reporte_actual = self.interpretador.interpretar_resultados(
                q_ans, probs_sintomas, factores_usuario
            )
            self._mostrar_resultados()
            
        except Exception as e:
            messagebox.showerror("Error", f"Error durante la evaluacion: {e}")

    def _mostrar_resultados(self):
        self._clear()
        frm = ttk.Frame(self.root, padding=25)
        frm.pack(fill='both', expand=True)

        ttk.Label(frm, 
                 text='RESULTADOS DE LA EVALUACION', 
                 font=('Helvetica', 14, 'bold'),
                 anchor='center',
                 justify='center').pack(pady=(15, 10), fill='x')

        center_frame = ttk.Frame(frm)
        center_frame.pack(fill='x') 
        
        prob = self.reporte_actual['probabilidad_ansiedad'] * 100

        ttk.Label(center_frame, 
                 text='PROBABILIDAD DE ANSIEDAD:', 
                 font=('Helvetica', 12, 'bold')).pack(pady=(8,2)) 

        bar_frame = ttk.Frame(center_frame)
        bar_frame.pack(fill='x', padx=50, pady=(0, 5)) 

        bar = ttk.Progressbar(bar_frame, 
                              orient='horizontal', 
                              length=300, 
                              mode='determinate', 
                              maximum=100, 
                              value=prob)
        bar.pack(side='left', fill='x', expand=True, padx=5) 

        prob_label = ttk.Label(bar_frame, 
                               text=f'{prob:.1f}%', 
                               font=('Helvetica', 11, 'bold'))
        prob_label.pack(side='left', padx=5)

        ttk.Label(center_frame, 
                 text=f'NIVEL DE RIESGO: {self.reporte_actual["nivel_riesgo"]}',
                 font=('Helvetica', 11, 'bold')).pack(pady=4)

        ttk.Label(center_frame, 
                 text='FACTORES DE RIESGO IDENTIFICADOS:',
                 font=('Helvetica', 10, 'bold')).pack(pady=(10, 3))

        factor_frame = ttk.Frame(center_frame)
        factor_frame.pack()
        if self.reporte_actual['factores_influyentes']:
            for factor in self.reporte_actual['factores_influyentes']:
                ttk.Label(factor_frame, text=f'- {factor}').pack(anchor='w') 
        else:
            ttk.Label(factor_frame, text='- Ninguno identificado.').pack(anchor='w')

        ttk.Label(center_frame, 
                 text='SINTOMAS PRINCIPALES DETECTADOS:',
                 font=('Helvetica', 10, 'bold')).pack(pady=(10, 3))

        sintoma_frame = ttk.Frame(center_frame)
        sintoma_frame.pack()
        if self.reporte_actual['sintomas_principales']:
            for sintoma in self.reporte_actual['sintomas_principales']:
                ttk.Label(sintoma_frame, text=f'- {sintoma}').pack(anchor='w')
        else:
            ttk.Label(sintoma_frame, text='- Ninguno seleccionado.').pack(anchor='w')


        ttk.Label(center_frame, 
                 text=f'RECOMENDACION: {self.reporte_actual["recomendacion"]}',
                 font=('Helvetica', 10, 'italic'),
                 wraplength=400,
                 justify='center').pack(pady=10)

        btn_frame = ttk.Frame(frm)
        btn_frame.pack(side='bottom', pady=20)
        ttk.Button(btn_frame, text='Generar PDF', 
                  command=self._generar_pdf).pack(side='left', padx=10)
        ttk.Button(btn_frame, text='Nueva Evaluacion', 
                  command=self._build_welcome).pack(side='left', padx=10)

    def _generar_pdf(self):
        try:
            filename = self.exportador.generar_reporte(self.reporte_actual)
            messagebox.showinfo("Exito", f"PDF generado: {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el PDF: {e}")


if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = InterfazUsuario(root)
        root.mainloop()
    except Exception as e:
        print(f"Error al ejecutar la aplicación: {e}")