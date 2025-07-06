import multiprocessing
import time
from utils import generate_biometric_data, log_message, TOTAL_SAMPLES, SAMPLE_INTERVAL


class SimpleDataGenerator:
    """Generador simple de datos biométricos"""
    
    def __init__(self):
        self.pipes = []
        self.running = False
    
    def create_communication_channels(self, num_analyzers=3):
        """Crea canales de comunicación con analizadores"""
        self.pipes = []
        for i in range(num_analyzers):
            parent_conn, child_conn = multiprocessing.Pipe()
            self.pipes.append((parent_conn, child_conn))
        log_message(f"Creados {num_analyzers} canales de comunicación")
    
    def start_generation(self, test_mode=False):
        samples = 5 if test_mode else TOTAL_SAMPLES
        self.running = True

        log_message(f"Iniciando generación - {samples} muestras")
        for i in range(samples):
            data = generate_biometric_data()
            self.broadcast_data(data)
            print(f"[GEN] Muestra {i+1}/{samples} enviada")
            print(f"[GEN]                   {data['timestamp']} | frecuencia: {data['frecuencia']:3d} | presion: {data['presion']} | oxigeno(%): {data['oxigeno(%)']:3d}")
            time.sleep(SAMPLE_INTERVAL)
        log_message("Generación completada")
        self.send_termination_signal()
        
    def broadcast_data(self, data):
        """Envía datos a todos los analizadores"""
        for parent_conn, _ in self.pipes:
            parent_conn.send(data)
        
    def send_termination_signal(self):
        """Envía señal de terminación"""
        for parent_conn, _ in self.pipes:
            parent_conn.send(None)
    
    def get_child_connections(self):
        """Retorna conexiones para procesos hijo"""
        return [child_conn for parent_conn, child_conn in self.pipes]
    
    def cleanup(self):
        """Limpia recursos"""
        for parent_conn, child_conn in self.pipes:
            try:
                parent_conn.close()
                child_conn.close()
            except:
                pass

if __name__ == "__main__":
    # Prueba del generador
    generator = SimpleDataGenerator()
    generator.create_communication_channels(3)
    generator.start_generation(test_mode=True)  # Solo 5 muestras
    generator.cleanup()