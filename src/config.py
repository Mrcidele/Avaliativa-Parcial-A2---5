"""Configurações padrão do sistema de monitoramento de ocupação."""

# Modelo YOLO pré-treinado no dataset COCO (80 classes). A versão "n" (nano)
# é a mais leve e roda em tempo real até em CPU.
MODELO_PADRAO = "yolov8n.pt"

# No COCO, a classe 0 é "person".
CLASSE_PESSOA = 0

# Detecções com confiança abaixo desse valor são descartadas.
CONFIANCA_MINIMA = 0.40

# Capacidade máxima da sala (número de pessoas).
CAPACIDADE_PADRAO = 10

# Faixas de ocupação (em % da capacidade) para o status exibido na tela.
LIMITE_ATENCAO = 0.70  # a partir de 70% -> ATENCAO
LIMITE_LOTADO = 1.00   # a partir de 100% -> LOTADO

# Cores em BGR (padrão do OpenCV).
COR_LIVRE = (80, 175, 76)     # verde
COR_ATENCAO = (0, 191, 255)   # amarelo/laranja
COR_LOTADO = (60, 60, 230)    # vermelho
COR_CAIXA = (255, 160, 0)     # azul claro para as bounding boxes
COR_TEXTO = (255, 255, 255)
COR_PAINEL = (30, 30, 30)

# Pasta onde ficam CSV, prints e vídeos gerados.
PASTA_RESULTADOS = "resultados"
