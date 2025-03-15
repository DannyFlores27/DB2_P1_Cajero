import tkinter as tk
import cx_Oracle

# Leer código del ATM desde archivo
with open("codigo_atm.txt", "r") as file:
    CODIGO_ATM = file.read().strip()

# Conexión a Oracle
DSN = cx_Oracle.makedsn("localhost", "1521", service_name="umg")
CONN = cx_Oracle.connect(user="system", password="Umg$2025", dsn=DSN)

# CONN = cx_Oracle.connect("system", "123", "localhost:1521/umg")

def centrar_ventana(ventana, ancho=400, alto=300):
    pantalla_ancho = ventana.winfo_screenwidth()
    pantalla_alto = ventana.winfo_screenheight()
    x = (pantalla_ancho // 2) - (ancho // 2)
    y = (pantalla_alto // 2) - (alto // 2)
    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")

def sp_validar_ingreso(id_tarjeta):
    with CONN.cursor() as cursor:
        out_id_titular = cursor.var(cx_Oracle.NUMBER)
        out_id_caja = cursor.var(cx_Oracle.NUMBER)
        cursor.callproc("sp_validar_ingreso", [id_tarjeta, out_id_titular, out_id_caja])
        return out_id_titular.getvalue(), out_id_caja.getvalue()

def sp_realizar_extraccion(id_caja, id_titular, pin, codigo_atm, monto):
    with CONN.cursor() as cursor:
        out_mensaje = cursor.var(cx_Oracle.STRING)
        cursor.callproc("sp_realizar_extraccion", [id_caja, id_titular, pin, codigo_atm, monto, out_mensaje])
        return out_mensaje.getvalue()

def sp_realizar_transferencia(id_caja_origen, id_caja_destino, id_titular, pin, codigo_atm, monto):
    with CONN.cursor() as cursor:
        out_mensaje = cursor.var(cx_Oracle.STRING)
        cursor.callproc("sp_realizar_transferencia", [id_caja_origen, id_caja_destino, id_titular, pin, codigo_atm, monto, out_mensaje])
        return out_mensaje.getvalue()

def iniciar_cajero():
    root = tk.Tk()
    root.title("Cajero Automático")
    centrar_ventana(root)

    tk.Label(root, text="Bienvenido al Cajero Automático", font=("Arial", 14, "bold")).pack(pady=10)
    
    def validar_tarjeta():
        id_tarjeta = entry_tarjeta.get()
        id_titular, id_caja = sp_validar_ingreso(id_tarjeta)
        if id_titular is None or id_caja is None:
            label_mensaje.config(text="Tarjeta inválida o cuenta no encontrada.", fg="red")
            return
        root.destroy()
        mostrar_menu(id_titular, id_caja, "")

    tk.Label(root, text="Ingrese su número de tarjeta:").pack(pady=5)
    entry_tarjeta = tk.Entry(root)
    entry_tarjeta.pack(pady=5)
    tk.Button(root, text="Ingresar", command=validar_tarjeta).pack(pady=5)
    label_mensaje = tk.Label(root, text="", fg="red")
    label_mensaje.pack(pady=5)

    root.mainloop()

def mostrar_menu(id_titular, id_caja, mensaje):
    menu = tk.Tk()
    menu.title("Menú Principal")
    centrar_ventana(menu)

    tk.Label(menu, text="Menú Principal", font=("Arial", 14, "bold")).pack(pady=10)
    
    def abrir_extraccion():
        menu.destroy()
        realizar_extraccion(id_titular, id_caja)

    def abrir_transferencia():
        menu.destroy()
        realizar_transferencia(id_titular, id_caja)

    tk.Button(menu, text="Extracción", command=abrir_extraccion).pack(pady=10)
    tk.Button(menu, text="Transferencia", command=abrir_transferencia).pack(pady=10)
    tk.Button(menu, text="Salir", command=menu.destroy).pack(pady=10)

    label_mensaje = tk.Label(menu, text=mensaje, fg="green")
    label_mensaje.pack(pady=10)

    menu.mainloop()

def realizar_extraccion(id_titular, id_caja):
    ventana = tk.Tk()
    ventana.title("Extracción")
    centrar_ventana(ventana)

    def confirmar_extraccion():
        monto = float(entry_monto.get())
        pin = entry_pin.get()
        mensaje = sp_realizar_extraccion(id_caja, id_titular, pin, CODIGO_ATM, monto)
        ventana.destroy()
        mostrar_menu(id_titular, id_caja, mensaje)

    tk.Label(ventana, text="Ingrese monto a extraer:").pack(pady=5)
    entry_monto = tk.Entry(ventana)
    entry_monto.pack(pady=5)
    tk.Label(ventana, text="Ingrese PIN:").pack(pady=5)
    entry_pin = tk.Entry(ventana, show="*")
    entry_pin.pack(pady=5)
    tk.Button(ventana, text="Confirmar", command=confirmar_extraccion).pack(pady=10)

    ventana.mainloop()

def realizar_transferencia(id_titular, id_caja_origen):
    ventana = tk.Tk()
    ventana.title("Transferencia")
    centrar_ventana(ventana)

    def confirmar_transferencia():
        id_caja_destino = entry_cuenta_destino.get()
        monto = float(entry_monto_transferencia.get())
        pin = entry_pin_transferencia.get()
        mensaje = sp_realizar_transferencia(id_caja_origen, id_caja_destino, id_titular, pin, CODIGO_ATM, monto)
        ventana.destroy()
        mostrar_menu(id_titular, id_caja_origen, mensaje)

    tk.Label(ventana, text="Ingrese cuenta destino:").pack(pady=5)
    entry_cuenta_destino = tk.Entry(ventana)
    entry_cuenta_destino.pack(pady=5)
    tk.Label(ventana, text="Ingrese monto a transferir:").pack(pady=5)
    entry_monto_transferencia = tk.Entry(ventana)
    entry_monto_transferencia.pack(pady=5)
    tk.Label(ventana, text="Ingrese PIN:").pack(pady=5)
    entry_pin_transferencia = tk.Entry(ventana, show="*")
    entry_pin_transferencia.pack(pady=5)
    tk.Button(ventana, text="Confirmar", command=confirmar_transferencia).pack(pady=10)

    ventana.mainloop()

if __name__ == "__main__":
    iniciar_cajero()
