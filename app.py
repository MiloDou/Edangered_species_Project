
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, filedialog
import numpy as np

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

GREEN_BG = "#162417"
CARD_BG = "#1f3320"
INPUT_BG = "#2b4a2d"
INPUT_BORDER = "#4f7a55"
TEXT_SOFT = "#cfe8d1"
TEXT_BASE = "#e5f6e9"
TEXT_ACCENT = "#bce6be"

STATE_LABELS = ["No presenta peligro", "Amenazado", "Crítico", "Extinto"]


def format_float(x, prec=6):
    return f"{x:.{prec}f}"


def is_row_stochastic(M: np.ndarray, tol=1e-9) -> tuple[bool, str]:
    if M.shape != (4, 4):
        return False, "La matriz debe ser 4×4."
    if np.any(M < -tol) or np.any(M > 1 + tol):
        return False, "Todos los valores deben estar en el rango [0, 1]."
    sums = M.sum(axis=1)
    if not np.allclose(sums, 1.0, atol=1e-6):
        details = ", ".join([f"fila {i+1}={sums[i]:.6f}" for i in range(4)])
        return False, f"Cada fila debe sumar 1. Sumas actuales → {details}"
    return True, ""


class TransitionMatrixApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Estado de Especies en Peligro")
        self.geometry("1160x820")
        self.configure(fg_color=GREEN_BG)

        header = ctk.CTkFrame(self, fg_color=GREEN_BG)
        header.pack(fill="x", padx=24, pady=(16, 6))
        ctk.CTkLabel(
            header,
            text="Estado de Especies en Peligro",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=TEXT_BASE
        ).pack(side="left")

        right = ctk.CTkFrame(header, fg_color=GREEN_BG)
        right.pack(side="right")
        ctk.CTkLabel(right, text="Especie:", text_color=TEXT_SOFT).pack(side="left", padx=(0, 6))
        self.species_var = tk.StringVar(value="Tortuga Marina")
        ctk.CTkOptionMenu(right, values=["Tortuga Marina", "Jaguar", "Cóndor", "Quetzal", "Guacamaya", "Personalizado"],
                          variable=self.species_var, fg_color="#315e38", button_color="#3e6b45").pack(side="left")

        card = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=16)
        card.pack(padx=24, pady=8, fill="x")

        ctk.CTkLabel(card, text=(
            "Defina la matriz de transición. Active 'Extinto absorbente' para fijar la última fila a [0,0,0,1].\n"
            "Cada fila debe sumar 1."
        ), text_color=TEXT_SOFT).grid(row=0, column=0, columnspan=8, pady=(14, 10), sticky="w")

        self.absorbent_var = tk.BooleanVar(value=True)
        ctk.CTkCheckBox(card, text="Extinto absorbente (última fila = [0,0,0,1])",
                        variable=self.absorbent_var, command=self._toggle_absorbing,
                        text_color=TEXT_SOFT).grid(row=1, column=0, columnspan=8, sticky="w", pady=(0, 10))

        # headers
        ctk.CTkLabel(card, text="", width=150).grid(row=2, column=0)  # spacer
        for j, lbl in enumerate(STATE_LABELS):
            ctk.CTkLabel(card, text=lbl, text_color="#b3ddb4",
                         font=ctk.CTkFont(size=13, weight="bold")).grid(row=2, column=j+1, padx=6, pady=6)

        self.matrix_entries: list[list[ctk.CTkEntry]] = []
        for i, row_name in enumerate(STATE_LABELS):
            ctk.CTkLabel(card, text=f"Desde {row_name}", text_color="#a9d2ad").grid(row=3+i, column=0, padx=6, pady=6, sticky="e")
            row = []
            for j in range(4):
                e = ctk.CTkEntry(card, width=110, fg_color=INPUT_BG, border_color=INPUT_BORDER)
                e.grid(row=3+i, column=1+j, padx=6, pady=6)
                row.append(e)
            self.matrix_entries.append(row)

        self._load_example_matrix()

        actions = ctk.CTkFrame(self, fg_color=GREEN_BG)
        actions.pack(padx=24, pady=(6, 2), fill="x")
        ctk.CTkButton(actions, text="✅ Validar Matriz", command=self._validate_matrix,
                      fg_color="#4a874d", hover_color="#5fa162").pack(side="left", padx=(0, 8))
        ctk.CTkButton(actions, text="🌱 Cargar Ejemplo", command=self._load_example_matrix,
                      fg_color="#3f6f42", hover_color="#558f59").pack(side="left", padx=8)
        ctk.CTkButton(actions, text="🧹 Limpiar", command=self._clear_all,
                      fg_color="#355a39", hover_color="#4e7a52").pack(side="left", padx=8)

        calc = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=16)
        calc.pack(padx=24, pady=10, fill="x")
        ctk.CTkLabel(calc, text="Estado inicial:", text_color=TEXT_BASE).grid(row=0, column=0, padx=6, pady=10, sticky="e")
        ctk.CTkLabel(calc, text="Estado objetivo:", text_color=TEXT_BASE).grid(row=0, column=2, padx=6, pady=10, sticky="e")
        ctk.CTkLabel(calc, text="Pasos n:", text_color=TEXT_BASE).grid(row=0, column=4, padx=6, pady=10, sticky="e")

        self.start_state_var = tk.StringVar(value=STATE_LABELS[0])
        self.target_state_var = tk.StringVar(value=STATE_LABELS[1])
        self.steps_var = tk.StringVar(value="2")

        ctk.CTkOptionMenu(calc, values=STATE_LABELS, variable=self.start_state_var).grid(row=0, column=1, padx=6)
        ctk.CTkOptionMenu(calc, values=STATE_LABELS, variable=self.target_state_var).grid(row=0, column=3, padx=6)
        self.steps_entry = ctk.CTkEntry(calc, textvariable=self.steps_var, width=80, fg_color=INPUT_BG, border_color=INPUT_BORDER)
        self.steps_entry.grid(row=0, column=5, padx=6)

        ctk.CTkButton(calc, text="🔢 Calcular P(n)", command=self._calculate_probability,
                      fg_color="#4a874d", hover_color="#5fa162").grid(row=0, column=6, padx=12)
        ctk.CTkButton(calc, text="📄 Exportar P^n a CSV", command=self._export_csv,
                      fg_color="#315d36", hover_color="#3f7446").grid(row=0, column=7, padx=12)

        self.result_label = ctk.CTkLabel(self, text="Resultado: —", text_color=TEXT_ACCENT,
                                         font=ctk.CTkFont(size=16, weight="bold"))
        self.result_label.pack(padx=24, pady=(6, 8), anchor="w")

        self.matrixn_text = ctk.CTkTextbox(self, height=200, fg_color=CARD_BG, text_color=TEXT_SOFT)
        self.matrixn_text.pack(padx=24, pady=(0, 16), fill="x")
        self.matrixn_text.insert("1.0", "Matriz P^n aparecerá aquí tras el cálculo.\n")
        self.matrixn_text.configure(state="disabled")

        ctk.CTkLabel(self, text="Hecho por - Ronaldo Emilio Méndez Mayorga y Carlos Hugo Escobar Gómez",
                     text_color="#9fd3a6").pack(pady=(0, 10))

        self._last_Pn: np.ndarray | None = None
        self._last_n: int | None = None

    def _toggle_absorbing(self):
        for j in range(4):
            entry = self.matrix_entries[3][j]
            if self.absorbent_var.get():
                entry.configure(state="normal")
                entry.delete(0, "end")
                entry.insert(0, "0" if j < 3 else "1")
                entry.configure(state="disabled")
            else:
                entry.configure(state="normal")
                if not entry.get():
                    entry.insert(0, "0")

    def _read_matrix(self) -> np.ndarray | None:
        M = np.zeros((4, 4), dtype=float)
        try:
            for i in range(4):
                for j in range(4):
                    txt = self.matrix_entries[i][j].get().strip().replace(",", ".")
                    val = float(txt)
                    if val < 0 or val > 1:
                        raise ValueError(f"Fuera de rango [0,1] en fila {i+1}, columna {j+1}: {val}")
                    M[i, j] = val
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return None
        if self.absorbent_var.get():
            M[3, :] = np.array([0, 0, 0, 1], dtype=float)
        return M

    def _auto_close_rows(self, M: np.ndarray):
        for i in range(4):
            s = M[i].sum()
            if abs(s - 1.0) <= 1e-6:
                M[i, -1] += (1.0 - s)

    def _validate_matrix(self):
        M = self._read_matrix()
        if M is None:
            return False
        self._auto_close_rows(M)
        ok, msg = is_row_stochastic(M)
        if not ok:
            messagebox.showerror("Matriz inválida", msg)
            return False
        messagebox.showinfo("Matriz válida", " ✔ La matriz es estocástica por filas.")
        return True

    def _load_example_matrix(self):
        example = np.array([
            [0.5, 0.4, 0.05, 0.05],
            [0.1, 0.6, 0.2, 0.1],
            [0.05, 0.25, 0.6, 0.1],
            [0.0, 0.0, 0.0, 1.0],
        ], dtype=float)
        for i in range(4):
            for j in range(4):
                e = self.matrix_entries[i][j]
                e.configure(state="normal")
                e.delete(0, "end")
                e.insert(0, f"{example[i, j]:.6g}")
        if self.absorbent_var.get():
            self._toggle_absorbing()

    def _clear_all(self):
        for i in range(4):
            for j in range(4):
                e = self.matrix_entries[i][j]
                e.configure(state="normal")
                e.delete(0, "end")
                e.insert(0, "0")
        if self.absorbent_var.get():
            self._toggle_absorbing()
        self.result_label.configure(text="Resultado: —")
        self.matrixn_text.configure(state="normal")
        self.matrixn_text.delete("1.0", "end")
        self.matrixn_text.insert("1.0", "Matriz P^n aparecerá aquí tras el cálculo.\n")
        self.matrixn_text.configure(state="disabled")
        self._last_Pn = None
        self._last_n = None

    def _calculate_probability(self):
        M = self._read_matrix()
        if M is None:
            return
        self._auto_close_rows(M)
        ok, msg = is_row_stochastic(M)
        if not ok:
            messagebox.showerror("Matriz inválida", msg)
            return

        try:
            n = int(self.steps_var.get())
            if n < 0:
                raise ValueError
        except Exception:
            messagebox.showerror("Error", "Número de pasos inválido. Debe ser un entero ≥ 0.")
            return

        start_idx = STATE_LABELS.index(self.start_state_var.get())
        target_idx = STATE_LABELS.index(self.target_state_var.get())

        Pn = np.linalg.matrix_power(M, n)
        prob = float(Pn[start_idx, target_idx])

        self._last_Pn = Pn
        self._last_n = n

        self.result_label.configure(
            text=f"Resultado: P({STATE_LABELS[start_idx]} → {STATE_LABELS[target_idx]}, n={n}) = {prob:.6f}"
        )
        with np.printoptions(precision=6, suppress=True):
            txt = str(Pn)
        self.matrixn_text.configure(state="normal")
        self.matrixn_text.delete("1.0", "end")
        self.matrixn_text.insert("1.0", f"P^{n} =\n{txt}\n")
        self.matrixn_text.configure(state="disabled")

    def _export_csv(self):
        if self._last_Pn is None:
            messagebox.showwarning("Sin datos", "Primero calcula P(n) para exportar la matriz.")
            return
        default_name = f"P_pow_{self._last_n}.csv"
        file = filedialog.asksaveasfilename(defaultextension=".csv", initialfile=default_name,
                                            filetypes=[("CSV", "*.csv")])
        if not file:
            return
        try:
            np.savetxt(file, self._last_Pn, delimiter=",", fmt="%.8f")
            messagebox.showinfo("Exportado", f"Se guardó la matriz P^{self._last_n} en:\n{file}")
        except Exception as e:
            messagebox.showerror("Error al exportar", str(e))


if __name__ == "__main__":
    app = TransitionMatrixApp()
    app.mainloop()
