import customtkinter as ctk
from tkinter import messagebox

ctk.set_appearance_mode("light")


class Calculadora(ctk.CTk):
    BLANCO = "#FFFFFF"
    ROSA_FONDO = "#FDEFF4"
    ROSA_PASTEL = "#FBD5E3"
    ROSA = "#F6B9D0"
    ROSA_TEXTO = "#C98BA6"
    TINTA = "#8A4B66"

    LIMITE_HISTORIAL = 50

    def __init__(self):
        super().__init__()
        self.title("Calculadora")
        self.geometry("460x700")
        self.resizable(False, False)
        self.configure(fg_color=self.ROSA_FONDO)

        self.numero = ctk.StringVar(value="0")
        self.pantalla = ctk.StringVar(value="0")
        self.texto_izquierda = ""
        self.pendiente_operador = ""
        self.acumulado = None
        self.esperando_numero = True
        self.resultado_mostrado = False
        self.historial = []
        self.ventana_historial = None
        self.indice_seleccionado = None

        self.crear_interfaz()
        self.configurar_teclado()

    def crear_interfaz(self):
        for columna in range(4):
            self.columnconfigure(columna, weight=1)

        titulo = ctk.CTkLabel(
            self,
            text="Calculadora",
            text_color=self.ROSA_TEXTO,
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        titulo.grid(row=0, column=0, columnspan=4, pady=(18, 8), sticky="ew")

        marco_pantalla = ctk.CTkFrame(self, fg_color=self.ROSA_PASTEL, corner_radius=10)
        marco_pantalla.grid(
            row=1,
            column=0,
            columnspan=4,
            padx=20,
            pady=(0, 10),
            sticky="ew",
        )

        self.etiqueta_pantalla = ctk.CTkLabel(
            marco_pantalla,
            textvariable=self.pantalla,
            anchor="e",
            fg_color=self.BLANCO,
            text_color=self.TINTA,
            corner_radius=8,
            font=ctk.CTkFont(family="Consolas", size=34, weight="bold"),
            height=70,
        )
        self.etiqueta_pantalla.pack(fill="both", expand=True, padx=4, pady=4)

        self.boton_historial = ctk.CTkButton(
            self,
            text="Historial",
            command=self.abrir_historial,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color=self.BLANCO,
            hover_color=self.ROSA_PASTEL,
            text_color=self.TINTA,
            corner_radius=10,
            height=38,
            cursor="hand2",
        )
        self.boton_historial.grid(
            row=2,
            column=0,
            columnspan=4,
            padx=20,
            pady=(0, 14),
            sticky="ew",
        )

        panel_botones = ctk.CTkFrame(self, fg_color="transparent")
        panel_botones.grid(
            row=3,
            column=0,
            columnspan=4,
            padx=20,
            pady=(0, 20),
            sticky="nsew",
        )
        for indice in range(4):
            panel_botones.columnconfigure(indice, weight=1)
            panel_botones.rowconfigure(indice, weight=1)

        botones = [
            [
                ("C", self.limpiar, "claro"),
                ("⌫", self.borrar, "claro"),
                ("%", self.porcentaje, "claro"),
                ("÷", lambda: self.operar("/"), "operador"),
            ],
            [
                ("7", lambda: self.introducir("7"), "numero"),
                ("8", lambda: self.introducir("8"), "numero"),
                ("9", lambda: self.introducir("9"), "numero"),
                ("×", lambda: self.operar("*"), "operador"),
            ],
            [
                ("4", lambda: self.introducir("4"), "numero"),
                ("5", lambda: self.introducir("5"), "numero"),
                ("6", lambda: self.introducir("6"), "numero"),
                ("−", lambda: self.operar("-"), "operador"),
            ],
            [
                ("1", lambda: self.introducir("1"), "numero"),
                ("2", lambda: self.introducir("2"), "numero"),
                ("3", lambda: self.introducir("3"), "numero"),
                ("+", lambda: self.operar("+"), "operador"),
            ],
            [
                ("±", self.cambiar_signo, "claro"),
                ("0", lambda: self.introducir("0"), "numero"),
                (".", lambda: self.introducir("."), "numero"),
                ("=", self.igual, "igual"),
            ],
        ]

        for fila, botones_fila in enumerate(botones):
            for columna, (texto, comando, tipo) in enumerate(botones_fila):
                boton = ctk.CTkButton(
                    panel_botones,
                    text=texto,
                    command=comando,
                    font=ctk.CTkFont(size=22, weight="bold"),
                    fg_color=self.color_botones(tipo),
                    hover_color=self.color_activo(tipo),
                    text_color=self.color_texto(tipo),
                    corner_radius=12,
                    height=52,
                    cursor="hand2",
                )
                boton.grid(
                    row=fila,
                    column=columna,
                    padx=5,
                    pady=5,
                    sticky="nsew",
                )

    def color_botones(self, tipo):
        if tipo == "igual":
            return self.ROSA_TEXTO
        if tipo == "operador":
            return self.ROSA
        if tipo == "claro":
            return self.ROSA_PASTEL
        return self.BLANCO

    def color_texto(self, tipo):
        return self.BLANCO if tipo == "igual" else self.TINTA

    def color_activo(self, tipo):
        if tipo == "igual":
            return self.TINTA
        if tipo == "numero":
            return self.ROSA_FONDO
        return self.ROSA

    def configurar_teclado(self):
        self.bind("<Return>", lambda event: self.igual())
        self.bind("<KP_Enter>", lambda event: self.igual())
        self.bind("<Escape>", lambda event: self.limpiar())
        self.bind("<BackSpace>", lambda event: self.borrar())
        self.bind("<percent>", lambda event: self.porcentaje())
        self.bind("<period>", lambda event: self.introducir("."))
        self.bind("<KP_Decimal>", lambda event: self.introducir("."))
        self.bind("<Key-h>", lambda event: self.abrir_historial())
        self.bind("<Key-H>", lambda event: self.abrir_historial())

        for digito in "0123456789":
            self.bind(
                digito,
                lambda event, valor=digito: self.introducir(valor),
            )

        for tecla, operador in (("+", "+"), ("-", "-"), ("*", "*"), ("/", "/")):
            self.bind(
                tecla,
                lambda event, valor=operador: self.operar(valor),
            )

    def refrescar_pantalla(self):
        self.pantalla.set(
            self.texto_izquierda + self.pendiente_operador + self.numero.get()
        )

    def introducir(self, valor):
        if self.resultado_mostrado:
            self.reiniciar_operacion()
            self.numero.set("")

        texto = self.numero.get()
        if valor == ".":
            if "." not in texto:
                self.numero.set((texto if texto else "0") + ".")
        elif texto in ("", "0"):
            self.numero.set(valor)
        elif texto in ("-", "-0"):
            self.numero.set("-" + valor)
        else:
            self.numero.set(texto + valor)

        self.esperando_numero = False
        self.refrescar_pantalla()

    def valor_actual(self):
        try:
            return float(self.numero.get())
        except ValueError:
            return 0.0

    def formatear(self, numero):
        if abs(numero) < 1e-12:
            return "0"
        if numero.is_integer() and abs(numero) < 1e15:
            return str(int(numero))
        return f"{numero:.12g}"

    def calcular(self, izquierda, derecha, operador):
        if operador == "+":
            return izquierda + derecha
        if operador == "-":
            return izquierda - derecha
        if operador == "*":
            return izquierda * derecha
        if operador == "/":
            if derecha == 0:
                raise ZeroDivisionError
            return izquierda / derecha
        raise ValueError

    def operar(self, operador):
        if self.pendiente_operador and not self.esperando_numero:
            derecha = self.valor_actual()
            try:
                resultado = self.calcular(
                    self.acumulado, derecha, self.pendiente_operador
                )
            except ZeroDivisionError:
                self.mostrar_error(self.acumulado, derecha, self.pendiente_operador)
                return
            self.acumulado = resultado
            self.texto_izquierda = self.formatear(resultado)
        else:
            self.acumulado = self.valor_actual()
            self.texto_izquierda = self.formatear(self.acumulado)

        self.pendiente_operador = operador
        self.esperando_numero = True
        self.resultado_mostrado = False
        self.numero.set("")
        self.refrescar_pantalla()

    def igual(self):
        if not self.pendiente_operador or self.acumulado is None:
            return
        if self.esperando_numero and self.numero.get() == "":
            return

        izquierda = self.formatear(self.acumulado)
        derecha = self.valor_actual()
        operador = self.pendiente_operador

        try:
            resultado = self.calcular(self.acumulado, derecha, operador)
        except ZeroDivisionError:
            self.mostrar_error(self.acumulado, derecha, operador)
            return

        self.registrar(
            f"{izquierda} {operador} {self.formatear(derecha)} = "
            f"{self.formatear(resultado)}"
        )

        self.numero.set(self.formatear(resultado))
        self.texto_izquierda = ""
        self.pendiente_operador = ""
        self.acumulado = None
        self.esperando_numero = True
        self.resultado_mostrado = True
        self.refrescar_pantalla()

    def porcentaje(self):
        self.numero.set(self.formatear(self.valor_actual() / 100))
        self.esperando_numero = False
        self.resultado_mostrado = False
        self.refrescar_pantalla()

    def cambiar_signo(self):
        texto = self.numero.get()
        if texto == "":
            return
        if texto.startswith("-"):
            self.numero.set(texto[1:])
        elif texto != "0":
            self.numero.set("-" + texto)
        self.refrescar_pantalla()

    def registrar(self, texto):
        self.historial.append(texto)
        if len(self.historial) > self.LIMITE_HISTORIAL:
            del self.historial[0]
        self.actualizar_historial()

    def mostrar_error(self, izquierda, derecha, operador):
        self.registrar(
            f"{self.formatear(izquierda)} {operador} {self.formatear(derecha)}"
            " = Error (división entre cero)"
        )
        self.reiniciar_operacion()
        self.numero.set("Error")
        self.esperando_numero = True
        self.resultado_mostrado = True
        self.refrescar_pantalla()
        messagebox.showerror(
            "División entre cero",
            "No se puede dividir entre cero.",
            parent=self,
        )

    def borrar(self):
        if self.resultado_mostrado:
            self.limpiar()
            return

        texto = self.numero.get()
        if texto:
            self.numero.set(texto[:-1] if len(texto) > 1 else "")
        elif self.pendiente_operador:
            self.pendiente_operador = ""
            self.texto_izquierda = self.texto_izquierda[:-1]
            self.acumulado = None

        self.refrescar_pantalla()

    def limpiar(self):
        self.reiniciar_operacion()
        self.numero.set("0")
        self.refrescar_pantalla()

    def reiniciar_operacion(self):
        self.texto_izquierda = ""
        self.pendiente_operador = ""
        self.acumulado = None
        self.esperando_numero = True
        self.resultado_mostrado = False

    def abrir_historial(self):
        if self.ventana_historial is not None and self.ventana_historial.winfo_exists():
            self.ventana_historial.lift()
            self.ventana_historial.focus_force()
            return

        ventana = ctk.CTkToplevel(self)
        ventana.title("Historial de operaciones")
        ventana.geometry("400x420")
        ventana.configure(fg_color=self.ROSA_PASTEL)
        ventana.transient(self)

        ctk.CTkLabel(
            ventana,
            text="Historial",
            text_color=self.ROSA_TEXTO,
            font=ctk.CTkFont(size=20, weight="bold"),
        ).pack(fill="x", pady=(14, 8))

        marco_lista = ctk.CTkFrame(ventana, fg_color=self.BLANCO, corner_radius=10)
        marco_lista.pack(fill="both", expand=True, padx=12)

        self.marco_filas = ctk.CTkScrollableFrame(
            marco_lista,
            fg_color="transparent",
            label_text="",
            scrollbar_button_color=self.ROSA,
            scrollbar_button_hover_color=self.ROSA_TEXTO,
        )
        self.marco_filas.pack(fill="both", expand=True, padx=6, pady=6)

        self.filas_historial = []

        botones = ctk.CTkFrame(ventana, fg_color="transparent")
        botones.pack(fill="x", pady=12, padx=12)

        ctk.CTkButton(
            botones,
            text="Reusar",
            command=lambda: self.reusar(self.indice_seleccionado),
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.BLANCO,
            hover_color=self.ROSA,
            text_color=self.TINTA,
            corner_radius=10,
            height=36,
            cursor="hand2",
        ).pack(side="left", fill="x", expand=True, padx=(0, 5))

        ctk.CTkButton(
            botones,
            text="Borrar historial",
            command=self.borrar_historial,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color=self.ROSA_TEXTO,
            hover_color=self.TINTA,
            text_color=self.BLANCO,
            corner_radius=10,
            height=36,
            cursor="hand2",
        ).pack(side="left", fill="x", expand=True, padx=(5, 0))

        self.ventana_historial = ventana
        self.actualizar_historial()

    def seleccionar_historial(self, indice):
        self.indice_seleccionado = indice
        for posicion, fila in enumerate(self.filas_historial):
            fila.configure(
                fg_color=self.ROSA if posicion == indice else "transparent"
            )

    def reusar(self, indice):
        if indice is None or indice >= len(self.historial):
            return
        resultado = self.historial[indice].split(" = ")[-1]
        if resultado.startswith("Error"):
            messagebox.showwarning(
                "Operación no válida",
                "Esa operación dio error, no se puede reutilizar.",
                parent=self,
            )
            return
        self.reiniciar_operacion()
        self.numero.set(resultado)
        self.esperando_numero = True
        self.resultado_mostrado = True
        self.refrescar_pantalla()
        self.ventana_historial.destroy()
        self.ventana_historial = None
        self.indice_seleccionado = None

    def borrar_historial(self):
        if not self.historial:
            return
        confirmacion = messagebox.askyesno(
            "Borrar historial",
            "¿Seguro que quieres borrar todo el historial?",
            parent=self,
        )
        if confirmacion:
            self.historial.clear()
            self.actualizar_historial()

    def actualizar_historial(self):
        if self.ventana_historial is None:
            return
        if not self.ventana_historial.winfo_exists():
            self.ventana_historial = None
            return

        for fila in self.filas_historial:
            fila.destroy()
        self.filas_historial = []
        self.indice_seleccionado = None

        for indice, operacion in enumerate(self.historial):
            fila = ctk.CTkButton(
                self.marco_filas,
                text=f"{indice + 1}. {operacion}",
                command=lambda i=indice: self.seleccionar_historial(i),
                anchor="w",
                font=ctk.CTkFont(family="Consolas", size=12),
                fg_color="transparent",
                hover_color=self.ROSA_PASTEL,
                text_color=self.TINTA,
                corner_radius=6,
                height=30,
                cursor="hand2",
            )
            fila.pack(fill="x", pady=1)
            self.filas_historial.append(fila)


if __name__ == "__main__":
    Calculadora().mainloop()